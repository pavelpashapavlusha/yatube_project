from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.user1 = User.objects.create(username='author')
        cls.post = Post.objects.create(
            author=cls.user1,
            text='Тестовый текст',
        )
        cls.group = Group.objects.create(
            title='Group-title',
            slug='group-slug',
            description='Описание group',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

    def test_create_post(self):
        """Валидная форма создает запись в post."""
        # Подсчитаем количество записей в post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            ('posts:profile'), kwargs={'username': 'author'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user1,
                text=self.post.text,
                group=self.group.id,
            ).exists()
        )
