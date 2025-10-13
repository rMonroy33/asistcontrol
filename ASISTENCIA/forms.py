from django import forms
from .models import Alumno

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'carrera', 'num_control']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del alumno',
                'required': True
            }),
            'carrera': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carrera del alumno',
                'required': True
            }),
            'num_control': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de control único',
                'required': True
            }),
        }
        labels = {
            'nombre': 'Nombre completo',
            'carrera': 'Carrera',
            'num_control': 'Número de control',
        }
        help_texts = {
            'num_control': 'Código único del alumno (ej: 20120001)',
        }

    def clean_num_control(self):
        num_control = self.cleaned_data.get('num_control')
        if num_control:
            num_control = num_control.strip().upper()
            # Verificar que no exista otro alumno con el mismo número de control
            if Alumno.objects.filter(num_control=num_control).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe un alumno con este número de control.")
        return num_control

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip().title()
        return nombre

    def clean_carrera(self):
        carrera = self.cleaned_data.get('carrera')
        if carrera:
            carrera = carrera.strip().title()
        return carrera