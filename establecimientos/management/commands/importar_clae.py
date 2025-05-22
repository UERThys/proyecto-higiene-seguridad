import csv
from django.core.management.base import BaseCommand
from establecimientos.models import ActividadCLAE

class Command(BaseCommand):
    help = 'Importa el nomenclador CLAE desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('archivo_csv', type=str)

    def handle(self, *args, **options):
        archivo_csv = options['archivo_csv']
        with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            total = 0
            for row in reader:
                try:
                    ActividadCLAE.objects.update_or_create(
                        codigo=row['clae6'].strip(),
                        defaults={
                            'descripcion': row['clae6_desc'].strip(),
                            'clae3': row['clae3'].strip(),
                            'clae3_desc': row['clae3_desc'].strip(),
                            'clae2': row['clae2'].strip(),
                            'clae2_desc': row['clae2_desc'].strip(),
                            'letra': row['letra'].strip(),
                            'letra_desc': row['letra_desc'].strip(),
                        }
                    )
                    total += 1
                except Exception as e:
                    self.stderr.write(f"Error en fila: {row} - {e}")
        self.stdout.write(self.style.SUCCESS(f"Importación completada. {total} registros cargados."))
