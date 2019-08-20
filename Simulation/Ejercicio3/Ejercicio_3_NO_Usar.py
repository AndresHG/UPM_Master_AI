from pprint import pprint as pp
import math
import random
import numpy as np
import copy
import matplotlib.pyplot as plt

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
def fitnessSolution2(sol):
    sc = sol.count(1)
    dumy_fitness = sc if isSolution(sol) else sc + PENALTY
    return dumy_fitness

# Segunda opción de fitness, no usar de momento
def fitnessSolution(sol):
    sc = sol.count(1) + (NUM_DISTRITOS - len(getDistrictCovered(sol)))
    dumy_fitness = sc if isSolution(sol) else sc + PENALTY # Nunca se cogen las soluciones si no son factibles
    return dumy_fitness

def getDistrictCovered(sol):
    district_covered = []
    for i, district in enumerate(sol):
        if district == 1:
            district_covered += [dist for dist in DISTRITOS[i].get_adyacentes() if dist not in district_covered]
    return district_covered

# Comprubea si uns solución parcial puede ser solución del problema
def isSolution(sol):
    district_covered = getDistrictCovered(sol)

    if set(FULL_DISTRICTS).issubset(district_covered): return True
    else: return False

# Genera una nueva solución a partir de la anterior
def exploreNewSolution(sol, T, To):
    i_swap1, i_swap2 = random.randint(0,NUM_DISTRITOS-1), random.randint(0,NUM_DISTRITOS-1)
    while i_swap1 == i_swap2:
        i_swap1, i_swap2 = random.randint(0,NUM_DISTRITOS-1), random.randint(0,NUM_DISTRITOS-1)
    i_mutation = random.randint(0,NUM_DISTRITOS-1)
    new_sol = copy.deepcopy(sol)

    # Se hace el intercambio de los distritos y se muta el valor de uno de los distritos
    swapDistritos(new_sol, i_swap1, i_swap2)
    
    p_mut = T/To
    p_random = random.random()
    if (p_random < To/T):
        if new_sol[i_mutation] == 0: new_sol[i_mutation] = 1
        else: new_sol[i_mutation] = 0

    # Se devuelve la nueva solución
    return new_sol

# Calcula la probabilidad de coger la solución dada
def calculateProb(old, new):
    if fitnessSolution(new) < fitnessSolution(old): return 1
    else: return math.exp(-((fitnessSolution(new) - fitnessSolution(old))/T))


if __name__ == "__main__":

        T_min = 50
        T_max = 70
        n_iteraciones_benchmark = 50
        registro_benchmark_temperaturas = []

        for i in range(T_min, T_max + 1):
            n_veces_solucion_optima = 0
            To = i
            print("Temperatura : ", i)
            for j in range(n_iteraciones_benchmark):
                T = i
                iteration = 1
                old_sol = [1 if random.random() > 0.5 else 0 for x in range(16)]
                best_sol = copy.deepcopy(old_sol)

                while T >  MIN_T:
                    new_sol = exploreNewSolution(old_sol, T, To)
                    prob = random.random()

                    # Calcula la probabilidad de cambio
                    if prob <= calculateProb(old_sol, new_sol):
                        old_sol = copy.deepcopy(new_sol)
                    # Comprueba si es la mejor solución hasta el momento
                    if fitnessSolution(new_sol) < fitnessSolution(best_sol):
                        best_sol = copy.deepcopy(new_sol)

                    if iteration % ItDT == 0:
                        T = T * alpha
                    iteration += 1
                    if (fitnessSolution(best_sol) == 3):
                        n_veces_solucion_optima +=1
            #print("Mejor solución encontrada pone parques de bomberos en: {}, con fitness: {}".format([i+1 for i, e in enumerate(best_sol) if e == 1], fitnessSolution(best_sol)))
            registro_benchmark_temperaturas.append(n_veces_solucion_optima)
            n_veces_solucion_optima = 0

        plt.plot(range(T_min, T_max + 1), registro_benchmark_temperaturas)
        plt.show()
