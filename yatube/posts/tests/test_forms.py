import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
            kwargs={'username': f'{self.user}'})
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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormImage(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Имя')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.form = PostForm()
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_with_image(self):
        """Проверяем, что создается пост с картинкой"""
        posts_count = Post.objects.count()
        uploaded = self.uploaded
        form_data = PostForm(data={
            'text': 'Тестовый текст',
            'image': uploaded,
        })
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data.data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif',
            ).exists()
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user.username])
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)


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
