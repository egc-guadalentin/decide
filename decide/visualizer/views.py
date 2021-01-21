import json

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import Http404, HttpResponseForbidden

from base import mods
from voting.models import Voting
from voting.models import Question
from census.models import Census
from store.models import Vote
from authentication.models import UserProfile
from datetime import datetime
from django.core.exceptions import PermissionDenied


class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]

            # Se verifica que el usuario es un superuser o pertenece al algún censo de la votación. 
            if self.request.user.is_superuser is False: 
                try:
                    census = Census.objects.filter(voting_id=vid, voter_id=self.request.user.id)
                
                except:
                    raise PermissionDenied

            # Solo se mostrarán las gráficas de aquellas votaciones finalizadas y postprocesadas.
            if voting['end_date'] != None and voting['postproc'][0] != None:
                postproc = voting['postproc'][0]

                if postproc['type'] == 'IDENTITY':
                    self.statistics_identity(context, voting)
                elif postproc['type'] == 'BORDA':
                    self.statistics_borda(context, voting)
                elif postproc['type'] == 'EQUALITY':
                    self.statistics_equality(context, voting)
                else:
                    self.statistics_points(context, voting)
            
                context['postproc_type'] = voting['postproc'][0]['type']

            context['voting'] = voting

        except PermissionDenied:
            raise HttpResponseForbidden

        except:
            raise Http404

        return context

    def statistics_borda(self, context, voting):
        labels = []
        postproc = []
        votes = []
        points = voting['postproc'][0]['options'][0]['points']
        question = voting['postproc'][0]['options'][0]['question']
        type = voting['postproc'][0]["type"]
        name = voting["name"]
        desc = voting["desc"]
        for option in voting['postproc'][0]['options']:
            labels.append(option['option'])
            postproc.append((option['postproc']))
            votes.append(option['votes'])

        context['labels'] = labels
        context['postpro'] = postproc
        context['votes'] = votes
        context['name'] = name
        context['desc'] = desc
        return context

    def statistics_equality(self, context, voting):
        options = []
        votes_men = []
        votes_women = []
        gender_census = []
        results = []
        men_census = 0
        women_census = 0

        # Obtenemos las opciones de la votación
        aux = voting['question'][0]['options']
        for opt in aux:
            options.append(opt['option'])
        
        # Obtenemos el número de votos según el género
        for votes in voting['postproc'][0]['options']:
            votes_men.append(votes['votes_masc'])
            votes_women.append(votes['votes_fem'])
        

        # Obtenemos el censo según el género
        census = Census.objects.filter(voting_id=voting['id']).all()
        for c in census:
            user = UserProfile.objects.get(id=c.voter_id)
            gender = user.sex
            if gender == 'F':
                women_census += 1

            else:    
                men_census += 1

        gender_census.append(men_census)
        gender_census.append(women_census)

        # Obtenemos el resultado de la votación para mostrarlo graficamente
        total = 0
        postproc = voting['postproc'][0]['options']
        print(postproc)
        for opt in postproc:
            total += opt['postproc']
        
        for i in range(len(postproc)):
            results.append(round((postproc[i]['postproc']/total)*100, 2))

        # Agregamos todos los parámetro que necesitamos al context

        context['options'] = options
        context['votes_men'] = votes_men
        context['votes_women'] = votes_women
        context['gender_census'] = gender_census
        context['results'] = results
        

    def statistics_points(self, context, voting):
        labels = []
        postproc = []
        votes = []
        points = voting['postproc'][0]['options'][0]['points']
        question = voting['postproc'][0]['options'][0]['question']
        type = voting['postproc'][0]["type"]
        name = voting["name"]
        desc = voting["desc"]
        for option in voting['postproc'][0]['options']:
            labels.append(option['option'])
            postproc.append((option['postproc']))
            votes.append(option['votes'])

        context['labels'] = labels
        context['postproc'] = postproc
        context['votes'] = votes
        context['question'] = question
        context['points'] = points
        context['type'] = type
        context['name'] = name
        context['desc'] = desc

        return context

    def statistics_identity(self, context, voting):
        labels = []
        data = []
        postproc = voting.get('postproc')[0]['options']

        for option in postproc:
            labels.append(option['option'])
            data.append(int(option['postproc']))
        context['labels'] = labels
        context['data'] = data

class StatisticsView(TemplateView):
    template_name = 'visualizer/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            males_c = 0
            females_c = 0
            r = mods.get('voting', params={'id': vid})
            census = Census.objects.filter(voting_id=vid).all()
            votes = Vote.objects.filter(voting_id=vid).all()
            c=census.count()
            v=votes.count()
            stat = {"census": c, "votes": v}
            males = 0
            females = 0
            if v>0:
                stat["percentage"] = round(v/c*100,2);
            else:
                stat["percentage"] = 0;

            voting = Voting.objects.filter(id=vid).all()[0]
            start = voting.start_date
            end = voting.end_date
            if start is None:
                stat["start"] = "Not started yet"
            else:
                stat["start"] = datetime.strftime(start, "%b %d %Y %H:%M:%S")
            if end is None:
                stat["end"] = "Not finished yet"
            else:
                stat["end"] = datetime.strftime(end, "%b %d %Y %H:%M:%S")
            if start is not None and end is not None:
                stat["time"]=str(end-start)
            else:
                stat["time"]="Not finished yet"
            if voting.postproc is not None:
                stat["type"] = voting.postproc[0]["type"]
            else:
                stat["type"] = "Undefined"
            if voting.tally is not None or voting.tallyF is not None or voting.tallyM is not None:
                stat["tally"] = "Finished"
            else:
                stat["tally"] = "Not started"
            for vote in votes:
                voter = list(UserProfile.objects.filter(id=vote.voter_id))[0]
                if voter is not None:
                    if(voter.sex=="M"):
                        males=males+1
                    if(voter.sex=="F"):
                        females=females+1
            for cen in census:
                user = list(UserProfile.objects.filter(id=cen.voter_id))[0]
                if user is not None:
                    if(user.sex=="M"):
                        males_c=males+1
                    if(user.sex=="F"):
                        females_c=females+1
            stat["males_v"] = males
            stat["females_v"] = females
            if(males_c+females_c>0):
                stat["males_c"] = round(males_c / (males_c+females_c) *100,2)
                stat["females_c"] = round(females_c / (males_c+females_c) *100,2)
            else:
                stat["males_c"] = 0
                stat["females_c"] = 0
            if (males + females > 0):
                stat["males_v_percentage"] = round(males / (males + females) * 100, 2)
                stat["females_v_percentage"] = round(females / (males + females) * 100, 2)
            else:
                stat["males_v_percentage"] = 0
                stat["females_v_percentage"] = 0

            context['voting'] = json.dumps(r[0])
            context['stats'] = json.dumps(stat)
        except:
            raise Http404

        return context


def get_list_votings(request):
    filter = request.GET.get('filter')
    busqueda = request.GET.get('nombre')
    list = None
    try:
        if filter == 'F':
            list = Voting.objects.filter(start_date__isnull=False, end_date__isnull=False).all()
        elif filter == 'A':
            list = Voting.objects.filter(start_date__isnull=False, end_date__isnull=True).all()
        elif filter == 'S':
            list = Voting.objects.filter(start_date__isnull=True, end_date__isnull=True).all()
        elif filter == 'Fn':
            list = Voting.objects.filter(start_date__isnull=False, end_date__isnull=False, postproc__isnull=True).all()
        else:
            if busqueda is None:
                list = Voting.objects.all()
            else:
                list = Voting.objects.filter(name__contains=busqueda).all()
    except:
        raise Http404
    # Si no soy superuser solo veo las votaciones en las que estoy censado
    if not request.user.is_superuser:
        census = Census.objects.filter(voter_id=request.user.id).all()
        new_list = []
        for c in census:
            for voting in list:
                if voting.id == c.voting_id:
                    new_list.append(voting)
        list = new_list
        user = False
    else:
        user = True
    questions = []
    for voting in list:
        question = Question.objects.filter(voting__id=voting.id).all()
        types = []
        for q in question:
            if q.type == 0:
                types.append('IDENTITY')
            if q.type == 1:
                types.append('BORDA')
            if q.type == 3:
                types.append('EQUALITY')
            if q.type == 2:
                types.append('HONDT')
            if q.type == 4:
                types.append('DROOP')
            if q.type == 5:
                types.append('IMPERIALI')
        questions.append(types)
    return render(request, 'visualizer/listVisualizer.html', {'votings': list, 'questions': questions, 'user': user})


def get_global_view(request):
    vt = 0
    ct = 0
    nvs = 0

    try:
        votings = Voting.objects.all()
        abstm = 0
        porvotm = 0
        vtm = 0
        ctm = 0
        abstr = 100
        porvotr = 100
        vtr = 999999999999999999
        ctr = 999999999999999999
        tabst = 0
        tporvot = 0
        for vot in votings:
            if vot.end_date:
                vid = vot.id
                census = Census.objects.filter(voting_id=vid).all().count()
                votes = Vote.objects.filter(voting_id=vid).all().count()
                # Votos totales y mayor / menor
                vt = vt + votes
                if vtm < votes:
                    vtm = votes
                if vtr > votes:
                    vtr = votes
                # Censo total y mayor / menor
                ct = ct + census
                if ctm < census:
                    ctm = census
                if ctr > census:
                    ctr = census

                # Numero de votaciones
                nvs = nvs + 1
                # Porcentaje de abstencion y mayor / menor
                if census != 0:
                    abst = ((votes / census) - 1) * (-100)
                    tabst = tabst + abst
                    if abstm < abst:
                        abstm = abst
                    if abstr > abst:
                        abstr = abst
                    # Porcentaje de voto y mayor / menor
                    porvot = (votes / census) * 100
                    tporvot = tporvot + porvot
                    if porvotm < porvot:
                        porvotm = porvot
                    if porvotr > porvot:
                        porvotr = porvot

    except:

        raise Http404

    return render(request, 'visualizer/globalVisualizer.html',
                  {'votes': vt, 'votesm': vtm, 'census': ct, 'censusm': ctm, 'nvoting': nvs,
                   'abst': tabst, 'abstm': abstm, 'porvot': tporvot, 'porvotm': porvotm, 'porvotr': porvotr,
                   'abstr': abstr, 'votesr': vtr, 'censusr': ctr})