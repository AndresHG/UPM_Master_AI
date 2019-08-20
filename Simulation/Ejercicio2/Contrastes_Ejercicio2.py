#Importamos las librerías necesarias para ejecutar el programa.
import numpy as np
from scipy import stats
from scipy.stats import norm, expon, exponweib, uniform
import matplotlib.pyplot as plt
from statsmodels.stats.diagnostic import kstest_normal
import math

# ATERRIZAJES

#Cargamos las muestras de tiempo de las maniobras de aterrizajes
text_file = open("E4.aterrizajes.txt")
datos = np.array(text_file.read().split('\n'))
np.set_printoptions(threshold=np.nan)
datos = datos[:-1].astype(float)

#Ajustamos las muestras de tiempo a las diferentes distribuciones que queremos contrastar
parametros_normal = norm.fit(datos)
parametros_exponencial = expon.fit(datos)
parametros_uniforme = uniform.fit(datos)

#Mostramos los parámetros obtenidos del ajuste de las distintas distribuciones a los datos
print("=============ATERRIZAJES=============")
print("Ajuste de parámetros de una distribución normal: ", parametros_normal)
print("Ajuste de parámetros de una distribución exponencial: ", parametros_exponencial)  
print("Ajuste de parámetros de una distribución uniforme: ", parametros_uniforme)  

#Realizamos el contraste de las distribuciones que hemos obtenido del ajuste anterior con las muestras de tiempo

print("KS Test Normal: ", stats.kstest(datos, cdf='norm', args=(parametros_normal[0], parametros_normal[1])))
print("KS Test Exponencial: ", stats.kstest(datos, cdf='expon', args=(parametros_exponencial[0], parametros_exponencial[1])))
print("KS Test Uniforme: ", stats.kstest(datos, cdf='uniform', args=(parametros_uniforme[0],parametros_uniforme[1])))

print("=======================================")

## Representación gráfica del histograma de los datos de aterrizajes frente a los ajustes de las diferentes distribuciones.
rv_normal = norm(parametros_normal[0], parametros_normal[1])
rv_exponential = expon(parametros_exponencial[0], parametros_exponencial[1])
rv_uniforme = uniform(parametros_uniforme[0], parametros_uniforme[1])
_,x,_ = plt.hist(datos, normed=True)
plt.plot(x, rv_normal.pdf(np.array(x)), label='normal')
plt.plot(x, rv_exponential.pdf(np.array(x)), label='exponencial')
plt.plot(x, rv_uniforme.pdf(np.array(x)), label='uniforme')
plt.legend(loc='upper right')
plt.title("ATERRIZAJES")



# DESEMBARQUES
#Cargamos las muestras de tiempo de los desembarques
text_file = open("E4.desembarques.txt")
datos = np.array(text_file.read().split('\n'))
datos = datos[:-1].astype(float)

#Ajustamos las muestras de tiempo a las diferentes distribuciones que queremos contrastar

parametros_exponencial = expon.fit(datos)
parametros_weibull = exponweib.fit(datos, floc=0, fa=1) #Establecemos el parámetro a de la distribución Weibull exponencial para obtener
                                                        #la Weibull, además de establecer la media a 0 (puesto que la Weibull tiene media 0)
parametros_normal = norm.fit(datos)

print("=============DESEMBARQUES=============")
print("Ajuste de parámetros de una distribución exponencial: ", parametros_exponencial)
print("Ajuste de parámetros de una distribución weibull: ", parametros_weibull)  
print("Ajuste de parámetros de una distribución normal: ", parametros_normal)  

#Realizamos el contraste de las distribuciones que hemos obtenido del ajuste anterior con las muestras de tiempo
print("KS Test Exponencial: ", stats.kstest(datos, cdf='expon', args=(parametros_exponencial[0], parametros_exponencial[1])))
print("KS Test Normal: ", stats.kstest(datos, cdf='norm', args=(parametros_normal[0], parametros_normal[1])))
print("KS Test Weibull: ", stats.kstest(datos, cdf='exponweib', args=(parametros_weibull[0],parametros_weibull[1], parametros_weibull[2], parametros_weibull[3])))
print("=======================================")

## Representación gráfica del histograma de los datos de aterrizajes frente a los ajustes de las diferentes distribuciones.
rv_exponential = expon(parametros_exponencial[0], parametros_exponencial[1])
rv_weibull = exponweib(parametros_weibull[0],parametros_weibull[1], parametros_weibull[2], parametros_weibull[3])
rv_normal = norm(parametros_normal[0], parametros_normal[1])
plt.figure()
_,x,_ = plt.hist(datos, normed=True)
plt.plot(x, rv_exponential.pdf(np.array(x)), label='exponencial')
plt.plot(x, rv_weibull.pdf(np.array(x)), label='weibull')
plt.plot(x, rv_normal.pdf(np.array(x)), label='normal')
plt.legend(loc='upper right')
plt.title("DESEMBARQUES")
plt.show()




