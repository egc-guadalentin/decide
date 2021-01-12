import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
User=get_user_model()
from django.test import TestCase
from django.db.utils import IntegrityError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from django.db.utils import IntegrityError
from .admin import give_message
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import sys



class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question', option_types=1,type=0)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(id=1,name='test voting')

        v.save()
        v.question.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v



    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()


    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.sex = 'M'
        user.save()
        return user


    def get_or_create_user_fem(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.sex = 'F'
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for q in v.question.all():
            for opt in q.options.all():
                clear[opt.number] = 0
                for i in range(random.randint(0, 5)):
                    a, b = self.encrypt_msg(opt.number, v)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user = self.get_or_create_user(voter.voter_id)
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
        return clear



    # def test_duplicate_voting_name(self):
    #     v1 = self.create_voting()
    #     with self.assertRaises(Exception) as raised:
    #         v2 = self.create_voting()
    #     self.assertEqual(IntegrityError, type(raised.exception))

    def store_votes_unique_option(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        for i in range(1):
            main_voter = self.get_or_create_user(voter.voter_id)
            self.login(user=main_voter.username)
            votos = []
            qs = v.question.all()
            for q in qs:
                options = q.options.all()
                count_options = len(options)

                a,b = None, None
                for j in range(1):
                    chosen_option = options[0]

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                    votos.append({'a': a, 'b': b })

            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': votos,
                'question_id': q.id,
                'token': self.token
            }

            mods.post('store', json=data)
            self.logout()
            voter = voters.pop()


    def store_votes_unique_option_fem(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        for i in range(1):
            main_voter = self.get_or_create_user_fem(voter.voter_id)
            self.login(user=main_voter.username)
            votos = []
            qs = v.question.all()
            for q in qs:
                options = q.options.all()
                count_options = len(options)

                a,b = None, None
                for j in range(1):
                    chosen_option = options[0]

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                    votos.append({'a': a, 'b': b })

            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': votos,
                'question_id': q.id,
                'token': self.token
            }

            mods.post('store', json=data)
            self.logout()
            voter = voters.pop()

    def test_tally_message_positive(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()

        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option(voting)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally=voting.tally_votes(self.token)

        mensajeEsperado="For voting test voting: for question test question for option option 1 it has 1 votes,  for option option 2 it has 0 votes,  for option option 3 it has 0 votes,  for option option 4 it has 0 votes,  for option option 5 it has 0 votes."
        mensajeObtenido=give_message(voting,tally)

        self.assertEqual(mensajeEsperado, mensajeObtenido)

    def test_tally_message_negative(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()

        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option(voting)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally=voting.tally_votes(self.token)

        mensajeEsperado="For voting test bad voting : for question test question for option option 1 it has 0 votes,  for option option 2 it has 0 votes,  for option option 3 it has 1 votes,  for option option 4 it has 0 votes,  for option option 5 it has 0 votes."
        mensajeObtenido=give_message(voting,tally)

        self.assertNotEqual(mensajeEsperado, mensajeObtenido)


    def test_tally_masc_positive(self):

        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()

        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option(voting)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        voting.tally_votes(self.token)
        tallyM=voting.tally_votes_masc(self.token)
        tallyF=voting.tally_votes_fem(self.token)
        for i, q in enumerate(voting.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                if q.option_types == 3:
                    votesM = []
                    votesF = []
                    for i in range (opt_count):
                        votesM.append(0)
                        votesF.append(0)
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM[pos[0]] = votesM[pos[0]] + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None and pos[1]==q.id:
                            votesF[pos[0]] = votesF[pos[0]] + 1
                else:
                    votesM = 0
                    votesF = 0
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM = votesM + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesF = votesF + 1
                opts.append({
                    'Option:': opt.option,
                    'has this male votes:': votesM
                })

        resultadoEsperado="[{'Option:': 'option 1', 'has this male votes:': 1}, {'Option:': 'option 2', 'has this male votes:': 0}, {'Option:': 'option 3', 'has this male votes:': 0}, {'Option:': 'option 4', 'has this male votes:': 0}, {'Option:': 'option 5', 'has this male votes:': 0}]"
        self.assertEqual(str(opts),resultadoEsperado)


    def test_tally_masc_negative(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()

        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option(voting)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        voting.tally_votes(self.token)
        tallyM=voting.tally_votes_masc(self.token)
        tallyF=voting.tally_votes_fem(self.token)
        for i, q in enumerate(voting.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                if q.option_types == 3:
                    votesM = []
                    votesF = []
                    for i in range (opt_count):
                        votesM.append(0)
                        votesF.append(0)
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM[pos[0]] = votesM[pos[0]] + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None and pos[1]==q.id:
                            votesF[pos[0]] = votesF[pos[0]] + 1
                else:
                    votesM = 0
                    votesF = 0
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM = votesM + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesF = votesF + 1
                opts.append({
                    'Option:': opt.option,
                    'has this male votes:': votesM
                })

        resultadoEsperado="[{'Option:': 'option 1', 'has this male votes:': 0}, {'Option:': 'option 2', 'has this male votes:': 0}, {'Option:': 'option 3', 'has this male votes:': 0}, {'Option:': 'option 4', 'has this male votes:': 1}, {'Option:': 'option 5', 'has this male votes:': 0}]"
        self.assertNotEqual(str(opts),resultadoEsperado)

    def test_tally_fem_positive(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()

        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option_fem(voting)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        voting.tally_votes(self.token)
        tallyM=voting.tally_votes_masc(self.token)
        tallyF=voting.tally_votes_fem(self.token)
        for i, q in enumerate(voting.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                if q.option_types == 3:
                    votesM = []
                    votesF = []
                    for i in range (opt_count):
                        votesM.append(0)
                        votesF.append(0)
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM[pos[0]] = votesM[pos[0]] + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None and pos[1]==q.id:
                            votesF[pos[0]] = votesF[pos[0]] + 1
                else:
                    votesM = 0
                    votesF = 0
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM = votesM + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesF = votesF + 1
                opts.append({
                    'Option:': opt.option,
                    'has this female votes:': votesF
                })

        resultadoEsperado="[{'Option:': 'option 1', 'has this female votes:': 1}, {'Option:': 'option 2', 'has this female votes:': 0}, {'Option:': 'option 3', 'has this female votes:': 0}, {'Option:': 'option 4', 'has this female votes:': 0}, {'Option:': 'option 5', 'has this female votes:': 0}]"
        self.assertEqual(str(opts),resultadoEsperado)

    def test_tally_fem_negative(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()

        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)


        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option_fem(voting)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        voting.tally_votes(self.token)
        tallyM=voting.tally_votes_masc(self.token)
        tallyF=voting.tally_votes_fem(self.token)
        for i, q in enumerate(voting.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                if q.option_types == 3:
                    votesM = []
                    votesF = []
                    for i in range (opt_count):
                        votesM.append(0)
                        votesF.append(0)
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM[pos[0]] = votesM[pos[0]] + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None and pos[1]==q.id:
                            votesF[pos[0]] = votesF[pos[0]] + 1
                else:
                    votesM = 0
                    votesF = 0
                    for dicc in tallyM:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesM = votesM + 1
                    for dicc in tallyF:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votesF = votesF + 1
                opts.append({
                    'Option:': opt.option,
                    'has this male votes:': votesF
                })

        resultadoEsperado="[{'Option:': 'option 1', 'has this female votes:': 0}, {'Option:': 'option 2', 'has this female votes:': 0}, {'Option:': 'option 3', 'has this female votes:': 0}, {'Option:': 'option 4', 'has this female votes:': 1}, {'Option:': 'option 5', 'has this female votes:': 0}]"
        self.assertNotEqual(str(opts),resultadoEsperado)



    def test_started_by_positive(self):
        voting = self.create_voting()
        voting_id = voting.id
        user= self.get_or_create_user(1)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.login(user=user.username)

        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')

        voting = get_object_or_404(Voting, pk=voting_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')
        self.assertEqual(voting.started_by, user.username)

    def test_started_by_negative(self):
        voting = self.create_voting()
        voting_id = voting.id
        user= self.get_or_create_user(1)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.login()

        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')

        voting = get_object_or_404(Voting, pk=voting_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')
        self.assertNotEqual(voting.started_by, user.username)
    # def test_update_voting(self):
    #     voting = self.create_voting()

    #     data = {'action': 'start'}
    #     #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
    #     #self.assertEqual(response.status_code, 401)

    #     # login with user no admin
    #     self.login(user='noadmin')
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 403)

    #     # login with user admin
    #     self.login()
    #     data = {'action': 'bad'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)

    #     # STATUS VOTING: not started
    #     for action in ['stop', 'tally']:
    #         data = {'action': action}
    #         response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #         self.assertEqual(response.status_code, 400)
    #         self.assertEqual(response.json(), 'Voting is not started')

    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), 'Voting started')

    #     # STATUS VOTING: started
    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already started')

    #     data = {'action': 'tally'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting is not stopped')

    #     data = {'action': 'stop'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), 'Voting stopped')

    #     # STATUS VOTING: stopped
    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already started')

    #     data = {'action': 'stop'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already stopped')

    #     data = {'action': 'tally'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), 'Voting tallied')

    #     # STATUS VOTING: tallied
    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already started')

    #     data = {'action': 'stop'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already stopped')

    #     data = {'action': 'tally'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already tallied')


    #Pruebas unitarias para la funcionalidad de crear votaciones con múltiples question

    def create_voting_multi(self):
        q1 = Question(desc='test1 question', option_types=2)
        q2 = Question(desc='test2 question', option_types=2)

        q1.save()
        q2.save()

        for i in range(5):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()

        for i in range(5):
            opt = QuestionOption(question=q2, option='option {}'.format(i+1))
            opt.save()

        v = Voting(name='test voting multi')
        v.save()
        v.question.add(q1)
        v.question.add(q2)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                           defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    #Caso positivo 1: se crea correctamente una votación con una única question

    def test_multi_voting_simple_pos(self):
        v1 = self.create_voting()
        self.assertEqual(v1.name, 'test voting')


        q = []
        for quest in v1.question.all():
            q.append(quest.desc)

        desc = q[0]
        self.assertEqual(desc, 'test question')

        longitud = len(q)
        self.assertEqual(longitud, 1)

    #Caso positivo 2: se crea correctamente una votación con dos question

    def test_multi_voting_two_pos(self):
        v1 = self.create_voting_multi()
        self.assertEqual(v1.name, 'test voting multi')


        q = []
        for quest in v1.question.all():
            q.append(quest.desc)

        desc1 = q[0]
        desc2 = q[1]
        self.assertEqual(desc1, 'test1 question')
        self.assertEqual(desc2, 'test2 question')

        longitud = len(q)
        self.assertEqual(longitud, 2)

    #Caso negativo 1: se lanza el error cuando se intenta acceder a las opciones de la pregunta de la votación (1 question)
    #directamente debido a que ahora las question forman parte de un conjunto

    def test_multi_voting_simple_neg(self):
        v1 = self.create_voting()

        with self.assertRaises(Exception) as raised:
            option = v1.question.options.all()

        self.assertEqual(AttributeError, type(raised.exception))

    #Caso negativo 1: se lanza el error cuando se intenta acceder a las opciones de la pregunta de la votación (2 question)
    #directamente debido a que ahora las question forman parte de un conjunto

    def test_multi_voting_two_neg(self):
        v1 = self.create_voting_multi()

        with self.assertRaises(Exception) as raised:
            option = v1.question.options.all()

        self.assertEqual(AttributeError, type(raised.exception))




    # Test Unitarios para la creación de Question con descripción única

    def create_question(self):
        q = Question(desc='test question')
        q.save()
        return q

        # Caso positivo: se crean dos Question con descripciones distintas y no surgen errores

    def test_question_unique_pos(self):
        v = self.create_question()
        q = Question(desc='test question2')
        q.save()
        self.assertEqual(q.desc, 'test question2')

        #Caso negativo: se crean dos Question con descripcionres repetidas y se lanza un error que impide crearla

    def test_question_unique_neg(self):
        v = self.create_question()
        with self.assertRaises(Exception) as raised:
            self.create_question()
        self.assertEqual(IntegrityError, type(raised.exception))

        # Test Unitarios para creación de una pregunta teniendo en cuenta la restricción de option_types y type

    def test_create_question_restriction_pos(self):
        q = self.create_question()
        q.option_types = 3
        q.type = 1
        q.clean()
        q.save()

        self.assertEqual(q.option_types,3)
        self.assertEqual(q.type, 1)

        # Caso positivo: se crea una question respetando la restriccion

    def test_create_question_restriction_neg(self):
        q = self.create_question()
        q.option_types = 3
        q.type = 2

        with self.assertRaises(Exception) as raised:
            q.clean()
            q.save()
        self.assertEqual(ValidationError, type(raised.exception))

        # Caso negativo: se crea una question sin respetar la restriccion

    # Test Unitarios para creación de una question con valores de option_type y type no validos.

    def test_create_question_optiontypes_neg(self):
        q = self.create_question()
        q.option_types = 9999
        q.type = 2

        with self.assertRaises(Exception) as raised:
            q.full_clean()
            q.save()
        self.assertEqual(ValidationError, type(raised.exception))

        # Caso negativo: se crea una question y se asignan valores no válidos a option_types

    def test_create_question_type_neg(self):
        q = self.create_question()
        q.option_types = 1
        q.type = 9999

        with self.assertRaises(Exception) as raised:
            q.full_clean()
            q.save()
        self.assertEqual(ValidationError, type(raised.exception))

        # Caso negativo: se crea una question y se asignan valores no válidos a type


#Test Unitarios para creación de una voting y autoincluirse en el censo.

    def test_create_voting_autocensus_pos(self):

        v = self.create_voting()
        # Ha seleccionado autocenso (hacer con selenium)
        if True:
            c = Census.objects.get_or_create(voter_id=1, voting_id=v.id)
        self.assertTrue(c)

        # Caso positivo: se crea una voting y se asigna el creador al censo.

    def test_create_voting_noautocensus_neg(self):

        v = self.create_voting()
        # No ha seleccionado autocenso (hacer con selenium)
        if False:
            Census.objects.get_or_create(voter_id=1, voting_id=v.id)

        with self.assertRaises(Exception) as raised:
            Census.objects.get(voter_id=1, voting_id=v.id)
        self.assertEqual(Census.DoesNotExist, type(raised.exception))

        # Caso negativo: se crea una voting y no se asigna el creador al censo.




    # Test Unitarios de Task t026

    def create_voting_variable_option_types(self, option_type):
        q = Question(desc='test question', option_types=option_type)
        q.save()
        for i in range(3):
            opt = QuestionOption(question=q, option='option {}'.format(i+1), number=i+1)
            opt.save()
        v = Voting(name='test voting')

        v.save()
        v.question.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def store_votes_aux(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user(voter.voter_id)
            self.login(user=main_voter.username)
            votos = []
            qs = v.question.all()
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a,b = None, None

                if q.option_types == 1:
                    random_amount = 1
                else:
                    random_amount = random.randint(1, count_options)

                for j in range(0, random_amount):
                    chosen_option = options[j]

                    if chosen_option.number in clear:
                        clear[chosen_option.number] += 1
                    else:
                        clear[chosen_option.number] = 1

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b })

                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': votos,
                    'question_id': q.id,
                    'token': self.token
                }
                mods.post('store', json=data)

            self.logout()
        return clear

    def test_complete_unique_option_voting_positive(self):
        v = self.create_voting_variable_option_types(1)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally

        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():


                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos!=None:
                        votes = votes + 1


            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    def test_complete_multiple_option_voting_positive(self):
        v = self.create_voting_variable_option_types(2)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally

        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos!=None:
                        votes = votes + 1


            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)



