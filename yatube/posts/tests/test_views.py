import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Follow, Group, Post

User = get_user_model()


class InitTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Поэты',
            slug='test-slug',
            description='Это описание группы Поэты'
        )
        cls.group_mayak = Group.objects.create(
            title='Маяковский',
            slug='mayak',
            description='Это описание группы'
        )
        cls.author = User.objects.create_user(
            username='Zenon', email='Zenon@mail.com', password='top_secret')
        cls.user = User.objects.create_user(username='user')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='текст',
            author=cls.author,
            group=cls.group,
            image=uploaded
        )


class PostPagesTests(InitTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.authorized_client_user = Client()
        self.authorized_client_user.force_login(self.user)
        cache.clear()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates_names = {
            reverse('index'): 'posts/index.html',
            reverse('group', kwargs={'slug': 'test-slug'}): 'posts/group.html',
            reverse('profile', kwargs={'username': 'Zenon'}):
                'posts/profile.html',
            reverse('post', kwargs={'username': 'Zenon', 'post_id': 1}):
                'posts/post.html',
            reverse('new_post'): 'posts/edit.html',
            reverse('post_edit', kwargs={'username': 'Zenon', 'post_id': 1}):
                'posts/edit.html',
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse('index'))
        post = response.context['page'][0]
        self.assertEqual(post, self.post)

    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )
        group = response.context['group']
        post = response.context['page'][0]
        self.assertEqual(post, self.post)
        self.assertEqual(group, self.group)

    def test_new_page_shows_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_page_shows_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('post_edit', kwargs={'username': 'Zenon', 'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['action'], 'post_edit')

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('profile', kwargs={'username': 'Zenon'})
        )
        post = response.context['page'][0]
        author = response.context['author']
        self.assertEqual(post, self.post)
        self.assertEqual(author, self.author)

    def test_post_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('post', kwargs={'username': 'Zenon', 'post_id': 1}))
        post = response.context['post']
        self.assertEqual(post, self.post)

    def test_group_pages_dont_show_another_post(self):
        """Шаблон group не показывает посты из другой группы."""
        response = self.authorized_client_author.get(
            reverse('group', kwargs={'slug': 'mayak'})
        )
        group = response.context['group']
        count_post = response.context['page'].object_list.count()
        self.assertEqual(group, self.group_mayak)
        self.assertEqual(count_post, 0)

    def test_group_pages_dont_show_another_post_after_edit(self):
        """Шаблон group не показывает посты из другой группы
        после редактирования"""
        post = Post.objects.get(id=1)
        post.group = self.group_mayak
        post.save()
        response = self.authorized_client_author.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )
        count_post = len(response.context['page'].object_list)
        self.assertEqual(count_post, 0)
        response = self.authorized_client_author.get(
            reverse('group', kwargs={'slug': 'mayak'})
        )
        group = response.context['group']
        received_post = response.context['page'].object_list[0]
        self.assertEqual(group, self.group_mayak)
        self.assertEqual(received_post, post)

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей"""
        count_follow = Follow.objects.count()
        self.authorized_client_user.get(
            reverse('profile_follow', kwargs={'username': 'Zenon'})
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)

    def test_profile_unfollow(self):
        """Авторизованный пользователь может отписываться от других
        пользователей"""
        Follow.objects.create(user=self.user, author=self.author)
        count_follow = Follow.objects.count()
        self.authorized_client_user.get(
            reverse('profile_unfollow', kwargs={'username': 'Zenon'})
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_page_shows_correct_context(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан"""
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client_user.get(reverse('follow_index'))
        post = response.context['page'][0]
        self.assertEqual(post, self.post)

    def test_follow_page_dont_shows_another_post(self):
        """Новая запись пользователя не появляется в ленте тех, кто на него
        не подписан"""
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client_author.get(reverse('follow_index'))
        count_post = len(response.context['page'].object_list)
        self.assertEqual(count_post, 0)

    def test_cache_index_page(self):
        """Кэш главной страницы работает правильно"""
        response = self.authorized_client_author.get(reverse('index'))
        cached_content = response.content
        Post.objects.create(text='Новый пост', author=self.author)
        response = self.authorized_client_author.get(reverse('index'))
        self.assertEqual(cached_content, response.content)
        cache.clear()
        response = self.authorized_client_author.get(reverse('index'))
        self.assertNotEqual(cached_content, response.content)


class PaginatorViewsTest(InitTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(1, 13):
            Post.objects.create(
                text=f'текст {i}',
                author=cls.author,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_page_contains_count_records(self):
        pages_counts = {
            reverse('index'): 10,
            reverse('index') + '?page=2': 3,
            reverse('group', kwargs={'slug': 'test-slug'}): 10,
            reverse('group', kwargs={'slug': 'test-slug'}) + '?page=2': 3,
        }
        for reverse_name, count_expected in pages_counts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                count_post = len(response.context.get('page').object_list)
                self.assertEqual(count_post, count_expected)
