from django.urls import path
from booth import views as booth_views

urlpatterns = [
    path('', booth_views.LoginView.as_view(), name="login"),
    path('logout/', booth_views.LogoutView.as_view(), name="logout"),
    path('dashboard/', booth_views.authentication_login, name="dashboard"),
    path('<int:voting_id>/<int:question_id>/', booth_views.BoothView.as_view(), name="voting"),
    path('suggesting/', booth_views.SuggestingFormView.as_view(), name="suggesting-form"),
    path('suggesting/<int:suggesting_id>/', booth_views.SuggestingDetailView.as_view(), name="suggesting-detail"),
    path('suggesting/send/', booth_views.send_suggesting_form, name="suggesting-send"),
]
