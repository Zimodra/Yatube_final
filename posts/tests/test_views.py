import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache
from posts.models import Group, Post, Follow, Comment

User = get_user_model()


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create_user(username='Oleg')
        cls.user = User.objects.create_user(username='Kseniya')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
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
            ),
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author.force_login(self.author)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug'}),
            'new.html': reverse('new_post'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug'}),
            'new.html': reverse('new_post'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_pages_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('new_post')
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_group(self):
        Group.objects.create(
            title='Другая группа',
            slug='post_slug'
        )
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'post_slug'})
        )
        response_index = self.authorized_client.get(
            reverse('index')
        )
        response_group = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'testing_slug'})
        )
        self.assertNotIn(
            self.post, response.context.get('page').paginator.object_list
        )
        self.assertIn(
            self.post, response_index.context.get('page').paginator.object_list
        )
        self.assertIn(
            self.post, response_group.context.get('page').paginator.object_list
        )

    def test_post_edit_correct_context(self):
        response_post_edit = self.authorized_author.get(
            reverse('post_edit', kwargs={'username': 'Oleg', 'post_id': 1})
        )
        group = Post.objects.filter(pk='1')
        context = {
            self.post.text: response_post_edit.context['form'].initial['text'],
            PagesTests.group.title: group[0].group.title
        }
        for value, expected in context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

        response_profile = self.authorized_author.get(
            reverse('profile', kwargs={'username': 'Oleg'})
        )
        self.assertEqual(
            response_profile.context['page'][0].text, self.post.text
        )
        self.assertEqual(
            response_profile.context['page'][0].author, self.post.author
        )
        self.assertEqual(
            response_profile.context['page'][0].group, self.post.group
        )
        self.assertEqual(
            response_profile.context['page'][0].image, self.post.image
        )
        response_post = self.authorized_author.get(
            reverse('post', kwargs={'username': 'Oleg', 'post_id': 1})
        )
        self.assertEqual(response_post.context['post'].text, self.post.text)
        self.assertEqual(
            response_post.context['post'].author, self.post.author
        )
        self.assertEqual(response_post.context['post'].group, self.post.group)

    def test_about_url(self):
        response_author = self.guest_client.get(
            reverse('about:author')
        )
        response_tech = self.guest_client.get(
            reverse('about:tech')
        )
        self.assertEqual(response_author.status_code, 200)
        self.assertEqual(response_tech.status_code, 200)

    def test_about_correct_template(self):
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_code_404(self):
        response = self.guest_client.get('index_test')
        self.assertEqual(response.status_code, 404)

    def test_index_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('index')
        )
        response_text = response.context['page'][0].text
        response_author = response.context['page'][0].author
        response_image = response.context['page'][0].image
        self.assertEqual(response_text, self.post.text)
        self.assertEqual(response_author, self.author)
        self.assertEqual(response_image, self.post.image)

    def test_follow_on_other_authors(self):
        follow_count = Follow.objects.count()
        Follow.objects.create(user=self.user, author=self.author)
        form_data = {
            'user': 'follower',
            'author': self.author,
        }
        response = self.authorized_client.get(
            reverse(
                'profile_follow', kwargs={'username': self.user}
            ), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('profile', kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_new_post_for_following(self):
        follow = Follow.objects.create(user=self.user, author=self.author)
        post = Post.objects.create(
            text='Пост автора',
            author=self.author,
        )
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertIn(post, response.context.get('page').paginator.object_list)

    def test_authorized_user_can_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий',
        }
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={'username': self.user, 'post_id': 1}), data=form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
    
    def test_cache_index_page(self):
        response_1 = self.authorized_client.get(reverse('index'))
        post_1 = Post.objects.create(
            text='Текстовый текст 1', 
            author=self.author
        )
        response_2 = self.authorized_client.get(reverse('index'))

        self.assertEqual(
            response_1.content, response_2.content)

        cache.clear()

        response_3 = self.authorized_client.get(reverse('index'))
        
        self.assertNotEqual(
            response_2.content, response_3.content)
