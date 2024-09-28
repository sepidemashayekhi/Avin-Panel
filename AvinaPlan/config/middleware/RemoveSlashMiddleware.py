from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponsePermanentRedirect
from django.urls import resolve
class RemoveSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path.endswith('/') and len(request.path) > 1:
            # اصلاح مسیر با اضافه کردن اسلش
            new_path = request.path + '/'

            # دریافت ویو مرتبط با مسیر جدید
            view_func, args, kwargs = resolve(new_path)

            # اجرای ویو با درخواست اصلی (حفظ متد POST یا GET)
            return view_func(request, *args, **kwargs)