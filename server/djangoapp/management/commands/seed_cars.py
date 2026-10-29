from django.core.management.base import BaseCommand

from djangoapp.populate import initiate


class Command(BaseCommand):
    help = "Populate demonstration car makes and models"

    def handle(self, *args, **options):
        initiate()
        self.stdout.write(self.style.SUCCESS("Car makes and models are ready."))
