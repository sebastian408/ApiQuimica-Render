# Requerimientos:
# 1. Experimento se crea desde una página; al inicio se registra su fecha y hora, pero no se establece hora_finalizacion.
# 2. Solo puede haber un experimento en curso (activo) a la vez; se agrega un campo 'activa' para controlar esto.
# 3. SensorData se asocia al experimento en curso y se elimina en cascada si se borra el experimento.
# 4. PuntoClave tiene la misma estructura que SensorData.
# 5. SensorData y PuntoClave guardan la hora de registro automáticamente.
from django.db import models
from django.utils import timezone

class Experimento(models.Model):
    num = models.IntegerField(default=0)  # Valor por defecto: 0
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)  # Se asigna automáticamente al crear
    hora_inicio = models.TimeField(auto_now_add=True)         # Se asigna automáticamente al crear
    hora_finalizacion = models.TimeField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    comentario = models.TextField(blank=True, null=True)

class SensorData(models.Model):
    experimento = models.ForeignKey(Experimento, on_delete=models.CASCADE, related_name='sensor_data')
    # Se asigna la hora actual al crear el registro
    hora = models.DateTimeField(default=timezone.now)
    temperatura = models.FloatField(default=0.0)
    presion1 = models.FloatField(default=0.0)
    presion2 = models.FloatField(default=0.0)



class PuntoClave(models.Model):
    experimento = models.ForeignKey(Experimento, on_delete=models.CASCADE, related_name='puntos_clave')
    # Se asigna la hora actual al crear el registro
    hora = models.DateTimeField(default=timezone.now)
    temperatura = models.FloatField(default=0.0)
    presion1 = models.FloatField(default=0.0)
    presion2 = models.FloatField(default=0.0)


def cargar_sensor_data(temperatura, presion1, presion2):
    """
    Crea y guarda un registro en SensorData, asociándolo al experimento activo.
    Solo se crea si existe un experimento con activa=True.
    Retorna la instancia creada o None si no se encontró un experimento activo.
    """
    try:
        experimento = Experimento.objects.get(activa=True)
    except Experimento.DoesNotExist:
        # No existe un experimento activo
        return None
    
    # Crear el registro en SensorData
    instancia = SensorData.objects.create(
        experimento=experimento,
        temperatura=temperatura,
        presion1=presion1,
        presion2=presion2
    )
    return instancia

def cargar_punto_clave(temperatura, presion1, presion2):
    """
    Crea y guarda un registro en PuntoClave, asociándolo al experimento activo.
    Se espera que los datos sean exactamente iguales a los de SensorData.
    Retorna la instancia creada o None si no se encontró un experimento activo.
    """
    try:
        experimento = Experimento.objects.get(activa=True)
    except Experimento.DoesNotExist:
        # No existe un experimento activo
        return None
    
    # Crear el registro en PuntoClave
    instancia = PuntoClave.objects.create(
        experimento=experimento,
        temperatura=temperatura,
        presion1=presion1,
        presion2=presion2
    )
    return instancia
from datetime import datetime
import csv
from django.http import HttpResponse

def finalizar_experimento(experimento):
    """
    Finaliza el experimento actual:
      - Cambia el campo 'activa' a False.
      - Registra la hora de finalización (solo la hora, ya que el campo es TimeField).
    Retorna la instancia modificada o None si el experimento ya estaba finalizado.
    """
    if experimento.activa:
        experimento.activa = False
        experimento.hora_finalizacion = datetime.now().time()
        experimento.save()
        return experimento
    return None

def descargar_datos(queryset, campos, nombre_archivo="datos.csv"):
    """
    Convierte un queryset en un archivo CSV descargable.
    
    Parámetros:
      - queryset: Conjunto de datos a exportar.
      - campos: Lista de nombres de campos (atributos) a incluir como columnas.
      - nombre_archivo: Nombre del archivo CSV resultante.
      
    Retorna un HttpResponse con el CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    writer = csv.writer(response)
    
    # Escribir la cabecera (los nombres de los campos)
    writer.writerow(campos)
    
    # Escribir cada fila del queryset
    for obj in queryset:
        fila = [getattr(obj, campo) for campo in campos]
        writer.writerow(fila)
    
    return response



