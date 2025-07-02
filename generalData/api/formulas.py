# filters.py
from datetime import datetime
from .names import names, machine_to_area_subarea # Importa desde el nuevo archivo names.py

class Filtros:
    def __init__(self,) -> None:
        self.maqtotales = {"maq_totales":0}
        self.groupedData = {}
        self.status = {}
        self.errores = []
        self.set = {}
        self.subarea={}
        self.all_machines_data = {} 

    def SetVal(self,datos):
        self.set.clear()
        for area,subarea_dict in datos.items():
            sub= {}
            for subarea_name,maquinas_dict in subarea_dict.items():
                maq ={} 
                for maquina, datos in maquinas_dict.items():
                    valorcounter = datos.get("CTO",0)
                    valorjornada = datos.get("CTO",0) 
                    try:
                        maq[maquina] = {"setconteo": valorcounter[0],
                                         "setJornada" : valorjornada[0],
                                         "vconteo" : 0,
                                         "vjornada":0
                                         }
                            
                    except:
                        maq[maquina] = {"setconteo": valorcounter,
                                         "setJornada" : valorjornada,
                                         "vconteo" : 0,
                                         "vjornada":0
                                         }
                sub[subarea_name] = maq 
            self.set[area]=sub
    
    def WriteJornada():
        pass

    def SetJornada(self,datos):
        pass
            
    def Agroup(self, alex_data): # Eliminamos opcua_data ya que no se usa en este Agroup
        self.errores.clear()
        self.groupedData.clear()
        self.all_machines_data.clear()
        maquinas_alex_dict = {data["codMaquina"]: data for data in alex_data}

        new_grouped_data = {}
        for maquina_cod, alex_info in maquinas_alex_dict.items():
            if maquina_cod in machine_to_area_subarea:
                area_info = machine_to_area_subarea[maquina_cod]
                area_name = area_info["area"]
                subarea_name = area_info["subarea"]

                if area_name not in new_grouped_data:
                    new_grouped_data[area_name] = {}
                if subarea_name not in new_grouped_data[area_name]:
                    new_grouped_data[area_name][subarea_name] = {}

                # Aquí, ya que no estamos usando datos OPCUA en este Agroup, 
                # los valores de OPCUA se inicializan a 0 o valores predeterminados.
                opcua_machine_data = {} 

                counter = opcua_machine_data.get("CTO", 0)
                try:
                    count = counter[0] if isinstance(counter, list) else counter
                except TypeError:
                    count = counter

                if count is None:
                    count = 0

                try:
                    machine_details = {
                        "nomMaquina": names.get(maquina_cod, alex_info.get("nomMaquina")),
                        "idTipOrd": alex_info.get("idTipOrd"),
                        "abrTipOrd2": alex_info.get("abrTipOrd2"),
                        "idNumOrd": alex_info.get("idNumOrd"),
                        "cantidadOrden": alex_info.get("cantidadOrden"),
                        "desOperacion": alex_info.get("desOperacion"),
                        "itemProceso": alex_info.get("itemProceso"),
                        "inicio": alex_info.get("inicio"),
                        "termino": alex_info.get("termino"),
                        "cantidadStd": alex_info.get("cantidadStd"),
                        "operario": alex_info.get("operario"),
                        "inicioParada": alex_info.get("inicioParada"),
                        "cantidadReal": int(alex_info.get("cantidadReal", 0)),
                        "PXH": opcua_machine_data.get("PXH", 0), # Será 0 si no hay OPCUA
                        "CTO": counter, # Será 0 si no hay OPCUA
                        "ON": opcua_machine_data.get("ON", [0, ""])[0] # Será 0 si no hay OPCUA
                    }
                    new_grouped_data[area_name][subarea_name][maquina_cod] = machine_details
                    self.all_machines_data[maquina_cod] = machine_details 
                except Exception as e:
                    self.errores.append(f"{maquina_cod}: {e}")
            else:
                self.errores.append(f"Máquina {maquina_cod} no encontrada en machine_to_area_subarea.")
        self.groupedData = new_grouped_data

    def get_machine_data(self, machine_code: str):
        """
        Devuelve directamente los atributos de una máquina específica.
        """
        return self.all_machines_data.get(machine_code.upper(), {})

    # Métodos GetMaqTotal, GetMaqStatus, AgroupSubarea se mantienen si los necesitas,
    # pero no son directamente relevantes para la API de un solo GET de máquina.
    # Los he omitido aquí para la brevedad y enfoque en la consulta principal,
    # pero puedes copiarlos si los mantienes en tu lógica.
    def GetMaqTotal(self,datos:dict):
        self.maqtotales["maq_totales"]=0
        for area,subarea in datos.items():
            for subarea,maquinas in subarea.items():
                self.maqtotales["maq_totales"] += len(maquinas.items())

    def GetMaqStatus(self,datos:dict):
        self.status.clear()
        g_mantenimiento = 0
        g_totales = 0
        g_trabajando = 0
        g_eficiencia = 0
        g_porcentaje = 0
        for area,subarea_dict in datos.items():
            base = {}
            for subarea_name,maquinas_dict in subarea_dict.items():
                base[subarea_name] = {"maq_mantenimiento":0,
                                 "maq_totales":0,
                                 "maq_trabajando":0,
                                 "p_eficiencia":0,
                                 "porcentaje":0}
                base[subarea_name]["maq_totales"]+=len(maquinas_dict.items())
                g_totales += len(maquinas_dict.items())
                for maquina,datos_maq in maquinas_dict.items():
                    try:
                        if area in self.groupedData and subarea_name in self.groupedData[area] and maquina in self.groupedData[area][subarea_name]:
                            if self.groupedData[area][subarea_name][maquina]["desOperacion"] == "TRABAJOS DE MANTENIMIENTO MAQUINA":
                                base[subarea_name]["maq_mantenimiento"] +=1
                                g_mantenimiento +=1
                            else:
                                on_status = datos_maq["ON"][0] if isinstance(datos_maq["ON"], list) else datos_maq["ON"]
                                base[subarea_name]["maq_trabajando"] += on_status
                                g_trabajando += on_status
                        
                    except Exception as e:
                        pass
                    
                if base[subarea_name]["maq_totales"] > 0:
                    base[subarea_name]["porcentaje"] = round((base[subarea_name]["maq_trabajando"]/base[subarea_name]["maq_totales"])*100,1)
                else:
                    base[subarea_name]["porcentaje"] = 0

            nombre =area.split(" ")[1] if " " in area else area
            base[f"INFO.{nombre}"] = {"maq_mantenimiento":g_mantenimiento,
                                        "maq_totales":g_totales,
                                        "maq_trabajando":g_trabajando,
                                        "p_eficiencia":g_eficiencia,
                                        "porcentaje":round(g_porcentaje,1)}
            g_totales=0
            g_mantenimiento = 0
            g_trabajando = 0
            g_eficiencia = 0
            g_porcentaje = 0
            self.status[area]=base

    def AgroupSubarea(self, maquinas_alex, maquinas_opcua): # Renombré el segundo parámetro para mayor claridad
        maq = {}
        for maquina, datos in maquinas_opcua.items(): # Asumo que 'maquinas' aquí son los datos de OPCUA
            if maquina not in self.subarea:
                valorcounter = datos.get("CTO", 0)
                valorjornada = datos.get("CTO", 0)
                try:
                    self.subarea[maquina] = {
                        "setconteo": valorcounter[0],
                        "setJornada": valorjornada[0],
                        "vconteo": 0,
                        "vjornada": 0
                    }
                except (TypeError, IndexError): # Capturar TypeError si no es lista, IndexError si es lista vacía
                    self.subarea[maquina] = {
                        "setconteo": valorcounter,
                        "setJornada": valorjornada,
                        "vconteo": 0,
                        "vjornada": 0
                    }
            else:
                counter = datos.get("CTO", 0)
                try:
                    count = counter[0] if isinstance(counter, list) else counter
                    if count >= self.subarea[maquina]["setconteo"]:
                        self.subarea[maquina]["vconteo"] += count - self.subarea[maquina]["setconteo"]
                        self.subarea[maquina]["setconteo"] = count
                    else:
                        # Esto es una lógica compleja para decrementos. 
                        # Si el contador se reinicia (va de 100 a 5, por ejemplo)
                        # esto sumará la diferencia con el setconteo previo.
                        # Asegúrate de que esta lógica es la que necesitas para reinicios de contadores.
                        self.subarea[maquina]["vconteo"] += self.subarea[maquina]["setconteo"] 
                        self.subarea[maquina]["vconteo"] += count # Suma el nuevo contador
                        self.subarea[maquina]["setconteo"] = count

                except (TypeError, IndexError):
                    count = counter
                    if count >= self.subarea[maquina]["setconteo"]:
                        self.subarea[maquina]["vconteo"] += count - self.subarea[maquina]["setconteo"]
                        self.subarea[maquina]["setconteo"] = count
                    else:
                        self.subarea[maquina]["vconteo"] += self.subarea[maquina]["setconteo"]
                        self.subarea[maquina]["vconteo"] += count
                        self.subarea[maquina]["setconteo"] = count
        
            cantidadRealOpe = int(maquinas_alex.get(maquina, {}).get("cantidadReal", 0)) + int(self.subarea[maquina]["vconteo"])
            
            alex_data_for_machine = maquinas_alex.get(maquina, {})

            try:
                maq[maquina] = {
                    "nomMaquina": names.get(maquina, alex_data_for_machine.get("nomMaquina")),
                    "idTipOrd": alex_data_for_machine.get("idTipOrd"),
                    "abrTipOrd2": alex_data_for_machine.get("abrTipOrd2"),
                    "idNumOrd": alex_data_for_machine.get("idNumOrd"),
                    "cantidadOrden": alex_data_for_machine.get("cantidadOrden"),
                    "desOperacion": alex_data_for_machine.get("desOperacion"),
                    "itemProceso": alex_data_for_machine.get("itemProceso"),
                    "inicio": alex_data_for_machine.get("inicio"),
                    "termino": alex_data_for_machine.get("termino"),
                    "cantidadStd": alex_data_for_machine.get("cantidadStd"),
                    "operario": alex_data_for_machine.get("operario"),
                    "inicioParada": alex_data_for_machine.get("inicioParada"),
                    "cantidadReal": cantidadRealOpe,
                    "PXH": datos.get("PXH", 0),
                    "CTO": datos.get("CTO", 0),
                    "ON": datos.get("ON", [0, ""])[0],
                    "last": self.subarea[maquina]["vconteo"],
                    "jornada": self.subarea[maquina]["vconteo"]
                }        
            except Exception as e:
                self.errores.append(f"{maquina}: {e}")
        return maq