# data_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from datetime import datetime, time, date
from django.db.models import Q # Importar Q para combinar filtros
from .models import (
    Seriada062025, Llaves062025, Forja062025, Maestranza062025,
    Seriada072025, Llaves072025, Forja072025, Maestranza072025
)

class DataQueryAPIView(APIView):
    """
    API para obtener el conteo acumulado de datos de una tabla específica.
    Filtra por 'codmaq' (que contenga '%cto%' Y el 'codmaq').
    Maneja reinicios del contador y filtra por un rango de fechas y hora de inicio.
    Recibe 'area', 'codmaq', 'fecha_inicio_str', 'fecha_fin_str', y 'hora_inicio_str' como parámetros de la URL.
    Devuelve el conteo acumulado.
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
            # Asumimos que el formato de fecha es 'YYYY-MM-DD'
            start_date_only = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            end_date_only = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

            # Parsear la hora de inicio
            start_hour = int(hora_inicio_str)
            if not (0 <= start_hour <= 23):
                raise ValueError("La hora de inicio debe ser un número entre 0 y 23.")

            # Combinar la fecha de inicio con la hora de inicio proporcionada
            start_datetime = datetime.combine(start_date_only, time(start_hour, 0, 0))
            # La fecha fin siempre será hasta el final del día
            end_datetime = datetime.combine(end_date_only, time(23, 59, 59, 999999))


            # Filtro base: t_stamp dentro del rango de fechas y horas
            filters = Q(t_stamp__range=(start_datetime, end_datetime))

            # Condición para codmaq: debe contener 'cto'
            filters &= Q(codmaq__icontains='cto')

            # Condición adicional para codmaq: debe contener el valor de codmaq
            filters &= Q(codmaq__icontains=codmaq)


            # Aplicar los filtros combinados y ordenar por t_stamp
            queryset = model.objects.filter(filters).order_by('t_stamp')


            data_values = queryset.values_list('valor', flat=True)

            accumulated_count = 0
            previous_value = None
            is_reset_pending = False

            for val_str in data_values:
                try:
                    current_value = int(float(val_str))
                except ValueError:
                    continue

                if previous_value is None:
                    previous_value = current_value
                    continue

                if current_value > previous_value:
                    if is_reset_pending:
                        is_reset_pending = False
                    else:
                        accumulated_count += (current_value - previous_value)
                else:
                    is_reset_pending = True

                previous_value = current_value

            return Response(
                {"area": area, "codmaq_buscado": codmaq, "fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str, "hora_inicio": hora_inicio_str, "acumulado": accumulated_count},
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
