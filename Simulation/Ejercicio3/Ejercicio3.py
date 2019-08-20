from pprint import pprint as pp
import math
import random
import numpy as np
import copy
import time
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
T = 84 # Temperatura actual (ya optimizada)
MAX_FITNESS = 13 + PENALTY # Valor máximo que toma fitness
MIN_T = 1 # Temperatura mínima
MIWC = 50 # Max iterations without change (NO USAR)
ItDT = 140 # Iterations to decrease temperature
alpha = 0.96

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
def exploreNewSolution(sol):
    i_swap1, i_swap2 = random.randint(0,NUM_DISTRITOS-1), random.randint(0,NUM_DISTRITOS-1)
    while i_swap1 == i_swap2:
        i_swap1, i_swap2 = random.randint(0,NUM_DISTRITOS-1), random.randint(0,NUM_DISTRITOS-1)
    i_mutation = random.randint(0,NUM_DISTRITOS-1)
    new_sol = copy.deepcopy(sol)

    # Se hace el intercambio de los distritos y se muta el valor de uno de los distritos
    swapDistritos(new_sol, i_swap1, i_swap2)
    if random.random() < probMutation(sol):
        if new_sol[i_mutation] == 0: new_sol[i_mutation] = 1
        else: new_sol[i_mutation] = 0

    # Se devuelve la nueva solución
    return new_sol

# Calcula la probabilidad de coger la solución dada
def calculateProb(old, new):
    if fitnessSolution(new) < fitnessSolution(old): return 1
    else: return math.exp(-((fitnessSolution(new) - fitnessSolution(old))/T))

# Calculate mutation probability
def probMutation(sol):
    return math.exp(-((MAX_FITNESS - fitnessSolution(sol))/T))

# Función principal
def calculateBestSol():

    iteration = 1
    iwc = 0 # Iterations without change
    old_sol = [1 if random.random() > 0.5 else 0 for x in range(16)]
    best_sol = copy.deepcopy(old_sol)
    fitness_solutions_explored = []

    global T
    while T >  MIN_T:
        new_sol = exploreNewSolution(old_sol)
        fitness_solutions_explored.append(fitnessSolution(new_sol))
        prob = random.random()

        # Calcula la probabilidad de cambio
        if prob <= calculateProb(old_sol, new_sol):
            old_sol = copy.deepcopy(new_sol)
            # Comprueba si es la mejor solución hasta el momento
            if fitnessSolution(new_sol) < fitnessSolution(best_sol):
                best_sol = copy.deepcopy(new_sol)

                # Comprobamos is es la mejor solución del problema
                # if fitnessSolution(best_sol) == 3:
                # print(iteration)

        if iteration % ItDT == 0:
            T = T * alpha
        iteration += 1

    return (best_sol, fitness_solutions_explored)


if __name__ == "__main__":

    # Test 1: Temperatura fijada de 82 y establecer un rango de +-15 a esa temperatura
    # temperaturas = [i for i in range(T-15, T+15 + 1)]

    # Test 2: alfa variable entre 0'9 y 0'99
    # alfas = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]

    # Test 3: iteraciones en bajar la temperatura
    iteraciones = [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145]

    num_test = 20
    datos_grafico = []

    # Test 1
    # for temp in temperaturas:

    # Test 2
    # for alf in alfas:

    # Test 3
    # for it in iteraciones:
    #     aciertos = 0
    #     for nt in range(0,num_test):
    #         # Test 1
    #         # T = temp

    #         # Test 2
    #         # T = 84
    #         # alpha = alf

    #         # Test 3
    #         T = 84
    #         ItDT = it

    #         best_sol = calculateBestSol()

    #         if fitnessSolution(best_sol) == 3: aciertos += 1
    #     # Test 1
    #     # print('Temperatura: ', temp, '\tAciertos(20):', aciertos, '\n')

    #     # Test 2
    #     # print('Alfa: ', alf, '\tAciertos(20):', aciertos, '\n')

    #     # Test 3
    #     print('Iteraciones: ', it, '\tAciertos(20):', aciertos, '\n')

    #     datos_grafico.append(aciertos)
    #     aciertos = 0

    start_time = time.time()
    sol = calculateBestSol()
    best_sol, fitness_solutions_explored = sol

    end_time = time.time()
    time_spent = end_time - start_time
    print("Han pasado {} segundos".format(time_spent))
    print("Mejor solución encontrada pone parques de bomberos en: {}, con fitness: {}".format([i+1 for i, e in enumerate(best_sol) if e == 1], fitnessSolution(best_sol)))

    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)
    # ax.set_ylabel('Número de aciertos')

    # Mostrar resultados de una sola iteración
    ax.set_ylabel('Fitness')
    ax.set_xlabel('Iteraciones')
    plt.plot([x for x in range(len(fitness_solutions_explored))], fitness_solutions_explored)

    # Test 1
    # plt.plot(temperaturas, datos_grafico)
    # ax.set_title('Número de aciertos en función de la temperatura')
    # ax.set_xlabel('Temperatura')

    # Test 2
    # plt.plot(alfas, datos_grafico)
    # ax.set_title('Número de aciertos en función de las alfas')
    # ax.set_xlabel('Alfa')

    # Test 3
    # plt.plot(iteraciones, datos_grafico)
    # ax.set_title('Número de aciertos en función de las iteraciones para decrementar la temperatura')
    # ax.set_xlabel('Itereaciones que la temperatura permanece estable')

    plt.show()
