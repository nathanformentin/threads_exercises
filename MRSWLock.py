from threading import Thread
from random import randint
import threading
from contextlib import contextmanager
from threading  import Lock

"""
Alunos: Nathan Formentin Garcia, Romulo Strzoda
Números de matrícula: 116508, 108318
Curso: Engenharia de Computação
Novembro de 2020

Enunciado: Crie diversas threads para simular sequências de operações em paralelo e, aleatoriamente, defina qual conta receberá a operação, o tipo de operação (crédito ou débito), e o valor da operação.
Realize simulações com diferentes números de threads. Após, assuma que existe uma nova operação que realiza a consulta do saldo.
A principal diferença para esta operação é que múltiplas threads podem consultar o saldo de uma conta simultaneamente, desde que nenhuma outra thread esteja realizando uma operação de crédito ou débito.
 Operações de débito e crédito continuam precisando de acesso exclusivo aos registros da conta para executarem adequadamente. 

 Solução: para resolver o problema proposto, utilizamos uma estrutura conhecida como MRSW (Multi Reader Single Writer) Lock. Essa estrutura garante exclusiva as operações de escrita e que seja permitido diversas
 operacoes de leitura ao mesmo tempo. Isto é, enquanto há escrita, se ocorrerem diversas requisições de operações de leitura, elas entrarão numa fila até a liberação. Cada tipo de operação conta com uma Lock
 (que é uma estrutura primitiva para basicamente trancar ou destrancar o andamento de uma thread). Essa estrutura é utilizada para lidar com problemas de região crítica, ou seja, regiões de memória que são recursos
 compartilhados e não devem ser acessadas concorrentemente.

 O algoritmo funciona da seguinte forma: primeiro, o usuário define o número de clientes e o número de movimentações. Após isso, iniciamos os objetos de cada cliente, esses que são formados por uma id (um inteiro de identificação) e o saldo inicial, 
 que foi definido como zero. Além disso, como não importa realizarmos uma operação de leitura na conta do cliente 1 enquanto realizamos uma operação de escrita na conta do cliente 2, cada cliente conta com
 um objeto mrswLock. Esse objeto tem como atributos uma lock para escrita, uma lock para leitura e uma fila de leituras acumuladas. Após essa etapa, criamos operações sorteadas
 (tanto as operações quanto os clientes que sofrerão as operações são sorteados). Depois, através de outro laço, iniciamos as threads e por fim realizamos o join, para a thread main aguardar as threads de
 processamento. Mais informações sobre o funcionamento geral estão presentes no código.

 O modelo de apresentação do algoritmo é o seguinte:
 - Para operações de crédito (adição de um determinado valor da variável saldo) o seguinte template é utilizado:

    "Operação de crédito na conta de id 1 de valor: 100"

 - Para operações de débito (subtração de um determinado valor da variável saldo) o seguinte template é utilizado:
    "Operação de débito na conta de id 0 de valor: 50"

 - Para operações de saldo, utilizamos o seguinte template:
    "O saldo da conta de id2 é 0"
"""


class mrswLock(object):

    """
    A ideia do objeto mrswLock é garantir que possamos fazer diversas leituras concorrentes. No entanto, quando queremos realizar a operação de escrita, ela deve ser exclusiva. Essa implementação dá uma certa prioridade
    para leituras. Essa função é baseada na proposta de Michel Raynal (Um pseudocodigo pode ser encontrado aqui: https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock#Using_two_mutexes). Não existia um mecanismo
    como esse para Python como existe para outras linguagens como Rust, Go e em bibliotecas do C++. Portanto essa implementação foi construída sobre os objetos e métodos já disponíveis na biblioteca de threads base
    do Python. 

    """

    def __init__(self): #construtor do mrsw
        self.lock_escrita = Lock() #iniciando a lock para escritas
        self.lock_leitura = Lock() #iniciando lock para leituras
        self.num_leituras = 0 #fila de leituras

    def leitura_lock(self):
        self.lock_leitura.acquire() #tenta lockar leitura
        self.num_leituras = self.num_leituras + 1 #adiciona um na fila de leituras
        if self.num_leituras == 1: #se nao tem ngm 
            self.lock_escrita.acquire() #executa operacao de leitura
        self.lock_leitura.release() #quando termina, libera a lock

    def leitura_unlock(self): #operacao para sair da fila apos o termino da operacao de leitura
        assert self.num_leituras > 0 #checa se o numero de leituras eh maior de zero, se nao for retorna erro
        self.lock_leitura.acquire() #tranca  a leitura
        self.num_leituras = self.num_leituras -  1
        if self.num_leituras == 0: #se acabaram as leituras
            self.lock_escrita.release() #destranca a escrita se nao ha mais leituras
        self.lock_leitura.release() #destranca a leitura


    #metodos de escrita

    def escrita_lock(self):
        self.lock_escrita.acquire() #tranca escrita

    def escrita_unlock(self):
        self.lock_escrita.release() #destranca escrita

    @contextmanager #para utilizar com with e garantir que as execucoes vao ate o final independente de excecoes
    def escrita_locked(self): #base do funcionamento de escrita, tenta lockar, no final sempre ocorrerá o unlock graças ao finally (que garante que os recursos serão liberados após a execução)
        try:
            self.escrita_lock()
            yield
        finally:
            self.escrita_unlock()

    @contextmanager
    def leitura_locked(self): #base do funcionamento de leitura, tenta lockar e também no final o unlock sempre acontece por causa do finally, mesmo que ocorra algum problema ou que tenha alguma fila, por exemplo.
        try: 
            self.leitura_lock()
            yield
        finally: #finally garante que ocorrerá o release da leitura independente do resultado do try
            self.leitura_unlock()

class cliente:
    def __init__(self,idConta,saldoInicial,rw_mutex): #cada cliente é um objeto da classe cliente, que tem como atributos o id da conta, o saldo (que é iniciado com zero) e seus locks de leitura e escrita
        self.idConta = idConta
        self.saldo = saldoInicial
        self.rw_mutex = rw_mutex

    def debito(self,valor): #a funcao de debito verifica se a escrita esta trancada, se nao esta ela realiza a operacao
        with self.rw_mutex.escrita_locked():
            print ("Operação de débito na conta de id " + str(self.idConta) + " de valor: " + str(valor) + '\n')
            self.saldo = self.saldo - valor

    def credito(self,valor): #a funcao de debito verifica se a escrita esta trancada, se nao esta ela realiza a operacao
        with self.rw_mutex.escrita_locked():
            print ("Operação de crédito na conta de id " + str(self.idConta) + " de valor: " + str(valor) + '\n')
            self.saldo = self.saldo + valor
    
    def consultaSaldo(self): #a funcao de consulta de saldo veirfica se a leitura está trancada, se não ela realiza a operaçao
        with self.rw_mutex.leitura_locked():
            print ('O saldo da conta de id' + str(self.idConta) + ' é ' + str(self.saldo) + '\n')


mutex = mrswLock()
n_contas = int(input("Quantos clientes serão utilizados? \n"))
n_movimentacoes = int(input("Quantas movimentações bancárias ocorrerão? \n"))
clientes = []
for x in range(n_contas):
    clientes.append(cliente(x,0,mutex)) #todo objeto cliente é iniciado com um id, um saldo inicial (zero) e suas locks de leitura/escrita
threads = []
for i in range(n_movimentacoes): #o numero de threads é igual ao numero de movimentacoes.
    conta = randint(0,n_contas-1) #seleciona uma das contas para fazer operacao
    operacao = randint(0,2) #0 = credito, 1 = debito, 2 = saldo
    if operacao == 0:
        valor = randint(10,100) #os valores de credito variam entre 10 reais e 100 reais
        threads.append(Thread(target=clientes[conta].credito,args=([valor])))
    elif operacao == 1:
        valor = randint(10,100) #os valores de debito variam entre 10 e 100 reais
        threads.append(Thread(target=clientes[conta].debito,args=([valor])))
    elif operacao == 2:
        threads.append(Thread(target=clientes[conta].consultaSaldo,args=()))

for i in range(len(threads)):
    threads[i].start() #começa as threads

for z in range(len(threads)): #para terminar as threads juntas
    threads[i].join()




