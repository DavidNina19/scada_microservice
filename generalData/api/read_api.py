# readApi.py
from datetime import datetime
import requests

class Api:
    def __init__(self) -> None:
        self.url = "http://192.168.252.6/serviciowebaccesonet/api/authentication/logintercero"
        self.data = {"User": "SCADAEME", "Password": "SCADAEME2024"}
        self.headers = {"Accept" : "application/json"}
        self.DataMachines = None
        # self.machine_filter = np.array([...]) # Eliminado: ya no se filtra aquí

    def Get(self):
        try:
            response = requests.post(self.url, headers=self.headers, json=self.data)
            response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx

            data = response.json()
            token = data["accessToken"]
            newUrl = "http://192.168.252.6/serviciowebtercerosnet/api/MaquinaOrdenParte/1"
            headers = {"Accept" : "application/json", "Authorization": f"Bearer {token}"}
                            
            newResponse = requests.get(newUrl, headers=headers)
            newResponse.raise_for_status()

            # self.DataMachines = [ # Eliminado: ya no se filtra aquí
            #     machine for machine in newResponse.json() 
            #     if machine.get("codMaquina") in self.machine_filter
            # ]
            self.DataMachines = newResponse.json() # Ahora se asignan TODAS las máquinas
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la API: {e}")
            self.DataMachines = [] # Asegura que DataMachines sea una lista vacía en caso de error
        except KeyError:
            print("Token de acceso no encontrado en la respuesta de la API.")
            self.DataMachines = []
        except Exception as e:
            print(f"Ocurrió un error inesperado en Api.Get: {e}")
            self.DataMachines = []