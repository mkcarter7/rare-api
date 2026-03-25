from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rareapi.models import RareUser


class RareAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'token':
                return None
            user = RareUser.objects.get(pk=int(token))
            if not user.active:
                raise AuthenticationFailed('User account is deactivated')
            return (user, None)
        except (ValueError, RareUser.DoesNotExist):
            raise AuthenticationFailed('Invalid token')
