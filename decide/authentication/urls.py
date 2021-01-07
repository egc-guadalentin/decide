from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView, ChangeStyleView, PageLoginView, PageLogoutView


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('changestyle/', ChangeStyleView.as_view()),
    path('page-login/', PageLoginView.as_view()),
    path('page-logout/', PageLogoutView.as_view()),
    path('register/', RegisterView.as_view()),
]
