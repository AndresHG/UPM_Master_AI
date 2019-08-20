from pprint import pprint as pp
import math
import random
import numpy as np
import copy

# Estructura de un distrito
class Distrito:

    # Inicializacion de la clase
    def __init__(self, numero, adyacentes):
        self.numero = numero
        self.adyacentes = adyacentes

    def __str__(self):
        return "Valores: {}, {}".format(self.get_numero(), self.get_adyacentes())

    # Devuelve el distrito
    def get_numero(self):
        return self.numero

    # Devuelve los distritos adyacentes
    def get_adyacentes(self):
        return self.adyacentes


# Lista con todos los distritos
FULL_DISTRICTS = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

# Definición de variables globales
PENALTY = 8
NUM_DISTRITOS = 16
T = 80 # Temperatura actual
MIN_T = 1 # Temperatura mínima
MIWC = 50 # Max iterations without change
ItDT = 200 # Iterations to decrease temperature
alpha = 0.95

# Define los distritos del problema
DISTRITOS = [
    Distrito(1, [1, 2, 4, 5]),
    Distrito(2, [1, 2, 3, 5, 6]),
    Distrito(3, [2, 3, 6, 7]),
    Distrito(4, [1, 4, 5, 8, 10, 11]),
    Distrito(5, [1, 2, 4, 5, 6, 8]),
    Distrito(6, [2, 3, 5, 6, 7, 8, 9]),
    Distrito(7, [3, 6, 7, 9, 13]),
    Distrito(8, [4, 5, 6, 8, 9, 11, 12]),
    Distrito(9, [6, 7, 8, 9, 12, 13]),
    Distrito(10, [4, 10, 11, 14]),
    Distrito(11, [4, 8, 10, 11, 12, 14, 15]),
    Distrito(12, [8, 9, 11, 12, 13, 14, 15]),
    Distrito(13, [7, 9, 12, 13, 15, 16]),
    Distrito(14, [10, 11, 12, 15]),
    Distrito(15, [11, 12, 13, 14, 15, 16]),
    Distrito(16, [13, 15, 16])
]

# Intercambia los dos distritos indicados con ind1 y ind2 de la solución actual
def swapDistritos(sol, ind1, ind2):
    temp = sol[ind1]
    del sol[ind1]
    sol.insert(ind1, sol[ind2-1])
    del sol[ind2]
    sol.insert(ind2, temp)

# Devuelve un score/fitness para la solución
def fitnessSolution(sol):
    sc = sol.count(1)
    dumy_fitness = sc if isSolution(sol) else sc + PENALTY
    return dumy_fitness

# Segunda opción de fitness, no usar de momento
def fitnessSolution2(sol):
    sc = sol.count(1)
    dumy_fitness = sc if isSolution(sol) else np.inf # Nunca se cogen las soluciones si no son factibles
    return dumy_fitness

# Comprubea si uns solución parcial puede ser solución del problema
def isSolution(sol):
    district_covered = []
    for i, district in enumerate(sol):
        if district == 1:
            district_covered += DISTRITOS[i].get_adyacentes()

    if set(FULL_DISTRICTS).issubset(district_covered): return True
    else: return False

# Genera una nueva solución a partir de la anterior
def exploreNewSolution(sol):
    i_swap1, i_swap2 = random.randint(0,NUM_DISTRITOS-1), random.randint(0,NUM_DISTRITOS-1)
    while i_swap1 == i_swap2:
        i_swap1, i_swap2 = random.randint(0,NUM_DISTRITOS-1), random.randint(0,NUM_DISTRITOS-1)
    i_mutation = random.randint(0,NUM_DISTRITOS-1)
    new_sol = copy.deepcopy(sol)

    # Se hace el intercambio de los distritos y se muta el valor de uno de los distritos
    swapDistritos(new_sol, i_swap1, i_swap2)
    if new_sol[i_mutation] == 0: new_sol[i_mutation] = 1
    else: new_sol[i_mutation] = 0

    # Se devuelve la nueva solución
    return new_sol

# Calcula la probabilidad de coger la solución dada
def calculateProb(old, new):
    if fitnessSolution(new) < fitnessSolution(old): return 1
    else: return math.exp(-((fitnessSolution(new) - fitnessSolution(old))/T))


if __name__ == "__main__":

    import time
    NUM_TEST = 100
    T_INICIAL = T
    TEMPERATURAS = [-10, -30, -60, 0, 10, 30, 60]

    for temp_modif in TEMPERATURAS:
        time_start = time.time()
        aciertos = 0

        for _ in range(0, NUM_TEST):
            T = T_INICIAL + temp_modif


            iteration = 1
            iwc = 0 # Iterations without change
            old_sol = [1 if random.random() > 0.5 else 0 for x in range(16)]
            best_sol = old_sol

            while T >  MIN_T and iwc < MIWC:
                new_sol = exploreNewSolution(old_sol)
                prob = random.random()

                # Calcula la probabilidad de cambio
                if prob < calculateProb(old_sol, new_sol):
                    old_sol = copy.deepcopy(new_sol)
                    # Comprueba si es la mejor solución hasta el momento
                    if fitnessSolution(new_sol) < fitnessSolution(best_sol): best_sol = copy.deepcopy(new_sol)
                    iwc = 0
                else: iwc += 1

                if iteration % ItDT == 0:
                    T = T * alpha
                iteration += 1

            #---------------TEST-----------------
            zonas = [i+1 for i, e in enumerate(best_sol) if e == 1]
            if (len(zonas) == 3): aciertos += 1
            #------------------------------------


        ft = (time.time() - time_start)/NUM_TEST
        print('---------------------------------------')
        print('Temperatura: ', (T_INICIAL + temp_modif))
        print('Tiempo medio: %.2f' % round(ft, 2))
        print('Aciertos: %d%%' % (aciertos/NUM_TEST*100))


    #print("Mejor solución encontrada pone parques de bomberos en: {}, con fitness: {}".format([i+1 for i, e in enumerate(best_sol) if e == 1], fitnessSolution(best_sol)))
