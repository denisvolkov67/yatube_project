from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            text='т' * 50,
            author=User.objects.create_user(
                username='Zenon', email='Zenon@mail.com', password='top_secret'
            )
        )

    def test_object_name_is_text_field(self):
        """В поле __str__  объекта post записано значение поля
post.text[:15]."""
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Group.objects.create(
            title='Поэты',
            slug='test-slug',
            description='Это описание группы Поэты'
        )

    def test_object_name_is_title_field(self):
        """В поле __str__  объекта group записано значение поля
group.title."""
        post = self.post
        expected_object_name = post.title
        self.assertEqual(expected_object_name, str(post))
