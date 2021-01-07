import datetime
import time

from django.test import TestCase

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from base.tests import BaseTestCase
from .models import SuggestingForm

from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from authentication.models import UserProfile
from census.models import Census
from .views import check_unresolved_post_data, is_future_date
# from voting.tests import VotingTestCase
from mixnet.models import Auth

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time


from base import mods

NOW_DATE = timezone.now().date()
S_DATE = NOW_DATE + datetime.timedelta(weeks=1)
M_DATE = NOW_DATE - datetime.timedelta(days=31)
E_DATE = NOW_DATE - datetime.timedelta(weeks=1)

def sumalista(listaNumeros):
    laSuma = 0
    for i in listaNumeros:
        laSuma = laSuma + i
    return laSuma

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#-----------------------------TEST DEL CONTROLADOR DE SUGERENCIAS-----------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

class SuggestingFormTests(TestCase):
    def setUp(self):
        super().setUp()
        session = self.client.session
        session['voter_id'] = 1
        session.save()

    def tearDown(self):
        super().tearDown()

    def test_was_published_recently_more_than_month(self):
        now = timezone.now().date()
        past_date = now - datetime.timedelta(weeks=4, days=1)
        past_suggesting_form = SuggestingForm(send_date=past_date, suggesting_date=now)
        self.assertIs(past_suggesting_form.was_published_recently(), False)

    def test_was_published_recently_last_week(self):
        now = timezone.now().date()
        past_date = now - datetime.timedelta(weeks=1)
        past_suggesting_form = SuggestingForm(send_date=past_date, suggesting_date=now)
        self.assertIs(past_suggesting_form.was_published_recently(), True)

    def test_get_suggesting_detail_success(self):
        SuggestingForm.objects.create(id=1, user_id=1, title="Suggesting title", suggesting_date=S_DATE, content="Suggesting content...", send_date=NOW_DATE)
        response = self.client.get(reverse('suggesting-detail', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['suggesting'].id, 1)
        self.assertEqual(response.context['suggesting'].user_id, 1)
        self.assertEqual(response.context['suggesting'].title, "Suggesting title")
        self.assertEqual(response.context['suggesting'].suggesting_date, S_DATE)
        self.assertEqual(response.context['suggesting'].content, "Suggesting content...")
        self.assertEqual(response.context['suggesting'].send_date, NOW_DATE)
        self.assertEqual(response.context['suggesting'].is_approved, None)

    def test_get_suggesting_detail_not_found(self):
        response = self.client.get(reverse('suggesting-detail', args=(2,)), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_send_suggesting_form_success(self):
        data = {'suggesting-title': 'Suggestsing', 'suggesting-date': '2021-01-08', 'suggesting-content': 'Full suggesting content...'}
        initital_suggesting_counter = SuggestingForm.objects.all().count()

        response = self.client.post('/booth/suggesting/send/', data, follow=True)

        afterpost_suggesting_counter = SuggestingForm.objects.all().count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(afterpost_suggesting_counter, initital_suggesting_counter + 1)

    def test_send_suggesting_form_with_error(self):
        data = {'suggesting-title': 'Suggestsing', 'suggesting-date': '2020-12-01', 'suggesting-content': 'Full suggesting content...'}
        initital_suggesting_counter = SuggestingForm.objects.all().count()

        response = self.client.post('/booth/suggesting/send/', data, follow=True)

        afterpost_suggesting_counter = SuggestingForm.objects.all().count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(afterpost_suggesting_counter, initital_suggesting_counter)

    def test_check_unresolved_post_data(self):
        context = {}
        session = self.client.session
        session['title'] = "Suggesting title"
        session['suggesting_date'] = "2020-12-01"
        session['content'] = "Suggesting content..."
        session['errors'] = "Suggesting error msg!"
        session.save()

        context['post_data'] = check_unresolved_post_data(session)

        self.assertEqual(context['post_data']['title'], "Suggesting title")
        self.assertEqual('title' in session, False)
        self.assertEqual('suggesting_date' in session, False)
        self.assertEqual('content' in session, False)
        self.assertEqual('errors' in session, False)

    def test_check_unresolved_post_data_with_empty_session(self):
        context = {}
        session = self.client.session

        context['post_data'] = check_unresolved_post_data(session)

        self.assertEqual(not context['post_data'], True)

    def test_is_future_date_with_past_date(self):
        date = timezone.now().date() - datetime.timedelta(weeks=1)
        self.assertEqual(is_future_date(date), False)

    def test_is_future_date_with_now_date(self):
        date = timezone.now().date()
        self.assertEqual(is_future_date(date), False)

    def test_is_future_date_with_future_date(self):
        date = timezone.now().date() + datetime.timedelta(weeks=1)
        self.assertEqual(is_future_date(date), True)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------TEST DE INTERFAZ DE LOGIN-----------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

class LoginInterfaceTests(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.base.tearDown()
        self.driver.quit()

    def test_interface_login_success(self):
        self.driver.get(f'{self.live_server_url}/booth/')
        self.driver.find_element_by_id('username').send_keys("noadmin")
        self.driver.find_element_by_id('password').send_keys("qwerty",Keys.ENTER)

        #Cuando el login es correcto, se redirige a la página de dashboard
        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/dashboard/')

    def test_interface_login_fail(self):
        #Se loguea con un usuario inexistente
        self.driver.get(f'{self.live_server_url}/booth/')
        self.driver.find_element_by_id('username').send_keys("badvoter1")
        self.driver.find_element_by_id('password').send_keys("badpass1",Keys.ENTER)

        #Cuando el login es incorrecto, se mantiene en la página y aparece una alerta
        alert = self.driver.find_element_by_id('loginFail')
        self.assertEquals(alert.text,'El usuario no está registrado en el sistema.')
        self.assertEquals(self.driver.current_url,f'{self.live_server_url}/booth/dashboard/')

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#--------------------------------------TEST DE BOOTH------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

class BoothTests(TestCase):
    def setUp(self):
        #Create user
        self.client = APIClient()
        mods.mock_query(self.client)
        u = UserProfile(id=1, username='voter1', sex='M')
        u.set_password('123')
        u.save()
        token= mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '123'})
        #Add session token
        session = self.client.session
        session['user_token'] = token
        session.save()
        #Create voting

        #Create question 1
        q1 = Question(id=1,desc='Unique option question', option_types=1)
        q1.save()
        for i in range(3):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()

        #Create question 2
        q2 = Question(id=2,desc='Multiple option question', option_types=2)
        q2.save()
        for i in range(4):
            opt = QuestionOption(question=q2, option='option {}'.format(i+1))
            opt.save()

        #Create question 3
        q3 = Question(id=3,desc='Rank order scale question', option_types=3)
        q3.save()
        for i in range(5):
            opt = QuestionOption(question=q3, option='option {}'.format(i+1))
            opt.save()

        v = Voting(id=1, name='Single question voting',desc='Single question voting...', points=1, start_date=timezone.now())
        v.save()
        v.question.add(q1), v.question.add(q2), v.question.add(q3)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'base'})    
        a.save()
        v.auths.add(a)
        Voting.create_pubkey(v)
        #Add user to census
        census = Census(voting_id=v.id, voter_id=u.id)
        census.save()

    def tearDown(self):
        super().tearDown()

    def test_get_multiple_question_voting_success(self):
        response = self.client.get(reverse('voting', args=(1,1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['next_question_id'], 2)
        response = self.client.get(reverse('voting', args=(1,2,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['next_question_id'], 3)
        response = self.client.get(reverse('voting', args=(1,3,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIs(response.context['last_question'], True)
        #TODO more asserts

    def test_get_multiple_question_voting_not_found(self):
        response = self.client.get(reverse('voting', args=(2,2,)), follow=True)
        self.assertEqual(response.status_code, 404)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------TEST LOGIN-----------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class LoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = UserProfile(id=1, username='voter1', sex='M')
        u.set_password('123')
        u.save()
        token= mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '123'})
        #Add session token
        session = self.client.session
        session['user_token'] = token
        session['voter_id']=u.id
        session['username']=u.username
        session.save()

    def tearDown(self):
        super().tearDown()

    def test_get_logout(self):
        session = self.client.session
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('user_token' in session, False)
        self.assertEqual('voter_id' in session, False)
        self.assertEqual('username' in session, False)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------TEST DASHBOARD----------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class DashboardTest(TestCase):
    def setUp(self):
        #Create user
        self.client = APIClient()
        mods.mock_query(self.client)
        u = UserProfile(id=1, username='voter1', sex='M')
        u.set_password('123')
        u.save()
        token= mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '123'})
        #Add session token
        session = self.client.session
        session['user_token'] = token
        session['voter_id'] = u.id
        session.save()
        #Create voting 1

        #Create question 1
        q1 = Question(id=1,desc='Unique option question', option_types=1)
        q1.save()
        for i in range(3):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()

        #Create question 2
        q2 = Question(id=2,desc='Multiple option question', option_types=2)
        q2.save()
        for i in range(4):
            opt = QuestionOption(question=q2, option='option {}'.format(i+1))
            opt.save()

        #Create question 3
        q3 = Question(id=3,desc='Rank order scale question', option_types=3)
        q3.save()
        for i in range(5):
            opt = QuestionOption(question=q3, option='option {}'.format(i+1))
            opt.save()
        
        v1 = Voting(id=1, name='Single question voting',desc='Single question voting...', points=1, start_date=timezone.now())
        v1.save()
        v1.question.add(q1), v1.question.add(q2), v1.question.add(q3)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'base'})
        a.save()
        v1.auths.add(a)
        Voting.create_pubkey(v1)

        #Create voting 2

        #Create question 4
        q4 = Question(id=4, desc='Unique option question 2', option_types=1)
        q4.save()
        for i in range(3):
            opt = QuestionOption(question=q4, option='option {}'.format(i+1))
            opt.save()

        v2 = Voting(id=2, name='Single question voting 2',desc='Single question voting...', points=1, start_date=M_DATE, end_date=E_DATE)
        v2.save()
        v2.question.add(q4)
        v2.auths.add(a)
        Voting.create_pubkey(v2)

        #Add user to census
        census1 = Census(voting_id=v1.id, voter_id=u.id)
        census1.save()
        census2 = Census(voting_id=v2.id, voter_id=u.id)
        census2.save()

        #Create suggestion 1
        s1 = SuggestingForm(id=1, user_id=u.id, title="Suggesting title", suggesting_date=S_DATE, content="Suggesting content...", send_date=NOW_DATE, is_approved=True)
        s1.save()

    def tearDown(self):
        super().tearDown()

    def test_dashboard_details(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vot_dis']), 1)
        self.assertEquals(sumalista(response.context['votaciones_por_meses']), 1)
        self.assertEquals(len(response.context['months']), 12)
        #self.assertEqual(response.context['tipo_votaciones'][0], 0)
        #self.assertEqual(response.context['tipo_votaciones'][1], 0)
        #self.assertEqual(response.context['tipo_votaciones'][2], 0)
        self.assertEqual(len(response.context['approved_suggestions']), 1)
        self.assertEqual(len(response.context['recent_suggestions']), 1)