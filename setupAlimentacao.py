def setup():
    busAddress={ #Lista os barramentos utilizados, separando em input e output
        "outputs":{
            0x22:["","","","","","","",""],
            0x23:["","","","","","","",""]
        },
        "inputs":{
            0x26:["","","","","","","",""],
            0x27:["","","","","","","",""]
        }
    }
    dataAddress={ #Identifica em qual barramento e posicao está cada IO
        "outputs":{
            #Seguranca
            "e1":[0x23, 6,"seguranca"],
            #"e2":["","","seguranca"],
            #"e3":["","","seguranca"],
            #"luz":["","","seguranca"],
            #"ar":["","","seguranca"],
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
            "m3":[,,"esteira3"],
            #C
            #B
            #Função atuadores (direita e esquerda)
            
            #Armazenamento
            "at3":["","","armazenamento"],
            "me":["","","armazenamento"],
            "fim_elevador":["","","armazenamento"]
            },
        
        "inputs":{
            #Seguranca
            "sp1":["","","seguranca"],
            "sp2":["","","seguranca"],
            "emergencia":[0x27, 6,"seguranca"],
            "restart":[0x27, 7,"seguranca"],
            
            #Alimentacao
            "s1":[0x26,0,"alimentacao"],   
            "bpRetorno":[0x26,2,"alimentacao"],
            
            #Esteira 1 e 2
            "s2":[0x26,1,"esteiras"],
            "s3":[0x26,3,"esteiras"],
            #"s4":[0x27,6,"esteiras"],
            "at1open":[0x26,6,"esteiras"],
            #"at1close":["","","inoculacao"],
            
            #alimentacao2
            "s4":[0x27,1,"alimentacao2"],
            "s5":[0x26,7,"alimentacao2"],
            #"at2open":["","","alimentacao2"],
            #"at2close":["","","alimentacao2"],

            #Esteira3
            "s6":[,,"esteira3"],
            "at3direita":["","","esteira3"],
            "at3esquerda":["","","esteira3"],
            
            #Armazenamento
            "se":["","","armazenamento"],
            "at3direita":["","","armazenamento"],
            "at3esquerda":["","","armazenamento"]
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
        "armazenamento":[]
    }

    #configurando stateBusID, distribuindo os busID nos states
    for ioName, address in dataAddress["outputs"].items():
        if address[0] not in stateBusID[address[2]]:
            stateBusID[address[2]]+=[address[0]]

    return busAddress, dataAddress, stateBusID