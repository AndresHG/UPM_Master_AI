
import numpy as np
import random
from pprint import pprint as pp
from uuid import uuid4, UUID

T = 43200
PISTAS = 3
VEHICULOS = 20
TASA_EXPONENCIAL = 30
PUERTAS = 50

MINUTOS_DIA = (24 * 60)
MINUTOS_HORA = 60

FILE_ATERRIZAJES = "E4.aterrizajes.txt"
FILE_DESEMBARQUES = "E4.desembarques.txt"

class Aeropuerto:

    def __init__(self):
        # Número de aviones en cada nodo (variable de estado)
        self.n1 = self.n2 = self.n3 = self.n14 = 0
        self.aviones_n1 = []
        self.aviones_n2 = []
        self.aviones_n3 = []
        self.aviones_n14 = []
        # Número de aviones esperando
        self.n_esperando_1 = self.n_esperando_14 = self.pistas_ocupadas = 0
        # Tiempo esperando aviones
        self.t_m_e_ll = self.t_m_e_ss = self.tiempo_pistas_ocupadas = 0
         # Número medio de aviones en cada nodo en el instante j-esimo
        self.n_m1 = self.n_m2 = self.n_m3 = self.n_m14 = 0
        # t: Tiempo actual en el que nos encontramos
        self.t = 0
        # Número de llegadas totales a cada nodo hasta el instante t
        self.nll1 =  self.nll2 = self.nll3 = self.nll14 = 0
         # Número de salidas totales a cada nodo hasta el instante t
        self.ns1 =  self.ns2 = self.ns3 = self.ns14 = 0
        # Instante en el que sucederán los eventos
        self.eventos = {
            "ll1": [("a",1000)],
            "sn1": [],
            "sn2": [],
            "sn3": [],
            "sn14": []
        }
        # Instante en el que llegan y salen del sistema cada avión
        self.ll1 = {}
        self.ss1 = {}
        self.ll2 = {}
        self.ss2 = {}
        self.ll3 = {}
        self.ss3 = {}
        self.ll14 = {}
        self.ss14 = {}
        # Valores de los aterrizajes aleatorios
        with open(FILE_ATERRIZAJES) as f:
            self.aterrizajes = [float(x) for x in f.readlines()]
        # Valores de los desembarques aleatorios
        with open(FILE_DESEMBARQUES) as f:
            self.desembarques = [float(x) for x in f.readlines()]



    # Funciones auxiliaresde distribuciones
    def getTAterrizaje(self):
        return float(np.random.choice(self.aterrizajes, 1))

    def getTDesembarque(self):
        return float(np.random.choice(self.desembarques, 1))

    def getTDespegue(self):
        return np.random.uniform(10,15)

    def auxAvion(self, instante_tiempo):
        instante_tiempo %= MINUTOS_DIA / MINUTOS_HORA

        if(0 <= instante_tiempo < 5):
            return (2/5)*instante_tiempo + 5
        elif(5 <= instante_tiempo < 8):
            return -(1/3)*instante_tiempo + (26/3)
        elif(8 <= instante_tiempo < 15):
            return (3/7)*instante_tiempo + (18/7)
        elif(15 <= instante_tiempo < 17):
            return -(3/2)*instante_tiempo + (63/2)
        elif(17 <= instante_tiempo < 24):
            return -(1/7)*instante_tiempo + (59/7)

    def getSigAvion(self, instante_tiempo):
        return np.random.exponential(1/self.auxAvion(instante_tiempo))*60

    def getTExponential(self):
        #TODO
        return np.random.exponential(TASA_EXPONENCIAL)


    # Funciones auxiliares
    def getNextEvent(self):
        minimun = ("", np.inf)
        ret = "FIN"
        for ele in self.eventos:
            try:
                d = self.eventos[ele]
                if min(d, key=lambda x: x[1])[1] < minimun[1]:
                    minimun = min(d, key=lambda x: x[1])
                    ret = ele
            except Exception as e:
                pass
        return ret

    def noStop(self):
        return len(self.eventos.get("ll1")) != 0 or len(self.eventos.get("sn1")) != 0 or len(self.eventos.get("sn2")) != 0 or len(self.eventos.get("sn3")) != 0 or len(self.eventos.get("sn14")) != 0


    # Getter functions
    def getNextEventInfo(self, event):
        return min(self.eventos[event], key=lambda x: x[1])

    # Setter functions
    def setEventTime(self, event, ttime, uid):
        try:
            if min(self.eventos[event], key=lambda x: x[1])[1] == 1000: self.eventos[event].remove(min(self.eventos[event], key=lambda x: x[1]))
        except Exception as e:
            pass
        self.eventos[event].append((uid, ttime))

    def deleteNextEvent(self, event):
        self.eventos[event].remove(min(self.eventos[event], key=lambda x: x[1]))




    # Eventos
    def llegadaAvion(self, event):
        tsuc = event[1]
        uid = event[0]
        print("Llega avión: {}".format(tsuc))

        #Variables para las medias
        self.t_m_e_ll += self.n_esperando_1 * (tsuc - self.t)
        self.t_m_e_ss += self.n_esperando_14 * (tsuc - self.t)
        if self.pistas_ocupadas == PISTAS:
            self.tiempo_pistas_ocupadas += tsuc - self.t
        self.n_m1 += self.n1 * (tsuc - self.t)
        self.n_m2 += self.n2 * (tsuc - self.t)
        self.n_m3 += self.n3 * (tsuc - self.t)
        self.n_m14 += self.n14 * (tsuc - self.t)

        # Actualizar contadores y tiempos del nodo 1
        self.n_esperando_1 += 1
        self.n1 += 1
        self.aviones_n1.append(uid)
        self.nll1 +=1
        self.ll1[uid] = tsuc
        self.deleteNextEvent('ll1')
        self.t = tsuc

        # Calculamos cuando llegará el siguiente avión
        t_avion = self.getSigAvion(self.t)
        pp("-- Siguiente avión: {}".format(self.t + t_avion))
        if self.t + t_avion < T:
            avion_id = str(uuid4())
            self.setEventTime('ll1', self.t + t_avion, avion_id)

        # Si no estan todas las pistas ocupadas, le asignamos pista al avión para que aterrice
        # Para comprobar si estan todas las pistas ocupadas, hay que comprobar las longitudes
        # de ambas listas de tiempos
        if (self.pistas_ocupadas <= PISTAS) and (self.n_esperando_1 > 0 or self.n_esperando_14 > 0):
            self.n_esperando_1 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn1', self.t + t_aterrizaje, uid)


    def servicio_nodo1(self, event):
        tsuc = event[1]
        uid = event[0]
        print("Servicio nodo 1 (aterrizaje) terminado: {}".format(tsuc))

        #Variables para las medias
        self.t_m_e_ll += self.n_esperando_1 * (tsuc - self.t)
        self.t_m_e_ss += self.n_esperando_14 * (tsuc - self.t)
        if self.pistas_ocupadas == PISTAS:
            self.tiempo_pistas_ocupadas += tsuc - self.t
        self.n_m1 += self.n1 * (tsuc - self.t)
        self.n_m2 += self.n2 * (tsuc - self.t)
        self.n_m3 += self.n3 * (tsuc - self.t)
        self.n_m14 += self.n14 * (tsuc - self.t)

        # Actualizar contadores y tiempos de los eventos
        self.t = tsuc
        self.n1 -= 1
        self.aviones_n1.remove(uid)
        self.ns1 += 1
        self.ss1[uid] = tsuc
        self.deleteNextEvent('sn1')
        self.pistas_ocupadas -= 1

        # Actualizar contadores y tiempos del siguiente nodo
        self.nll2 += 1
        self.ll2[uid] = tsuc
        self.aviones_n2.append(uid)
        self.n2 += 1

        # Comprobamos si en las colas 1 o 14 queda alguien esperando para ser asignado pista
        # ya que acabamos de liberar una pista
        if self.n_esperando_1 > 0:
            av_uid = self.aviones_n1[-self.n_esperando_1]
            self.n_esperando_1 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn1', self.t + t_aterrizaje, av_uid)

        elif self.n_esperando_14 > 0:
            av_uid = self.aviones_n14[-self.n_esperando_14]
            self.n_esperando_14 -= 1
            self.pistas_ocupadas += 1
            t_despegue = self.getTDespegue()
            self.setEventTime('sn14', self.t + t_despegue, av_uid)

        # Si no estan todos los vehiculos ocupados, le asignamos uno al avión que acaba de aterrizar
        if self.n2 <= VEHICULOS:
            t_vehiculo = self.getTExponential()
            self.setEventTime('sn2', self.t + t_vehiculo, uid)

    def servicio_nodo2(self, event):
        tsuc = event[1]
        uid = event[0]
        print("Servicio nodo 2 (vehiculo) terminado: {}".format(tsuc))

        # Variables para las medias
        self.t_m_e_ll += self.n_esperando_1 * (tsuc - self.t)
        self.t_m_e_ss += self.n_esperando_14 * (tsuc - self.t)
        if self.pistas_ocupadas == PISTAS:
            self.tiempo_pistas_ocupadas += tsuc - self.t
        self.n_m1 += self.n1 * (tsuc - self.t)
        self.n_m2 += self.n2 * (tsuc - self.t)
        self.n_m3 += self.n3 * (tsuc - self.t)
        self.n_m14 += self.n14 * (tsuc - self.t)

        # Actualizar contadores y tiempos del nodo actual
        self.t = tsuc
        self.n2 -= 1
        self.ns2 += 1
        self.aviones_n2.remove(uid)
        self.ss2[uid] = tsuc
        self.deleteNextEvent('sn2')

        # Actualizar contadores y tiempos del siguiente nodo
        self.ll3[uid] = tsuc
        self.aviones_n3.append(uid)
        self.nll3 += 1
        self.n3 += 1

        # Si hay menos de 20 aviones esperando, todos ellos tendrán ya un coche asignado
        # pero si hay más, hay que asignarle uno nuevo (ya que uno se acaba de quedar libre)
        if self.n2 >= VEHICULOS:
            t_vehiculo = self.getTExponential()
            av_uid = self.aviones_n2[VEHICULOS]
            self.setEventTime('sn2', self.t + t_vehiculo, av_uid)

        # Para desembarcar hay 50 puertas
        if self.n3 <= PUERTAS:
            t_desembarque = self.getTDesembarque()
            self.setEventTime('sn3', self.t + t_desembarque, uid)

    def servicio_nodo3(self, event):
        tsuc = event[1]
        uid = event[0]
        print("Servicio nodo 3 (desembarque) terminado: {}".format(tsuc))

        # Variables para las medias
        self.t_m_e_ll += self.n_esperando_1 * (tsuc - self.t)
        self.t_m_e_ss += self.n_esperando_14 * (tsuc - self.t)
        if self.pistas_ocupadas == PISTAS:
            self.tiempo_pistas_ocupadas += tsuc - self.t
        self.n_m1 += self.n1 * (tsuc - self.t)
        self.n_m2 += self.n2 * (tsuc - self.t)
        self.n_m3 += self.n3 * (tsuc - self.t)
        self.n_m14 += self.n14 * (tsuc - self.t)

        # Actualizar contadores y tiempos de los eventos
        self.t = tsuc
        self.n3 -= 1
        self.ns3 += 1
        self.aviones_n3.remove(uid)
        self.ss3[uid] = tsuc
        self.deleteNextEvent('sn3')

        # Actualizar contadores y tiempos del siguiente nodo
        self.ll14[uid] = tsuc
        self.aviones_n14.append(uid)
        self.nll14 += 1
        self.n14 += 1
        self.n_esperando_14 += 1

        # Comprobamos si queda gente en la cola del nodo 3
        if self.n3 >= PUERTAS:
            t_desembarque = self.getTDesembarque()
            av_uid = self.aviones_n3[PUERTAS]
            self.setEventTime('sn3', self.t + t_desembarque, av_uid)

        # Ponemos comprobamos si hay pistas libres
        if (self.pistas_ocupadas <= PISTAS) and (self.n_esperando_1 > 0 or self.n_esperando_14 > 0):
            self.n_esperando_14 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn14', self.t + t_aterrizaje, uid)

    def salidaAvion(self, event):
        tsuc = event[1]
        uid = event[0]
        print("Despega avión: {}".format(tsuc))

        # Variables para las medias
        self.t_m_e_ll += self.n_esperando_1 * (tsuc - self.t)
        self.t_m_e_ss += self.n_esperando_14 * (tsuc - self.t)
        if self.pistas_ocupadas == PISTAS:
            self.tiempo_pistas_ocupadas += tsuc - self.t
        self.n_m1 += self.n1 * (tsuc - self.t)
        self.n_m2 += self.n2 * (tsuc - self.t)
        self.n_m3 += self.n3 * (tsuc - self.t)
        self.n_m14 += self.n14 * (tsuc - self.t)

        # Actualizar contadores y tiempos de los eventos
        self.t = tsuc
        self.n14 -= 1
        self.ns14 += 1
        self.aviones_n14.remove(uid)
        self.ss14[uid] = tsuc
        self.deleteNextEvent('sn14')
        self.pistas_ocupadas -= 1

        # Comprobamos si en las colas 1 o 14 queda alguien esperando para ser asignado pista
        if self.n_esperando_1 > 0:
            av_uid = self.aviones_n1[-self.n_esperando_1]
            self.n_esperando_1 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn1', self.t + t_aterrizaje, av_uid)

        elif self.n_esperando_14 > 0:
            av_uid = self.aviones_n14[-self.n_esperando_14]
            self.n_esperando_14 -= 1
            self.pistas_ocupadas += 1
            t_despegue = self.getTDespegue()
            self.setEventTime('sn14', self.t + t_despegue, av_uid)


a = Aeropuerto()

UUID(int=random.getrandbits(128))
tsuc = a.getSigAvion(0)
if tsuc > T:
    print("return -1")
else:
    event = (str(uuid4()), tsuc)
    a.llegadaAvion(event)
    while(a.noStop()):

        # pp(a.eventos)
        nextEvent = a.getNextEvent()
        if nextEvent == "ll1":
            event = a.getNextEventInfo("ll1")
            a.llegadaAvion(event)

        elif nextEvent == "sn1":
            event = a.getNextEventInfo("sn1")
            a.servicio_nodo1(event)

        elif nextEvent == "sn2":
            event = a.getNextEventInfo("sn2")
            a.servicio_nodo2(event)

        elif nextEvent == "sn3":
            event = a.getNextEventInfo("sn3")
            a.servicio_nodo3(event)
        else:
            event = a.getNextEventInfo("sn14")
            a.salidaAvion(event)

        # Good by
# Tiempo desde T hasta que el último cliente abandona el sistema
Tp = max(0.0, a.t-T)

# Tiempo medio que pasan los clientes en el sistema
max_llegada = 0
acumulado1 = acumulado2 = acumulado3 = acumulado14 = 0
for indi in a.ll1:
    tmp = a.ss1[indi] - a.ll1[indi]
    if tmp > max_llegada: max_llegada = tmp
    acumulado1 += tmp

acumulado2 = sum(a.ss2[indi] - a.ll2[indi] for indi in a.ll2)
acumulado3 = sum(a.ss3[indi] - a.ll3[indi] for indi in a.ll3)

max_salida = 0
for indi in a.ll14:
    tmp = a.ss14[indi] - a.ll14[indi]
    if tmp > max_salida: max_salida = tmp
    acumulado14 += tmp

# Tiempo medio del sistema
t_med_sistema = (acumulado1/a.nll1) + (acumulado2/a.nll2) + (acumulado3/a.nll3) + (acumulado14/a.nll14)
media_aviones_sistema = (a.n_m1 + a.n_m14 + a.n_m2 + a.n_m3)/T

pp("Tiempo desde {} hasta que el último avión abandona el sistema: {}".format(T, Tp))

pp("Tiempo máximo entre espera y servicio para aterrizar: {}".format(max_llegada))
pp("Tiempo máximo entre espera y servicio para aterrizardespegar: {}".format(max_salida))
pp("Tiempo medio de espera llegadas: {}".format(acumulado1/a.nll1))
pp("Tiempo medio de espera salidas: {}".format(acumulado14/a.nll14))
pp("Tiempo medio de las pistas ocupadas (solo cuando las {} pistas estan siendo utilizadas): {}%".format(PISTAS, round((a.tiempo_pistas_ocupadas/T)*100, 2)))
pp("Número medio de aviones en el sistema (todos los aviones que ha habido en el sistema dividido por el tiempo total): {}".format(media_aviones_sistema))


pp("Tiempo medio acumulado en 1: {}".format(acumulado1/a.nll1))
pp("Tiempo medio acumulado en 2: {}".format(acumulado2/a.nll2))
pp("Tiempo medio acumulado en 3: {}".format(acumulado3/a.nll3))
pp("Tiempo medio acumulado en 14: {}".format(acumulado14/a.nll14))

pp("Tiempo medio del sistema: {}".format(t_med_sistema))
