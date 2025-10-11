from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Alumno, Asistencia
from datetime import date

def registro_asistencia(request):
    """Vista para registrar la asistencia de un alumno."""
    if request.method == 'POST':
        codigo_alumno = request.POST.get('codigo').strip().upper()
        
        try:
            alumno = Alumno.objects.get(codigo=codigo_alumno)
        except Alumno.DoesNotExist:
            messages.error(request, f"Error: No se encontró al alumno con el código '{codigo_alumno}'.")
            return redirect('registro_asistencia')

        hoy = date.today()
        if Asistencia.objects.filter(alumno=alumno, fecha=hoy).exists():
            messages.warning(request, f"{alumno.nombre} ya registró su asistencia el día de hoy.")
        else:
            Asistencia.objects.create(alumno=alumno)
            messages.success(request, f"Asistencia registrada con éxito para {alumno.nombre}.")

        return redirect('registro_asistencia')

    return render(request, 'asistencia/registro_asistencia.html')