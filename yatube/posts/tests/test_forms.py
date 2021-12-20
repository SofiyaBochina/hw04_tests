from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

TEST_USERNAME = 'auth'
TEST_SLUG = 'test-slug'
CREATED_POST_TEXT = 'Новый пост'
EDITED_POST_TEXT = 'Изменённый пост'

POST_DETAIL = 'posts:post_detail'
PROFILE = 'posts:profile'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Редирект после создания нового поста и добавление в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': CREATED_POST_TEXT,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(POST_CREATE),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            PROFILE,
            kwargs={'username': TEST_USERNAME}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=CREATED_POST_TEXT,
            ).exists()
        )

    def test_post_edit(self):
        """Изменения в БД после редактирования поста."""
        form_data = {
            'text': EDITED_POST_TEXT,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(POST_EDIT, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            POST_DETAIL,
            kwargs={'post_id': self.post.id}
        ))
        self.assertTrue(
            Post.objects.filter(
                text=EDITED_POST_TEXT,
            ).exists()
        )
