from django.db import models

class Provincia(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Departamento(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='departamentos')

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"
