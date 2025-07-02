from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CircutorData
from datetime import datetime, time, date, timedelta
from django.db.models import Q # Importar Q para combinar filtros

class AcumuladoCostoAPIView(APIView):
    """
    Energia acumulado por rango de tiempo
    """
    def get(self, request, area, fecha_inicio_str, fecha_fin_str, hora_inicio_str, *args, **kwargs):
        if not area or not fecha_inicio_str or not fecha_fin_str or not hora_inicio_str:
            return Response(
                {"error": "Los parámetros 'area', 'fechaInicio', 'fechaFin' y 'horaInicio' son requeridos en la URL."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        model = CircutorData
        if not model:
            return Response(
                {"error": f"Área '{area}' no válida. Las áreas permitidas son: seriada, llaves, forja, maestranza."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            start_date_only = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            end_date_only = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

            start_hour = int(hora_inicio_str)
            if not (0 <= start_hour <= 23):
                raise ValueError("La hora de inicio debe ser un número entre 0 y 23.")

            start_datetime = datetime.combine(start_date_only, time(start_hour, 0, 0))
            end_datetime = datetime.combine(end_date_only, time(23, 59, 59, 999999))

            filters = Q(t_stamp__range=(start_datetime, end_datetime))
            filters &= Q(area__icontains='celda principal')
            filters &= Q(area__icontains='energia activa positiva')
            filters &= Q(area__icontains=area)

            queryset = model.objects.filter(filters).order_by('t_stamp')
            data_records = queryset.values_list('valor', flat=True) # Obtener ambos campos
            energia = []
            accumulated_count = 0
            previous_value = None
            is_reset_pending = False
            for record in data_records:
                try:
                    current_value = int(float(record))
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
                        {'name:':f'CELDA PRINCIPAL {area} - ENERGIA ACTIVA POSITIVA',
                         'data':accumulated_count},
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

