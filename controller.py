import smbus
import time
import json
import Adafruit_GPIO.I2C as I2C
temperatura = 0
nivel_elevador = 0
num_peca = 0


#para_esteira = 0

#print('kdahjksdhkashdkshakjdhsjkahdjkahhdakshjkdhka')

# Funcões secundárias: Obs: as funcões secundárias devem ser iguais para o view.py (Sistema Django) e para o
# controller.py (Sistema Raspberry)

# 1 - Funcao controller: Aplica alteracões no raspberry e atualiza o dataValues
def controller(dataValues):
    bus = smbus.SMBus(1)  # Configuração do barramento bus
    [busAddress, dataAddress,stateBusID] = setup()  # Funcao que calcula e inicia as variaveis auxiliares  #Verificar pq ta
    # diferente do sistema Django
    #print(busAddress)
    #print(stateBusID)
    read_inputs(bus, busAddress, dataValues)  # Funcao de leitura dos inputs do raspberry
    dataValues["state"] = newstate_function(dataValues)  # Funcao para calcular o novo state (criar as maquinas de
    # estado - alterar)
    writestate_function(dataValues)  # Funcao para atualizar os valores dos outputs (criar as maquinas de estados - 
    # alterar) 
    write_outputs(bus, busAddress, dataValues, stateBusID)  # Funcao para aplicar os outputs conforme o state calculado
    return dataValues  # Retorna o dataValues atualizado


# 2 - Funcao de SETUP para inicializar os dados. Para testar diferentes máquinas de estados, alterar essa funcao. 
# Também quando configurar o hardware alterar aqui. A função SETUP deve ser importada do Setup que for escolhido 

from setupAlimentacao import setup

# 3 - Funcao de leitura dos inputs do raspberry
def read_inputs(bus, busAddress, dataValues):
    for busID in busAddress["inputs"]:
        bus.write_byte_data(busID, 0x00, 0xFF)
        byte = bus.read_byte_data(busID, 0xFF)
        str_byte = format(byte, '#010b')
        for id in range(0, 8):
            ioName = busAddress["inputs"][busID][id]
            if ioName:
                dataValues["inputs"][ioName] = int(str_byte[9 - id])
                #print (dataValues["inputs"][ioName])
        #print ("////////////////")


# 4 - Funcao para calcular o novo state. Função com a lógica de transição da máquina de estados.
# Obs: Todo novo estado tem que estar com 2o argumento como True

class Melexis:

    def __init__(self, address=0x5A):
        self._i2c = I2C.Device(address,busnum=1)

    def readAmbient(self):
        return self._readTemp(0x06)

    def readObject1(self):
        return self._readTemp(0x07)

    def readObject2(self):
        return self._readTemp(0x08)

    def _readTemp(self, reg):
        temp = self._i2c.readS16(reg)
        temp = temp * .02 - 273.15
        return temp

def newstate_function(dataValues):
    global temperatura
    global nivel_elevador
    global num_peca

    state = dataValues["state"]
    newstate = state
    
    # Seguranca
    if state["seguranca"][0] == "Ligada":
        #print('d')
        if dataValues["inputs"]["emergencia"] == 1:
            newstate["seguranca"] = ["Parada", True]
            newstate["alimentacao"] = ["Parada", True]
            newstate["esteiras"] = ["Parada", True]
            newstate["alimentacao2"] = ["Parada", True]
            newstate["esteira3"] = ["Parada", True]
            #print('d1')
            
    elif state["seguranca"][0] == "Parada"and dataValues["inputs"]["emergencia"] == 1:
        #print('c')
        if dataValues["inputs"]["restart"] == 0 :
            newstate["seguranca"] = ["Start", True]
            newstate["alimentacao"] = ["Parada", True]
            newstate["esteiras"] = ["Parada", True]
            newstate["alimentacao2"] = ["Parada", True]
            newstate["esteira3"] = ["Parada", True]
            #print('c')

    elif state["seguranca"][0] == "Start":
        #print('a11')
        if dataValues["inputs"]["emergencia"]==0 and dataValues["inputs"]["restart"] == 0:
            #print('a')
            newstate["seguranca"] = ["Ligada", True]
            newstate["alimentacao"] = ["Espera", True]
            newstate["esteiras"] = ["Espera", True]
            newstate["alimentacao2"] = ["Espera", True]
            newstate["esteira3"] = ["Espera", True]
        
        elif dataValues["inputs"]["emergencia"] == 1 and dataValues["inputs"]["restart"] == 1:
            newstate["seguranca"] = ["Parada", True]
            newstate["alimentacao"] = ["Parada", True]
            newstate["esteiras"] = ["Parada", True]
            newstate["alimentacao2"] = ["Parada", True]
            newstate["esteira3"] = ["Parada", True]
            


    # Alimentacao
    if state["alimentacao"][0] == "Espera":
        if dataValues["local"]["qtdPlacas"] == 0:
            newstate["alimentacao"] = ["Parada", True]
        
        elif dataValues["inputs"]["s2"] == 1:
            newstate["alimentacao"] = ["Liga Ali", True]
            
    elif state["alimentacao"][0] == "Liga Ali":

        if dataValues["inputs"]["s1"] == 0 and dataValues["inputs"]["bpRetorno"] == 1:
            newstate["alimentacao"] = ["Acionamento b1", True]

    elif state["alimentacao"][0] == "Acionamento b1":
        if dataValues["inputs"]["s1"] == 0 and dataValues["inputs"]["bpRetorno"] == 0 and dataValues["inputs"]["s2"] == 1:
            newstate["alimentacao"] = ["Espera bomba", True]
            
        else: newstate["alimentacao"] = ["Delay b1", True]
    
    if state["alimentacao"][0] == "Delay b1":
        if dataValues["inputs"]["s1"] == 0 and dataValues["inputs"]["bpRetorno"] == 0 and dataValues["inputs"]["s2"] == 1:
            newstate["alimentacao"] = ["Espera bomba", True]
    
    elif state["alimentacao"][0] == "Espera bomba" :
        if dataValues["inputs"]["s1"] == 1 and dataValues["inputs"]["s2"]==1:
            newstate["alimentacao"] = ["Liga Ali", True]
            
    
    # Esteira M1 e M2
    if state["esteiras"][0] == "Espera":
        if dataValues["inputs"]["s3"] == 1 and dataValues["inputs"]["s2"] == 0 and dataValues["local"]["stop"] == 0:
            newstate["esteiras"] = ["Liga m1", True]
            #print("entra no espera")
            
        elif dataValues["inputs"]["s3"] == 0:
            newstate["esteiras"] = ["Aciona atuador", True]
            #print("não entra no espera")

    elif state["esteiras"][0] == "Liga m1":
        #print("entra liga m1")
        if dataValues["inputs"]["s2"] == 1:

            newstate["esteiras"] = ["Desliga m1", True]

    elif state["esteiras"][0] == "Desliga m1":
        sensor = Melexis()
        temperatura = round(sensor.readObject1(),1)
        print(temperatura)
        #print("entra desli m1")
        if dataValues["inputs"]["s3"] == 0 and temperatura <= 30:  # olhar testes valor da temperatura 
            newstate["esteiras"] = ["Aciona atuador", True]
            
        elif dataValues["inputs"]["s2"] == 0 and dataValues["inputs"]["s3"] == 1 and dataValues["local"]["stop"] == 0:
            newstate["esteiras"] = ["Liga m1", True]

    elif state["esteiras"][0] == "Aciona atuador":
        #print("entra aqui aciona atuador")
        #print(dataValues["inputs"]["at1open"])
        if dataValues["inputs"]["at1open"] == 0 and dataValues["inputs"]["s2"] == 0 and dataValues["local"]["stop"] == 0:
            newstate["esteiras"] = ["Liga m1", True]
           #print("entra aqui liga m1")


    # Alimentação 2
    if state["alimentacao2"][0] == "Espera":
        #print("entra aqui ali 2 espera")
        if dataValues["inputs"]["s4"] == 0:
        #and dataValues["local"]["tampas"] > 0:
            newstate["alimentacao2"] = ["Liga ali2", True]
            #print("entra aqui liga ali2")

        #elif dataValues["inputs"]["tampas"] == 0:
            #newstate["alimentacao2"] = ["Fim tampas", True]

        #if dataValues["local"]["tampas"] > 0:
            #newstate["alimentacao2"] = ["Espera", True]

    elif state["alimentacao2"][0] == "Liga ali2":
        if dataValues["inputs"]["s5"] == 0:
            newstate["alimentacao2"] = ["Desliga ali2", True]

    elif state["alimentacao2"][0] == "Desliga ali2":
        if dataValues["inputs"]["s4"] == 1:
            newstate["alimentacao2"] = ["Espera", True]
            
    # Esteira3
    if state["esteira3"][0] == "Espera":
        #print("entra aqui ali 2 espera")
        if dataValues["inputs"]["s6"] == 0 and num_peca <= 3:
            newstate["esteira3"] = ["Atuador Direita", True]
        
        elif dataValues["inputs"]["s6"] == 0 and num_peca >= 4:
            newstate["esteira3"] = ["Atuador Esquerda", True]

    elif state["esteira3"][0] == "Atuador Direita":
        if num_peca >= 6:
            newstate["esteira3"] = ["Incremento elevador", True]

        elif num_peca < 6 and dataValues["inputs"]["s6"] == 1 and dataValues["inputs"]["at3direita"] == 0:
            newstate["esteira3"] = ["Espera", True]

    elif state["esteira3"][0] == "Atuador Esquerda":
        if num_peca >= 6:
            newstate["esteira3"] = ["Incremento elevador", True]

        elif num_peca < 6 and dataValues["inputs"]["s6"] == 1 and dataValues["inputs"]["at3esquerda"] == 0:
            newstate["esteira3"] = ["Espera", True] 

    elif state["esteira3"][0] == "Incremento elevador":
        if dataValues["inputs"]["s6"] == 1:
            newstate["esteira3"] = ["Espera", True]
            print('elevador subiu')
        
    return newstate

    # Armazenamento
    
    #if state["armazenamento"][0] == "Espera":
        #if dataValues["inputs"]["se"] == 1:
            #newstate["armazenamento"] = ["Fechar atuador", True]

    
# 5 - Funcao para atualizar os valores dos outputs. Função com a lógica de saída da máquina de estados.
def writestate_function(dataValues):
    global temperatura
    global nivel_elevador
    global num_peca
    state = dataValues["state"]

    if state["seguranca"][1]:
        if state["seguranca"][0] == "Ligada":
            dataValues["outputs"]["e1"] = 1
            dataValues["outputs"]["alarme"] = 0

        elif state["seguranca"][0] == "Parada":
            dataValues["outputs"]["e1"] = 0
            dataValues["outputs"]["alarme"] = 1

        elif state["seguranca"][0] == "Start":
            dataValues["outputs"]["e1"] = 1
            dataValues["outputs"]["alarme"] = 1

    if state["alimentacao"][1]:
        if state["alimentacao"][0] == "Espera":
            dataValues["outputs"]["mv1"] = 0
            dataValues["outputs"]["mr1"] = 0
            dataValues["outputs"]["bp"] = 0
        
        if state["alimentacao"][0] == "Liga Ali":
            dataValues["outputs"]["mv1"] = 1
            dataValues["outputs"]["mr1"] = 1
            dataValues["outputs"]["bp"] = 0
            #dataValues["outputs"]["fim_placas"] = 0

        if state["alimentacao"][0] == "Acionamento b1":
            dataValues["outputs"]["mv1"] = 0
            dataValues["outputs"]["mr1"] = 0
            dataValues["outputs"]["bp"] = 1
            #dataValues["outputs"]["fim_placas"] = 0
            
        if state["alimentacao"][0] == "Delay b1":
            dataValues["outputs"]["mv1"] = 0
            dataValues["outputs"]["mr1"] = 0
            dataValues["outputs"]["bp"] = 0
            time.sleep(1)
            
        if state["alimentacao"][0] == "Espera bomba":
            dataValues["outputs"]["mv1"] = 1
            dataValues["outputs"]["mr1"] = 1
            dataValues["outputs"]["bp"] = 0

        if state["alimentacao"][0] == "Parada":
            dataValues["outputs"]["mv1"] = 0
            dataValues["outputs"]["mr1"] = 0
            dataValues["outputs"]["bp"] = 0
            #dataValues["outputs"]["fim_placas"] = 0,
            
        if state["alimentacao"][0] == "Ligado":
            dataValues["outputs"]["mv1"] = 0
            dataValues["outputs"]["mr1"] = 0
            dataValues["outputs"]["bp"] = 0


    if state["esteiras"][1]:
        if state["esteiras"][0] == "Espera":
            dataValues["outputs"]["esteira1"] = 0
            dataValues["outputs"]["esteira2"] = 0

        if state["esteiras"][0] == "Liga m1":
            dataValues["outputs"]["esteira1"] = 1
            dataValues["outputs"]["esteira2"] = 1

        if state["esteiras"][0] == "Desliga m1":
            dataValues["outputs"]["esteira1"] = 0
            dataValues["outputs"]["esteira2"] = 0
            #chamar função Temperatura (sensor)


        if state["esteiras"][0] == "Aciona atuador":
            dataValues["outputs"]["esteira1"] = 0
            dataValues["outputs"]["esteira2"] = 0
            #chamar função Aciona Atuador
            
        if state["esteiras"][0] == "Parada":
            dataValues["outputs"]["esteira1"] = 0
            dataValues["outputs"]["esteira2"] = 0
                     
        if state["esteiras"][0] == "Ligado":
            dataValues["outputs"]["esteira1"] = 0
            dataValues["outputs"]["esteira2"] = 0
            

    if state["alimentacao2"][1]:
        if state["alimentacao2"][0] == "Espera":
            dataValues["outputs"]["mv2"] = 0
            dataValues["outputs"]["mr2"] = 0

        if state["alimentacao2"][0] == "Liga ali2":
            dataValues["outputs"]["mv2"] = 1
            dataValues["outputs"]["mr2"] = 1
            dataValues["local"]["stop"] = 1
            #para_esteira = 1
           #print("entra aqui alimentacao liga ali2->")
            #print(para_esteira)

        if state["alimentacao2"][0] == "Desliga ali2":
            dataValues["outputs"]["mv2"] = 0
            dataValues["outputs"]["mr2"] = 0
            dataValues["local"]["stop"] = 0
            #para_esteira = 0
            #print('valor saida ->')
            #print(para_esteira)

        if state["alimentacao2"][0] == "Parada":
            dataValues["outputs"]["mv2"] = 0
            dataValues["outputs"]["mr2"] = 0
            dataValues["local"]["stop"] = 1
            
        
    if state["esteira3"][1]:
        if state["esteira3"][0] == "Espera":
            dataValues["outputs"]["m3"] = 1
            num_peca = num_peca + 1

        #if state["esteira3"][0] == "Atuador direita":
            #chamar função para atuar atuador

        if state["esteira3"][0] == "Incremento elevador":
            dataValues["outputs"]["m3"] = 0
            num_peca = 0
            nivel_elevador = nivel_elevador + 1
            #colocar função elevador
            #gira_motor_horario(5)

        #if state["esteira3"][0] == "Atuador esquerda":
            #chamar função para atuar atuador

        if state["esteira3"][0] == "Parada":
            dataValues["outputs"]["m3"] = 0



# 6 - Funcao para aplicar os outputs conforme o state calculado
def write_outputs(bus, busAddress, dataValues, stateBusID):
    state = dataValues["state"]
    busIDReloaded = []
    for stateName, value in state.items():
        if value[1] and stateBusID[stateName] != ['']:
            #print(value)
            print(state)
            #print(dataValues["local"])
            for busID in stateBusID[stateName]:
                if busID not in busIDReloaded:
                    busIDReloaded += [busID]
                    outputs = [0, 0, 0, 0, 0, 0, 0, 0]
                    n = 0
                    byte = 0
                    for n in range(0,8):
                        ioName=busAddress["outputs"][busID][n]
                        if ioName:                            
                            outputs[n] = dataValues["outputs"][ioName]
                            #n+=1 
                            #print('teste')
                            #print(ioName)
                            #print(n)
                    print(outputs)
                    print('outputs aqui')

                    for id in range(0, 8):  #fdp 
                        byte=byte+outputs[id]*2**id #Sem inversor, testar quando já estiver na placa final
                        #byte = byte + (1 - outputs[id]) * 2 ** id  # Com inversor, utilizar essa linha na protoboard
                    #print(outputs[0])
                    #print('byte antes')
                    #print(byte)
                    #print('byte dps')
                    #byte = 128 não descomentar
                    bus.write_byte_data(busID, 0x00, byte)
                    #print(byte)
                    #print(bin(byte))
                    #print(outputs)
            value[1] = False

 
timeRepeat = 0.1  # Colocar o mesmo tempo do html, só que em segundos
# [busAddress, dataAddress, stateBusID]=setup(); #Inicialização da funço setup inicializando JSdataValues com uma 
# string que representa o JSON. A variável armazenará todos os dados necessários para exibir a página e é utilizada 
# nas funções. Para atualizo sempre é preciso converter para variavel utilizando JSON.parse e depois converter 
# novamente com JSON.stringify no Javascript (json.load e json.dumps no Python (código da view.py)) 

JSdataValues = '{"outputs": {"e1": "", "alarme": "", "mv1": "", "mr1": "", "bp": "", "esteira1": "","esteira2": "", "mv2": "", "mr2": "", "m3": ""}, ' \
               '"inputs": {"emergencia": "", "restart": "", "s1": "", "bpRetorno": "", "s2": "","s3": "", "at1open": "", "s4": "", "s5": "", "s6": "", "at3direita": "", "at3esquerda": ""}, ' \
               '"local": {"stop": 0,"portas": "", "seguranca": "", "qtdPlacas": "", "qtdTampas": "", "qtdPlacasProntas": "", "nivelElevadorMaxElevador": ""},' \
               '"settings": {"tempInoculacaoMax": "", "nivelElevadorMax": ""}, ' \
               '"state": {"seguranca": ["Parada", true], "esteiras": ["Parada", true],"alimentacao": ["Parada", true], "alimentacao2": ["Parada", true], "esteira3": ["Parada", true]}}';


#print(JSdataValues)
    
    
while (1):
    time.sleep(timeRepeat)
    dataValues = json.loads(JSdataValues)
    dataValues = controller(dataValues)  # Funcao controller que faz toda a lógica de consulta e atualizacao do 
    # raspberry. Para rodar no computador, comentar essa linha dataValues["inputs"]["tempInoculacao"]=2              
    # #Linha pra teste no computador. Pode trocar o valor para testar dataValues["local"]["qtdPlacasProntas"]=52     
    # #Linha pra teste no computador. Pode trocar o valor para testar dataValues["state"]["alimentacao"]=["Espera", 
    # True]        #Linha pra teste no computador. Pode trocar o valor para testar dataValues["state"][ 
    # "inoculacao"]=["Resfriamento",True]   #Linha pra teste no computador. Pode trocar o valor para testar 
    # dataValues["state"]["fechamento"]=["Nova Tampa",True]     #Linha pra teste no computador. Pode trocar o valor 
    # para testar dataValues["state"]["armazenamento"]=["Subir Nível",True] #Linha pra teste no computador. Pode 
    # trocar o valor para testar 
    JSdataValues = json.dumps(dataValues)
    #print ("EM")
    #print(dataValues["inputs"]["emergencia"])
    #print ("RT")
    #print(dataValues["inputs"]["restart"])
    #dataValues["local"]["qtdPlacas"]== 52
    #dataValues["local"]["tempInoculacao"]= 29
    
    