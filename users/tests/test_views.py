
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('users:signup')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        self.login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

    def test_signup_GET(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_POST_valid(self):
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_POST_invalid(self):
        
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'wrongpass'
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)  
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_GET(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_POST_valid(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(self.login_url, self.login_data)
        self.assertEqual(response.status_code, 302)  

    def test_login_POST_invalid(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200) 