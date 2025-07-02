from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from opcua import Client
import os

class selectorAPI(APIView):
    def get(self, request, *args, **kwargs):
        # Your original GET logic, possibly for listing variables from 'nodo.txt' or similar.
        # This part of the API won't receive OPC UA values.
        variables_leidas = []
        file_path = os.path.join(os.path.dirname(__file__), 'nodos.txt')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as archivo_txt:
                    for linea in archivo_txt:
                        linea = linea.strip()
                        if linea:
                            partes = linea.split(',', 1)
                            if len(partes) == 2:
                                concepto = partes[0].strip()
                                node_id = partes[1].strip()
                                variables_leidas.append((concepto, node_id))
            except FileNotFoundError:
                return Response(
                    {"error": "Archivo 'nodos.txt' no encontrado en el servidor."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                    {"error": f"ARCHIVO {file_path} NO EXISTE"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        if variables_leidas:
            return Response(variables_leidas, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": f"No se encontraron variables en 'nodo.txt'."},
                status=status.HTTP_404_NOT_FOUND
            )