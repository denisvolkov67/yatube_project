import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Post, Group, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Поэты',
            slug='test-slug',
            description='Это описание группы Поэты'
        )
        cls.user = User.objects.create_user(
            username='Zenon', email='Zenon@mail.com', password='top_secret'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_new.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст',
                group__title='Поэты',
                image='posts/small_new.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        Post.objects.create(
            text='текст',
            author=self.user,
            group=self.group
        )
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small_edit.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст NEW',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'Zenon', 'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('post', kwargs={'username': 'Zenon', 'post_id': 1}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Текст NEW',
                group__title='Поэты',
                image='posts/small_edit.gif'
            ).exists()
        )

    def test_add_comment(self):
        """Авторизированный пользователь может комментировать посты."""
        comment_count = Comment.objects.count()
        post = Post.objects.create(text='Teкст', author=self.user)
        form_data = {
            'text': 'Комментарий',
            'author': self.user,
            'post': post,
        }
        response = self.authorized_client.post(
            reverse('add_comment',
                    kwargs={'username': self.user.username,
                            'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': post.id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Комментарий',
                author=self.user,
                post=post
            ).exists()
        )
