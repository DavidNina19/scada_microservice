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

class HorasTrabajadasAPIView(APIView):
    """
    API para obtener la producción por hora (PxH) de datos de una tabla específica,
    y las horas trabajadas y no trabajadas.
    Filtra por 'codmaq' (que contenga '%cto%' Y el 'codmaq').
    Calcula la suma de diferencias en intervalos de 3 minutos, maneja reinicios,
    y extrapola a PxH (multiplicando por 20).
    Calcula las horas trabajadas basándose en la continuidad de los registros (menos de 1 minuto entre ellos).
    Calcula las horas no trabajadas como la diferencia entre el rango total y las horas trabajadas.
    Recibe 'area', 'codmaq', 'fecha_inicio_str', 'fecha_fin_str', y 'hora_inicio_str' como parámetros de la URL.
    Devuelve una lista de objetos {fecha: timestamp_intervalo, pxh: valor_pxh},
    más las horas_trabajadas y horas_no_trabajadas totales.
    """
    def get(self, request, area, codmaq, fecha_inicio_str, fecha_fin_str, hora_inicio_str, *args, **kwargs):
        if not area or not codmaq or not fecha_inicio_str or not fecha_fin_str or not hora_inicio_str:
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

            # Combinar la fecha de inicio con la hora de inicio proporcionada y hacerla timezone-aware
            naive_start_datetime = datetime.combine(start_date_only, time(start_hour, 0, 0))
            start_datetime = timezone.make_aware(naive_start_datetime)

            # La fecha fin siempre será hasta el final del día y hacerla timezone-aware
            naive_end_datetime = datetime.combine(end_date_only, time(23, 59, 59, 999999))
            end_datetime = timezone.make_aware(naive_end_datetime)


            # Filtros para la consulta a la base de datos
            filters = Q(t_stamp__range=(start_datetime, end_datetime))
            filters &= Q(codmaq__icontains='cto')
            filters &= Q(codmaq__icontains=codmaq)

            # Obtener todos los datos filtrados y ordenados por t_stamp
            queryset = model.objects.filter(filters).order_by('t_stamp')
            data_records = list(queryset.values('t_stamp', 'valor')) # Convertir a lista para poder iterar múltiples veces y acceder por índice

# --- Cálculo de Horas Trabajadas y No Trabajadas ---
            total_worked_seconds = 0
            
            # Obtener la primera y última marca de tiempo real de los datos
            first_data_timestamp = None
            last_data_timestamp = None

            if data_records:
                first_data_timestamp = data_records[0]['t_stamp']
                last_data_timestamp = data_records[-1]['t_stamp']
                
                previous_record_timestamp = first_data_timestamp

                for i in range(1, len(data_records)):
                    current_record_timestamp = data_records[i]['t_stamp']
                    time_diff = current_record_timestamp - previous_record_timestamp

                    # Si la diferencia de tiempo es menor o igual a 1 minuto, se considera trabajo continuo
                    # (60 segundos)
                    if time_diff <= timedelta(minutes=1):
                        total_worked_seconds += time_diff.total_seconds()
                    # Si el salto es mayor a 1 minuto, esa brecha no se suma como trabajada.
                    # El 'previous_record_timestamp' simplemente se actualiza para el siguiente cálculo.
                    
                    previous_record_timestamp = current_record_timestamp

            # Convertir segundos a horas
            horas_trabajadas = total_worked_seconds / 3600.0

            # Calcular las horas no trabajadas:
            # Ahora, el total de segundos del "span" se calcula desde el inicio solicitado
            # hasta el último registro de datos real.
            horas_no_trabajadas = 0.0
            if first_data_timestamp and last_data_timestamp:
                # El tiempo total transcurrido desde el inicio solicitado hasta el último registro
                # Si el primer registro es posterior a start_datetime, el tiempo transcurrido empieza desde start_datetime
                # Si no hay registros, entonces total_elapsed_seconds es 0, y horas_no_trabajadas será el total del rango solicitado.
                
                # Usar el máximo entre start_datetime y first_data_timestamp para el inicio real del span
                # y last_data_timestamp para el final real
                actual_span_start = max(start_datetime, first_data_timestamp)
                total_elapsed_seconds = (last_data_timestamp - actual_span_start).total_seconds()
                
                if total_elapsed_seconds > total_worked_seconds:
                    horas_no_trabajadas = (total_elapsed_seconds - total_worked_seconds) / 3600.0
                else:
                    horas_no_trabajadas = 0.0 # No puede ser negativo


            return Response(
                {
                    "area": area,
                    "codmaq_buscado": codmaq,
                    "fecha_inicio": fecha_inicio_str,
                    "fecha_fin": fecha_fin_str,
                    "hora_inicio": hora_inicio_str,
                    "horas_trabajadas": round(horas_trabajadas, 2), # Redondear a 2 decimales
                    "horas_no_trabajadas": round(horas_no_trabajadas, 2) # Redondear a 2 decimales
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