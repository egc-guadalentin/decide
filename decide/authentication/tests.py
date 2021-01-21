from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from .models import UserProfile
from rest_framework.authtoken.models import Token
from django.db.utils import DataError

from base import mods


class AuthTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        u = UserProfile(username='voter1', sex='M', style='N')
        u.set_password('123')
        u.save()

        u2 = UserProfile(username='admin', sex='F', style='N')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_changestyle(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json().get('token')
        
        data = {'token': token, 'style': 'C'}
        response = self.client.post('/authentication/changestyle/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_changestyle_tritanopia(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json().get('token')
        
        data = {'token': token, 'style': 'T'}
        response = self.client.post('/authentication/changestyle/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_changestyle_night(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json().get('token')
        
        data = {'token': token, 'style': 'O'}
        response = self.client.post('/authentication/changestyle/', data, format='json')
        self.assertEqual(response.status_code, 200)    

    def test_register_bad_request_bad_sex(self):
        data = {'username': 'admin', 'password': 'admin' }
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1', 'sex': 'NB', 'style': 'N'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_changestyle_inexistent_style(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json().get('token')
        
        data = {'token': token, 'style': 'W'}
        response = self.client.post('/authentication/changestyle/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_changestyle_inexistent_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)
        
        data = {'token': 'inventado', 'style': 'N'}
        response = self.client.post('/authentication/changestyle/', data, format='json')
        self.assertEqual(response.status_code, 400)

    # Test del método de registro que se usa en la vista signin.html en /sign-in/
    def test_signin_username_required(self):
        data = {'password':'test1234','sex':'M','style':'T'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signin_password_required(self):
        data = {'username':'user1234','sex':'M','style':'O'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signin_sex_required(self):
        data = {'username':'user1234','password':'test1234','style':'T','email':'user1234@gmail.com'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signin_style_required(self):
        data = {'username':'user1234','password':'test1234','sex':'F','email':'user1234@gmail.com'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)
        
    def test_signin_email_format_invalid(self):
        data = {'username':'user1234','password':'test1234','sex':'F','style':'T','email':'prueba'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signin_password_format_invalid(self):
        data = {'username':'user1234','password':'test','sex':'F','style':'T','email':'prueba@gmail.com'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signin_user_already_exist(self):
        data = {'username':'admin','password':'admin','sex':'M','style':'N','email':'admin@gmail.com'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_signin_success(self):
        data = {'username':'user1234','password':'test1234','sex':'F','style':'T','email':'prueba@gmail.com'}
        response = self.client.post('/authentication/register/', data, format='json')
        self.assertEqual(response.status_code, 200)