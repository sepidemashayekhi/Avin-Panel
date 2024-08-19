from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied
from django.urls import resolve
import jwt
from Users.models import User, UserAccess
JWT_SECRET = 'secret'

def get_licensed_menus(user_id, current_route):
    user_access_path = UserAccess.objects.filter(UserId__UserId=user_id).values_list('UrlPath', flat=True)
    if not user_access_path:
        return False
    if current_route in user_access_path:
        return True
    return False


class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        without_licens = ['/user/create/']
        current_route = request.path_info

        auth_header = request.headers.get('Authorization')

        if current_route not in without_licens:
            if auth_header and auth_header.startswith('Token '):
                token_key = auth_header.split(' ')[1]
                decode = jwt.decode(token_key, algorithms='HS512', key=JWT_SECRET)
                licens = get_licensed_menus(decode['user_id'], current_route)
                if not licens:
                    raise PermissionDenied('not access')
            else:
                raise PermissionDenied('not access')


