import csv
from django.core.management.base import BaseCommand
from ubicaciones.models import Provincia, Departamento

class Command(BaseCommand):
    help = "Importa provincias y departamentos desde un archivo CSV"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Ruta al archivo provincias_deptos.csv")

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            provincias_creadas = 0
            deptos_creados = 0

            for row in reader:
                prov_id = int(row['id_provincia'])
                prov_nombre = row['nombre_provincia'].strip()

                provincia, created = Provincia.objects.get_or_create(
                    id=prov_id,
                    defaults={'nombre': prov_nombre}
                )
                if created:
                    provincias_creadas += 1

                depto_id = int(row['id_depto'])
                depto_nombre = row['nombre_depto'].strip()

                departamento, created = Departamento.objects.get_or_create(
                    id=depto_id,
                    defaults={
                        'nombre': depto_nombre,
                        'provincia': provincia
                    }
                )
                if created:
                    deptos_creados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Importación completada: {provincias_creadas} provincias nuevas, {deptos_creados} departamentos nuevos."
        ))