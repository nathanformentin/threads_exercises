
#AUTORES: NATHAN FORMENTIN GARCIA E ROMULO STRZODA
#DISCIPLINA: SISTEMAS OPERACIONAIS (ENGENHARIA DE COMPUTAÇÃO)
#NOVEMBRO DE 2020

#RESUMO DO ALGORITMO: O objetivo do algoritmo é realizar a multiplicação de matrizes utilizando threads. É importante frisar que o usuário determina o número de threads, esse que necessariamente deve ser inferior a
#quantidade de numeros dentro da matriz (se nao é impossivel alocar um valor para cada thread, no minimo). Nao foi utilizado tecnicas como tilling, já que o usuário define as threads, então a divisao da matriz
#é feita através de numeros sequenciais (a primeira thread pode pegar, por exemplo, os tres primeiros valores da matriz, a segunda entre 3 e 6) não relacionando as linhas e colunas. Para determinação do endereço
#desse valor na matriz, foi criada a funcao buscaEndereco, que calcula a linha e a coluna que pertence o valor da atual iteracao (se é o terceiro valor, de acordo com as dimensões da matriz resultante, podemos calcular)
#os índices que deve ser inserido esse valor, e consequentemente as partes da multiplicação que geram ele. De resto, multiplicação de matriz normalmente, para cada valor da matriz.
from threading import Thread
import random
import math

def multiply(inicio,fim):
    global result
    global A
    global B
    for i in range(inicio,fim):
        coluna, linha = search_address(len(result[0]),len(result),i)
        for k in range(len(A[0])): #satisfaz a necessidade de igualdade linha-coluna entre as matrizes
            result[coluna][linha] += A[coluna][k] * B[k][linha]

def search_address(n_colunas,n_linhas,iteracaoAtual):
    linha = int(iteracaoAtual/n_colunas) #define a linha em que o valor se encontra
    coluna =  n_colunas - (((linha+1)*n_colunas) - (iteracaoAtual)) #define a coluna correspondente
    return coluna,linha

valid = 0 #para garantir que a operação entre as matrizes é valida (numero de colunas da primeira matriz deve ser igual ao numero de linhas da segunda matriz). alem disso, o numero de threads deve ser menor
#que o numero total de valores dentro da matriz resultante, para devida alocação de pelo menos um numero
while valid == 0:
    MA = int(input('Digite o numero de linhas da tabela 1: '))
    NA = int(input('\nDigite o numero de colunas da tabela 1: '))
    MB = int(input('\nDigite o numero de linhas da tabela 2: '))
    NB = int(input('\nDigite o numero de colunas da tabela 2: '))
    n_threads = int(input('\nDigite o numero de threads: '))
    if (NA != MB):
        print ('A quantidade de colunas da primeira matriz deve ser igual a quantidade de linhas da segunda matriz! \n')
    else:
        if (n_threads > NB*MA):
            print ('A quantidade de threads é superior a quantidade de valores na matriz resultante! Impossível alocar um valor no minimo para cada thread! \n')
        else:
            valid = 1

global A
A = [[random.randint(1,100) for x in range(NA)] for y in range(MA)] #gera a matriz inserindo numeros aleatorios entre 1-100
global B
B = [[random.randint(1,100) for x in range(NB)] for y in range(MB)]
global result
result = [[0 for x in range(MA)] for y in range(NB)] #preenche a matriz com zeros

threads = [] #inicia o vetor que guardara as threads
numbers_per_thread = int((MA*NB)/n_threads)
 #define o intervalo de numeros a serem enviados para cada thread
inicio = 0 #define a posicao inicial do primeiro intervalo na lista
fim = numbers_per_thread #define a posicao final do primeiro intervalo na lista
n_numbers = MA*NB #a matriz tera formado NA*MB, portanto isso define a quantidade de numeros no vetor
distribution = n_numbers%n_threads #pega o resto da divisao para distribuir os numeros que sobraram entre as threads
for i in range(n_threads):
    if distribution > 0:
        threads.append(Thread(target=multiply,args=(inicio,int(fim+1)))) #monta a thread para o devido intervalo, i identifica qual o intervalo, se i = 1, deve popular o ultimo intervalo da lista
        fim += 1
        inicio += 1
        distribution -= 1
    else:
        threads.append(Thread(target=multiply,args=(inicio,int(fim))))
    inicio += numbers_per_thread #atualiza o intervalo
    fim += numbers_per_thread #atualiza o intervalo

for i in range(len(threads)):
    threads[i].start() #começa as threads

for z in range(len(threads)):
    threads[i].join()
    
print ('A primeira matriz (A) é: ' + '\n')
for x in range(len(A)):
	print (A[x])
print ('A segunda matriz (B) é: ' + '\n')
for x in range(len(B)):
	print (B[x])
print ('A matriz resultante é: ' + '\n')
for x in range(len(result)):
	print (result[x])
