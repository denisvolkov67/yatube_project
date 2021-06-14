from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='т' * 50,
            author=User.objects.create_user(
                username='Zenon', email='Zenon@mail.com', password='top_secret'
            )
        )
        Group.objects.create(
            title='Поэты',
            slug='test-slug',
            description='Это описание группы Поэты'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_without_post = Client()
        self.authorized_client_without_post.force_login(
            User.objects.create_user(username='mayak'))
        cache.clear()

    def test_urls_anonymous_exists_at_desired_location(self):
        """Страницы доступны анонимному пользователю"""
        address_status_code_names = {
            '/': 200,
            '/group/test-slug/': 200,
            '/new/': 302,
            '/Zenon/': 200,
            '/Zenon/1/': 200,
            '/Zenon/1/edit/': 302,
            '/Zenon/1/comment/': 302,
            '/none-author/': 404,
        }
        for address, status_code in address_status_code_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_exists_at_desired_location(self):
        """Страницы доступны авторизированному пользователю"""
        address_status_code_names = {
            '/new/': 200,
            '/Zenon/1/edit/': 200,
        }
        for address, status_code in address_status_code_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_without_post_exists_at_desired_location(self):
        """Страницы доступны авторизированному пользователю без постов"""
        address_status_code_names = {
            '/Zenon/1/edit/': 302,
        }
        for address, status_code in address_status_code_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_without_post.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_template_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group.html',
            '/Zenon/': 'posts/profile.html',
            '/Zenon/1/': 'posts/post.html',
            '/new/': 'posts/edit.html',
            '/Zenon/1/edit/': 'posts/edit.html',
        }
        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_no_access_redirect(self):
        """URL-адрес использует соответствующий redirect при
недостаточных правах."""
        url_template_names = {
            '/Zenon/1/edit/': '/Zenon/1/',
        }
        for address, redirect in url_template_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_without_post.get(address)
                self.assertRedirects(response, redirect)
