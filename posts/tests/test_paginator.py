from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Oleg')
        cls.user = User.objects.create_user(username='Kseniya')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='06.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок', slug='testing_slug'
            )
        )

        cls.post1 = Post.objects.create(
            text='Тестовый текст 1',
            pub_date='07.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 1', slug='testing_slug_1'
            )
        )

        cls.post2 = Post.objects.create(
            text='Тестовый текст 2',
            pub_date='08.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 2', slug='testing_slug_2'
            )
        )

        cls.post3 = Post.objects.create(
            text='Тестовый текст 3',
            pub_date='09.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 3', slug='testing_slug_3'
            )
        )

        cls.post4 = Post.objects.create(
            text='Тестовый текст 4',
            pub_date='10.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 4', slug='testing_slug_4'
            )
        )

        cls.post5 = Post.objects.create(
            text='Тестовый текст 5',
            pub_date='11.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 5', slug='testing_slug_5'
            )
        )

        cls.post6 = Post.objects.create(
            text='Тестовый текст 6',
            pub_date='12.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 6', slug='testing_slug_6'
            )
        )

        cls.post7 = Post.objects.create(
            text='Тестовый текст 7',
            pub_date='13.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 7', slug='testing_slug_7'
            )
        )

        cls.post8 = Post.objects.create(
            text='Тестовый текст 8',
            pub_date='14.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 8', slug='testing_slug_8'
            )
        )

        cls.post9 = Post.objects.create(
            text='Тестовый текст 9',
            pub_date='15.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 9', slug='testing_slug_9'
            )
        )

        cls.post10 = Post.objects.create(
            text='Тестовый текст',
            pub_date='16.04.2021',
            author=cls.author,
            group=Group.objects.create(
                title='Заголовок 10', slug='testing_slug_10'
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author.force_login(self.author)

    def test_paginator(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)
