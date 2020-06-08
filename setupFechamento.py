def setup():
    busAddress={ #Lista os barramentos utilizados, separando em input e output
        "outputs":{
            0x23:["","","","","","","",""]
        },
        "inputs":{
            0x27:["","","","","","","",""]
        }
    }
    dataAddress={ #Identifica em qual barramento e posicao está cada IO
        "outputs":{
            #Seguranca
            "e1":["","","seguranca"],
            "e2":["","","seguranca"],
            "e3":["","","seguranca"],
            "luz":["","","seguranca"],
            "ar":["","","seguranca"],
            "alarme":["","","seguranca"],
            #Alimentacao
            "mv1":[0x23,0,"alimentacao"],  #0x20 endereco do ci dos Leds / 0 é posicao do Led
            "mr1":[0x23,1,"alimentacao"],
            "bp":[0x23,2,"alimentacao"],
            "fim_placas":[0x23,3,"alimentacao"],
            #Inoculacao
            "at1":["","","inoculacao"],
            "bi":["","","inoculacao"],
            #Fechamento
            "at2":["","","fechamento"],
            "mv2":["","","fechamento"],
            "mr2":["","","fechamento"],
            "fim_tampas":["","","fechamento"],
            #Armazenamento
            "at3":["","","armazenamento"],
            "me":["","","armazenamento"],
            "fim_elevador":["","","armazenamento"]
            },
        "inputs":{
            #Seguranca
            "sp1":["","","seguranca"],
            "sp2":["","","seguranca"],
            "emergencia":["","","seguranca"],
            "restart":["","","seguranca"],
            #Alimentacao
            "s1":[0x27,0,"alimentacao"],    #0x24 endereco do ci dos botões / 0 é posicao do botao
            "s2":[0x27,1,"alimentacao"],
            "bpRetorno":[0x27,2,"alimentacao"],
            #Inoculacao
            "temp":["","","inoculacao"],
            "biRetorno":["","","inoculacao"],
            "s3":["","","inoculacao"],
            "at1open":["","","inoculacao"],
            "at1close":["","","inoculacao"],
            #Fechamento
            "s4":["","","fechamento"],
            "s5":["","","fechamento"],
            "at2open":["","","fechamento"],
            "at2close":["","","fechamento"],
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
        "inoculacao":[],
        "alimentacao":[],
        "fechamento":[],
        "armazenamento":[]
    }

    #configurando stateBusID, distribuindo os busID nos states
    for ioName, address in dataAddress["outputs"].items():
        if address[0] not in stateBusID[address[2]]:
            stateBusID[address[2]]+=[address[0]]

    return busAddress, dataAddress, stateBusID