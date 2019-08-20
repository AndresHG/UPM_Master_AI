import random

####### Defino las variables

fichero = 'dataset'
num_dataset = 4000
numeros_en_grupo = 40
num_bits = 32

random.seed(1846)

dataset = [[random.getrandbits(num_bits) for x in range(0, num_dataset)] for y in range(0, (num_dataset / numeros_en_grupo))]


####### Escribe el dataset generado en un fichero

f = open(fichero + '_' + str(num_dataset) + '.txt', 'w+')
f.write("type: d")
f.write("\ncount: " + str(num_dataset))
f.write("\nnumbit: "+ str(num_bits))

for i in range(0, len(dataset)):
    for j in range(0, len(dataset[i])):
        f.write("\n" + str(dataset[i][j]))
