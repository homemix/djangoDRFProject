from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from .models import Item
from django.contrib.auth.models import User


class ItemAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user to authenticate against
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # URL for user registration
        # self.registration_url = reverse('dj-rest-auth-registration')
        self.registration_url = reverse('rest_register')
        # URL for login and obtaining a JWT token
        self.token_url = reverse('token_obtain_pair')

        # URL for CRUD operations
        self.item_list_url = reverse('item-list')

        # Sample data for Item
        self.item_data = {
            'category': 'Electronics',
            'subcategory': 'Mobile Phones',
            'name': 'iPhone',
            'amount': 5
        }
        # Create an initial item in the DB for testing GET and PUT
        self.item = Item.objects.create(**self.item_data)

    def test_user_registration(self):
        """Test that a user can register successfully"""
        url = reverse('rest_register')
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        response = self.client.post(self.registration_url, registration_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # self.assertIn('access', response.data)  # Check for JWT access token in response

    def test_login_and_get_jwt_token(self):
        """Test that a user can log in and receive a JWT token"""
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpassword'
        }, format='json')

        # Check for a successful response and that it returns tokens
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Store the access token for authenticated requests
        self.access_token = response.data['access']

    def test_create_item_with_auth(self):
        """Test that a logged-in user can create an item"""
        # First, log in to get the JWT token
        self.test_login_and_get_jwt_token()

        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Test creating a new item with authenticated request
        new_item_data = {
            'category': 'Appliances',
            'subcategory': 'Refrigerator',
            'name': 'Samsung Fridge',
            'amount': 15
        }
        response = self.client.post(self.item_list_url, new_item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure that the item was created
        self.assertEqual(Item.objects.count(), 2)
        self.assertEqual(Item.objects.get(id=response.data['id']).name, 'Samsung Fridge')

    def test_access_item_list_without_auth(self):
        """Test that unauthenticated users cannot access the item list"""
        response = self.client.get(self.item_list_url, format='json')
        # Check for a 401 Unauthorized status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_item_list_with_auth(self):
        """Test that authenticated users can access the item list"""
        # First, log in to get the JWT token
        self.test_login_and_get_jwt_token()

        # Authenticate the client with the JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Access the item list
        response = self.client.get(self.item_list_url, format='json')

        # Check for a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the correct number of items are returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'iPhone')

    def test_update_item_with_auth(self):
        """Test that authenticated users can update an item"""
        # Log in to get the JWT token
        self.test_login_and_get_jwt_token()

        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # URL for updating the specific item
        url = reverse('item-detail', kwargs={'pk': self.item.id})

        updated_item_data = {
            'category': 'Electronics',
            'subcategory': 'Mobile Phones',
            'name': 'iPhone X',
            'amount': 10
        }

        # Send a PUT request to update the item
        response = self.client.put(url, updated_item_data, format='json')

        # Check for a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the item was updated correctly
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'iPhone X')
        self.assertEqual(self.item.amount, 10)

    def test_delete_item_with_auth(self):
        """Test that authenticated users can delete an item"""
        # Log in to get the JWT token
        self.test_login_and_get_jwt_token()

        # Authenticate the client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # URL for deleting the specific item
        url = reverse('item-detail', kwargs={'pk': self.item.id})

        # Send a DELETE request to delete the item
        response = self.client.delete(url)

        # Check for a 204 No Content status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the item was deleted
        self.assertEqual(Item.objects.count(), 0)
