from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CircutorData # Asumiendo que CircutorData es tu modelo
from datetime import datetime, time, date, timedelta
from django.db.models import Q
from django.db.models import Min, Max # Importa Min y Max para obtener el primer y último registro

class ConsumoMensualAPIView(APIView):
    """
    Retorna el consumo mensual (ultimo_valor - primer_valor) para un área específica.
    """
    def get(self, request, area, anio, mes, *args, **kwargs):
        if not area or not anio or not mes:
            return Response(
                {"error": "Los parámetros 'area', 'anio' y 'mes' son requeridos en la URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            anio = int(anio)
            mes = int(mes)

            if not (1 <= mes <= 12):
                raise ValueError("El mes debe ser un número entre 1 y 12.")

            # Determinar el primer día del mes
            start_date_month = date(anio, mes, 1)
            # Determinar el último día del mes
            # Si es el mes actual, el end_date_month debe ser la fecha actual
            # Si es un mes pasado, será el último día de ese mes
            if anio == datetime.now().year and mes == datetime.now().month:
                end_date_month = datetime.now().date()
            else:
                # Para meses pasados, el último día del mes
                if mes == 12:
                    end_date_month = date(anio, mes, 31)
                else:
                    end_date_month = date(anio, mes + 1, 1) - timedelta(days=1)
            
            # Combinar con horas para el rango de búsqueda
            start_datetime = datetime.combine(start_date_month, time(0, 0, 0))
            end_datetime = datetime.combine(end_date_month, time(23, 59, 59, 999999))

            # Filtros base para el área y tipo de dato
            filters = Q(t_stamp__range=(start_datetime, end_datetime))
            filters &= Q(area__icontains='celda principal')
            filters &= Q(area__icontains='energia activa positiva')
            filters &= Q(area__icontains=area)

            # Obtener el primer y el último valor directamente de la base de datos
            # Asegúrate de que tu modelo 'CircutorData' tenga un campo 'valor' y 't_stamp'
            first_record = CircutorData.objects.filter(filters).order_by('t_stamp').first()
            last_record = CircutorData.objects.filter(filters).order_by('-t_stamp').first()

            if not first_record or not last_record:
                return Response(
                    {"message": "No se encontraron datos para el área y período especificados."},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                primer_valor = int(float(first_record.valor))
                ultimo_valor = int(float(last_record.valor))
            except ValueError:
                return Response(
                    {"error": "Los valores de energía en la base de datos no son numéricos."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            consumo_mensual = ultimo_valor - primer_valor

            return Response(
                {
                    'name': f'CELDA PRINCIPAL {area} - ENERGIA ACTIVA POSITIVA - Consumo Mensual',
                    'data': consumo_mensual,
                    'fecha_inicio_data': first_record.t_stamp.isoformat(),
                    'fecha_fin_data': last_record.t_stamp.isoformat()
                },
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            return Response(
                {"error": f"Formato de año o mes inválido: {str(ve)}. Use números enteros para año y mes."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )