from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from bank.models import *
from bank.serializers import *

ACCOUNT_URL = reverse('bank:account-list')

class PublicBankApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBankApiTest(TestCase):
    """Test authenticated API accept"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='ghbrjkmxbr',
            username='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_account(self):
        url = ACCOUNT_URL + str(self.user.id) + '/'
        res = self.client.get(url)
        serializer = AccountSerializer(Account.objects.get(user=self.user))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_permission_denied_for_list_accounts(self):
        res = self.client.get(ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_not_found_another_account(self):
        user2 = get_user_model().objects.create_user(
            username = 'test2',
            password = 'ghbrjkmxbr2'
        )
        url = ACCOUNT_URL + str(user2.id) + '/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
