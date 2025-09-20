from datetime import datetime, UTC
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import CustomUserModel
from auth_app.serializers import RegisterCustomUserSerializer
from auth_app.utils import TokenService


class RegisterAPIView(APIView):
    """
    endpoint для регистрации пользователя POST
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterCustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUserModel.objects.create_user(**serializer.validated_data)
            access_token, refresh_token = TokenService.generate_jwt_tokens(user,
                                                                           ip_address=request.META.get("REMOTE_ADDR"),
                                                                           user_agent=request.META.get(
                                                                               "HTTP_USER_AGENT"))
            user.last_login = datetime.now(UTC)
            user.save()
            # user = serializer.save()  # TODO будет время переопределить в сериализаторе что бы хэшировался пароль
            return Response(
                {
                    'success': True,
                    'message': 'Регистрация прошла успешно!',
                    'data': {
                        'access': access_token,
                        'refresh': refresh_token,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response({
                'success': False,
                'message': 'Невалидные данные для регистрации!',
                'data':{
                    'error': serializer.errors
                },  # TODO может быть переименовать в data
            }, status=status.HTTP_400_BAD_REQUEST)
