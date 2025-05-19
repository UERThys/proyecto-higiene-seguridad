import json
from django.core.management.base import BaseCommand
from establecimientos.models import Provincia, Localidad

class Command(BaseCommand):
    help = "Carga provincias y localidades desde archivo JSON oficial INDEC"

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Ruta al archivo JSON con las localidades')

    def handle(self, *args, **kwargs):
        path = kwargs['json_path']

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Guardamos provincias en un dict para evitar repetidos
        provincias_cache = {}

        for loc in data['localidades']:
            prov_id = int(loc['provincia']['id'])
            prov_nombre = loc['provincia']['nombre']

            # Crear provincia si no existe
            if prov_id not in provincias_cache:
                provincia, _ = Provincia.objects.update_or_create(codigo=prov_id, defaults={'nombre': prov_nombre})
                provincias_cache[prov_id] = provincia
            else:
                provincia = provincias_cache[prov_id]

            # Crear localidad
            localidad_id = int(loc['id'])
            nombre = loc['nombre']

            Localidad.objects.update_or_create(
                codigo=localidad_id,
                provincia=provincia,
                defaults={'nombre': nombre},
            )

        self.stdout.write(self.style.SUCCESS('¡Provincias y localidades cargadas correctamente!'))
