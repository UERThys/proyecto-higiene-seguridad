from django.contrib import admin
from .models import Empresa, Establecimiento, CIIU, Provincia, Localidad, CodigoPostal

class EstablecimientoInline(admin.TabularInline):
    model = Establecimiento
    extra = 1
    fields = ('nombre', 'cuit', 'numero_establecimiento', 'principal')
    show_change_link = True

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre_fantasia', 'cuit', 'tipo_organismo', 'organismo')  # Cambio 'razon_social' por 'nombre_fantasia'
    search_fields = ('nombre_fantasia', 'cuit')  # Cambié aquí también
    inlines = [EstablecimientoInline]

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cuit', 'razon_social_empresa', 'numero_establecimiento', 'principal')
    search_fields = ('nombre', 'cuit')

    def razon_social_empresa(self, obj):
        return obj.empresa.nombre_fantasia if obj.empresa else "-"  # Cambié 'razon_social' por 'nombre_fantasia'
    razon_social_empresa.short_description = "Empresa"

@admin.register(CodigoPostal)
class CodigoPostalAdmin(admin.ModelAdmin):
    list_display = ('provincia', 'localidad', 'cp', 'cpa')
    search_fields = ('localidad__nombre', 'cp', 'cpa')
    list_filter = ('provincia',)

