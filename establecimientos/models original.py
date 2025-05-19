from django.db import models

class Establecimiento(models.Model):
    cuit_empleador = models.CharField("CUIT del empleador", max_length=13)
    nombre = models.CharField("Nombre del establecimiento", max_length=100)
    direccion = models.CharField("Dirección", max_length=255)
    localidad = models.CharField("Localidad", max_length=100)
    provincia = models.CharField("Provincia", max_length=100)
    codigo_postal = models.CharField("Código Postal", max_length=10)
    telefono = models.CharField("Teléfono", max_length=20)
    email = models.EmailField("Correo electrónico")
    tipo_establecimiento = models.CharField("Tipo de establecimiento", max_length=100)
    actividad_clae = models.CharField("Código CLAE", max_length=10)
    descripcion_actividad = models.TextField("Descripción de la actividad")
    cantidad_trabajadores = models.PositiveIntegerField("Cantidad de trabajadores")
    turnos = models.CharField("Turnos de trabajo", max_length=100)
    trabajo_nocturno = models.BooleanField("¿Hay trabajo nocturno?")
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.localidad} ({self.cuit_empleador})"
