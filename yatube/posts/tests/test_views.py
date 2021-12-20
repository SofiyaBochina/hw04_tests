from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import NUM_OF_PAGES

from ..models import Group, Post, User

TEST_SLUG = 'test-slug'
TEST_USERNAME = 'auth'

INDEX = 'posts:index'
POST_CREATE = 'posts:post_create'
GROUP_LIST = 'posts:group_list'
POST_DETAIL = 'posts:post_detail'
PROFILE = 'posts:profile'
POST_EDIT = 'posts:post_edit'

TEMPLATES = [
    'posts/index.html',
    'posts/group_list.html',
    'posts/profile.html',
    'posts/post_detail.html',
    'posts/create_post.html',
    'posts/create_post.html'
]


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
        for i in range(1, 13):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
                id=i
            )
        cls.reverses = [
            reverse(INDEX),  # 0
            reverse(GROUP_LIST, kwargs={'slug': TEST_SLUG}),  # 1
            reverse(PROFILE, kwargs={'username': TEST_USERNAME}),  # 2
            reverse(POST_DETAIL, kwargs={'post_id': cls.post.id}),  # 3
            reverse(POST_EDIT, kwargs={'post_id': cls.post.id}),  # 4
            reverse(POST_CREATE)  # 5
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for i in range(len(TEMPLATES)):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertTemplateUsed(response, TEMPLATES[i])

    def test_paginator_and_context_on_pages_with_paginator(self):
        """Паджинатор отображает 10 постов, передается нужный контекст."""
        for i in range(0, 2):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.client.get(self.reverses[i])
                self.assertEqual(len(
                    response.context['page_obj']),
                    NUM_OF_PAGES
                )
                self.assertEqual(
                    response.context['page_obj'].object_list[0].text,
                    self.post.text
                )

    def test_context_on_pages_with_post(self):
        """На страницы, где есть пост, передаётся нужный контекст"""
        for i in range(3, 4):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertEqual(response.context['post'].text, self.post.text)

    def test_context_on_post_create(self):
        """На страницу создания нового поста передается нужный контекст."""
        response = self.authorized_client.get(self.reverses[5])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
