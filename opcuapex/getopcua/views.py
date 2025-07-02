from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from opcua import Client

class OPCUAHandler(APIView):
    """
    API para obtener los datos en tiempo real de la PEX 003E.
    """
    def __init__(self):
        self.server_url = "opc.tcp://192.168.146.50:4840"
        self.client = None
        self.previous_values = {
            "valuep": None,
            "valueaux": None,
            "valuetocho": None,
            "valuemotor": None,
            "valuetanque": None
        }

    def connect(self):
        self.client = Client(self.server_url)
        self.client.connect()

    def disconnect(self):
        if self.client:
            self.client.disconnect()

    def obtenerTemp(self):
        datos = {}
        try:
            # Obtener valores de los nodos
            valor = self.client.get_node("ns=2;i=7")
            datos["valuep"] = valor.get_value()

            valor = self.client.get_node("ns=2;i=8")
            datos["valueaux"] = valor.get_value()

            valor = self.client.get_node("ns=2;i=3")
            datos["valuetocho"] = valor.get_value()

            valor = self.client.get_node("ns=2;i=6")
            datos["valuemotor"] = valor.get_value()

            valor = self.client.get_node("ns=2;i=9")
            datos["valuetanque"] = valor.get_value()
            
            valor = self.client.get_node("ns=2;i=5")
            datos["presionauxiliar"] = valor.get_value()
            
            valor = self.client.get_node("ns=2;i=4")
            datos["presionprincipal"] = valor.get_value()

        except Exception as e:
            print(f"Error: {e}")
            datos = {"error": "Error al obtener los datos"}

        return datos

    def get(self, request, *args, **kwargs):
        self.connect()
        datos = self.obtenerTemp()
        self.disconnect()
        if datos:
            return Response(datos, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": f"Máquina 'no params' no encontrada o sin datos."},
                status=status.HTTP_404_NOT_FOUND
            )
