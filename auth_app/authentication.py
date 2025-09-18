from django.contrib.auth.backends import BaseBackend
from rest_framework.authtoken.admin import User


class EmailBackend(BaseBackend):
    def authenticate(self, request):

        print("HERE", request.POST.get('email'))
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    return user
                else:
                    return None
            except User.DoesNotExist:
                return None



    def get_user(self, user_id):

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None