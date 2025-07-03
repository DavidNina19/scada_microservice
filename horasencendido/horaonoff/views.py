# data_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time, date, timedelta
from django.db.models import Q # Importar Q para combinar filtros
from django.utils import timezone # Importar timezone para manejar zonas horarias
from .models import (
    Seriada062025, Llaves062025, Forja062025, Maestranza062025,
    Seriada072025, Llaves072025, Forja072025, Maestranza072025
)

class HorasEncendidasAPIView(APIView):
    """
    API para obtener los datos de encendido y apagado (fecha y valor) de una tabla específica,
    y calcular las horas encendidas y apagadas.
    Filtra por 'codmaq' (que contenga '%cto%' Y el 'codmaq').
    Filtra por un rango de fechas y hora de inicio.
    Recibe 'area', 'codmaq', 'fecha_inicio_str', 'fecha_fin_str', y 'hora_inicio_str' como parámetros de la URL.
    Devuelve una lista de objetos {fecha: timestamp, valor: valor_registro},
    más las horas_encendidas y horas_apagadas totales.
    """
    def get(self, request, area, codmaq, fecha_inicio_str, fecha_fin_str, hora_inicio_str, minute_inicio_str, hora_fin_str, minute_fin_str, *args, **kwargs):
        if not area or not codmaq or not fecha_inicio_str or not fecha_fin_str or not hora_inicio_str or not minute_inicio_str or not hora_fin_str or not minute_fin_str:
            return Response(
                {"error": "Los parámetros 'area', 'codmaq', 'fechaInicio', 'fechaFin' y 'horaInicio' son requeridos en la URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parsear fechas
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        mes_consulta = fecha_inicio.month
        
        # Mapeo de modelos por área y mes
        model_maps = {
            6: {  # Junio
                'seriada': Seriada062025,
                'llaves': Llaves062025,
                'forja': Forja062025,
                'maestranza': Maestranza062025,
            },
            7: {  # Julio
                'seriada': Seriada072025,
                'llaves': Llaves072025,
                'forja': Forja072025,
                'maestranza': Maestranza072025,
            }
            # Agregar más meses según sea necesario
        }

        # Obtener el modelo correcto
        area_normalized = area.lower()
        model_map = model_maps.get(mes_consulta)

        if not model_map:
            return Response(
                {"error": f"No hay modelos definidos para el mes {mes_consulta}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        model = model_map.get(area_normalized)

        try:
            # Parsear las cadenas de fecha a objetos datetime
            start_date_only = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            end_date_only = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

            start_hour = int(hora_inicio_str)
            if not (0 <= start_hour <= 23):
                raise ValueError("La hora de inicio debe ser un número entre 0 y 23.")
            start_minute = int(minute_inicio_str)
            if not (0 <= start_minute <= 60):
                raise ValueError("La hora de inicio debe ser un número entre 0 y 23.")
            end_hour = int(hora_fin_str)
            if not (0 <= end_hour <= 23):
                raise ValueError("La hora de fin debe ser un número entre 0 y 23.")
            end_minute = int(minute_fin_str)
            if not (0 <= end_minute <= 60):
                raise ValueError("La hora de inicio debe ser un número entre 0 y 23.")

            # Combinar la fecha de inicio con la hora de inicio proporcionada y hacerla timezone-aware
            naive_start_datetime = datetime.combine(start_date_only, time(start_hour, start_minute, 0))
            start_datetime = timezone.make_aware(naive_start_datetime)

            # La fecha fin siempre será hasta el final del día y hacerla timezone-aware
            naive_end_datetime = datetime.combine(end_date_only, time(end_hour, end_minute, 59, 999999))
            end_datetime = timezone.make_aware(naive_end_datetime)


            # Filtros para la consulta a la base de datos
            filters = Q(t_stamp__range=(start_datetime, end_datetime))
            filters &= Q(codmaq__icontains='on')
            filters &= Q(codmaq__icontains=codmaq) # Corregido: usar codmaq

            # Obtener todos los datos filtrados y ordenados por t_stamp
            queryset = model.objects.filter(filters).order_by('t_stamp')
            
            # Formatear los resultados para la respuesta y preparar para cálculos
            on_off_data_raw = [] # Para almacenar los datos con el valor normalizado
            for record in queryset.values('t_stamp', 'valor'):
                value_from_db = record['valor']
                newValue = '0' # Default value if conversion fails or is unexpected

                if isinstance(value_from_db, bool):
                    newValue = '1' if value_from_db else '0'
                elif isinstance(value_from_db, str):
                    if value_from_db.lower() == 'true' or value_from_db == '1':
                        newValue = '1'
                    elif value_from_db.lower() == 'false' or value_from_db == '0':
                        newValue = '0'
                    # If it's another string, it will remain '0' from default, or you can assign value_from_db directly
                elif isinstance(value_from_db, int):
                    newValue = '1' if value_from_db == 1 else '0'
                
                on_off_data_raw.append({
                    'fecha': record['t_stamp'], # Mantener como datetime para cálculos
                    'valor': newValue
                })

            # --- Cálculo de Horas Encendidas y Apagadas ---
            total_on_seconds = 0
            current_on_start_time = None
            
            # Iterar sobre los datos normalizados para calcular las horas encendidas
            # Se busca un '1' para iniciar el conteo y un '0' para detenerlo y sumar la duración.
            for record in on_off_data_raw:
                current_time = record['fecha']
                current_value = record['valor']

                if current_value == '1' and current_on_start_time is None:
                    # La máquina se acaba de encender (transición de 0 a 1 o inicio de datos en 1)
                    current_on_start_time = current_time
                
                elif current_value == '0' and current_on_start_time is not None:
                    # La máquina se acaba de apagar (transición de 1 a 0)
                    # Sumar la duración del período de encendido
                    total_on_seconds += (current_time - current_on_start_time).total_seconds()
                    current_on_start_time = None # Resetear para el siguiente período de encendido

            # Manejar el caso en que la máquina está encendida al final del período de datos
            # Si el último registro fue '1' y no se encontró un '0' posterior dentro del rango,
            # se asume que la máquina sigue encendida hasta el final del rango solicitado o hasta ahora.
            if current_on_start_time is not None:
                # El tiempo de finalización para este último bloque encendido es el mínimo entre:
                # 1. La hora actual (timezone.localtime(timezone.now()))
                # 2. El final del rango de fecha solicitado (end_datetime)
                time_until_now_or_end = min(timezone.localtime(timezone.now()), end_datetime)
                total_on_seconds += (time_until_now_or_end - current_on_start_time).total_seconds()

            horas_encendidas = total_on_seconds / 3600.0

            # Calcular las horas apagadas
            # El "tiempo total transcurrido" se calcula desde el 'start_datetime'
            # hasta la hora actual (timezone.localtime(timezone.now())) o el 'end_datetime' del rango solicitado,
            # lo que ocurra primero.
            actual_span_end_time = min(timezone.localtime(timezone.now()), end_datetime)
            total_span_seconds = (actual_span_end_time - start_datetime).total_seconds()

            # Horas apagadas = (Tiempo total transcurrido en el span - Horas encendidas)
            horas_apagadas = (total_span_seconds - total_on_seconds) / 3600.0
            
            # Asegurarse de que las horas no sean negativas (por posibles imprecisiones de flotante o lógicas de borde)
            if horas_apagadas < 0:
                horas_apagadas = 0.0

            # Preparar la lista final de datos de encendido/apagado para la respuesta (formato de cadena de fecha)
            on_off_data_formatted = []
            for record in on_off_data_raw:
                on_off_data_formatted.append({
                    'fecha': timezone.localtime(record['fecha']).strftime('%Y-%m-%d %H:%M:%S'), # Aplicar localtime aquí
                    'valor': record['valor']
                })


            return Response(
                {
                    "area": area,
                    "codmaq_buscado": codmaq, # Corregido: usar codmaq
                    "fecha_inicio": fecha_inicio_str, # Corregido: usar la cadena de fecha original
                    "fecha_fin": fecha_fin_str,       # Corregido: usar la cadena de fecha original
                    "hora_inicio": hora_inicio_str,
                    "horas_encendidas": round(horas_encendidas, 2),
                    "horas_apagadas": round(horas_apagadas, 2)
                },
                status=status.HTTP_200_OK
            )
        except ValueError as ve:
            return Response(
                {"error": f"Formato de fecha u hora inválido: {str(ve)}. Use %Y-%m-%d para fechas y un número entre 0-23 para la hora."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )