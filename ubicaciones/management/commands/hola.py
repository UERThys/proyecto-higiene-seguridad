# ubicaciones/management/commands/hola.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Un simple comando de prueba que imprime Hola Mundo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('¡Hola Mundo desde el comando de ubicaciones!'))