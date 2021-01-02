import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import SuggestingForm

NOW_DATE = timezone.now().date()
S_DATE = NOW_DATE + datetime.timedelta(weeks=1)

class SuggestingFormModelTests(TestCase):
    def setUp(self):
        super().setUp()
        session = self.client.session
        session['voter_id'] = 1
        session.save()

    def tearDown(self):
        super().tearDown()
    
    def test_was_published_recently_more_than_month(self):
        """
        was_published_recently() debe retornar False si la sugerencia se envió
        hace más de un mes.
        """
        now = timezone.now().date()
        past_date = now - datetime.timedelta(weeks=4, days=1)
        past_suggesting_form = SuggestingForm(send_date=past_date, suggesting_date=now)
        self.assertIs(past_suggesting_form.was_published_recently(), False)

    def test_was_published_recently_last_week(self):
        """
        was_published_recently() debe retornar True si la sugerencia se envió
        hace una semana.
        """
        now = timezone.now().date()
        past_date = now - datetime.timedelta(weeks=1)
        past_suggesting_form = SuggestingForm(send_date=past_date, suggesting_date=now)
        self.assertIs(past_suggesting_form.was_published_recently(), True)

    def test_get_suggesting_detail_success(self):
        """
        Se comprueba que la petición del detalle de una sugerencia existente se retorna
        de forma exitosa con un código de estado HTTP 200.

        Además se comprueba que los datos de la instancia devuelta son correctos.
        """
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
        """
        Se comprueba que la petición del detalle de una sugerencia no existente se retorna
        de forma exitosa con un código de estado HTTP 404
        """
        response = self.client.get(reverse('suggesting-detail', args=(2,)), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_suggesting_form_success(self):
        """
        Se comprueba que la petición de registro de una sugerencia se realiza de forma
        correcta y que persiste en base de datos, retornando un código de estado HTTP 200
        """
        data = {'suggesting-title': 'Suggestsing', 'suggesting-date': '2021-01-08', 'suggesting-content': 'Full suggesting content...'}

        initital_suggesting_counter = SuggestingForm.objects.all().count()

        response = self.client.post('/booth/suggesting/send/', data, follow=True)

        afterpost_suggesting_counter = SuggestingForm.objects.all().count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(afterpost_suggesting_counter, initital_suggesting_counter + 1)

