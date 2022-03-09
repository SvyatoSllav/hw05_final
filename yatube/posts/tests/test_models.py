from django.test import TestCase
from ..models import Post, Group, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='jonh',
            email='terrefregre.fddf@gmail.com',
            password='alta2002'
        )
        cls.group = Group.objects.create(
            title='smt',
            slug='ofoo',
            description='random-group'
        )
        cls.post = Post.objects.create(
            text=('foo' * 50),
            author=cls.author,
            group=cls.group
        )

    def test_post_str(self):
        post = PostsModelTest.post
        text = post.text[:15]
        str_text = post.__str__()
        self.assertEqual(text, str_text)

    def test_group_str(self):
        post = PostsModelTest.post
        group_title = post.group.title
        group_str = post.group.__str__()
        self.assertEqual(group_title, group_str)

    def test_verbose_names(self):
        post = PostsModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группы поста'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        post = PostsModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
