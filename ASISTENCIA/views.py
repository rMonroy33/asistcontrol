from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Alumno, Asistencia
from .forms import AlumnoForm
from datetime import date, timedelta
from django.db.models import Count

def dashboard(request):
    hoy = date.today()
    
    # Estadísticas generales
    total_alumnos = Alumno.objects.count()
    asistencias_hoy = Asistencia.objects.filter(fecha=hoy).count()
    
    # Asistencias de los últimos 7 días
    hace_semana = hoy - timedelta(days=7)
    asistencias_semana = Asistencia.objects.filter(fecha__gte=hace_semana).count()
    
    # Alumnos más activos (con más asistencias)
    alumnos_activos = Alumno.objects.annotate(
        total_asistencias=Count('asistencia')
    ).order_by('-total_asistencias')[:5]
    
    # Asistencias por día de los últimos 7 días
    asistencias_por_dia = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        cantidad = Asistencia.objects.filter(fecha=fecha).count()
        asistencias_por_dia.append({
            'fecha': fecha,
            'cantidad': cantidad
        })
    asistencias_por_dia.reverse()  # Para mostrar de más antiguo a más reciente
    
    # Últimas asistencias registradas
    ultimas_asistencias = Asistencia.objects.select_related('alumno').order_by('-fecha', '-hora_entrada')[:10]
    
    context = {
        'total_alumnos': total_alumnos,
        'asistencias_hoy': asistencias_hoy,
        'asistencias_semana': asistencias_semana,
        'alumnos_activos': alumnos_activos,
        'asistencias_por_dia': asistencias_por_dia,
        'ultimas_asistencias': ultimas_asistencias,
        'fecha_hoy': hoy,
    }
    return render(request, 'asistencia/dashboard.html', context)

def alumnosGet(request):
    alumnos = Alumno.objects.all().order_by('nombre')
    total_alumnos = alumnos.count()
    
    context = {
        'alumnos': alumnos,
        'total_alumnos': total_alumnos,
    }
    return render(request, 'asistencia/alumnosGet.html', context)

def registro_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save()
            messages.success(request, f'Alumno {alumno.nombre} registrado exitosamente con número de control {alumno.num_control}.')
            return redirect('alumnosGet')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AlumnoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'asistencia/registro_alumno.html', context)

def asistenciasGet(request):
    hoy = date.today()
    
    # Asistencias del día actual
    asistencias_hoy = Asistencia.objects.filter(fecha=hoy).select_related('alumno').order_by('-hora_entrada')
    
    # Asistencias de los últimos 7 días
    hace_semana = hoy - timedelta(days=7)
    asistencias_semana = Asistencia.objects.filter(fecha__gte=hace_semana).select_related('alumno').order_by('-fecha', '-hora_entrada')
    
    context = {
        'asistencias_hoy': asistencias_hoy,
        'asistencias_semana': asistencias_semana,
        'fecha_hoy': hoy,
        'total_hoy': asistencias_hoy.count(),
        'total_semana': asistencias_semana.count(),
    }
    return render(request, 'asistencia/asistenciasGet.html', context)

def registro_asistencia(request):
    """Vista para registrar la asistencia de un alumno."""
    if request.method == 'POST':
        codigo_alumno = request.POST.get('codigo').strip().upper()
        
        try:
            alumno = Alumno.objects.get(num_control=codigo_alumno)
        except Alumno.DoesNotExist:
            messages.error(request, f"Error: No se encontró al alumno con el número de control '{codigo_alumno}'.")
            return redirect('registro_asistencia')

        hoy = date.today()
        if Asistencia.objects.filter(alumno=alumno, fecha=hoy).exists():
            messages.warning(request, f"{alumno.nombre} ya registró su asistencia el día de hoy.")
        else:
            Asistencia.objects.create(alumno=alumno)
            messages.success(request, f"Asistencia registrada con éxito para {alumno.nombre}.")

        return redirect('asistenciasGet')

    context = {}
    return render(request, 'asistencia/registro_asistencia.html', context)