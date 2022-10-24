from django.test import TestCase
from django.contrib.auth import get_user_model
# from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


CREATE_USER_URL = '/rest-auth/registration/'
TOKEN_URL = '/rest-auth/login/'

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the user api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """test creating user with valid payload is successfull"""
        payload = {
            'username': 'test',
            'email': 'test@test.com',
            'password1': 'ghbrjkmxbr',
            'password2': 'ghbrjkmxbr'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(username=payload['username'])
        self.assertTrue(user.check_password(payload['password1']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists"""
        payload1 = {
            'email': 'test@test.com',
            'password': 'ghbrjkmxbr',
            'username': 'test'
        }

        payload2 = {
            'username': 'test',
            'email': 'test@test.com',
            'password1': 'ghbrjkmxbr',
            'password2': 'ghbrjkmxbr'
        }

        create_user(**payload1)

        res = self.client.post(CREATE_USER_URL, payload2)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token created for user"""
        payload = {
            'email': 'test@test.com',
            'password': 'ghbrjkmxbr',
            'username': 'test'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, {'username': payload['username'],
                                           'password': payload['password']})
        self.assertIn('key', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credential(self):
        """Test that token is not created when
           invalid credential are given"""
        payload = {
            'email': 'test@test.com',
            'password': 'ghbrjkmxbr',
            'username': 'test'
        }
        create_user(**payload)

        payload2 = {
            'email': 'test@test.com',
            'password': 'ghbrjkmxbr'
        }
        res = self.client.post(TOKEN_URL, payload2)

        self.assertNotIn('key', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exists"""
        payload = {
            'email': 'test@test.com',
            'password': 'ghbrjkmxbr'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('key', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



ME_URL = '/rest-auth/user/'

class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='ghbrjkmxbr',
            username='test',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'pk': self.user.pk,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
                    "username": "test_new",
                    "first_name": "first_test_new",
                    "last_name": "second_test_new"
                  }

        res = self.client.patch(ME_URL, payload)
        self.assertEqual(self.user.username, payload['username'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
