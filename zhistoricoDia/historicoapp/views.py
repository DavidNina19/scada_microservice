from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CircutorDataDia
from datetime import datetime, time, date, timedelta
from django.db.models import Q # Importar Q para combinar filtros

class HistoricoDiaAPIView(APIView):
    """
    Energia acumulado por rango de tiempo
    """
    def get(self, request, *args, **kwargs):
        #if not area or not fecha_inicio_str or not fecha_fin_str or not hora_inicio_str:
        #    return Response(
        #        {"error": "Los parámetros 'area', 'fechaInicio', 'fechaFin' y 'horaInicio' son requeridos en la URL."},
        #        status=status.HTTP_400_BAD_REQUEST
        #    )
        
        model = CircutorDataDia
        if not model:
            return Response(
                {"error": f"Área '{model}' no válida. Las áreas permitidas son: seriada, llaves, forja, maestranza."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            queryset = model.objects.all().values('fecha', 'valor')  
            return Response(
                        queryset,
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

