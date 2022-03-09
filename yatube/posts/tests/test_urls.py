from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='jonh')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='smt',
            slug='test_slug',
            description='random-group'
        )
        cls.post = Post.objects.create(
            text='Some Text',
            author=cls.user,
            group=cls.group
        )
        cls.group_slug = cls.group.slug
        cls.username = cls.user.username
        cls.post_id = cls.post.id
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group_slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post_id}/', 'posts/post_detail.html'),
        )
        cls.private_urls = (
            (f'/posts/{cls.post_id}/edit/', 'posts/create_post.html'),
            ('/create/', 'posts/create_post.html')
        )
        cls.post_url = f'/posts/{StaticURLTests.post_id}/'
        cls.post_edit_url = f'/posts/{StaticURLTests.post_id}/edit/'

    def test_public_pages(self):
        for address, _ in StaticURLTests.public_urls:
            with self.subTest(address=address):
                response = StaticURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_uses_correct_template(self):
        for address, template in StaticURLTests.public_urls:
            with self.subTest(address=address):
                response = StaticURLTests.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_private_urls_uses_correct_template(self):
        for address, template in StaticURLTests.private_urls:
            with self.subTest(address=address):
                response = StaticURLTests.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_only_author_can_edit(self):
        response = StaticURLTests.authorized_client.get(
            StaticURLTests.post_edit_url
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_authorized_user_can_not_edit(self):
        response = StaticURLTests.guest_client.get(
            StaticURLTests.post_edit_url
        )
        self.assertRedirects(response, StaticURLTests.post_url)

    def test_only_authorized_can_create_post(self):
        response = StaticURLTests.authorized_client.get(
            '/create/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_authtorized_can_not_create_post(self):
        response = StaticURLTests.guest_client.get(
            '/create/'
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_404_on_not_existing_page(self):
        response = StaticURLTests.authorized_client.get(
            '/not_exists/'
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
