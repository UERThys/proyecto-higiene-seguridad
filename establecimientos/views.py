from django.shortcuts import render, redirect
from .forms import EstablecimientoForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Localidad

@csrf_exempt
def cargar_localidades(request):
    provincia_id = request.GET.get('provincia_id')
    if not provincia_id:
        return JsonResponse({'error': 'Falta provincia_id'}, status=400)

    localidades = Localidad.objects.filter(provincia_id=provincia_id).order_by('nombre')
    data = [{'id': loc.id, 'nombre': loc.nombre} for loc in localidades]
    return JsonResponse(data, safe=False)

def crear_establecimiento(request):
    if request.method == 'POST':
        form = EstablecimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El establecimiento fue registrado exitosamente.')
            return redirect('lista_establecimientos')
    else:
        form = EstablecimientoForm()
    return render(request, 'establecimientos/formulario.html', {'form': form})

from .models import Establecimiento

def lista_establecimientos(request):
    establecimientos = Establecimiento.objects.select_related('provincia', 'localidad').all()
    return render(request, 'establecimientos/lista.html', {'establecimientos': establecimientos})

from django.shortcuts import get_object_or_404

def editar_establecimiento(request, id):
    establecimiento = get_object_or_404(Establecimiento, id=id)
    if request.method == 'POST':
        form = EstablecimientoForm(request.POST, instance=establecimiento)
        if form.is_valid():
            form.save()
            messages.success(request, 'El establecimiento fue actualizado correctamente.')
            return redirect('lista_establecimientos')
    else:
        form = EstablecimientoForm(instance=establecimiento)
    
    return render(request, 'establecimientos/formulario.html', {'form': form})

def eliminar_establecimiento(request, id):
    establecimiento = get_object_or_404(Establecimiento, id=id)
    if request.method == 'POST':
        establecimiento.delete()
        messages.success(request, 'El establecimiento fue eliminado.')
        return redirect('lista_establecimientos')
    return render(request, 'establecimientos/eliminar_confirmacion.html', {'establecimiento': establecimiento})
