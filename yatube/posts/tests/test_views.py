from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
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
            reverse('posts:index'),  # 0
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),  # 1
            reverse('posts:profile', kwargs={'username': 'auth'}),  # 2
            reverse('posts:post_detail', kwargs={'post_id': 1}),  # 3
            reverse('posts:post_edit', kwargs={'post_id': 1}),  # 4
            reverse('posts:post_create')  # 5
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html'
        ]
        for i in range(len(templates)):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.authorized_client.get(self.reverses[i])
                self.assertTemplateUsed(response, templates[i])

    def test_paginator_and_context_on_pages_with_paginator(self):
        """Паджинатор отображает 10 постов, передается нужный контекст."""
        for i in range(0, 2):
            with self.subTest(reverse_name=self.reverses[i]):
                response = self.client.get(self.reverses[i])
                self.assertEqual(len(response.context['page_obj']), 10)
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
