
import numpy as np
from pprint import pprint as pp
from uuid import uuid4

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
            "ll1": [1000],
            "sn1": [1000],
            "sn2": [1000],
            "sn3": [1000],
            "sn14": [1000]
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

    # def getSigAvion(self, instante_tiempo):
    #     instante_tiempo %= MINUTOS_DIA / MINUTOS_HORA

    #     if(0 <= instante_tiempo < 5):
    #         return (2/5)*instante_tiempo + 5
    #     elif(5 <= instante_tiempo < 8):
    #         return -(1/3)*instante_tiempo + (26/3)
    #     elif(8 <= instante_tiempo < 15):
    #         return (3/7)*instante_tiempo + (18/7)
    #     elif(15 <= instante_tiempo < 17):
    #         return -(3/2)*instante_tiempo + (63/2)
    #     elif(17 <= instante_tiempo < 24):
    #         return -(1/7)*instante_tiempo + (59/7)

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
        minimun = np.inf
        ret = "FIN"
        for ele in self.eventos:
            try:
                if min(self.eventos[ele]) < minimun:
                    minimun = min(self.eventos[ele])
                    ret = ele
            except Exception as e:
                pass
        return ret

    def noStop(self):
        return len(self.eventos.get("ll1")) != 0 or len(self.eventos.get("sn1")) != 0 or len(self.eventos.get("sn2")) != 0 or len(self.eventos.get("sn3")) != 0 or len(self.eventos.get("sn14")) != 0


    # Getter functions
    def getNextEventTime(self, event):
        return min(self.eventos.get(event))

    # Setter functions
    def setEventTime(self, event, ttime):
        try:
            if min(self.eventos[event]) == 1000: self.eventos[event].remove(min(self.eventos[event]))
        except Exception as e:
            pass
        self.eventos[event].append(ttime)

    def deleteNextEvent(self, event):
        self.eventos[event].remove(min(self.eventos[event]))




    # Eventos
    def llegadaAvion(self, tsuc):
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
        self.nll1 +=1
        self.ll1[self.nll1] = tsuc
        self.t = tsuc

        # Calculamos cuando llegará el siguiente avión
        t_avion = self.getSigAvion(self.t)
        pp("-- Siguiente avión: {}".format(self.t + t_avion))
        if self.t + t_avion < T:
            self.deleteNextEvent('ll1')
            self.setEventTime('ll1', self.t + t_avion)
        else:
            self.deleteNextEvent('ll1')

        # Si no estan todas las pistas ocupadas, le asignamos pista al avión para que aterrice
        # Para comprobar si estan todas las pistas ocupadas, hay que comprobar las longitudes
        # de ambas listas de tiempos
        if (self.pistas_ocupadas <= PISTAS) and (self.n_esperando_1 > 0 or self.n_esperando_14 > 0):
            self.n_esperando_1 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn1', self.t + t_aterrizaje)


    def servicio_nodo1(self, tsuc):
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
        self.ns1 += 1
        self.ss1[self.ns1] = tsuc
        self.deleteNextEvent('sn1')
        self.pistas_ocupadas -= 1

        # Actualizar contadores y tiempos del siguiente nodo
        self.nll2 += 1
        self.ll2[self.nll2] = tsuc
        self.n2 += 1

        # Comprobamos si en las colas 1 o 14 queda alguien esperando para ser asignado pista
        if self.n_esperando_1 > 0:
            self.n_esperando_1 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn1', self.t + t_aterrizaje)

        elif self.n_esperando_14 > 0:
            self.n_esperando_14 -= 1
            self.pistas_ocupadas += 1
            t_despegue = self.getTDespegue()
            self.setEventTime('sn14', self.t + t_despegue)

        # Si no estan todos los vehiculos ocupados, le asignamos uno al avión que acaba de aterrizar
        if self.n2 <= VEHICULOS:
            t_vehiculo = self.getTExponential()
            self.setEventTime('sn2', self.t + t_vehiculo)

    def servicio_nodo2(self, tsuc):
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
        self.ss2[self.ns2] = tsuc
        self.deleteNextEvent('sn2')

        # Actualizar contadores y tiempos del siguiente nodo
        self.ll3[self.nll3] = tsuc
        self.nll3 += 1
        self.n3 += 1

        # Si hay menos de 20 aviones esperando, todos ellos tendrán ya un coche asignado
        # pero si hay más, hay que asignarle uno nuevo (ya que uno se acaba de quedar libre)
        if self.n2 >= VEHICULOS:
            t_vehiculo = self.getTExponential()
            self.setEventTime('sn2', self.t + t_vehiculo)

        # Para desembarcar hay 50 puertas
        if self.n3 <= PUERTAS:
            t_desembarque = self.getTDesembarque()
            self.setEventTime('sn3', self.t + t_desembarque)

    def servicio_nodo3(self, tsuc):
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
        self.ss3[self.ns3] = tsuc
        self.deleteNextEvent('sn3')

        self.ll14[self.nll14] = tsuc
        self.nll14 += 1
        self.n14 += 1
        self.n_esperando_14 += 1

        # Comprobamos si queda gente en la cola del nodo 3
        if self.n3 >= PUERTAS:
            t_desembarque = self.getTDesembarque()
            self.setEventTime('sn3', self.t + t_desembarque)

        # Ponemos comprobamos si hay pistas libres
        if (self.pistas_ocupadas <= PISTAS) and (self.n_esperando_1 > 0 or self.n_esperando_14 > 0):
            self.n_esperando_14 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn14', self.t + t_aterrizaje)

    def salidaAvion(self, tsuc):
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
        self.ss14[self.ns14] = tsuc
        self.deleteNextEvent('sn14')
        self.pistas_ocupadas -= 1

        # Comprobamos si en las colas 1 o 14 queda alguien esperando para ser asignado pista
        if self.n_esperando_1 > 0:
            self.n_esperando_1 -= 1
            self.pistas_ocupadas += 1
            t_aterrizaje = self.getTAterrizaje()
            self.setEventTime('sn1', self.t + t_aterrizaje)

        elif self.n_esperando_14 > 0:
            self.n_esperando_14 -= 1
            self.pistas_ocupadas += 1
            t_despegue = self.getTDespegue()
            self.setEventTime('sn14', self.t + t_despegue)


a = Aeropuerto()

tsuc = a.getSigAvion(0)
if tsuc > T:
    print("return -1")
else:
    a.llegadaAvion(tsuc)
    while(a.noStop()):

        pp(a.eventos)
        nextEvent = a.getNextEvent()
        if nextEvent == "ll1":
            tsuc = a.getNextEventTime("ll1")
            a.llegadaAvion(tsuc)

        elif nextEvent == "sn1":
            tsuc = a.getNextEventTime("sn1")
            a.servicio_nodo1(tsuc)

        elif nextEvent == "sn2":
            tsuc = a.getNextEventTime("sn2")
            a.servicio_nodo2(tsuc)

        elif nextEvent == "sn3":
            tsuc = a.getNextEventTime("sn3")
            a.servicio_nodo3(tsuc)
        else:
            tsuc = a.getNextEventTime("sn14")
            a.salidaAvion(tsuc)

        # Good by
# Tiempo desde T hasta que el último cliente abandona el sistema
Tp = max(0.0, a.t-T)

# Tiempo medio que pasan los clientes en el sistema
acumulado1 = acumulado2 = acumulado3 = acumulado14 = 0
for indi in range(a.nll1):
    acumulado1 += a.ll1[indi] - a.ss1[indi]

acumulado2 = sum(a.ll2[indi] - a.ss2[indi] for indi in range(a.nll2))
acumulado3 = sum(a.ll3[indi] - a.ss3[indi] for indi in range(a.nll3))
acumulado14 = sum(a.ll14[indi] - a.ss14[indi] for indi in range(a.nll14))

# Tiempo medio del sistema
t_med_sistema = (acumulado1/a.nll1) + (acumulado2/a.nll2) + (acumulado3/a.nll3) + (acumulado14/a.nll14)
media_aviones_sistema = (a.n_m1 + a.n_m14 + a.n_m2 + a.n_m3)/T

pp("Tiempo desde {} hasta que el último avión abandona el sistema: {}".format(T, Tp))

pp("Tiempo medio de espera llegadas: {}".format(a.n_m1/a.nll1))
pp("Tiempo medio de espera salidas: {}".format(a.n_m14/a.nll14))
pp("Tiempo medio de las pistas ocupadas: {}%".format(round((a.tiempo_pistas_ocupadas/T)*100, 2)))
pp("Número medio de aviones en el sistema: {}".format(media_aviones_sistema))


# pp("Tiempo medio acumulado en 1: {}".format(acumulado1))
# pp("Tiempo medio acumulado en 2: {}".format(acumulado2))
# pp("Tiempo medio acumulado en 3: {}".format(acumulado3))
# pp("Tiempo medio acumulado en 14: {}".format(acumulado14))

# pp("Tiempo medio del sistema: {}".format(t_med_sistema))
