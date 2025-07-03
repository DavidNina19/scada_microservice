# data_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time
from django.db.models import Q # Importar Q para combinar filtros
from django.utils import timezone # Importar timezone para manejar zonas horarias
from .models import (
    Seriada062025, Llaves062025, Forja062025, Maestranza062025,
    Seriada072025, Llaves072025, Forja072025, Maestranza072025
)

class OnOffDataAPIView(APIView):
    """
    API para obtener los datos de encendido y apagado (fecha y valor) de una tabla específica.
    Filtra por 'codmaq' (que contenga '%cto%' Y el 'codmaq').
    Filtra por un rango de fechas y hora de inicio.
    Recibe 'area', 'codmaq', 'fecha_inicio_str', 'fecha_fin_str', y 'hora_inicio_str' como parámetros de la URL.
    Devuelve una lista de objetos {fecha: timestamp, valor: valor_registro}.
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
            filters &= Q(codmaq__icontains=codmaq)

            # Obtener todos los datos filtrados y ordenados por t_stamp
            queryset = model.objects.filter(filters).order_by('t_stamp')
            
            # Formatear los resultados para la respuesta
            on_off_data = []
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
                    # For example: else: newValue = value_from_db
                elif isinstance(value_from_db, int):
                    newValue = '1' if value_from_db == 1 else '0'
                
                on_off_data.append({
                    'fecha': record['t_stamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'valor': newValue
                })

            return Response(
                {
                    "area": area,
                    "codmaq_buscado": codmaq,
                    "fecha_inicio": fecha_inicio_str,
                    "fecha_fin": fecha_fin_str,
                    "hora_inicio": hora_inicio_str,
                    "encendido_apagado": on_off_data
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