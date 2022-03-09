from django.http import Http404
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from ..models import Post, Group, Comment, Follow
from django.urls import reverse
from django import forms
from django.core.cache import cache

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_2 = User.objects.create_user(username='test_user_2')
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='smt',
            slug='test_slug',
            description='random-group'
        )
        cls.image = ('posts/d60625a5fd7f47e21bd862554e0efbe0'
                     '--large-art-prints-cartoon-network.jpg')
        cls.number_of_created_posts = 13
        for _ in range(cls.number_of_created_posts):
            cls.post = Post.objects.create(
                text=('foo'),
                author=cls.user,
                group=cls.group,
                image=cls.image
            )
        cls.another_group = Group.objects.create(
            title='another_group',
            slug='new_slug',
            description='random-group_2'
        )
        cls.group_slug = cls.group.slug
        cls.post_id = cls.post.id
        cls.username = cls.user.username
        cls.index_url = (
            'posts:index',
            'posts/index.html',
            None
        )
        cls.group_list_url = (
            'posts:group_list',
            'posts/group_list.html',
            {'slug': cls.group_slug}
        )
        cls.profile_url = (
            'posts:profile',
            'posts/profile.html',
            {'username': cls.username}
        )
        cls.post_detail_url = (
            'posts:post_detail',
            'posts/post_detail.html',
            {'post_id': cls.post_id}
        )
        cls.post_comment_url = (
            'posts:add_comment',
            None,
            {'post_id': cls.post_id}
        )
        cls.post_edit_url = (
            'posts:post_edit',
            'posts/create_post.html',
            {'post_id': cls.post_id}
        )
        cls.post_create_url = (
            'posts:create',
            'posts/create_post.html',
            None
        )
        cls.index_follow = (
            'posts:follow_index',
            None,
            None
        )
        cls.profile_follow_url = (
            'posts:profile_follow',
            None,
            {'username': cls.user_2.username}
        )
        cls.profile_unfollow_url = (
            'posts:profile_unfollow',
            None,
            {'username': cls.user_2.username}
        )
        cls.pages_urls = (
            cls.index_url,
            cls.group_list_url,
            cls.profile_url,
            cls.post_detail_url,
            cls.post_edit_url,
            cls.post_create_url
        )
        cls.paginator_url = (
            cls.index_url,
            cls.group_list_url,
            cls.profile_url
        )
        cls.pages_with_post_images = (
            cls.index_url,
            cls.profile_url,
            cls.group_list_url,
        )
        cls.all_pks = [post.id for post in Post.objects.filter(
            image__isnull=False)
        ]

    def test_pages_uses_correct_templates(self):
        for reverse_name, template, args in PostsPagesTests.pages_urls:
            with self.subTest(reverse_name=reverse_name):
                response = PostsPagesTests.authorized_client.get(
                    reverse(reverse_name, kwargs=args)
                )
                self.assertTemplateUsed(response, template)

    def test_context_on_index_page(self):
        response = self.authorized_client.get(
            reverse(PostsPagesTests.index_url[0])
        )
        first_object = response.context['page_obj'][0]
        context_field = {
            'Последние обновления на сайте': response.context.get('title'),
            'foo': first_object.text,
            'test_user': first_object.author.username,
            'smt': first_object.group.title
        }
        for field, field_value in context_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, field_value)

    def test_context_on_group_list_page(self):
        response = self.authorized_client.get(
            reverse(PostsPagesTests.group_list_url[0],
                    kwargs={'slug': PostsPagesTests.group_slug}
                    )
        )
        first_object = response.context['page_obj'][0]
        context_field = {
            PostsPagesTests.post.group: first_object.group,
            'foo': first_object.text,
            'test_user': first_object.author.username,
            'smt': first_object.group.title
        }
        for field, field_value in context_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, field_value)

    def test_context_on_profile_page(self):
        response = self.authorized_client.get(
            reverse(PostsPagesTests.profile_url[0],
                    kwargs={'username': PostsPagesTests.username}
                    )
        )
        first_object = response.context['page_obj'][0]
        number_of_posts = PostsPagesTests.number_of_created_posts
        context_field = {
            PostsPagesTests.user: first_object.author,
            'test_user': response.context['username'],
            number_of_posts: response.context['number_of_posts'],
            'foo': first_object.text,
            'smt': first_object.group.title
        }
        for field, field_value in context_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, field_value)

    def test_context_on_post_detail_page(self):
        response = self.authorized_client.get(
            reverse(PostsPagesTests.post_detail_url[0],
                    kwargs={'post_id': PostsPagesTests.post_id}
                    )
        )
        post_title = PostsPagesTests.post.text[:30]
        number_of_posts = PostsPagesTests.number_of_created_posts
        context_field = {
            PostsPagesTests.post: response.context['post'],
            post_title: response.context['title'],
            number_of_posts: response.context['number_of_posts']
        }
        for field, field_value in context_field.items():
            with self.subTest(field=field):
                self.assertEqual(field, field_value)

    def test_form_of_create_post_page(self):
        response = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.post_create_url[0])
        )
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_form_of_editing_post_page(self):
        response = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.post_edit_url[0],
                    kwargs={'post_id': PostsPagesTests.post_id})
        )
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_of_create_posts(self):
        response = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.post_create_url[0])
        )
        is_edit = response.context.get('is_edit')
        self.assertFalse(is_edit)

    def test_context_of_editing_posts(self):
        response = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.post_edit_url[0],
                    kwargs={'post_id': PostsPagesTests.post_id})
        )
        is_edit = response.context.get('is_edit')
        self.assertTrue(is_edit)

    def test_first_page_contains_ten_records(self):
        for address, _, args in PostsPagesTests.paginator_url:
            with self.subTest(address=address):
                response = PostsPagesTests.authorized_client.get(
                    reverse(address, kwargs=args)
                )
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        for address, _, args in PostsPagesTests.paginator_url:
            with self.subTest(address=address):
                response = PostsPagesTests.authorized_client.get(
                    reverse(address, kwargs=args) + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_are_post_with_group_exists_in_appropriate_pages(self):
        for address, _, args in PostsPagesTests.paginator_url:
            with self.subTest(address=address):
                response = PostsPagesTests.authorized_client.get(
                    reverse(address, kwargs=args)
                )
                for number_of_post in range(10):
                    self.assertIsNotNone(
                        response.context['page_obj'][number_of_post]
                    )
                response = PostsPagesTests.authorized_client.get(
                    reverse(address, kwargs=args) + '?page=2'
                )
                for number_of_post in range(3):
                    self.assertIsNotNone(
                        response.context['page_obj'][number_of_post]
                    )

    def test_post_does_not_exist_in_incorrect_group(self):
        number_of_post_group = len((PostsPagesTests.group.title.split()))
        self.assertEqual(number_of_post_group, 1)

    def test_image_in_pages_with_posts(self):
        for address, _, args in PostsPagesTests.pages_with_post_images:
            with self.subTest(address=address):
                response = PostsPagesTests.authorized_client.get(
                    reverse(address, kwargs=args)
                )
                for number_of_post in range(10):
                    post = response.context['page_obj'][number_of_post]
                    self.assertEqual(post.image, PostsPagesTests.image)
                response = PostsPagesTests.authorized_client.get(
                    reverse(address, kwargs=args) + '?page=2'
                )
                for number_of_post in range(3):
                    post = response.context['page_obj'][number_of_post]
                    self.assertEqual(post.image, PostsPagesTests.image)

    def test_post_detail_image(self):
        for pk in PostsPagesTests.all_pks:
            response = PostsPagesTests.authorized_client.get(
                reverse(
                    PostsPagesTests.post_detail_url[0],
                    kwargs={'post_id': pk}
                )
            )
            post_image = response.context['post'].image
            self.assertEqual(post_image, PostsPagesTests.image)

    def test_new_comment_is_created(self):
        form_data = {
            'text': 'test_text'
        }
        PostsPagesTests.authorized_client.post(
            reverse(
                PostsPagesTests.post_comment_url[0],
                kwargs=PostsPagesTests.post_comment_url[2]
            ),
            data=form_data,
            follow=True
        )
        try:
            new_comment = get_object_or_404(Comment, text='test_text')
        except Http404:
            new_comment = None
        self.assertIsNotNone(new_comment)

    def test_index_post_is_in_cache_after_deleting(self):
        response_1 = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.index_url[0])
        )
        content_before_post_deletion = response_1.content
        post_to_delete = Post.objects.get(pk=1)
        post_to_delete.delete()
        response_2 = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.index_url[0])
        )
        content_after_post_deletion = response_2.content
        self.assertEqual(
            content_before_post_deletion,
            content_after_post_deletion)

    def test_index_post_is_not_in_content_if_cache_cleared(self):
        response_1 = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.index_url[0])
        )
        content_before_post_deletion = response_1.content
        post_to_delete = Post.objects.get(pk=1)
        post_to_delete.delete()
        cache.clear()
        response_2 = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.index_url[0])
        )
        content_after_post_deletion = response_2.content
        self.assertNotEqual(
            content_before_post_deletion,
            content_after_post_deletion)

    def test_authorized_user_can_follow(self):
        author_username = PostsPagesTests.profile_follow_url[2]['username']
        author = User.objects.get(username=author_username)
        PostsPagesTests.authorized_client.get(
            reverse(
                PostsPagesTests.profile_follow_url[0],
                kwargs={'username': author_username})
        )
        following = Follow.objects.filter(
            author=author,
            user=PostsPagesTests.user
        ).exists()
        self.assertTrue(following)

    def test_authorized_user_can_unfollow(self):
        author_username = PostsPagesTests.profile_follow_url[2]['username']
        author = User.objects.get(username=author_username)
        PostsPagesTests.authorized_client.get(
            reverse(
                PostsPagesTests.profile_follow_url[0],
                kwargs={'username': author_username})
        )
        PostsPagesTests.authorized_client.get(
            reverse(
                PostsPagesTests.profile_unfollow_url[0],
                kwargs={'username': author_username})
        )
        following = Follow.objects.filter(
            author=author,
            user=PostsPagesTests.user
        ).exists()
        self.assertFalse(following)

    def test_new_posts_from_following_are_exists(self):
        author_username = PostsPagesTests.profile_follow_url[2]['username']
        author = User.objects.get(username=author_username)
        PostsPagesTests.authorized_client.get(
            reverse(
                PostsPagesTests.profile_follow_url[0],
                kwargs={'username': author_username})
        )
        response = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.index_follow[0])
        ).content
        Post.objects.create(
            text='fdfsfsdfsdfsdfsdffvdcvcx',
            author=author,
        )
        response_2 = PostsPagesTests.authorized_client.get(
            reverse(PostsPagesTests.index_follow[0])
        ).content
        self.assertNotEqual(response, response_2)

    def test_new_posts_from_following_are_exists(self):
        author_username = PostsPagesTests.profile_follow_url[2]['username']
        author = User.objects.get(username=author_username)
        response = PostsPagesTests.authorized_client_2.get(
            reverse(PostsPagesTests.index_url[0])
        ).content
        Post.objects.create(
            text='fdfsfsdfsdfsdfsdffvdcvcx',
            author=author,
        )
        response_2 = PostsPagesTests.authorized_client_2.get(
            reverse(PostsPagesTests.index_url[0])
        ).content
        self.assertEqual(response, response_2)
