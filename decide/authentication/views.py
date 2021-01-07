from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import UserProfile
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .serializers import UserSerializer

from base import mods


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class ChangeStyleView(APIView):
    def post(self, request):
        # validating token
        token = request.data.get('token')
        user = mods.post('authentication', entry_point='/getuser/', json={'token': token})
        user_id = user.get('id', None)

        if not user_id:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        # validating style
        newstyle = request.data.get('style')
        if not newstyle in [i[0] for i in UserProfile.styles]:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        u = UserProfile.objects.get(pk=user_id)
        u.style = newstyle
        u.save(update_fields=['style'])

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        sex = request.data.get('sex', '')
        style = request.data.get('style', '')
        pwd = request.data.get('password', '')
        if not username or not pwd or not sex or not style:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile(username=username, sex=sex, style=style)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)
