import datetime
import random
from authentication.models import UserProfile
from django.utils import timezone
from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from .models import Vote
from .serializers import VoteSerializer
from base import mods
from base.models import Auth
from base.tests import BaseTestCase
from census.models import Census
from mixnet.models import Key
from voting.models import Voting, Question, QuestionOption



class StoreTextCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.question = Question(id=1,desc='test question', option_types=2)
        self.question.save()
        for i in range(5):
            opt = QuestionOption(question=self.question, option='option {}'.format(i+1))
            opt.save()

        self.voting = Voting(id=5001, name='test voting')

        self.voting.save()
        self.voting.question.add(self.question)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        self.voting.auths.add(a)

    def tearDown(self):
        super().tearDown()

    # def gen_voting(self, pk):
    #     question = Question(id=1,desc='test question', option_types=2)
    #     question.save()
    #     for i in range(5):
    #         opt = QuestionOption(question=question, option='option {}'.format(i+1))
    #         opt.save()

    #     voting = Voting(pk=pk, name='v' + str(pk), start_date=timezone.now(),
    #             end_date=timezone.now() + datetime.timedelta(days=1))
    #     voting.question.add(question)
    #     voting.save()
    #     return voting

    def get_or_create_user(self, pk):
        user, _ = UserProfile.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    # def gen_votes(self):
    #     votings = [random.randint(1, 5000) for i in range(10)]
    #     users = [random.randint(3, 5002) for i in range(50)]
    #     for v in votings:
    #         a = random.randint(2, 500)
    #         b = random.randint(2, 500)
    #         self.gen_voting(v)
    #         random_user = random.choice(users)
    #         user = self.get_or_create_user(random_user)
    #         self.login(user=user.username)
    #         census = Census(voting_id=v, voter_id=random_user)
    #         census.save()
    #         data = {
    #             "voting": v,
    #             "voter": random_user,
    #             "question_id": 1,
    #             "vote": [{ "a": a, "b": b }]
    #         }
    #         response = self.client.post('/store/', data, format='json')
    #         self.assertEqual(response.status_code, 200)

    #     self.logout()
    #     return votings, users

    def test_gen_vote_invalid(self):
        data = {
            "voting": 1,
            "voter": 1,
            "question_id": 1,
            "vote": [{ "a": 1, "b": 1 }]
        }
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_store_vote(self):
        VOTING_PK = 5001
        self.voting.start_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        census = Census(voting_id=VOTING_PK, voter_id=1)
        census.save()
        data = {
            "voting": VOTING_PK,
            "voter": 1,
            "question_id":1,
            "vote": [{ "a": '96', "b": '184' }]
        }
        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, VOTING_PK)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, '96')
        self.assertEqual(Vote.objects.first().b, '184')

    def test_vote(self):
        data = {
            "voting": 5001,
            "voter": 1,
            "question_id":1,
            "vote": [{ "a": '123', "b": '123' }]
        }
        response = self.client.get('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/store/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.count())

    # def test_filter(self):
    #     votings, voters = self.gen_votes()
    #     v = votings[0]

    #     response = self.client.get('/store/?voting_id={}'.format(v), format='json')
    #     self.assertEqual(response.status_code, 401)

    #     self.login(user='noadmin')
    #     response = self.client.get('/store/?voting_id={}'.format(v), format='json')
    #     self.assertEqual(response.status_code, 403)

    #     self.login()
    #     response = self.client.get('/store/?voting_id={}'.format(v), format='json')
    #     self.assertEqual(response.status_code, 200)
    #     votes = response.json()

    #     self.assertEqual(len(votes), Vote.objects.filter(voting_id=v).count())

    #     v = voters[0]
    #     response = self.client.get('/store/?voter_id={}'.format(v), format='json')
    #     self.assertEqual(response.status_code, 200)
    #     votes = response.json()

    #     self.assertEqual(len(votes), Vote.objects.filter(voter_id=v).count())

    # def test_hasvote(self):
    #     votings, voters = self.gen_votes()
    #     vo = Vote.objects.first()
    #     v = vo.voting_id
    #     u = vo.voter_id

    #     response = self.client.get('/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
    #     self.assertEqual(response.status_code, 401)

    #     self.login(user='noadmin')
    #     response = self.client.get('/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
    #     self.assertEqual(response.status_code, 403)

    #     self.login()
    #     response = self.client.get('/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
    #     self.assertEqual(response.status_code, 200)
    #     votes = response.json()

    #     self.assertEqual(len(votes), 1)
    #     self.assertEqual(votes[0]["voting_id"], v)
    #     self.assertEqual(votes[0]["voter_id"], u)

    def test_voting_status(self):
        data = {
            "voting": 5001,
            "voter": 1,
            "question_id": 1,
            "vote": [{ "a": '30', "b": '55' }]
        }
        census = Census(voting_id=5001, voter_id=1)
        census.save()
        # not opened
        self.voting.start_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # not closed
        self.voting.start_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        self.voting.end_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        # closed
        self.voting.end_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_duplicate_vote(self):
        data = {
                "voting": 5001,
                "voter": 1,
                "question_id": 1,
                "vote": [{ "a": '30', "b": '55' }]
            }
        census = Census(voting_id=5001, voter_id=1)
        census.save()
        # first vote
        self.voting.start_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        user = self.get_or_create_user(1)
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)
        # second vote
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 403)
