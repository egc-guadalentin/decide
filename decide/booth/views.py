import json
import datetime
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.functions import ExtractMonth
from django.db.models import Count

from base import mods
from census.models import Census
from voting.models import Voting, Question
from store.models import Vote
from .models import SuggestingForm

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
        today = datetime.datetime.now()
        last_month = today.month - 1
        if last_month == 0: last_month = 12

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

def suggestions_approved(voter_id):
    suggestions = SuggestingForm.objects.filter(user_id=voter_id).filter(is_approved=True)
    return suggestions

def suggestions_recent(voter_id):
    recent_suggestions = []
    suggestions = SuggestingForm.objects.filter(user_id=voter_id)
    for s in suggestions:
        if s.was_published_recently() == True:
            recent_suggestions.append(s)

    return recent_suggestions

def dashboard_details(voter_id):
    context={}
    available_votings = []
    votings_by_month = []
    months = []
    votings_by_type = []
    approved_suggestions = []
    recent_suggestions = []

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
        approved_suggestions = suggestions_approved(voter_id)
        recent_suggestions = suggestions_recent(voter_id)

    context['vot_dis'] = available_votings
    context['votaciones_por_meses'] = votings_by_month
    context['months'] = months
    context['tipo_votaciones'] = votings_by_type
    context['approved_suggestions'] = approved_suggestions
    context['recent_suggestions'] = recent_suggestions

    if len(available_votings) == 0:
        context['no_vot_dis'] = True

    if len(approved_suggestions) == 0:
        context['no_approved_suggs'] = True

    if len(recent_suggestions) == 0:
        context['no_recents_suggs'] = True

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
        token = request.session.get('user_token', None)
        if token == None:
            return render(request, 'booth/login.html')
        else:
            voter_id = request.session.get('voter_id', None)
            context = dashboard_details(voter_id)
            if 'username' in request.session:
                context['username'] = request.session['username']
            return render(request, 'booth/dashboard.html', context)

def question_position_by_id(questions_list, question_id):
    i=0
    for question in questions_list:
        if int(question['id']) == question_id:
            break
        else:
            i+=1

    return i

def get_user(self):
    token = self.request.session.get('user_token', None)
    voter = mods.post('authentication', entry_point='/getuser/', json=token)
    voter_id = voter.get('id', None)
    return json.dumps(token.get('token', None)), json.dumps(voter), voter_id

def check_next_question(context, current_question_position, number_of_questions, r):
    if current_question_position == number_of_questions-1:
        context['last_question']=True
    else:
        next_question_id = r[0]['question'][current_question_position+1]['id']
        context['next_question_id'] = next_question_id

def store_voting_and_question(context, current_question_position, r):
    context['voting'] = json.dumps(r[0])
    context['question'] = json.dumps(r[0]['question'][current_question_position])
    context['multiple_option'] = int(r[0]['question'][current_question_position]['option_types']) == 2
    context['rank_order_scale'] = int(r[0]['question'][current_question_position]['option_types']) == 3

def check_user_has_voted_question(context, voting_id, question_id, voter_id):
    number_of_votes = Vote.objects.filter(voting_id=voting_id, question_id=question_id, voter_id=voter_id).count()
    if number_of_votes !=0:
        context['voted'] = True

class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voting_id = kwargs.get('voting_id', 0)
        context['voting_id'] = voting_id
        question_id = kwargs.get('question_id', 0)
        context['question_id']=question_id

        context['token'], context['voter'], voter_id = get_user(self)
        context['KEYBITS'] = settings.KEYBITS

        try:
            r = mods.get('voting', params={'id': voting_id})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            number_of_questions = len(r[0]['question'])
            current_question_position = question_position_by_id(r[0]['question'], question_id)

            check_next_question(context, current_question_position, number_of_questions, r)

            store_voting_and_question(context, current_question_position, r)

            check_user_has_voted_question(context, voting_id, question_id, voter_id)

        except:
            raise Http404("This voting does not exist")

        return context

class SuggestingFormView(TemplateView):
    template_name="booth/suggesting.html"

    def dispatch(self, request, *args, **kwargs):
        if not 'user_token' in request.session:
            return HttpResponseRedirect(reverse('login'))

        return super(SuggestingFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['post_data'] = check_unresolved_post_data(self.request.session)

        return context

class SuggestingDetailView(TemplateView):
    template_name="booth/suggesting.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sid = kwargs.get('suggesting_id', 0)
        user_id = self.request.session['voter_id']

        try:
            suggesting = SuggestingForm.objects.get(pk=sid)

            if suggesting.user_id == user_id:
                context['suggesting'] = suggesting

                if suggesting.is_approved:
                    context['suggesting_state'] = "Su sugerencia ha sido aprobada."
                elif suggesting.is_approved is None:
                    context['suggesting_state'] = "Su sugerencia está pendiente de revisión."
                else:
                    context['suggesting_state'] = "Su sugerencia ha sido rechazada."
            else:
                context['access_blocked'] = True
        except:
            raise Http404("Suggesting Form %s does not exist" % sid)

        return context

def send_suggesting_form(request):

    if request.method == 'POST':
        user_id = request.session['voter_id']
        title = request.POST['suggesting-title']
        str_s_date = request.POST['suggesting-date']
        content = request.POST['suggesting-content']
        send_date = timezone.now().date()

        s_date = datetime.datetime.strptime(str_s_date, '%Y-%m-%d').date()

        if is_future_date(s_date):
            s = SuggestingForm(user_id=user_id, title=title, suggesting_date=s_date, content=content, send_date=send_date)
            s.save()
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            request.session['title'] = title
            request.session['suggesting_date'] = str_s_date
            request.session['content'] = content
            request.session['errors'] = "La fecha seleccionada ya ha pasado. Debe seleccionar una posterior al día de hoy."
            return HttpResponseRedirect(reverse('suggesting-form'))
    else:
        return HttpResponseRedirect(reverse('dashboard'))

def is_future_date(date):
    return date > timezone.now().date()

def check_unresolved_post_data(session):
    context = {}

    if 'title' in session and 'suggesting_date' in session and 'content' in session and 'errors' in session:
        context['title'] = session['title']
        context['suggesting_date'] = session['suggesting_date']
        context['content'] = session['content']
        context['errors'] = session['errors']
        del session['title']
        del session['suggesting_date']
        del session['content']
        del session['errors']

    return context
