import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from base import mods
from census.models import Census
from voting.models import Voting
from store.models import Vote
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.functions import ExtractMonth
from django.db.models import Count

class LoginView(TemplateView):
    template_name = 'booth/login.html'

class LogoutView(TemplateView):
    template_name = 'booth/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('user_token')

        if token:
            mods.post('authentication', entry_point='/logout/', json={'token':token})
            del self.request.session['user_token']
            del self.request.session['voter_id']
            del self.request.session['username']

        return context

def autenticacion(request, username, password):
    token= mods.post('authentication', entry_point='/login/', json={'username':username, 'password':password})
    request.session['user_token']=token
    voter = mods.post('authentication', entry_point='/getuser/', json=token)
    voter_id = voter.get('id', None)
    request.session['voter_id'] = voter_id

    if voter_id == None:
        return False, voter_id

    return True, voter_id

def available_votings_user(list_vid, voter_id):
    available_votings=[]
    try:
        votings = Voting.objects.filter(id__in=list_vid).filter(end_date__isnull=True).exclude(start_date__isnull=True)
        for v in votings:
            if Vote.objects.filter(voting_id=v.id, voter_id=voter_id).count()==0:
                available_votings.append(v)
    except Exception:
        error='No se encuentra la votación'
    return available_votings

def last_12_months_votings_user(list_vid):
    months = [0]*12
    str_months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    try:
        today = datetime.now()
        last_month = today.month - 1    # 0
        if last_month == 0: last_month = 12  # 11

        start = today.replace(minute=0, hour=0, second=0, microsecond=0, year=today.year-1, day=1)
        end = today.replace(minute=0, hour=0, second=0, microsecond=0, day=1)

        votaciones_meses = Voting.objects.filter(id__in=list_vid).exclude(start_date__isnull=True).filter(start_date__range=(start, end)).annotate(month=ExtractMonth('start_date')).values('month').annotate(votaciones=Count('id'))

        for v in votaciones_meses:
            months[v['month']-1] = v['votaciones']

    except Exception:
        error='No se encuentra la votación'

    second_counter_months = months[:last_month]
    first_counter_months = months[last_month:12]
    counter_months = first_counter_months + second_counter_months

    second_str_months = str_months[:last_month]
    first_str_months = str_months[last_month:12]
    str_months = first_str_months + second_str_months

    return counter_months, str_months

def votings_user_by_type(list_vid):
    votings_by_type = []
    unique = 0
    mult = 0
    rank = 0

    try:
        votings = Voting.objects.filter(id__in=list_vid).filter(end_date__isnull=False)
        for v in votings:
            if v.question.option_types == 1:
                unique+=1
            elif v.question.option_types == 2:
                mult+=1
            elif v.question.option_types == 3:
                rank+=1
    except Exception:
        error='No se encuentra la votación'

    votings_by_type.append(unique)
    votings_by_type.append(mult)
    votings_by_type.append(rank)
    return votings_by_type

def dashboard_details(voter_id):
    context={}
    available_votings = []
    votings_by_month = []
    months = []
    votings_by_type = []
    context['no_censo'], context['no_vot_dis'] = False, False

    census_by_user = Census.objects.filter(voter_id=voter_id)
    if census_by_user.count() == 0 :
        context['no_censo'] = True
    else:
        list_vid=[]
        for c in census_by_user:
            vid = c.voting_id
            list_vid.append(vid)

        available_votings = available_votings_user(list_vid, voter_id)
        votings_by_month, months = last_12_months_votings_user(list_vid)
        votings_by_type = votings_user_by_type(list_vid)

    context['vot_dis'] = available_votings
    context['votaciones_por_meses'] = votings_by_month
    context['months'] = months
    context['tipo_votaciones'] = votings_by_type

    if len(available_votings) == 0:
        context['no_vot_dis'] = True

    return context

def authentication_login(request):

    if request.method == 'POST':

        username = request.POST['username']
        request.session['username'] = username
        password = request.POST['password']
        # Autenticacion
        voter, voter_id = autenticacion(request, username, password)

        if not voter:
            return render(request, 'booth/login.html', {'no_user':True})
        else:
            context = dashboard_details(voter_id)
            context['username'] = username
            return render(request, 'booth/dashboard.html', context)
    else:
        if 'username' in request.session:
            context['username'] = request.session['username']
        token = request.session.get('user_token', None)
        if token == None:
            return render(request, 'booth/login.html')
        else:
            voter_id = request.session.get('voter_id', None)
            context = dashboard_details(voter_id)
            return render(request, 'booth/dashboard.html', context)


class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)
        token = self.request.session.get('user_token', None)
        context['token']= json.dumps(token.get('token', None))
        voter = mods.post('authentication', entry_point='/getuser/', json=token)
        context['voter']= json.dumps(voter)
        voter_id = voter.get('id', None)
        try:
            r = mods.get('voting', params={'id': vid})
            print(r)
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])

            if Vote.objects.filter(voting_id=vid, voter_id=voter_id).count()!=0:
                context['voted'] = True

        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        return context
