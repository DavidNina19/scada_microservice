# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Importa tu lógica de negocio y los datos
from .formulas import Filtros 
# from .clientopc import Opcua # Descomenta si vuelves a usar OPCUA
from .read_api import Api

class MachineAttributesView(APIView):
    """
    API para obtener los atributos de una máquina específica por su código.
    Espera 'codmaq' como parámetro en la URL.
    """
    def get(self, request, codmaq, *args, **kwargs):
        if not codmaq:
            return Response(
                {"error": "El parámetro 'codmaq' es requerido en la URL."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Instancia las clases necesarias
            # Opc = Opcua() # Descomenta si vuelves a usar OPCUA
            math = Filtros()
            api = Api()

            # Obtiene los datos de la API de Alex
            api.Get() 
            
            # Si necesitas OPCUA, descomenta y adapta esta sección:
            # Opc.begin_without_db(machine_to_area_subarea) # Necesitarías importar machine_to_area_subarea aquí también
            # Opc.ReadValues() 
            # math.Agroup(Opc.read_data, api.DataMachines) # Si OPCUA es relevante, usa este Agroup

            # Actualmente, tu Agroup modificado solo toma alex_data.
            # Si no usas OPCUA, la línea siguiente es correcta.
            math.Agroup(api.DataMachines) # Agrupa solo con los datos de Alex si no hay OPCUA

            # Obtiene los datos de la máquina específica
            result_data = math.get_machine_data(codmaq)

            if result_data:
                return Response(result_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": f"Máquina '{codmaq}' no encontrada o sin datos."},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            # Captura cualquier error inesperado y devuelve un error 500
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )