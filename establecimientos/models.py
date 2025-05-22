from django.db import models
from ubicaciones.models import Provincia

# Tabla auxiliar para CIIU
class CIIU(models.Model):
    codigo = models.IntegerField(unique=True)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

# Tabla auxiliar para Provincia
class Provincia(models.Model):
    codigo = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Tabla auxiliar para Localidad
class Localidad(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    codigo = models.BigIntegerField(unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.provincia})"

class Empresa(models.Model):
    cuit = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=255)
    tipo_organismo = models.IntegerField()
    organismo = models.IntegerField()

class Establecimiento(models.Model):
    #empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="establecimientos")
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, null=True, blank=True)
    cuit = models.CharField(max_length=11, default="00000000000")
    numero_establecimiento = models.IntegerField(default="0000")
    tipo_establecimiento = models.SmallIntegerField()
    descripcion = models.TextField(default="Sin nombre")
    nombre = models.CharField(max_length=255)  # este es "nombre_fantasia"
    calle = models.CharField(max_length=255, default="Sin calle")
    interseccion = models.CharField(max_length=255, blank=True, null=True)
    #altura = models.DecimalField(max_digits=10, decimal_places=2)
    altura = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    piso = models.CharField(max_length=10, blank=True, null=True)
    dpto = models.CharField(max_length=10, blank=True, null=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT)
    localidad_nombre = models.CharField(max_length=100,default="Sin nombre")
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    provincia_nombre = models.CharField(max_length=100,default="Sin nombre")
    cpa = models.CharField(max_length=10, blank=True, null=True)
    cp = models.CharField(max_length=10, blank=True, null=True)
    principal = models.BooleanField(default="0")
    latitud = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    tipo_organismo = models.IntegerField(default="0")
    organismo = models.IntegerField(default="0000")
    temporal = models.BooleanField(default="0")
    motivo_baja = models.IntegerField(blank=True, null=True)

    # Campos aún no incluidos:
    # codigos_art = ...
    # vinculado = ...
    # codigo_est_vinculado = ...
    # custom_fields = ...

    def __str__(self):
        return f"{self.nombre} - {self.cuit}"

class EstablecimientoEmpresa(models.Model):
    cuit = models.CharField(max_length=11)
    ciiu = models.ForeignKey(CIIU, on_delete=models.PROTECT)
    propio = models.BooleanField()
    fecha_inicio_actividad = models.DateTimeField()
    fecha_fin_actividad = models.DateTimeField()
    tipo_organismo = models.IntegerField()
    organismo = models.IntegerField()
    motivo_baja = models.IntegerField(blank=True, null=True)



    def __str__(self):
        return f"{self.razon_social} ({self.cuit})"
    
    # Relación con establecimiento se deja sin cargar por ahora
    # establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)

    # Campos aún no incluidos:
    # custom_fields = ...

    def __str__(self):
        return f"{self.cuit} - {self.ciiu.descripcion}"
    
class CodigoPostal(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT)
    cp = models.CharField(max_length=10)
    cpa = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ('provincia', 'localidad', 'cp')

    def __str__(self):
        return f"{self.localidad.nombre} ({self.cp} - {self.cpa})"

'''class Provincia(models.Model):
    id = models.IntegerField(primary_key=True)  # id_provincia
    nombre = models.CharField(max_length=100)   # nombre_provincia

    def __str__(self):
        return self.nombre'''

'''class Departamento(models.Model):
    id = models.IntegerField(primary_key=True)   # id_depto
    nombre = models.CharField(max_length=100)    # nombre_depto
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="departamentos")

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"'''

from django.db import models

class ActividadCLAE(models.Model):
    codigo = models.CharField(max_length=6, unique=True)
    descripcion = models.TextField()

    clae3 = models.CharField(max_length=3, null=True, blank=True)
    clae3_desc = models.TextField(null=True, blank=True)

    clae2 = models.CharField(max_length=2, null=True, blank=True)
    clae2_desc = models.TextField(null=True, blank=True)

    letra = models.CharField(max_length=1, null=True, blank=True)
    letra_desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"



