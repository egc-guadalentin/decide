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
from rest_framework import generics, status

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

    def create_voters_fem(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i),sex='F')
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

#-----------------------------------------------------------------------------------------------------------------------
    #MÉTODOS AUXILIARES

    def create_voting_prueba(self):
        q = Question(desc='test question 2', option_types=2)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i + 1))
            opt.save()
        v = Voting(name='test voting 2')

        v.save()
        v.question.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_question(self):
        q = Question(desc='test question')
        q.save()
        return q


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

    def create_voting_variable_option_types(self, option_type, points=1):
        q = Question(desc='test question', option_types=option_type)
        if option_type == 3:
            q.type = 1
        q.save()

        for i in range(3):
            opt = QuestionOption(question=q, option='option {}'.format(i + 1), number=i + 1)
            opt.save()
        v = Voting(name='test voting', points=points)

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
                a, b = None, None

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

                votos.append({'a': a, 'b': b})

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

    def store_votes_aux_fem(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user_fem(voter.voter_id)
            self.login(user=main_voter.username)
            votos = []
            qs = v.question.all()
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a, b = None, None

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

                votos.append({'a': a, 'b': b})

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

    def store_votes_aux_negative(self, v, number_of_voters):
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
                a, b = None, None

                if q.option_types == 1:
                    random_amount = 1
                else:
                    random_amount = random.randint(1, count_options)

                for j in range(0, random_amount):
                    chosen_option = options[j]

                    if chosen_option.number in clear:
                        clear[chosen_option.number] += 2
                    else:
                        clear[chosen_option.number] = 2

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b})

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

    def store_votes_aux_fem_negative(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user_fem(voter.voter_id)
            self.login(user=main_voter.username)
            votos = []
            qs = v.question.all()
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a, b = None, None

                if q.option_types == 1:
                    random_amount = 1
                else:
                    random_amount = random.randint(1, count_options)

                for j in range(0, random_amount):
                    chosen_option = options[j]

                    if chosen_option.number in clear:
                        clear[chosen_option.number] += 2
                    else:
                        clear[chosen_option.number] = 2

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b})

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

    def store_votes_ranked_aux(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user(voter.voter_id)
            self.login(user=main_voter.username)

            qs = v.question.all()
            votos = []
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a, b = None, None
                random_amount = random.randint(1, count_options)
                orden_opciones_voto = []

                zeros = []
                for element in options:
                    zeros.append(0)

                for j in range(0, random_amount):
                    chosen_option = options[j]
                    orden_opciones_voto.append(chosen_option.number)

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b})

                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': votos,
                    'question_id': q.id,
                    'token': self.token
                }
                mods.post('store', json=data)

                pos = 0
                for opt_number in orden_opciones_voto:
                    if opt_number in clear:
                        sum = clear[opt_number][pos] + 1
                        clear[opt_number][pos] = sum

                    else:
                        clear[opt_number] = zeros.copy()
                        sum = clear[opt_number][pos] + 1
                        clear[opt_number][pos] = sum
                    pos = pos + 1

            self.logout()
        return clear

    def store_votes_ranked_aux_fem(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user_fem(voter.voter_id)
            self.login(user=main_voter.username)

            qs = v.question.all()
            votos = []
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a, b = None, None
                random_amount = random.randint(1, count_options)
                orden_opciones_voto = []

                zeros = []
                for element in options:
                    zeros.append(0)

                for j in range(0, random_amount):
                    chosen_option = options[j]
                    orden_opciones_voto.append(chosen_option.number)

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b})

                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': votos,
                    'question_id': q.id,
                    'token': self.token
                }
                mods.post('store', json=data)

                pos = 0
                for opt_number in orden_opciones_voto:
                    if opt_number in clear:
                        sum = clear[opt_number][pos] + 1
                        clear[opt_number][pos] = sum

                    else:
                        clear[opt_number] = zeros.copy()
                        sum = clear[opt_number][pos] + 1
                        clear[opt_number][pos] = sum
                    pos = pos + 1

            self.logout()
        return clear

    def store_votes_ranked_aux_negative(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user(voter.voter_id)
            self.login(user=main_voter.username)

            qs = v.question.all()
            votos = []
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a, b = None, None
                random_amount = random.randint(1, count_options)
                orden_opciones_voto = []

                zeros = []
                for element in options:
                    zeros.append(0)

                for j in range(0, random_amount):
                    chosen_option = options[j]
                    orden_opciones_voto.append(chosen_option.number)

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b})

                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': votos,
                    'question_id': q.id,
                    'token': self.token
                }
                mods.post('store', json=data)

                pos = 0
                for opt_number in orden_opciones_voto:
                    if opt_number in clear:
                        sum = clear[opt_number][pos] + 2
                        clear[opt_number][pos] = sum

                    else:
                        clear[opt_number] = zeros.copy()
                        sum = clear[opt_number][pos] + 2
                        clear[opt_number][pos] = sum
                    pos = pos + 1

            self.logout()
        return clear

    def store_votes_ranked_aux_fem_negative(self, v, number_of_voters):
        voters = list(Census.objects.filter(voting_id=v.id))

        clear = {}
        for i in range(number_of_voters):
            voter = voters.pop()
            main_voter = self.get_or_create_user_fem(voter.voter_id)
            self.login(user=main_voter.username)

            qs = v.question.all()
            votos = []
            for q in qs:
                options = q.options.all()
                count_options = len(options)
                a, b = None, None
                random_amount = random.randint(1, count_options)
                orden_opciones_voto = []

                zeros = []
                for element in options:
                    zeros.append(0)

                for j in range(0, random_amount):
                    chosen_option = options[j]
                    orden_opciones_voto.append(chosen_option.number)

                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b:
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''

                    else:
                        a = str(x)
                        b = str(y)

                votos.append({'a': a, 'b': b})

                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': votos,
                    'question_id': q.id,
                    'token': self.token
                }
                mods.post('store', json=data)

                pos = 0
                for opt_number in orden_opciones_voto:
                    if opt_number in clear:
                        sum = clear[opt_number][pos] + 2
                        clear[opt_number][pos] = sum

                    else:
                        clear[opt_number] = zeros.copy()
                        sum = clear[opt_number][pos] + 2
                        clear[opt_number][pos] = sum
                    pos = pos + 1

            self.logout()
        return clear


    #-----------------------------------------------------------------------------------------------------------------------
    #PRUEBAS UNITARIAS

    # Test Unitarios para la task 018

    # Caso positivo: se crean dos votaciones con nombres diferentes y se cumple correctamente

    def test_duplicate_voting_name_positive(self):
        v1 = self.create_voting()
        v2 = self.create_voting_prueba()
        self.assertNotEqual(v1, v2)

    # Caso negativo: se crean dos votaciones con nombres repetidos y salta la excepción

    def test_duplicate_voting_name_negative(self):
        v1 = self.create_voting()
        with self.assertRaises(Exception) as raised:
            v2 = self.create_voting()
        self.assertEqual(IntegrityError, type(raised.exception))

        # Pruebas unitarias Task t019

        # Caso positivo

    def test_tally_message_positive_unit(self):
        v = self.create_voting_variable_option_types(1)
        resultadoEsperado=v.name
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tally = v.tally
        questions = v.question.all()
        
        mensajeObtenido=give_message(v, tally)
        self.assertIn(resultadoEsperado,mensajeObtenido)

        

    # Caso negativo

    def test_tally_message_negative_unit(self):
        mensajeEsperado = 'For voting test voting: for question test question for option option 1 it has 0 votes,  for option option 2 it has 3 votes,  for option option 3 it has 0 votes.'
        v = self.create_voting_variable_option_types(1)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tally = v.tally
        questions = v.question.all()

        self.assertNotEqual(give_message(v, tally), mensajeEsperado)

        # Test Unitarios para la creación de Question con descripción única

        # Caso positivo: se crean dos Question con descripciones distintas y no surgen errores

    def test_question_unique_pos(self):
        v = self.create_question()
        q = Question(desc='test question2')
        q.save()
        self.assertEqual(q.desc, 'test question2')

        # Caso negativo: se crean dos Question con descripcionres repetidas y se lanza un error que impide crearla

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

        self.assertEqual(q.option_types, 3)
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

    # Test Unitarios para creación de una voting y autoincluirse en el censo.

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

    # Pruebas unitarias t024

    # Caso positivo masculino

    def test_tally_masc_positive_unit(self):

        v = self.create_voting_variable_option_types(1)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        tallyMReal = 0
        tallyMEsperado = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        tallyMReal = tallyMReal + 1

            for clave in clear.keys():
                tallyMEsperado = tallyMEsperado + clear[clave]

        self.assertEqual(tallyMReal, tallyMEsperado)

    # Caso negativo masculino

    def test_tally_masc_negative_unit(self):
        tallyMNoEsperado = [{'0': [0, 1]}, {'0': [0, 1]}, {'1': [0, 1]}]
        v = self.create_voting_variable_option_types(1)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        self.assertNotEqual(tallyM, tallyMNoEsperado)

    # Caso positivo femenino

    def test_tally_fem_positive_unit(self):

        v = self.create_voting_variable_option_types(1)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_fem(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        tallyFReal = 0
        tallyFEsperado = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        tallyFReal = tallyFReal + 1

            for clave in clear.keys():
                tallyFEsperado = tallyFEsperado + clear[clave]

        self.assertEqual(tallyFReal, tallyFEsperado)

    # Caso negativo femenino

    def test_tally_fem_negative_unit(self):
        tallyFNoEsperado = [{'1': [0, 1]}, {'0': [0, 1]}, {'0': [0, 1]}]
        v = self.create_voting_variable_option_types(1)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_fem(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        self.assertNotEqual(tallyF, tallyFNoEsperado)

    # Pruebas unitarias para la funcionalidad de crear votaciones con múltiples question

    # Caso positivo 1: se crea correctamente una votación con una única question

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

    # Caso positivo 2: se crea correctamente una votación con dos question

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

    # Caso negativo 1: se lanza el error cuando se intenta acceder a las opciones de la pregunta de la votación (1 question)
    # directamente debido a que ahora las question forman parte de un conjunto

    def test_multi_voting_simple_neg(self):
        v1 = self.create_voting()

        with self.assertRaises(Exception) as raised:
            option = v1.question.options.all()

        self.assertEqual(AttributeError, type(raised.exception))

    # Caso negativo 2: se lanza el error cuando se intenta acceder a las opciones de la pregunta de la votación (2 question)
    # directamente debido a que ahora las question forman parte de un conjunto

    def test_multi_voting_two_neg(self):
        v1 = self.create_voting_multi()

        with self.assertRaises(Exception) as raised:
            option = v1.question.options.all()

        self.assertEqual(AttributeError, type(raised.exception))

    # Test Unitarios de Task t026

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

                    if pos != None:
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

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    # Test Unitarios de Task t027
    # Rank order (Opciones )

    def test_complete_ranked_option_voting_positive(self):
        voting_type = 3
        v = self.create_voting_variable_option_types(voting_type)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_ranked_aux(v, number_of_voters)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally

        questions = v.question.all()
        opts = {}
        for qs in questions:
            opciones = qs.options.all()
            opt_count = len(opciones)
            for opt in opciones:
                votes = []

                for i in range(opt_count):
                    votes.append(0)

                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))
                    if pos != None and pos[1] == qs.id:
                        votes[pos[0]] = votes[pos[0]] + 1

                empty = True
                for element in votes:
                    if element != 0:
                        empty = False
                        break

                if empty == False:
                    opts[opt.number] = votes

        self.assertEqual(opts, clear)

    # Voting points (Recuento proporcional)

    def test_voting_points_positive(self):
        points = 4
        voting_type = 3
        v = self.create_voting_variable_option_types(voting_type, points)
        v.points = points
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 4
        self.store_votes_ranked_aux(v, number_of_voters)

        self.login()  # set token
        v.tally_votes(self.token)

        v.tally
        postp = v.postproc

        for dicc in postp:
            options = dicc["options"]
            for dicc_aux in options:
                self.assertEqual(points, dicc_aux["points"])

    def test_voting_points_negative(self):
        points = -1

        with self.assertRaises(Exception) as raised:
            v = self.create_voting_variable_option_types(3, points)

        self.assertEqual(IntegrityError, type(raised.exception))

    #-----------------------------------------------------------------------------------------------------------------------
    #TEST DE MODELO

    # Tests de modelo de Task t042

    def test_store_unique_option_question_positive(self):
        options_type = 1
        q = Question(desc='test question', option_types=options_type)
        q.save()

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(options_type, Question.objects.all()[0].option_types)

    def test_store_multiple_option_question_positive(self):
        options_type = 2
        q = Question(desc='test question', option_types=options_type)
        q.save()

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(options_type, Question.objects.all()[0].option_types)

    def test_store_none_option_question_negative(self):
        options_type = None
        q = Question(desc='test question', option_types=options_type)

        with self.assertRaises(Exception) as raised:
            q.save()

        self.assertEqual(IntegrityError, type(raised.exception))

    # Tests de modelo de Task t043

    def test_store_ranked_option_question_positive(self):
        options_type = 3
        q = Question(desc='test question', option_types=options_type)
        q.save()

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(options_type, Question.objects.all()[0].option_types)

    def test_store_voting_points_positive(self):
        points = 2
        v = Voting(id=1, name='test voting', points=points)
        v.save()

        self.assertEqual(Voting.objects.count(), 1)
        self.assertEqual(points, Voting.objects.all()[0].points)

    def test_store_voting_points_negative(self):
        points = -2
        v = Voting(id=1, name='test voting', points=points)
        with self.assertRaises(Exception) as raised:
            v.save()

        self.assertEqual(IntegrityError, type(raised.exception))

    # Test de modelo de la t045

    # Caso positivo

    def test_store_unique_question_positive(self):
        options_type = 3
        q1 = Question(desc='test question desc 1', option_types=options_type)
        q1.save()

        q2 = Question(desc='test question desc 2', option_types=options_type)
        q2.save()

        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(q1.desc, 'test question desc 1')
        self.assertEqual(q2.desc, 'test question desc 2')

        # Caso negativo

    def test_store_unique_question_negative(self):
        options_type = 3
        q1 = Question(desc='test question desc 1', option_types=options_type)
        q1.save()

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(q1.desc, 'test question desc 1')

        q2 = Question(desc='test question desc 1', option_types=options_type)
        with self.assertRaises(Exception) as raised:
            q2.save()

        self.assertEqual(IntegrityError, type(raised.exception))

    # Pruebas de modelo para la t046

    # Caso positivo 1

    def test_store_multi_voting_positive_one(self):
        options_type = 3
        q1 = Question(desc='test question 1', option_types=options_type)
        q1.save()
        self.assertEqual(Question.objects.count(), 1)

        v = Voting(name='test voting multi')
        v.save()
        v.question.add(q1)
        self.assertEqual(Voting.objects.count(), 1)

        q = []
        for quest in v.question.all():
            q.append(quest.desc)

        self.assertEqual(len(q), 1)

    # Caso positivo 2

    def test_store_multi_voting_positive_two(self):
        options_type = 3
        q1 = Question(desc='test question 1', option_types=options_type)
        q1.save()
        self.assertEqual(Question.objects.count(), 1)

        q2 = Question(desc='test question 2', option_types=options_type)
        q2.save()
        self.assertEqual(Question.objects.count(), 2)

        v = Voting(name='test voting multi')
        v.save()
        v.question.add(q1)
        v.question.add(q2)
        self.assertEqual(Voting.objects.count(), 1)

        q = []
        for quest in v.question.all():
            q.append(quest.desc)

        self.assertEqual(len(q), 2)

        # Caso negativo 1

    def test_store_multi_voting_negative(self):
        options_type = 3
        q1 = Question(desc='test question 1', option_types=options_type)
        q1.save()

        with self.assertRaises(Exception) as raised:
            v = Voting(name='test voting multi', question=q1)

        self.assertEqual(TypeError, type(raised.exception))

    # Test de modelo de Task t044

    # Caso positivo tallyM con votacion de opción única

    def test_tallyM_unique_positive_model(self):
        v = self.create_voting_variable_option_types(1)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    # Caso negativo tallyM con votacion de opción única

    def test_tallyM_unique_negative_model(self):
        v = self.create_voting_variable_option_types(1)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_negative(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertNotEqual(votes, votes_aux)

    # Caso positivo tallyF con votacion de opción única

    def test_tallyF_unique_positive_model(self):
        v = self.create_voting_variable_option_types(1)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_fem(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    # Caso negativo tallyF con votacion de opción única

    def test_tallyF_unique_negative_model(self):
        v = self.create_voting_variable_option_types(1)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_fem_negative(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertNotEqual(votes, votes_aux)

    # Caso positivo tallyM con votacion de opción múltiple

    def test_tallyM_multiple_positive_model(self):
        v = self.create_voting_variable_option_types(2)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    # Caso negativo tallyM con votacion de opción múltiple

    def test_tallyM_multiple_negative_model(self):
        v = self.create_voting_variable_option_types(2)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_negative(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertNotEqual(votes, votes_aux)

    # Caso positivo tallyF con votacion de opción múltiple

    def test_tallyF_multiple_positive_model(self):
        v = self.create_voting_variable_option_types(2)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_fem(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    # Caso negativo tallyF con votacion de opción múltiple

    def test_tallyF_multiple_negative_model(self):
        v = self.create_voting_variable_option_types(2)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_aux_fem_negative(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertNotEqual(votes, votes_aux)

    # Caso positivo tallyM con votacion de opción ranked order

    def test_tallyM_ranked_order_positive_model(self):
        v = self.create_voting_variable_option_types(3)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_ranked_aux(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        questions = v.question.all()
        opts = {}
        for qs in questions:
            opciones = qs.options.all()
            opt_count = len(opciones)
            for opt in opciones:
                votes = []

                for i in range(opt_count):
                    votes.append(0)

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))
                    if pos != None and pos[1] == qs.id:
                        votes[pos[0]] = votes[pos[0]] + 1

                empty = True
                for element in votes:
                    if element != 0:
                        empty = False
                        break

                if empty == False:
                    opts[opt.number] = votes

        self.assertEqual(opts, clear)

    # Caso negativo tallyM con votacion de opción ranked order

    def test_tallyM_ranked_order_negative_model(self):
        v = self.create_voting_variable_option_types(3)
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_ranked_aux_negative(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyM = v.tallyM
        questions = v.question.all()

        questions = v.question.all()
        opts = {}
        for qs in questions:
            opciones = qs.options.all()
            opt_count = len(opciones)
            for opt in opciones:
                votes = []

                for i in range(opt_count):
                    votes.append(0)

                for dicc in tallyM:
                    indice = opt.number
                    pos = dicc.get(str(indice))
                    if pos != None and pos[1] == qs.id:
                        votes[pos[0]] = votes[pos[0]] + 1

                empty = True
                for element in votes:
                    if element != 0:
                        empty = False
                        break

                if empty == False:
                    opts[opt.number] = votes

        self.assertNotEqual(opts, clear)

    # Caso positivo tallyF con votacion de opción ranked order

    def test_tallyF_ranked_order_positive_model(self):
        v = self.create_voting_variable_option_types(3)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_ranked_aux_fem(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        questions = v.question.all()
        opts = {}
        for qs in questions:
            opciones = qs.options.all()
            opt_count = len(opciones)
            for opt in opciones:
                votes = []

                for i in range(opt_count):
                    votes.append(0)

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))
                    if pos != None and pos[1] == qs.id:
                        votes[pos[0]] = votes[pos[0]] + 1

                empty = True
                for element in votes:
                    if element != 0:
                        empty = False
                        break

                if empty == False:
                    opts[opt.number] = votes

        self.assertEqual(opts, clear)

    # Caso negativo tallyF con votacion de opción ranked order

    def test_tallyF_ranked_order_negative_model(self):
        v = self.create_voting_variable_option_types(3)
        self.create_voters_fem(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        number_of_voters = 3
        clear = self.store_votes_ranked_aux_fem_negative(v, number_of_voters)

        self.login()
        v.tally_votes(self.token)
        tallyF = v.tallyF
        questions = v.question.all()

        questions = v.question.all()
        opts = {}
        for qs in questions:
            opciones = qs.options.all()
            opt_count = len(opciones)
            for opt in opciones:
                votes = []

                for i in range(opt_count):
                    votes.append(0)

                for dicc in tallyF:
                    indice = opt.number
                    pos = dicc.get(str(indice))
                    if pos != None and pos[1] == qs.id:
                        votes[pos[0]] = votes[pos[0]] + 1

                empty = True
                for element in votes:
                    if element != 0:
                        empty = False
                        break

                if empty == False:
                    opts[opt.number] = votes

        self.assertNotEqual(opts, clear)

    # Pruebas de modelo Task t060

    # Caso positivo: se crean dos votaciones con nombres diferentes y se cumple correctamente
    def test_duplicate_voting_name_positive_model(self):
        q = Question(desc='test question 2', option_types=2)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i + 1))
            opt.save()
        v1 = Voting(name="test voting 2")

        v1.save()
        v1.question.add(q)
        a1, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                           defaults={'me': True, 'name': 'test auth'})
        a1.save()
        v1.auths.add(a1)

        self.assertEqual(Voting.objects.count(), 1)

        v2 = Voting(name="test voting 3")
        v2.save()
        v2.question.add(q)
        v2.auths.add(a1)
        self.assertEqual(Voting.objects.count(), 2)

        self.assertNotEqual(v1, v2)

    # Caso negativo: se crean dos votaciones con nombres repetidos y salta la excepción
    def test_duplicate_voting_name_negative_model(self):
        q = Question(desc='test question', option_types=1, type=0)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i + 1))
            opt.save()
        v = Voting(id=1, name='test voting')

        v.save()
        v.question.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        self.assertEqual(Voting.objects.count(), 1)

        with self.assertRaises(Exception) as raised:
            v2 = self.create_voting()
        self.assertEqual(IntegrityError, type(raised.exception))

    # Pruebas de modelo Task t061

    # Caso positivo: se crean tres preguntas con tipos de recuento distintos y funciona correctamente
    def test_type_question_positive_model(self):
        q0 = Question(desc='Unique option-IDENTITY', option_types=1, type=0)
        q0.save()

        self.assertEqual(Question.objects.count(), 1)

        q1 = Question(desc='Multiple option-HONDT', option_types=2, type=2)
        q1.save()

        self.assertNotEqual(q0, q1)

        self.assertEqual(Question.objects.count(), 2)

        q2 = Question(desc='Rank order scale-BORDA', option_types=3, type=1)
        q2.save()

        self.assertNotEqual(q0, q2)
        self.assertNotEqual(q1, q2)

        self.assertEqual(Question.objects.count(), 3)

        for i in range(5):
            opt0 = QuestionOption(question=q0, option='option {}'.format(i + 1))
            opt0.save()
        for i in range(5):
            opt1 = QuestionOption(question=q1, option='option {}'.format(i + 1))
            opt1.save()
        for i in range(5):
            opt2 = QuestionOption(question=q2, option='option {}'.format(i + 1))
            opt2.save()

        v1 = Voting(name="test voting with 3 kind of questions")

        v1.save()
        v1.question.add(q0)
        v1.question.add(q1)
        v1.question.add(q2)

        a1, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                           defaults={'me': True, 'name': 'test auth'})
        a1.save()
        v1.auths.add(a1)
        self.assertEqual(Voting.objects.count(), 1)

    # Caso negativo: se crean 3 votaciones con configuraciones inválidas y salta la excepción
    def test_type_question_negative_model(self):

        q0 = Question(desc='Unique option-IDENTITY', option_types=1, type=0)
        q0.save()

        self.assertEqual(Question.objects.count(), 1)

        q1 = Question(desc='Multiple option-HONDT', option_types=2, type=2)
        q1.save()

        self.assertNotEqual(q0, q1)

        self.assertEqual(Question.objects.count(), 2)

        q2 = Question(desc='Rank order scale-no-BORDA', option_types=3, type=6)
        with self.assertRaises(Exception) as raised:
            q2.full_clean()
            q2.save()
        self.assertEqual(ValidationError, type(raised.exception))
    

    # Pruebas de modelo Task t063

    # Caso positivo: se crean una nueva votación con autocensus y se valida correctamente
    def test_voting_autocensus_question_positive_model(self):
        q0 = Question(desc='Unique option-IDENTITY', option_types=1, type=0)
        q0.save()

        self.assertEqual(Question.objects.count(), 1)

        q1 = Question(desc='Multiple option-HONDT', option_types=2, type=2)
        q1.save()

        self.assertNotEqual(q0, q1)

        self.assertEqual(Question.objects.count(), 2)

        q2 = Question(desc='Rank order scale-BORDA', option_types=3, type=1)
        q2.save()

        self.assertNotEqual(q0, q2)
        self.assertNotEqual(q1, q2)

        self.assertEqual(Question.objects.count(), 3)

        for i in range(5):
            opt0 = QuestionOption(question=q0, option='option {}'.format(i + 1))
            opt0.save()
        for i in range(5):
            opt1 = QuestionOption(question=q1, option='option {}'.format(i + 1))
            opt1.save()
        for i in range(5):
            opt2 = QuestionOption(question=q2, option='option {}'.format(i + 1))
            opt2.save()

        v1 = Voting(name="test voting with 3 kind of questions")

        v1.save()
        v1.question.add(q0)
        v1.question.add(q1)
        v1.question.add(q2)

        a1, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                           defaults={'me': True, 'name': 'test auth'})
        a1.save()
        v1.auths.add(a1)
        self.assertEqual(Voting.objects.count(), 1)

        c = Census.objects.get_or_create(voter_id=1, voting_id=v1.id)
        self.assertTrue(c)

    # Caso negativo: se crea una nueva votación sin autocensus y se valida correctamente
    def test_voting_autocensus_question_negative_model(self):

        q0 = Question(desc='Unique option-IDENTITY', option_types=1, type=0)
        q0.save()

        self.assertEqual(Question.objects.count(), 1)

        q1 = Question(desc='Multiple option-HONDT', option_types=2, type=2)
        q1.save()

        self.assertNotEqual(q0, q1)

        self.assertEqual(Question.objects.count(), 2)

        q2 = Question(desc='Rank order scale-no-BORDA', option_types=3, type=6)

        with self.assertRaises(Exception) as raised:
            q2.full_clean()
            q2.save()
        self.assertEqual(ValidationError, type(raised.exception))

    #-----------------------------------------------------------------------------------------------------------------------
    #TEST DE API

    def test_update_voting(self):
        voting = self.create_voting_variable_option_types(3)
        voting2 = self.create_voting_multi()
        voting3 = self.create_voting_prueba()

        data = {'action': 'start'}
        response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting2.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not started')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting2.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting2.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting3.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not started')

    # Pruebas de API para la t049: votacion con múltiples preguntas

    def test_multi_voting_api(self):
        options_type = 3
        q1 = Question(desc='test question 1', option_types=options_type)
        q1.save()

        q2 = Question(desc='test question 2', option_types=options_type)
        q2.save()

        voting = Voting(name='test voting multi')
        voting.save()
        voting.question.add(q1)
        voting.question.add(q2)

        data = {'action': 'start'}
        response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

    #Pruebas de API Task t050

    #Caso positivo

    def test_tally_message_positive_api(self):
        voting = self.create_voting()
        resultadoEsperado=voting.name
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

        mensajeObtenido=give_message(voting,tally)

        self.assertIn(resultadoEsperado,mensajeObtenido)
    
    #Caso negativo

    def test_tally_message_negative_api(self):
        mensajeEsperado="For voting test bad voting : for question test question for option option 1 it has 0 votes,  for option option 2 it has 0 votes,  for option option 3 it has 1 votes,  for option option 4 it has 0 votes,  for option option 5 it has 0 votes."
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

        mensajeObtenido=give_message(voting,tally)

        self.assertNotEqual(mensajeEsperado, mensajeObtenido)

    
    #Pruebas de API t056

    #Caso positivo masculino
    def test_tally_masc_positive_api(self):

        voting = self.create_voting()
        resultadoEsperado="male"
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

        self.assertIn(resultadoEsperado,str(opts))

    #Caso negativo masculino

    def test_tally_masc_negative_api(self):
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
    
    #Caso positivo femenino

    def test_tally_fem_positive_api(self):
        voting = self.create_voting()
        resultadoEsperado="female"
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
        
        self.assertIn(resultadoEsperado,str(opts))
    
    #Caso negativo femenino

    def test_tally_fem_negative_api(self):
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

    # Tests de api de Task t053

    def test_complete_unique_option_voting_positive_api(self):
        voting = self.create_voting_variable_option_types(1)
        self.create_voters(voting)

        voting.create_pubkey()

        self.login()
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        number_of_voters = 3
        clear = self.store_votes_aux(voting, number_of_voters)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally = voting.tally_votes(self.token)

        questions = voting.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    def test_complete_multiple_option_voting_positive_api(self):
        voting = self.create_voting_variable_option_types(2)
        self.create_voters(voting)

        voting.create_pubkey()

        self.login()
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        number_of_voters = 3
        clear = self.store_votes_aux(voting, number_of_voters)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally = voting.tally_votes(self.token)

        questions = voting.question.all()

        votes = 0
        votes_aux = 0
        for qs in questions:
            for opt in qs.options.all():

                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))

                    if pos != None:
                        votes = votes + 1

            for clave in clear.keys():
                votes_aux = votes_aux + clear[clave]

        self.assertEqual(votes, votes_aux)

    # Tests de modelo de Task t054
    # Rank order

    def test_complete_ranked_option_voting_positive_api(self):
        voting_type = 3
        voting = self.create_voting_variable_option_types(voting_type)
        self.create_voters(voting)

        voting.create_pubkey()

        self.login()
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        number_of_voters = 3
        clear = self.store_votes_ranked_aux(voting, number_of_voters)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally = voting.tally_votes(self.token)

        questions = voting.question.all()
        opts = {}
        for qs in questions:
            opciones = qs.options.all()
            opt_count = len(opciones)
            for opt in opciones:
                votes = []

                for i in range(opt_count):
                    votes.append(0)

                for dicc in tally:
                    indice = opt.number
                    pos = dicc.get(str(indice))
                    if pos != None and pos[1] == qs.id:
                        votes[pos[0]] = votes[pos[0]] + 1

                empty = True
                for element in votes:
                    if element != 0:
                        empty = False
                        break

                if empty == False:
                    opts[opt.number] = votes

        self.assertEqual(opts, clear)

    # Voting points (Recuento proporcional)

    def test_voting_points_positive_api(self):
        points = 4
        voting_type = 3
        voting = self.create_voting_variable_option_types(voting_type, points)
        voting.points = points
        self.create_voters(voting)

        voting.create_pubkey()
        self.login()
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        number_of_voters = 4
        self.store_votes_ranked_aux(voting, number_of_voters)

        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally = voting.tally_votes(self.token)

        postp = voting.postproc

        for dicc in postp:
            options = dicc["options"]
            for dicc_aux in options:
                self.assertEqual(points, dicc_aux["points"])

    #T025 Started by

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
