from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import SensorData, PuntoClave, Experimento
from datetime import datetime
import csv
import json
from django.utils import timezone



def home(request):
    return render(request, 'home.html')

import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Experimento

import csv
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Experimento

def experiment_list(request):
    mensaje = ""
    # Procesamiento de acciones vía POST (crear, eliminar, finalizar)
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "crear":
            comentario = request.POST.get("comentario")
            # Calcula el número siguiente basado en el último experimento registrado
            last_exp = Experimento.objects.all().order_by("-num").first()
            next_num = (last_exp.num + 1) if last_exp else 1
            Experimento.objects.create(num=next_num, comentario=comentario)
            mensaje = f"Experimento {next_num} creado exitosamente."
        elif accion == "eliminar":
            num_eliminar = request.POST.get("num_experimento")
            try:
                exp = Experimento.objects.get(num=num_eliminar)
                exp.delete()
                mensaje = f"Experimento {num_eliminar} eliminado."
            except Experimento.DoesNotExist:
                mensaje = f"No existe el experimento con número {num_eliminar}."
        elif accion == "finalizar":
            try:
                exp = Experimento.objects.get(activa=True)
                exp.activa = False
                exp.hora_finalizacion = timezone.now().time()
                exp.save()
                mensaje = f"Experimento {exp.num} finalizado."
            except Experimento.DoesNotExist:
                mensaje = "No hay experimento activo para finalizar."
        return redirect("experiment_list")
    
    # Procesamiento de GET para descarga de un experimento específico
    if request.method == "GET":
        accion = request.GET.get("accion")
        if accion == "descargar":
            num_descargar = request.GET.get("num_experimento")
            try:
                exp = Experimento.objects.get(num=num_descargar)
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = f'attachment; filename="Experimento_{num_descargar}.csv"'
                writer = csv.writer(response)
                writer.writerow(["ID", "Num", "Descripcion", "Fecha Inicio", "Hora Inicio", "Hora Finalizacion", "Activa", "Comentario"])
                writer.writerow([exp.id, exp.num, exp.descripcion, exp.fecha_inicio, exp.hora_inicio, exp.hora_finalizacion, exp.activa, exp.comentario])
                return response
            except Experimento.DoesNotExist:
                mensaje = f"Experimento {num_descargar} no existe para descargar."
        elif accion == "descargar_todos":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="Experimentos_todos.csv"'
            writer = csv.writer(response)
            writer.writerow(["ID", "Num", "Descripcion", "Fecha Inicio", "Hora Inicio", "Hora Finalizacion", "Activa", "Comentario"])
            for exp in Experimento.objects.all().order_by("fecha_inicio"):
                writer.writerow([exp.id, exp.num, exp.descripcion, exp.fecha_inicio, exp.hora_inicio, exp.hora_finalizacion, exp.activa, exp.comentario])
            return response

    # En GET normal: obtener la lista completa de experimentos (ordenados de los más viejos a los más nuevos)
    experiments = Experimento.objects.all().order_by("fecha_inicio")
    active_experiment = Experimento.objects.filter(activa=True).first()
    crear_experimento = (active_experiment is None)
    # Calcular next_num para la creación de un nuevo experimento si es necesario
    last_exp = Experimento.objects.all().order_by("-num").first()
    next_num = (last_exp.num + 1) if last_exp else 1

    # Para el select, solo se muestran los experimentos inactivos (finalizados)
    inactive_experiments = Experimento.objects.filter(activa=False).order_by("fecha_inicio")
    default_exp = inactive_experiments.last() if inactive_experiments.exists() else None

    context = {
        "mensaje": mensaje,
        "experiments": experiments,
        "active_experiment": active_experiment,
        "crear_experimento": crear_experimento,
        "next_num": next_num,
        "inactive_experiments": inactive_experiments,
        "default_exp": default_exp,
    }
    return render(request, "experiment_list.html", context)



from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import SensorData, PuntoClave, Experimento
import csv

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import SensorData, PuntoClave, Experimento
import csv

def mostrar_tabla(request, tabla):
    # Obtener experimento a visualizar
    experimento_id = request.GET.get('experimento_id')
    if experimento_id:
        experimento = Experimento.objects.filter(num=experimento_id).first()
    else:
        experimento = Experimento.objects.order_by('-num').first()

    # Si no hay ningún experimento, retornar datos vacíos o un mensaje
    if not experimento:
        return render(request, 'mostrar_tabla.html', {
            'datos': [],
            'tabla': tabla,
            'titulo': 'Sin Experimentos',
            'experimento': None,
            'cantidad_actual': 'Todos',
            'anterior': None,
            'siguiente': None,
            'last_experiment': None,
        })

    # Captura de la cantidad de datos a mostrar
    cantidad_actual = request.GET.get('cantidad', 'Todos')

    # Filtrar los datos según la tabla
    if tabla == 'sensor':
        datos = SensorData.objects.filter(experimento=experimento).order_by('-hora')
        titulo = 'Datos del Sensor'
    elif tabla == 'punto':
        datos = PuntoClave.objects.filter(experimento=experimento).order_by('-hora')
        titulo = 'Puntos Clave'
    else:
        return HttpResponse("Tabla no válida", status=400)

    # Aplicar filtro de cantidad si es un número
    if cantidad_actual.isdigit():
        datos = datos[:int(cantidad_actual)]

    # Navegación
    anterior = Experimento.objects.filter(num__lt=experimento.num).order_by('-num').first()
    siguiente = Experimento.objects.filter(num__gt=experimento.num).order_by('num').first()
    last_experiment = Experimento.objects.order_by('-num').first()

    context = {
        'datos': datos,
        'tabla': tabla,
        'titulo': titulo,
        'experimento': experimento,
        'cantidad_actual': cantidad_actual,
        'anterior': anterior,
        'siguiente': siguiente,
        'last_experiment': last_experiment,
    }
    return render(request, 'mostrar_tabla.html', context)


import csv
from django.http import HttpResponse
from .models import Experimento, SensorData, PuntoClave

def descargar_datos(request, experimento_id, tabla):
    # Buscamos el experimento con el número dado
    try:
        exp = Experimento.objects.get(num=experimento_id)
    except Experimento.DoesNotExist:
        return HttpResponse("Experimento no encontrado", status=404)
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="Experimento_{experimento_id}.csv"'
    
    writer = csv.writer(response)
    # Escribimos la cabecera según la tabla solicitada
    if tabla == 'sensor':
        writer.writerow(["ID", "Experimento", "Hora", "Temperatura", "Presión 1", "Presión 2"])
        registros = SensorData.objects.filter(experimento=exp).order_by("-hora")
        for r in registros:
            writer.writerow([r.id, r.experimento.num, r.hora, r.temperatura, r.presion1, r.presion2])
    elif tabla == 'punto':
        writer.writerow(["ID", "Experimento", "Hora", "Temperatura", "Presión 1", "Presión 2"])
        registros = PuntoClave.objects.filter(experimento=exp).order_by("-hora")
        for r in registros:
            writer.writerow([r.id, r.experimento.num, r.hora, r.temperatura, r.presion1, r.presion2])
    else:
        # Por defecto, descargar detalles del experimento
        writer.writerow(["ID", "Num", "Descripcion", "Fecha Inicio", "Hora Inicio", "Hora Finalizacion", "Activa", "Comentario"])
        writer.writerow([exp.id, exp.num, exp.descripcion, exp.fecha_inicio, exp.hora_inicio, exp.hora_finalizacion, exp.activa, exp.comentario])
    
    return response



import json
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Experimento, SensorData, PuntoClave

@csrf_exempt
def upload_sensor_data(request):
    """
    Recibe datos continuos del Arduino (temperatura, presion1, presion2),
    busca un experimento activo y asocia los datos a SensorData.
    Si no hay experimento activo, retorna un error.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            temperatura = data.get('temperatura')
            presion1 = data.get('presion1')
            presion2 = data.get('presion2')
            if temperatura is None or presion1 is None or presion2 is None:
                return JsonResponse({'error': 'Faltan datos obligatorios'}, status=400)
            try:
                experimento = Experimento.objects.get(activa=True)
            except Experimento.DoesNotExist:
                return JsonResponse({'error': 'No hay experimento activo'}, status=400)
            SensorData.objects.create(
                experimento=experimento,
                temperatura=temperatura,
                presion1=presion1,
                presion2=presion2,
                hora=datetime.now()
            )
            return HttpResponse("Ok, Dato recibido", status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponse("Método no permitido", status=405)


@csrf_exempt
def upload_key_point_data(request):
    """
    Recibe datos del Arduino para punto clave (temperatura, presion1, presion2),
    busca un experimento activo y asocia los datos a PuntoClave.
    Si no hay experimento activo, retorna un error.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            temperatura = data.get('temperatura')
            presion1 = data.get('presion1')
            presion2 = data.get('presion2')
            if temperatura is None or presion1 is None or presion2 is None:
                return JsonResponse({'error': 'Faltan datos obligatorios'}, status=400)
            try:
                experimento = Experimento.objects.get(activa=True)
            except Experimento.DoesNotExist:
                return JsonResponse({'error': 'No hay experimento activo'}, status=400)
            PuntoClave.objects.create(
                experimento=experimento,
                temperatura=temperatura,
                presion1=presion1,
                presion2=presion2,
                hora=datetime.now()
            )
            return HttpResponse("Ok, Dato recibido", status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return HttpResponse("Método no permitido", status=405)


def visualizar_datos(request):
    """
    Renderiza una página de monitoreo que muestra SensorData y PuntoClave.
    Se puede filtrar por experimento mediante un parámetro GET.
    """
    experimento_id = request.GET.get('experimento_id')
    if experimento_id:
        sensor_data = SensorData.objects.filter(experimento__id=experimento_id).order_by('-fecha_hora')
        puntos_clave = PuntoClave.objects.filter(experimento__id=experimento_id).order_by('-fecha_hora')
    else:
        sensor_data = SensorData.objects.all().order_by('-fecha_hora')
        puntos_clave = PuntoClave.objects.all().order_by('-fecha_hora')
    
    context = {
        'sensor_data': sensor_data,
        'puntos_clave': puntos_clave,
    }
    return render(request, 'monitoring.html', context)

def download_csv(request):
    """
    Genera un archivo CSV con los datos solicitados.
    Se puede elegir la tabla (SensorData o PuntoClave) mediante un parámetro GET.
    """
    tabla = request.GET.get('tabla', 'sensor')
    experimento_id = request.GET.get('experimento_id')

    if tabla == 'punto':
        queryset = PuntoClave.objects.all()
    else:
        queryset = SensorData.objects.all()

    if experimento_id:
        queryset = queryset.filter(experimento__id=experimento_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="datos.csv"'
    
    writer = csv.writer(response)
    if tabla == 'punto':
        header = ['ID', 'Experimento', 'Fecha_Hora', 'Valor']
    else:
        header = ['ID', 'Experimento', 'Fecha_Hora', 'Temperatura', 'Presion1', 'Presion2']
    writer.writerow(header)
    
    for obj in queryset:
        if tabla == 'punto':
            writer.writerow([obj.id, obj.experimento.nombre, obj.fecha_hora, obj.valor])
        else:
            writer.writerow([obj.id, obj.experimento.nombre, obj.fecha_hora, obj.temperatura, obj.presion1, obj.presion2])
    
    return response
