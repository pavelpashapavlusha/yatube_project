from django import forms
from django.core.cache import cache
from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post, User


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Test_author')
        cls.user = User.objects.create_user(username='Test_user')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='offtopic',
            description='TestDesc',
        )
        cls.post = Post.objects.create(
            text='PostTestText',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostsViewsTests.author)

    def test_pages_uses_correct_context(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:posts'): 'posts/index.html',
            reverse('posts:groups', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts'))
        paginator = Paginator(Post.objects.order_by('-pub_date'), 10)
        expect = list(paginator.get_page(1).object_list)
        self.assertEqual(
            list(response.context['page_obj'].object_list), expect)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:groups', kwargs={'slug': self.group.slug}))
        paginator = Paginator(Post.objects.order_by('-group'), 10)
        expect = list(paginator.get_page(1).object_list)
        self.assertEqual(
            response.context['page_obj'].object_list, expect)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        post = response.context['post']
        expect = Post.objects.get(id=self.post.pk)
        self.assertEqual(post, expect)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        paginator = Paginator(Post.objects.order_by('-author_id'), 10)
        expect = list(paginator.get_page(1).object_list)
        self.assertEqual(
            response.context['page_obj'].object_list, expect)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_contains_correct_context(self):
        """Доп. проверка страниц на содержание указанного поста."""
        response = self.guest_client.get(reverse(
            'posts:posts'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group.title, self.group.title)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Имя')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        test_post = Post.objects.create(
            text='test',
            author=self.user
        )
        cached_index = self.client.get(reverse('posts:posts')).content
        test_post.delete()
        self.assertEqual(
            cached_index,
            self.client.get(reverse('posts:posts')).content
        )
        cache.clear()
        self.assertNotEqual(
            cached_index,
            self.client.get(reverse('posts:posts')).content
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='Noone_author')
        cls.user_not_author = User.objects.create_user(username='Just_Noone')
        cls.user_not_followed = User.objects.create_user(
            username='Not_followed'
        )
        cls.group_used = Group.objects.create(
            title='Test group used',
            slug='Test_group_used'
        )
        cls.group_single_used = Group.objects.create(
            title='Test group single used',
            slug='Test_group_single_use'
        )
        Post.objects.create(
            text='Test text',
            group=cls.group_used,
            author=cls.user_author,
        )
        cls.single_post = Post.objects.create(
            text='Test text with single group',
            group=cls.group_single_used,
            author=cls.user_author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_not_author = Client()
        self.authorized_not_followed = Client()
        self.authorized_author.force_login(self.user_author)
        self.authorized_not_author.force_login(self.user_not_author)
        self.authorized_not_followed.force_login(self.user_not_followed)

    def test_follow_unfollow(self):
        not_followed = Follow.objects.filter(
            author=self.user_author.id,
            user=self.user_not_author.id
        ).exists()
        self.assertFalse(not_followed)
        self.authorized_not_author.get(
            reverse('posts:profile_follow', args=[self.user_author])
        )
        followed = Follow.objects.filter(
            author=self.user_author.id,
            user=self.user_not_author.id
        ).exists()
        self.assertTrue(followed)
        self.authorized_not_author.get(
            reverse('posts:profile_unfollow', args=[self.user_author])
        )
        unfollowed = Follow.objects.filter(
            author=self.user_author.id,
            user=self.user_not_author.id
        ).exists()
        self.assertFalse(unfollowed)

    def test_post_view_followed(self):
        self.authorized_not_author.get(
            reverse('posts:profile_follow', args=[self.user_author])
        )
        self.follow_post = Post.objects.create(
            text='Follower post text',
            author=self.user_author,
        )
        response_follower = self.authorized_not_author.get(
            reverse('posts:follow_index')
        )
        objects = response_follower.context['page_obj'].object_list
        self.assertIn(self.follow_post, objects)
        response_not_follower = self.authorized_not_followed.get(
            reverse('posts:follow_index')
        )
        objects = response_not_follower.context['page_obj'].object_list
        self.assertNotIn(self.follow_post, objects)
