# data_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time, date, timedelta
from django.db.models import Q # Importar Q para combinar filtros
from .models import (
    Seriada062025, Llaves062025, Forja062025, Maestranza062025,
    Seriada072025, Llaves072025, Forja072025, Maestranza072025
)

class ProductionPerHourAPIView(APIView):
    """
    API para obtener la producción por hora (PxH) de datos de una tabla específica.
    Filtra por 'codmaq' (que contenga '%cto%' Y el 'codmaq').
    Calcula la suma de diferencias en intervalos de 3 minutos, maneja reinicios,
    y extrapola a PxH (multiplicando por 20).
    Recibe 'area', 'codmaq', 'fecha_inicio_str', 'fecha_fin_str', y 'hora_inicio_str' como parámetros de la URL.
    Devuelve una lista de objetos {fecha: timestamp_intervalo, pxh: valor_pxh}.
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

        if not model:
            return Response(
                {"error": f"Área '{area}' no válida. Las áreas permitidas son: seriada, llaves, forja, maestranza."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
                raise ValueError("La hora de fin debe ser un número entre 0 y 23.")
            

            start_datetime = datetime.combine(start_date_only, time(start_hour, start_minute, 0))
            end_datetime = datetime.combine(end_date_only, time(end_hour, end_minute, 59, 999999))

            # Filtros para la consulta a la base de datos
            filters = Q(t_stamp__range=(start_datetime, end_datetime))
            filters &= Q(codmaq__icontains='cto')
            filters &= Q(codmaq__icontains=codmaq)

            # Obtener todos los datos filtrados y ordenados por t_stamp
            queryset = model.objects.filter(filters).order_by('t_stamp')
            data_records = queryset.values('t_stamp', 'valor') # Obtener ambos campos


            pxh_results = []
            current_interval_start = None
            interval_accumulated_count = 0
            interval_previous_value = None
            is_reset_pending = False

            for record in data_records:
                current_timestamp = record['t_stamp']
                try:
                    current_value = int(float(record['valor']))
                except ValueError:
                    continue # Ignorar valores no numéricos

                # Determinar el inicio del intervalo de 3 minutos para el timestamp actual
                # Ejemplo: 10:01:30 -> 10:00:00, 10:04:15 -> 10:03:00
                interval_start_minute = (current_timestamp.minute // 3) * 3
                bucket_start = current_timestamp.replace(
                    minute=interval_start_minute,
                    second=0,
                    microsecond=0
                )

                # Si es el primer registro o entramos en un nuevo intervalo de 3 minutos
                if current_interval_start is None or bucket_start > current_interval_start:
                    # Si no es el primer intervalo, calcular y guardar el PxH del intervalo anterior
                    if current_interval_start is not None:
                        pxh = interval_accumulated_count * 20 # Multiplicar por 20 (60 min / 3 min = 20)
                        pxh_results.append({
                            'fecha': current_interval_start.strftime('%Y-%m-%d %H:%M:%S'),
                            'pxh': pxh
                        })
                    
                    # Iniciar un nuevo intervalo
                    current_interval_start = bucket_start
                    interval_accumulated_count = 0
                    interval_previous_value = None # Reiniciar previous_value para el nuevo intervalo
                    is_reset_pending = False

                # Lógica de cálculo de diferencias y manejo de reinicios dentro del intervalo actual
                if interval_previous_value is None:
                    interval_previous_value = current_value
                elif current_value > interval_previous_value:
                    if is_reset_pending:
                        is_reset_pending = False
                    else:
                        interval_accumulated_count += (current_value - interval_previous_value)
                else: # current_value <= interval_previous_value (reseteo o disminución)
                    is_reset_pending = True
                
                interval_previous_value = current_value # Actualizar para la siguiente iteración dentro del mismo intervalo

            # Procesar el último intervalo después de que el bucle termine
            if current_interval_start is not None:
                pxh = interval_accumulated_count * 20
                pxh_results.append({
                    'fecha': current_interval_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'pxh': pxh
                })

            return Response(
                {"area": area, "codmaq_buscado": codmaq, "fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str, "hora_inicio": hora_inicio_str, "produccion_por_hora": pxh_results},
                status=status.HTTP_200_OK
            )
        except ValueError as ve:
            return Response(
                {"error": f"Formato de fecha u hora inválido: {str(ve)}. Use YYYY-MM-DD para fechas y un número entre 0-23 para la hora."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )