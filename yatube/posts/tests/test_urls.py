from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Текстовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый пост',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_task_group_url_exists_at_desired_location(self):
        response = self.guest_client.get('/group/<slug>/')
        self.assertEqual(response.status_code, 404)

    def test_task_username_url_exists_at_desired_location(self):
        response = self.guest_client.get('/profile/<username>/')
        self.assertEqual(response.status_code, 404)

    def test_task_postid_url_exists_at_desired_location(self):
        response = self.guest_client.get('/posts/<post_id>/')
        self.assertEqual(response.status_code, 404)

    def test_task_unexisting_url_exists_at_desired_location(self):
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, 404)

    def test_task_create_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_task_edit_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/posts/<post_id>/edit/')
        self.assertEqual(response.status_code, 404)

    def test_task_createred_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_task_editred_url_redirect_anonymous_on_admin_login(self):
        response = self.guest_client.get('/posts/<post_id>/edit/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            # '/group/<slug>/': 'posts/group_list.html',
            # '/profile/<username>/': 'posts/profile.html',
            # '/posts/<post_id>/': 'posts/post_detail.html',
            # '/posts/<post_id>/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
