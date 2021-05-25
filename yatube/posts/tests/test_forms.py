from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Поэты',
            slug='test-slug',
            description='Это описание группы Поэты'
        )
        cls.user = User.objects.create_user(
            username='Zenon', email='Zenon@mail.com', password='top_secret'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
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
                group__title='Поэты'
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
        form_data = {
            'text': 'Текст NEW',
            'group': self.group.id,
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
                group__title='Поэты'
            ).exists()
        )
