from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('nuevo/', views.crear_establecimiento, name='crear_establecimiento'),
    path('lista/', views.lista_establecimientos, name='lista_establecimientos'),
    path('editar/<int:id>/', views.editar_establecimiento, name='editar_establecimiento'),
    path('eliminar/<int:id>/', views.eliminar_establecimiento, name='eliminar_establecimiento'),
    path('exito/', lambda request: render(request, 'establecimientos/exito.html'), name='exito'),
    path('ajax/cargar-localidades/', views.cargar_localidades, name='cargar_localidades'),
]
