from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class PostListViewTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='adamthethird', password='passkey123')

    def test_can_list_posts(self):
        adamthethird = User.objects.get(username='adamthethird')
        Post.objects.create(owner=adamthethird, title='a title')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_create_post(self):
        self.client.login(username='adamthethird', password='passkey123')
        adamthethird = User.objects.get(username='adamthethird')
        response = self.client.post('/posts/', {'title': 'a title', 'owner': adamthethird.id})
        count = Post.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cannot_creat_post(self):
        response = self.client.post('/posts/', {'title': 'a title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDetailViewTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='adam', password='pass')
        User.objects.create_user(username='brian', password='pass')

    def test_can_retrieve_post_using_valid_id(self):
        adam = User.objects.get(username='adam')
        Post.objects.create(owner=adam, title='a title')

        response = self.client.get('/posts/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'a title')

    def test_can_not_retrieve_post_using_invalid_id(self):
        response = self.client.get('/posts/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_post(self):
        adam = User.objects.get(username='adam')
        Post.objects.create(owner=adam, title='a title')
        self.client.login(username='adam', password='pass')
        response = self.client.put('/posts/1/', {'title': 'a new title', 'owner': adam.id})
        post = Post.objects.filter(pk=1).first()
        self.assertEqual(post.title, 'a new title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_own_post(self):
        adam = User.objects.get(username='adam')
        brian = User.objects.get(username='brian')
        Post.objects.create(owner=adam, title='a title')
        self.client.login(username='brian', password='pass')
        response = self.client.put('/posts/1/', {'title': 'a new title', 'owner': adam.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)