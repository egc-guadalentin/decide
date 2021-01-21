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
from .views import check_unresolved_post_data, is_future_date, get_participation_percentage
from voting.tests import VotingTestCase
from mixnet.models import Auth
from store.models import Vote

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

    def test_get_suggesting_detail_success_pending(self):
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

    def test_get_suggesting_detail_success_approved(self):
        SuggestingForm.objects.create(id=1, user_id=1, title="Suggesting title", is_approved=True, suggesting_date=S_DATE, content="Suggesting content...", send_date=NOW_DATE)
        response = self.client.get(reverse('suggesting-detail', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['suggesting'].id, 1)
        self.assertEqual(response.context['suggesting'].user_id, 1)
        self.assertEqual(response.context['suggesting'].title, "Suggesting title")
        self.assertEqual(response.context['suggesting'].suggesting_date, S_DATE)
        self.assertEqual(response.context['suggesting'].content, "Suggesting content...")
        self.assertEqual(response.context['suggesting'].send_date, NOW_DATE)
        self.assertEqual(response.context['suggesting'].is_approved, True)

    def test_get_suggesting_detail_success_rejected(self):
        SuggestingForm.objects.create(id=1, user_id=1, title="Suggesting title", is_approved=False, suggesting_date=S_DATE, content="Suggesting content...", send_date=NOW_DATE)
        response = self.client.get(reverse('suggesting-detail', args=(1,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['suggesting'].id, 1)
        self.assertEqual(response.context['suggesting'].user_id, 1)
        self.assertEqual(response.context['suggesting'].title, "Suggesting title")
        self.assertEqual(response.context['suggesting'].suggesting_date, S_DATE)
        self.assertEqual(response.context['suggesting'].content, "Suggesting content...")
        self.assertEqual(response.context['suggesting'].send_date, NOW_DATE)
        self.assertEqual(response.context['suggesting'].is_approved, False)

    # def test_get_suggesting_detail_access_blocked(self):
    #     session = self.client.session
    #     session['voter_id'] = 2
    #     session.save()
    #     SuggestingForm.objects.create(id=1, user_id=1, title="Suggesting title", suggesting_date=S_DATE, content="Suggesting content...", send_date=NOW_DATE)
    #     response = self.client.get(reverse('suggesting-detail', args=(1,)), follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.context['suggesting'].id, 1)
    #     self.assertEqual(response.context['suggesting'].user_id, 1)
    #     self.assertEqual(response.context['suggesting'].title, "Suggesting title")
    #     self.assertEqual(response.context['suggesting'].suggesting_date, S_DATE)
    #     self.assertEqual(response.context['suggesting'].content, "Suggesting content...")
    #     self.assertEqual(response.context['suggesting'].send_date, NOW_DATE)
    #     self.assertEqual(response.context['suggesting'].is_approved, None)

    def test_get_suggesting_detail_not_found(self):
        response = self.client.get(reverse('suggesting-detail', args=(2,)), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_send_suggesting_form_success(self):
        future_date = timezone.now().date() + datetime.timedelta(weeks=1)
        date = future_date.strftime("%Y-%m-%d")
        data = {'suggesting-title': 'Suggestsing', 'suggesting-date': date, 'suggesting-content': 'Full suggesting content...'}
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

    def test_send_suggesting_form_not_post_method(self):
        response = self.client.get('/booth/suggesting/send/')
        self.assertEqual(response.status_code, 302)

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

# #---------------------------------------------------------------------------------------------
# #---------------------------------------------------------------------------------------------
# #--------------------------------------TEST DE BOOTH------------------------------------------
# #---------------------------------------------------------------------------------------------
# #---------------------------------------------------------------------------------------------

class BoothTests(TestCase):
    def setUp(self):
        # Create user
        self.client = APIClient()
        mods.mock_query(self.client)
        u = UserProfile(id=1, username='voter1', sex='M')
        u.set_password('123')
        u.save()
        token= mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '123'})
        # Add session token
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

    def test_user_has_already_voted(self):
        vote = Vote.objects.create(voting_id=1, voter_id=1, question_id=1, sex="M", a="96", b="184")
        vote.save()
        number_of_votes = Vote.objects.filter(voting_id=1, question_id=1, voter_id=1).count()
        self.assertEqual(number_of_votes, 1)
        response = self.client.get(reverse('voting', args=(1,1,)), follow=True)
        self.assertEqual(response.status_code, 200)

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#--------------------------------------TEST LOGIN---------------------------------------------
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
        #Create user 1
        self.client = APIClient()
        mods.mock_query(self.client)
        u1 = UserProfile(id=1, username='voter1', sex='M')
        u1.set_password('123')
        u1.save()
        token1 = mods.post('authentication', entry_point='/login/', json={'username':'voter1', 'password': '123'})
        #Add session token 1
        session = self.client.session
        session['user_token'] = token1
        session['voter_id'] = u1.id
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

        #Create question 5
        q5 = Question(id=5, desc='Multiple option question 2', option_types=2)
        q5.save()
        for i in range(4):
            opt = QuestionOption(question=q5, option='option {}'.format(i+1))
            opt.save()

        #Create question 6
        q6 = Question(id=6, desc='Rank order scale question 2', option_types=3)
        q6.save()
        for i in range(5):
            opt = QuestionOption(question=q6, option='option {}'.format(i+1))
            opt.save()

        v2 = Voting(id=2, name='Single question voting 2',desc='Single question voting...', points=1, start_date=M_DATE, end_date=E_DATE)
        v2.save()
        v2.question.add(q4), v2.question.add(q5), v2.question.add(q6)
        v2.auths.add(a)
        Voting.create_pubkey(v2)

        #Add user to census
        census1 = Census(voting_id=v1.id, voter_id=u1.id)
        census1.save()
        census2 = Census(voting_id=v2.id, voter_id=u1.id)
        census2.save()

        #Create suggestion 1
        s1 = SuggestingForm(id=1, user_id=u1.id, title="Suggesting title", suggesting_date=S_DATE, content="Suggesting content...", send_date=NOW_DATE, is_approved=True)
        s1.save()

    def tearDown(self):
        super().tearDown()

    def test_dashboard_details(self):
        #Create user 2
        self.client = APIClient()
        mods.mock_query(self.client)
        u2 = UserProfile(id=2, username='voter2', sex='M')
        u2.set_password('123')
        u2.save()
        token2 = mods.post('authentication', entry_point='/login/', json={'username':'voter2', 'password': '123'})
        #Add session token 2
        session = self.client.session
        session['user_token'] = token2
        session['voter_id'] = u2.id
        session.save()
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_available_votings_user(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(len(response.context['vot_dis']), 1)

    def test_last_12_months_votings_user(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEquals(sumalista(response.context['votaciones_por_meses']), 1)
        self.assertEquals(len(response.context['months']), 12)

    def test_votings_user_by_type(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(response.context['tipo_votaciones'][0], 1)
        self.assertEqual(response.context['tipo_votaciones'][1], 1)
        self.assertEqual(response.context['tipo_votaciones'][2], 1)

    def test_suggestions_approved(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(len(response.context['approved_suggestions']), 1)

    def test_suggestions_recent(self):
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(len(response.context['recent_suggestions']), 1)

    def test_dashboard_details_no_votings_available(self):
        vote1 = Vote.objects.create(voting_id=1, voter_id=1, question_id=1, sex="M", a="96", b="184")
        vote1.save()
        vote2 = Vote.objects.create(voting_id=2, voter_id=1, question_id=2, sex="M", a="58", b="196")
        vote2.save()
        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_vot_dis'], True)

    def test_get_participation_percentage(self):
        x = [0,1,2,1,0,1,0,0,0,2,1,0]
        y = [0,2,4,0,0,1,1,1,0,2,4,0]

        res = get_participation_percentage(x, y)

        self.assertEqual(res[0], 0)
        self.assertEqual(res[3], 100)
        self.assertEqual(res[10], 25)