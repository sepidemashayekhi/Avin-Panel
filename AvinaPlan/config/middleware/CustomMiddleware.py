from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied
from django.http import HttpResponse
import jwt
from Users.models import User, UserAccess
JWT_SECRET = 'secret'
from django.urls import resolve

WITHOUTLICENS = ['index', 'schema-swagger-ui', 'user-create-user', 'user-login-user', 'user-set-newpass', 'user-set-pass',
                 'user-recover-pass'
                 ]

USERPORTAL = [
    '/portal/user/write/', '/portal/user/delete/', '/portal/user/read/'
]

def get_data(request):
    data = request.POST.dict() or request.GET.dict()
    user_id = data.get('UserId')
    return user_id

def get_licensed_menus(request,user_id, current_route):
    user = User.objects.filter(UserId=user_id).first()
    if not user:
        return False
    if user.IsAdmin and user.Active:
        return True
    user_access_path = UserAccess.objects.filter(UserId__UserId=user_id).values_list('UrlPath', flat=True)
    if current_route in USERPORTAL and user_id == get_data(request):
        return True
    if not user_access_path:
        return False
    if current_route in user_access_path:
        return True
    return False


class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        current_route_name = resolve(request.path_info).url_name
        auth_header = request.headers.get('Authorization')
        current_route = request.path_info

        if current_route_name not in WITHOUTLICENS:
            if auth_header and auth_header.startswith('Bearer '):
                token_key = auth_header.split(' ')[1]
                decode = jwt.decode(token_key, algorithms='HS256', key=JWT_SECRET)
                licens = get_licensed_menus(request ,decode['UserId'], current_route)
                if not licens:
                    return HttpResponse('not access', status=401)
            else:
                return HttpResponse('not access', status=401)


