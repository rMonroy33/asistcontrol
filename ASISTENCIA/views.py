import re
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

            nombre = form.cleaned_data['nombre']
            nombre = nombre.upper()
            if not re.match(r'^[A-ZÁÉÍÓÚÑ\s]+$', nombre):
                messages.error(request, 'El nombre solo puede contener letras')
                context = {'form': form}
                return render(request, 'asistencia/registro_alumno.html', context)        
    
            num_control = form.cleaned_data['num_control']
            if not re.match(r'^[0-9]{8}$', num_control):
                messages.error(request, 'El número de control debe contener solo dígitos (8)')
                context = {'form': form}
                return render(request, 'asistencia/registro_alumno.html', context)
            
            carrera = form.cleaned_data['carrera']
            carrera = carrera.upper()
            if not re.match(r'^[A-ZÁÉÍÓÚ\s]+$', carrera):
                messages.error(request, 'La carrera solo puede contener letras')
                context = {'form': form}
                return render(request, 'asistencia/registro_alumno.html', context)
            
            form.instance.nombre = nombre
            form.instance.carrera = carrera
            alumno = form.save()
            messages.success(request, f'Alumno {alumno.nombre} registrado exitosamente con número de control {alumno.num_control}.')
            return redirect('registro_alumno')
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
    if request.method == 'POST':
        codigo_alumno = request.POST.get('codigo').strip().upper()
        if not re.match(r'^[0-9]{8}$', codigo_alumno):
            messages.error(request, 'El código de alumno debe contener solo dígitos (8).')
            return redirect('registro_asistencia')
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

        return redirect('registro_asistencia')

    context = {}
    return render(request, 'asistencia/registro_asistencia.html', context)


# ======================== VISTAS PARA MÓDULO DE REPORTES ========================

def reportes_principal(request):
    """
    P7: Diseñar vista de Reportes
    Crear una página principal con opciones para seleccionar el tipo de reporte deseado (Diario, Semanal, Mensual)
    """
    return render(request, 'asistencia/reportes_principal.html')


def reporte_diario(request):
    """
    P8: Generar Reporte Diario
    Implementar la lógica en la vista para filtrar y mostrar la asistencia por un día específico
    """
    fecha_seleccionada = request.GET.get('fecha')
    
    if fecha_seleccionada:
        try:
            fecha_obj = date.fromisoformat(fecha_seleccionada)
        except ValueError:
            fecha_obj = date.today()
    else:
        fecha_obj = date.today()
    
    # Obtener asistencias del día seleccionado
    asistencias_dia = Asistencia.objects.filter(fecha=fecha_obj).select_related('alumno').order_by('hora_entrada')
    
    context = {
        'fecha_seleccionada': fecha_obj,
        'asistencias_dia': asistencias_dia,
    }
    return render(request, 'asistencia/reporte_diario.html', context)


def reporte_semanal(request):
    """
    P9: Generar Reporte Semanal
    Implementar la lógica para filtrar y agregar la asistencia por un rango de 7 días
    """
    fecha_inicio_str = request.GET.get('fecha_inicio')
    
    if fecha_inicio_str:
        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
        except ValueError:
            fecha_inicio = date.today() - timedelta(days=6)
    else:
        fecha_inicio = date.today() - timedelta(days=6)
    
    # Calcular fecha de fin (6 días después del inicio para completar 7 días)
    fecha_fin = fecha_inicio + timedelta(days=6)
    
    # Obtener asistencias en el rango de fechas
    asistencias_semana = Asistencia.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    ).select_related('alumno').order_by('fecha', 'hora_entrada')
    
    # Agrupar asistencias por día
    asistencias_por_dia = []
    for i in range(7):
        fecha_actual = fecha_inicio + timedelta(days=i)
        asistencias_del_dia = asistencias_semana.filter(fecha=fecha_actual)
        asistencias_por_dia.append({
            'fecha': fecha_actual,
            'asistencias': asistencias_del_dia,
            'total': asistencias_del_dia.count()
        })
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'asistencias_por_dia': asistencias_por_dia,
    }
    return render(request, 'asistencia/reporte_semanal.html', context)


def reporte_mensual(request):
    """
    P10: Generar Reporte Mensual
    Implementar la lógica para filtrar y resumir la asistencia por un mes y año específicos
    """
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    
    # Valores por defecto (mes y año actual)
    fecha_actual = date.today()
    if mes:
        try:
            mes = int(mes)
        except ValueError:
            mes = fecha_actual.month
    else:
        mes = fecha_actual.month
        
    if anio:
        try:
            anio = int(anio)
        except ValueError:
            anio = fecha_actual.year
    else:
        anio = fecha_actual.year
    
    # Obtener asistencias del mes
    asistencias_mes = Asistencia.objects.filter(
        fecha__year=anio,
        fecha__month=mes
    ).select_related('alumno').order_by('fecha', 'hora_entrada')
    
    # Estadísticas básicas del mes
    total_asistencias = asistencias_mes.count()
    
    # Obtener el nombre del mes
    import calendar
    nombre_mes = calendar.month_name[mes]
    
    context = {
        'mes': mes,
        'anio': anio,
        'nombre_mes': nombre_mes,
        'asistencias_mes': asistencias_mes,
        'total_asistencias': total_asistencias,
    }
    return render(request, 'asistencia/reporte_mensual.html', context)


def exportar_reportes(request):
    """
    P11: Exportar reportes a Excel
    Añadir funcionalidad a las vistas de reportes para que los datos puedan ser descargados en formato Excel
    """
    tipo_reporte = request.GET.get('tipo', 'diario')
    
    # Preparar datos según el tipo de reporte
    if tipo_reporte == 'diario':
        fecha = request.GET.get('fecha', str(date.today()))
        try:
            fecha_obj = date.fromisoformat(fecha)
        except ValueError:
            fecha_obj = date.today()
        
        asistencias = Asistencia.objects.filter(fecha=fecha_obj).select_related('alumno')
        filename = f'reporte_diario_{fecha_obj.strftime("%Y-%m-%d")}'
        
    elif tipo_reporte == 'semanal':
        fecha_inicio = request.GET.get('fecha_inicio', str(date.today() - timedelta(days=6)))
        try:
            fecha_inicio_obj = date.fromisoformat(fecha_inicio)
            fecha_fin_obj = fecha_inicio_obj + timedelta(days=6)
        except ValueError:
            fecha_inicio_obj = date.today() - timedelta(days=6)
            fecha_fin_obj = date.today()
        
        asistencias = Asistencia.objects.filter(
            fecha__range=[fecha_inicio_obj, fecha_fin_obj]
        ).select_related('alumno')
        filename = f'reporte_semanal_{fecha_inicio_obj.strftime("%Y-%m-%d")}_al_{fecha_fin_obj.strftime("%Y-%m-%d")}'
        
    else:  # mensual
        mes = int(request.GET.get('mes', date.today().month))
        anio = int(request.GET.get('anio', date.today().year))
        
        asistencias = Asistencia.objects.filter(
            fecha__year=anio,
            fecha__month=mes
        ).select_related('alumno')
        filename = f'reporte_mensual_{anio}-{mes:02d}'
    
    return _exportar_excel(asistencias, filename, tipo_reporte)


def _exportar_excel(asistencias, filename, tipo_reporte):
    """
    Función auxiliar para exportar datos a Excel
    Requiere la librería openpyxl: pip install openpyxl
    """
    try:
        import openpyxl
        from django.http import HttpResponse
        import io
        
        # Crear libro de Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Reporte {tipo_reporte.capitalize()}"
        
        # Encabezados
        ws['A1'] = 'Alumno'
        ws['B1'] = 'Número de Control'
        ws['C1'] = 'Carrera'
        ws['D1'] = 'Fecha'
        ws['E1'] = 'Hora de Entrada'
        
        # Agregar datos
        row = 2
        for asistencia in asistencias:
            ws[f'A{row}'] = asistencia.alumno.nombre
            ws[f'B{row}'] = asistencia.alumno.num_control
            ws[f'C{row}'] = asistencia.alumno.carrera
            ws[f'D{row}'] = asistencia.fecha.strftime('%Y-%m-%d')
            ws[f'E{row}'] = asistencia.hora_entrada.strftime('%H:%M:%S')
            row += 1
        
        # Guardar en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Crear respuesta HTTP
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        return response
        
    except ImportError:
        from django.http import HttpResponse
        response = HttpResponse("Error: La librería openpyxl no está instalada. Instálela con 'pip install openpyxl'", 
                              content_type='text/plain')
        return response


