from django import forms
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

FIRST_PAGE_COUNT = 10
SECOND_PAGE_COUNT = 1
AUTHOR = 'author'
GROUP_SLUG = 'the_group'
GROUP_TITLE = 'Тестовая группа 0'
GROUP_DESCRIPTION = 'Описание групппы'
ANOTHER_GROUP_SLUG = 'another_group1'
ANOTHER_GROUP_TITLE = 'Тестовая группа 1'
TEST_TEXT = 'Тестовый текст поста'


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=AUTHOR)
        cls.test_group0 = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.test_group1 = Group.objects.create(
            title=ANOTHER_GROUP_TITLE,
            slug=ANOTHER_GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        Post.objects.bulk_create([
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group1),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
            Post(text=TEST_TEXT, author=cls.test_user, group=cls.test_group0),
        ])
        cls.reverse_names = [
            reverse('posts:posts'),
            reverse('posts:groups', kwargs={'slug': GROUP_SLUG}),
            reverse('posts:profile', kwargs={'username': AUTHOR}),
        ]
        cls.templates_pages_names = {
            reverse('posts:posts'): 'posts/index.html',
            reverse('posts:groups', kwargs={'slug': GROUP_SLUG}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': AUTHOR}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': '1'}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}): (
                'posts/create_post.html'
            ),
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def setUp(self):
        self.user2 = User.objects.get(username=AUTHOR)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)
        self.post_created_from_test_group0 = (
            PostsPagesTests.test_group0.posts.get(id='2')
        )
        self.post_created_from_test_group1 = (
            PostsPagesTests.test_group1.posts.get(id='1')
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in (
            PostsPagesTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (
            self.authorized_client_author.get(reverse('posts:posts'))
        )
        posts_from_context = response.context['page_obj'][0]
        posts = Post.objects.all()[0]
        self.assertEqual(posts_from_context, posts)
        # Проверяем, что пост созданный от группы, есть на главной станице
    # posts_from_context1 = response.context['page_obj']
    # self.assertIn(self.post_created_from_test_group0, posts_from_context1)
    # self.assertIn(self.post_created_from_test_group1, posts_from_context1)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (
            self.authorized_client_author.get(
                reverse('posts:groups', kwargs={'slug': GROUP_SLUG})
            )
        )
        posts_from_context1 = response.context['page_obj'][0]
        filtered_by_test_group0 = (
            self.test_group0.posts.all()[0]
        )
        self.assertEqual(posts_from_context1, filtered_by_test_group0)

        # Проверяем, что пост созданный от группы, есть на странице группы
        posts_from_context0 = response.context['page_obj']
    # self.assertIn(self.post_created_from_test_group0, posts_from_context0)

        # Проверяем, что пост из группы another_group
        # не попал в группу the_group
        self.assertNotIn(
            self.post_created_from_test_group1, posts_from_context0
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.authorized_client_author.get(
                reverse('posts:profile', kwargs={'username': AUTHOR})
            )
        )
        posts_from_context1 = response.context['posts'][0]
        test_author = get_object_or_404(User, username=AUTHOR)
        filtered_by_test_author = (
            Post.objects.filter(author=test_author)[0]
        )
        self.assertEqual(posts_from_context1, filtered_by_test_author)

        # Проверяем, что пост созданный от группы, есть на странице автора
        posts_from_context0 = response.context['posts']
        self.assertIn(self.post_created_from_test_group0, posts_from_context0)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_client_author.get(
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            )
        )
        posts_from_context = response.context['post']
        test_post = Post.objects.get(id='1')
        self.assertEqual(posts_from_context, test_post)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (
            self.authorized_client_author.get(reverse('posts:post_create'))
        )
        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_edit_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = (
            self.authorized_client_author.get(
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            )
        )
        for value, expected in PostsPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        for reverse_name in PostsPagesTests.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), FIRST_PAGE_COUNT
                )

    def test_second_page_contains_some_records(self):
        for reverse_name in PostsPagesTests.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertGreaterEqual(
                    len(response.context['page_obj']), SECOND_PAGE_COUNT
                )
