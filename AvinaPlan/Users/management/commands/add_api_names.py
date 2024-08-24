from django.core.management.base import BaseCommand

from Users.models import Menu


class Command(BaseCommand):
    help = 'Add API names to the Menu model'

    def handle(self, *args, **kwargs):
        api_names = [
            "portal/passiveuser",
        ]

        for name in api_names:
            if not Menu.objects.filter(Title=name).exists():
                Menu.objects.create(Title=name)
                self.stdout.write(self.style.SUCCESS(f'Successfully added {name} to Menu'))
            else:
                self.stdout.write(self.style.WARNING(f'{name} already exists in Menu'))