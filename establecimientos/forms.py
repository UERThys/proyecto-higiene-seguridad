from django import forms
from .models import Establecimiento, Provincia, Localidad

class EstablecimientoForm(forms.ModelForm):
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.all().order_by('nombre'),
        label="Provincia",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all().order_by('nombre'),
        label="Localidad",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Establecimiento
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control'}),
            'piso': forms.TextInput(attrs={'class': 'form-control'}),
            'dpto': forms.TextInput(attrs={'class': 'form-control'}),
            'cpa': forms.TextInput(attrs={'class': 'form-control'}),
            'cp': forms.TextInput(attrs={'class': 'form-control'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_establecimiento': forms.NumberInput(attrs={'class': 'form-control'}),
            'numero_establecimiento': forms.NumberInput(attrs={'class': 'form-control'}),
            'temporal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'motivo_baja': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_organismo': forms.NumberInput(attrs={'class': 'form-control'}),
            'organismo': forms.NumberInput(attrs={'class': 'form-control'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
        }
