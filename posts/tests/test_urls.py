from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class GroupURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Oleg')
        cls.user = User.objects.create_user(username='Kseniya')

        Group.objects.create(
            title='Заголовок',
            slug='test_slug'
        )

        Post.objects.create(
            text='Тестовый текст',
            pub_date='06.04.2021',
            author=cls.author,
            group=Group.objects.create(title='test', slug='testing_slug')
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author.force_login(self.author)

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('index')
        )
        self.assertEqual(response.status_code, 200)

    def test_group_list_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('group', kwargs={'slug': 'test_slug'})
        )
        self.assertEqual(response.status_code, 200)

    def test_group_detail_url_exists_at_desired_location_authorized(self):
        response = self.authorized_client.get(
            reverse('new_post')
        )
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug'}),
            'new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_username_url_exists_at_desired_location(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'Kseniya'})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_id_edit_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get(
            reverse('post_edit', kwargs={
                'username': 'Test', 'post_id': 1
            }
            ), follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/Test/1/edit/')

    def test_post_id_edit_url_post_author(self):
        response = self.authorized_author.get(
            reverse('post_edit', kwargs={'username': 'Oleg', 'post_id': 1})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_uses_correct_template(self):
        response = self.authorized_author.get(
            reverse('post_edit', kwargs={'username': 'Oleg', 'post_id': 1})
        )
        self.assertTemplateUsed(response, 'new.html')
