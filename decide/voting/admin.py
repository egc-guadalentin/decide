from django import forms
from django.contrib import admin
from django.utils import timezone
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django.contrib import messages

from .models import QuestionOption
from .models import Question
from .models import Voting
from census.models import Census

from .filters import StartedFilter
from django.contrib.auth.models import User
from django.contrib.auth import logout


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.started_by=str(request.user)
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()
    logout(request)


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        tally=v.tally_votes(token)
        respuesta=give_message(v,tally)
        messages.info(request,respuesta)


def give_message(v,tally):
    mensj=""
    votos = v.votes_info_votos(tally)
    for voto in votos:
        pregunta = voto['pregunta']
        mensj = mensj + "for question " + pregunta
        for o in voto['opciones']:
            opcion = o['option']
            vots = o['votes']
            mensj = mensj + " for option " + str(opcion) +" it has " + str(vots) + " votes, "
    mensj = "For voting " + v.name + ": " + mensj   
    mensj = mensj[:-2]
    mensj = mensj + "."
    respuesta=v
    return mensj


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    fields = ('number', 'option',)


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]


class VotingModel(forms.ModelForm):
    autocenso = forms.BooleanField(required=False)

    class Meta:
        model = Voting
        exclude = []


class VotingAdmin(admin.ModelAdmin):
        
    list_display = ('name', 'start_date', 'end_date', 'started_by')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc', 'started_by')
    list_filter = (StartedFilter, ('start_date', DateRangeFilter), ('end_date', DateRangeFilter),)
    search_fields = ('name', )

    actions = [ start, stop, tally ]
    form = VotingModel

    def save_model(self, request, obj, form, change):
        super(VotingAdmin, self).save_model(request, obj, form, change)
        if form.cleaned_data.get('autocenso'):
            user = request.user
            Census.objects.get_or_create(voter_id=user.id, voting_id=obj.id)


class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('desc', 'option_types')
    inlines = [QuestionOptionInline]
    list_filter = ('option_types',)


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionOptionAdmin)