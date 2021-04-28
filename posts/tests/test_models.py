from django.test import TestCase
from posts.models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='06.04.2021',
            author=User.objects.create_user(username='Тестовое имя'),
            group=Group.objects.create(title='test')
        )

    def test_object_name_is_title_field(self):
        post = PostModelTest.post
        exp_obj_name = f"{post.author} - {post.pub_date} - {post.text[:15]}"
        self.assertEquals(exp_obj_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
        )

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Дайте короткое название заголовку',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
