import caches

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Kseniya')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='06.04.2021',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index_page(self):
        response = self.authorized_client.get(reverse('index'))
        post_1 = Post.objects.create(
            text='Тестовый текст 1',
            author=self.user,
            group=self.group,
        )
        response_1 = self.authorized_client.get(reverse('index'))
        self.assertEqual(response, response_1)

        cache.clear()

        response_clear = self.authorized_client.get(reverse('index'))

        self.assertNotEqual(response, response_clear)
