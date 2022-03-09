import shutil
import tempfile

from django.http import Http404
from django.shortcuts import get_object_or_404
from http import HTTPStatus
from django.test import TestCase, Client, override_settings
from ..models import Post, Group, Comment
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='foo',
            group=cls.group,
            author=cls.user
        )
        cls.post_id = cls.post.id
        cls.post_comment_url = (
            'posts:add_comment',
            None,
            {'post_id': cls.post_id}
        )
        cls.all_pk = set([post.id for post in Post.objects.all()])

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_post_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test_text',
            'group': PostCreateFormTest.group.id
        }
        response = PostCreateFormTest.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        all_pk_with_new_post = set([post.id for post in Post.objects.all()])
        new_posts_pks = all_pk_with_new_post.difference(
            PostCreateFormTest.all_pk
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'test_user'})
        )
        for pk in new_posts_pks:
            self.assertTrue(
                Post.objects.filter(
                    id=pk
                )
            )

    def test_form_post_edit(self):
        post_id = PostCreateFormTest.post.id
        old_post_text = PostCreateFormTest.post.text
        form_data = {
            'text': 'new_text',
            'group': PostCreateFormTest.group.id,
        }
        PostCreateFormTest.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=post_id)
        new_post_text = post.text
        self.assertNotEqual(new_post_text, old_post_text)

    def test_not_authorized_user_can_not_edit(self):
        post_id = PostCreateFormTest.post.id
        response = PostCreateFormTest.guest_client.get(
            f'/posts/{post_id}/edit/'
        )
        form_data = {
            'text': 'new_text',
            'group': PostCreateFormTest.group.id,
        }
        PostCreateFormTest.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, f'/posts/{post_id}/')
        try:
            new_post = get_object_or_404(Post, text='new_text')
        except Http404:
            new_post = 404
        self.assertEqual(new_post, HTTPStatus.NOT_FOUND)

    def test_not_authtorized_can_not_create_post(self):
        response = PostCreateFormTest.guest_client.get(
            '/create/'
        )
        form_data = {
            'text': 'test_text',
            'group': PostCreateFormTest.group.id
        }
        PostCreateFormTest.guest_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        try:
            new_post = get_object_or_404(Post, text='test_text')
        except Http404:
            new_post = 404
        self.assertEqual(new_post, HTTPStatus.NOT_FOUND)

    def test_creating_post_with_image(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'post_with_image',
            'group': PostCreateFormTest.group.id,
            'image': uploaded
        }
        PostCreateFormTest.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='post_with_image',
            group=PostCreateFormTest.group.id,
            image='posts/small.gif'
        ).exists())

    def test_only_authorized_used_can_comment(self):
        form_data = {
            'text': 'test_text'
        }
        PostCreateFormTest.authorized_client.post(
            reverse(
                PostCreateFormTest.post_comment_url[0],
                kwargs=PostCreateFormTest.post_comment_url[2]
            ),
            data=form_data,
            follow=True
        )
        new_comment = Comment.objects.get(text='test_text')
        self.assertTrue(new_comment)

    def test_not_authorized_used_can_not_comment(self):
        form_data = {
            'text': 'test_text'
        }
        PostCreateFormTest.guest_client.post(
            reverse(
                PostCreateFormTest.post_comment_url[0],
                kwargs=PostCreateFormTest.post_comment_url[2]
            ),
            data=form_data,
            follow=True
        )
        try:
            new_comment = get_object_or_404(Comment, text='test_text')
        except Http404:
            new_comment = None
        self.assertIsNone(new_comment)
