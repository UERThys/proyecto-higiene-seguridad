# ubicaciones/management/commands/importar_provincias_deptos.py
# ASEGÚRATE DE QUE TU ARCHIVO LOCAL TENGA ESTA VERSIÓN:
import csv
from django.core.management.base import BaseCommand
from ubicaciones.models import Provincia, Departamento # Asegúrate que los modelos sean de aquí

class Command(BaseCommand):
    help = "Importa provincias y departamentos desde un archivo CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',  # Así defines el argumento nombrado
            type=str,
            help="Ruta completa al archivo CSV con provincias y departamentos.",
            required=True # Opcional, pero bueno si el archivo es necesario
        )

    def handle(self, *args, **options): # Nota el uso de **options
        file_path = options['archivo']  # Así accedes al valor del argumento --archivo

        self.stdout.write(self.style.SUCCESS(f'Iniciando importación desde: {file_path}'))
        
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # ... (resto de tu lógica de importación) ...
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

                    # Asumiendo que tienes un modelo Departamento con campo 'provincia' ForeignKey
                    departamento, created = Departamento.objects.get_or_create(
                        id=depto_id,
                        defaults={
                            'nombre': depto_nombre,
                            'provincia': provincia  # Asegúrate que esto sea correcto
                        }
                    )
                    if created:
                        deptos_creados += 1
            
            self.stdout.write(self.style.SUCCESS(
                f"Importación completada: {provincias_creadas} provincias nuevas, {deptos_creados} departamentos nuevos."
            ))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Error: El archivo '{file_path}' no fue encontrado."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocurrió un error durante la importación: {e}"))