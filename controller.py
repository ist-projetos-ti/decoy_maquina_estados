import mysql.connector
import smbus
import time
import json
import Adafruit_GPIO.I2C as I2C
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep
#from __future__ import division


#conecção com banco de dados
db = mysql.connector.connect(
  host="localhost",
  user="decoy",
  password="senai@123",
  database="decoy"
)



# Import the PCA9685 module.
import Adafruit_PCA9685
#import adafruit_pca9685
import Adafruit_GPIO.I2C as I2C
#import board
#import busio


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH) #Enable do motor de passo
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW) #Direção motor de passo
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW) #PWM do motor de passo
#pwm=GPIO.PWM(12,500)     #Configura para 100 Hz
#pwm.start(50)            #Inicia com DC=0%

#i2c = busio.I2C(board.SCL, board.SDA)
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)

temperatura = 0
nivel_elevador = 0
num_peca = 0


def gira_motor_horario(voltas):
    GPIO.output(16, GPIO.LOW) # Turn on enable
    GPIO.output(22, GPIO.HIGH) # Sentido
    for y in range(voltas):
        for x in range(405):
            GPIO.output(12, GPIO.LOW) # Turn on enable
            time.sleep(0.01) 
            GPIO.output(12, GPIO.HIGH) # Sentido
            time.sleep(0.01)
            x=x+1
        y=y+1
    GPIO.output(16, GPIO.HIGH) # Turn on enable

        
def gira_motor_anti_horario(voltas):
    GPIO.output(16, GPIO.LOW) # Turn on enable
    GPIO.output(22, GPIO.LOW) # Sentido
    for y in range(voltas):
        for x in range(405):
            GPIO.output(12, GPIO.LOW) # Turn on enable
            time.sleep(0.001) 
            GPIO.output(12, GPIO.HIGH) # Sentido
            time.sleep(0.001)
            x=x+1
        y=y+1
    GPIO.output(16, GPIO.HIGH) # Turn on enable

def setup():
    #Lista os barramentos utilizados, separando em input e output
    busAddress={ 
        "outputs":{
            0x22:["","","","","","","",""],
            0x23:["","","","","","","",""]
        },
        "inputs":{
            0x26:["","","","","","","",""],
            0x27:["","","","","","","",""]
        }
    }

    # Identifica em qual barramento e posição está cada IO  
    dataAddress={ 
        "outputs":{

            #Seguranca
            "e1":[0x23, 6,"seguranca"],
            "alarme":[0x22, 2,"seguranca"],
            
            #Alimentacao
            "mv1":[0x23,0,"alimentacao"],  
            "mr1":[0x22,0,"alimentacao"],
            "bp":[0x23,1,"alimentacao"],
            #"fim_placas":[0x22,7,"alimentacao"],   #m1 = motor esteira 1
            
            #Esteira 1 e 2
            "esteira1":[0x23,7,"esteiras"], #motor 1
            "esteira2":[0x22,7,"esteiras"],  #motor 1
            
            #alimentacao2
            "mv2":[0x22,1,"alimentacao2"],
            "mr2":[0x23,2,"alimentacao2"],
            
            #Esteira3
            "m3":[0x22,6,"esteira3"]
            

            },
        
        "inputs":{
            #Seguranca
            "emergencia":[0x27, 6,"seguranca"],
            "restart":[0x27, 7,"seguranca"],
            
            #Alimentacao
            "s1":[0x26,6,"alimentacao"],   
            "bpRetorno":[0x26,7,"alimentacao"],
            
            #Esteira 1 e 2
            "s2":[0x26,1,"esteiras"],
            "s3":[0x26,2,"esteiras"],
            #"s4":[0x27,6,"esteiras"],
            "at1open":[0x26,3,"esteiras"],
            #"at1close":["","","inoculacao"],
            
            #alimentacao2
            "s4":[0x27,0,"alimentacao2"],
            "s5":[0x26,4,"alimentacao2"],
            #"at2open":["","","alimentacao2"],
            #"at2close":["","","alimentacao2"],
            
            #Esteira3
            "s6":[0x26,5,"esteira3"],
            "at3direita":[0x27,2,"esteira3"],
            "at3esquerda":[0x27,1,"esteira3"],
            "s7":[0x26,0,"esteira3"]
            
            }
        }

    #configuracao do busAddress, distribuindo os outputs e inputs    
    for ioMethod in ["inputs","outputs"]:
        for ioName, address in dataAddress[ioMethod].items():
            for bus in busAddress[ioMethod]:
                if address[0]==bus:
                    busAddress[ioMethod][bus][address[1]]=ioName

    stateBusID={
        "seguranca":[],
        "alimentacao":[],
        "esteiras":[],
        "alimentacao2":[],
        "esteira3":[]
    }

    #configurando stateBusID, distribuindo os busID nos states
    for ioName, address in dataAddress["outputs"].items():
        if address[0] not in stateBusID[address[2]]:
            stateBusID[address[2]]+=[address[0]]

    return busAddress, dataAddress, stateBusID



#para_esteira = 0

#print('teste')

# Funcões secundárias: Obs: as funcões secundárias devem ser iguais para o view.py (Sistema Django) e para o controller.py (Sistema Raspberry)

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
        
    cursor = db.cursor()
    cursor.execute("SELECT * FROM machine WHERE id = 1")
    result = cursor.fetchall()
    status_maq = result[0][1]    
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
            
            cursor = db.cursor()
            cursor.execute("SELECT * FROM orders WHERE num_order = (SELECT max(num_order) FROM orders)")
            result = cursor.fetchall()
            r = result[0][0]
            cursor.execute("INSERT INTO alarms (num_order,description,timestamp) VALUES ({0},'Maquina Parada - Segurança',CURRENT_TIMESTAMP)".format(r))    
            db.commit()
            
    elif state["seguranca"][0] == "Parada"and dataValues["inputs"]["emergencia"] == 1:
        #print('c')
        if dataValues["inputs"]["restart"] == 0 and status_maq==0:
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
            
            cursor = db.cursor()
            cursor.execute("SELECT * FROM orders WHERE num_order = (SELECT max(num_order) FROM orders)")
            result = cursor.fetchall()
            r = result[0][0]
            cursor.execute("INSERT INTO alarms (num_order,description,timestamp) VALUES ({0},'Maquina Ligada - Segurança',CURRENT_TIMESTAMP)".format(r))    
            db.commit()
            
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
        
        cursor = db.cursor()       
        cursor.execute("UPDATE machine SET temperature = {} WHERE id = 1".format(temperatura))
        db.commit()

        #print("entra desli m1")
        if dataValues["inputs"]["s3"] == 0 and temperatura <= 30:  # olhar testes valor da temperatura 
            newstate["esteiras"] = ["Aciona atuador", True]
            
            cursor = db.cursor()
            cursor.execute("SELECT * FROM orders WHERE num_order = (SELECT max(num_order) FROM orders)")
            result = cursor.fetchall()
            r = result[0][0]
            cursor.execute("INSERT INTO historyproduction (num_order,temperature,timestamp) VALUES ({0},{1},CURRENT_TIMESTAMP)".format(r,temperatura))
            db.commit()

            
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
            
    # Armazenamento
    if state["esteira3"][0] == "Espera":
        #print("entra aqui ali 2 espera")
        if dataValues["inputs"]["s6"] == 0 and dataValues["local"]["num_peca"] <= 3:
            newstate["esteira3"] = ["Atuador Direita", True]
        
        elif dataValues["inputs"]["s6"] == 0 and dataValues["local"]["num_peca"] >= 4:
            newstate["esteira3"] = ["Atuador Esquerda", True]
            
        elif dataValues["local"]["nivel_elevador"] == 0 and dataValues["inputs"]["s7"] == 1:
            newstate["esteira3"] = ["Incremento elevador", True]

    elif state["esteira3"][0] == "Atuador Direita":
        if dataValues["local"]["num_peca"] >= 6:
            newstate["esteira3"] = ["Incremento elevador", True]

        elif dataValues["local"]["num_peca"] < 6 and dataValues["inputs"]["s6"] == 1 and dataValues["inputs"]["at3direita"] == 0:
            newstate["esteira3"] = ["Espera", True]

    elif state["esteira3"][0] == "Atuador Esquerda":
        if dataValues["local"]["num_peca"] >= 6:
            newstate["esteira3"] = ["Incremento elevador", True]

        elif dataValues["local"]["num_peca"] < 6 and dataValues["inputs"]["s6"] == 1 and dataValues["inputs"]["at3esquerda"] == 0:
            newstate["esteira3"] = ["Espera", True] 

    elif state["esteira3"][0] == "Incremento elevador":
        if dataValues["local"]["nivel_elevador"] >= 5 or dataValues["local"]["nivel_elevador"] == 0 and dataValues["inputs"]["s7"] == 1:
            print('aquiiii')
            newstate["esteira3"] = ["Desce elevador", True]
        
        elif dataValues["local"]["nivel_elevador"] < 5:
            newstate["esteira3"] = ["Sobe elevador", True]
            gira_motor_horario(2)
            print('elevador subiu')

            
    elif state["esteira3"][0] == "Sobe elevador":
            newstate["esteira3"] = ["Espera", True]
         
    elif state["esteira3"][0] == "Desce elevador":
        GPIO.output(16, GPIO.LOW) # Turn on enable
        GPIO.output(22, GPIO.LOW) # Sentido antihorario
        for x in range(5):
            GPIO.output(12, GPIO.LOW) # Turn on enable
            time.sleep(0.001) 
            GPIO.output(12, GPIO.HIGH) # Sentido
            time.sleep(0.001)
            x=x+1
        GPIO.output(16, GPIO.HIGH) # Turn on enable
        #print('elevador desceu')
        if dataValues["inputs"]["s7"] == 0:
            newstate["esteira3"] = ["Espera", True]
   
    return newstate

    
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


        if state["esteiras"][0] == "Aciona atuador":
            dataValues["outputs"]["esteira1"] = 0
            dataValues["outputs"]["esteira2"] = 0
            pwm.set_pwm(1, 0, 600)
            time.sleep(2)
            pwm.set_pwm(1, 0, 100)     
            
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
            dataValues["local"]["stop"] = 0
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
            dataValues["local"]["stop"] = 0
            
        
    if state["esteira3"][1]:
        if state["esteira3"][0] == "Espera":
            dataValues["outputs"]["m3"] = 1
            dataValues["local"]["num_peca"] = dataValues["local"]["num_peca"] + 1
            GPIO.output(16, GPIO.HIGH) # Turn off enable
            #num_peca = num_peca + 1

        if state["esteira3"][0] == "Atuador Direita":
            pwm.set_pwm(0, 0, 600)
            time.sleep(1)

        if state["esteira3"][0] == "Incremento elevador":
            dataValues["outputs"]["m3"] = 0

        if state["esteira3"][0] == "Atuador Esquerda":
            print('to aqui')
            pwm.set_pwm(0, 0, 200)
            time.sleep(1)
            
        if state["esteira3"][0] == "Sobe elevador":
            dataValues["local"]["num_peca"] = 0
            dataValues["local"]["nivel_elevador"] = dataValues["local"]["nivel_elevador"]+1
            
        if state["esteira3"][0] == "Desce elevador":
            dataValues["local"]["num_peca"] = 0
            dataValues["local"]["nivel_elevador"] = 0

        if state["esteira3"][0] == "Parada":
            dataValues["outputs"]["m3"] = 0
            GPIO.output(16, GPIO.HIGH) # Turn off enable
            
   
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
               '"local": {"stop": 0,"nivel_elevador": 0, "num_peca": 0, "qtdPlacas": "", "qtdTampas": "", "qtdPlacasProntas": "", "nivelElevadorMaxElevador": ""},' \
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
    # para testar dataValues["state"]["elevador"]=["Subir Nível",True] #Linha pra teste no computador. Pode 
    # trocar o valor para testar 
    JSdataValues = json.dumps(dataValues)
    #print ("EM")
    #print(dataValues["inputs"]["emergencia"])
    #print ("RT")
    #print(dataValues["inputs"]["restart"])
    #dataValues["local"]["qtdPlacas"]== 52
    #dataValues["local"]["tempInoculacao"]= 29
    
    