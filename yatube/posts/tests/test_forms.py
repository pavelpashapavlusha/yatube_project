from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from posts.forms import CommentForm


class PostFormTest(TestCase):
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

    def test_create_task(self):
        """Валидная форма создает запись в Task."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста"""
        post = Post.objects.create(
            author=self.user,
            text='Тестовая пост',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый тест новый',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id}
            ))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый тест новый',
                group=self.group.id
            ).exists())
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id
            ).exists())


class PostCommentTest(TestCase):
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

    def test_comment_appears_in_post(self):
        form = CommentForm(data={
            'text': 'comment',
        })
        self.assertTrue(form.is_valid())

        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=form.data,
            follow=True,
        )

        self.assertEqual(self.post.comments.last().text, form.data['text'])

        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[self.post.pk])
        )
