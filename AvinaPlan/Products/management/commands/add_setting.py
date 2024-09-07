from django.core.management.base import BaseCommand

from Products.models import Setting

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        if not Setting.objects.filter(Title='effective_quantity').first():
            Setting.objects.create(Title='effective_quantity')
            self.stdout.write(f'Successfully added effective quantity to setting')
