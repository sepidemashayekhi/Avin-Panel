from django.core.management.base import BaseCommand

from Users.models import Flag, Access
import persian

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        flag_list = {
                        1: persian.convert_ar_characters('کاربران'),
                        2: persian.convert_ar_characters('گزارشات')
                     }
        access_list = ['read', 'write', 'create', 'delete']

        for flag in flag_list:
            if not Flag.objects.filter(Title=flag_list[flag]).first():
                Flag.objects.create(Title=flag_list[flag], Priority=flag)
                self.stdout.write(f'Successfully added {flag} to Flag')
        for access in access_list:
            if not Access.objects.filter(Title=access).first():
                Access.objects.create(Title=access)
                self.stdout.write(f'Successfully added {access} to Access')



