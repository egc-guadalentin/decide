from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.core.exceptions import ValidationError

from base import mods
from base.models import Auth, Key

class TypeVoting(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name

class Question(models.Model):
    ANSWER_TYPES = ((1, "Unique option"), (2,"Multiple option"), (3,"Rank order scale"))
    option_types = models.PositiveIntegerField(choices=ANSWER_TYPES, default="1")
    desc = models.TextField(unique=True)
    ANSWER_TYPES_VOTING = ((0, "IDENTITY"), (1, "BORDA"), (2, "HONDT"),
                    (3, "EQUALITY"), (4, "SAINTE_LAGUE"), (5, "DROOP"),
                    (6, "IMPERIALI"), (7, "HARE"))
    type = models.PositiveIntegerField(choices=ANSWER_TYPES_VOTING, default="0")

    def clean(self):
        if self.option_types == 3 and not self.type == 1:
            raise ValidationError(('Rank order scale option type must be selected with Borda type.'))


    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.CharField(max_length=200)

    def save(self):

        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()


    def __str__(self):
        return '{} ({})'.format(self.option, self.number)



class Voting(models.Model):
    name = models.CharField(max_length=200, unique = True)
    desc = models.TextField(blank=True, null=True)
    question =  models.ManyToManyField(Question, related_name='voting')
    points = models.PositiveIntegerField(default="1")

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    started_by = models.CharField(max_length=200, blank=True, null = True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    tallyM = JSONField(blank=True, null=True)
    tallyF = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)


    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return votes

    def get_votes_masc(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return votes

    def get_votes_fem(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return votes

    def get_info(self,token=''):
        votos=Voting.objects.get(id=self.id)
        return votos


    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votos  = self.get_votes(token)
        votes = []
        for i in votos:
            aa = i['a'].split(',')
            bb = i['b'].split(',')
            for j in range(len(aa)):
                votes.append([int(aa[j]), int(bb[j]), j, i['question_id']])
        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        tally=self.tally
        self.tally_votes_masc(token)
        return tally

    def tally_votes_masc(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''
        votos  = self.get_votes_masc(token)

        votes = []
        for i in votos:
            if i['sex'] == 'M':
                aa = i['a'].split(',')
                bb = i['b'].split(',')
                for j in range(len(aa)):
                    #[[int(i['a']), int(i['b'])] for i in votes if i['sex']=='F']
                    votes.append([int(aa[j]), int(bb[j]), j, i['question_id']])


        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tallyM = response.json()
        self.save()

        tallyM=self.tallyM

        self.tally_votes_fem(token)
        return tallyM

    def tally_votes_fem(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votos  = self.get_votes_fem(token)

        votes = []
        for i in votos:
            if i['sex'] == 'F':
                aa = i['a'].split(',')
                bb = i['b'].split(',')
                for j in range(len(aa)):
                    votes.append([int(aa[j]), int(bb[j]), j,i['question_id']])

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tallyF = response.json()
        self.save()

        tallyF=self.tallyF
        self.do_postproc()
        return tallyF







    def votes_info_votos(self,tally):
        data=[]
        for i, q in enumerate(self.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                if q.option_types == 3:
                    votes = []
                    for i in range (opt_count):
                        votes.append(0)

                    for dicc in tally:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None:
                            votes[pos[0]] = votes[pos[0]] + 1

                else:
                    votes = 0

                    for dicc in tally:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None:
                            votes = votes + 1
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes,
                })
            data.append({'pregunta': q.desc, 'opciones':opts})
        return data

    def do_postproc(self):
        tally = self.tally
        tallyM = self.tallyM
        tallyF = self.tallyF
        points = self.points
        tallies = ['IDENTITY', 'BORDA', 'HONDT', 'EQUALITY', 'SAINTE_LAGUE', 'DROOP', 'IMPERIALI', 'HARE']
        data = []

        for i, q in enumerate(self.question.all()):
            opciones = q.options.all()
            opt_count=len(opciones)
            opts = []
            for opt in opciones:
                if q.option_types == 3:
                    votes = []
                    votesM = []
                    votesF = []
                    for i in range (opt_count):
                        votes.append(0)
                        votesM.append(0)
                        votesF.append(0)

                    for dicc in tally:
                        indice = opt.number
                        pos = dicc.get(str(indice))
                        if pos!=None and pos[1]==q.id:
                            votes[pos[0]] = votes[pos[0]] + 1
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
                    votes = 0
                    votesM = 0
                    votesF = 0
                    for dicc in tally:
                        indice = opt.number
                        pos = dicc.get(str(indice))

                        if pos!=None and pos[1]==q.id:
                            votes = votes + 1

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
                    'question': opt.question.desc,
                    'question_id':opt.question.id,
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes,
                    'votes_masc': votesM,
                    'votes_fem': votesF,
                    'points': points
                })
            data.append( { 'type': tallies[q.type],'options': opts})
        print(data)
        postp = mods.post('postproc', json=data)
        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name