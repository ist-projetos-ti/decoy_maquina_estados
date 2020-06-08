def setup():
    busAddress={ #Lista os barramentos utilizados, separando em input e output
        "outputs":{
            0x20:["","","","","","","",""]
        },
        "inputs":{
            0x24:["","","","","","","",""]
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
            "mv1":["","","alimentacao"],  #0x20 endereco do ci dos Leds / 0 é posicao do Led
            "mr1":["","","alimentacao"],
            "bp":["","","alimentacao"],
            "fim_placas":["","","alimentacao"],

            #Inoculacao
            "at1":[0x20,0,"inoculacao"],
            "bi":[0x20,1,"inoculacao"],

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
            "s1":["","","alimentacao"],    #0x24 endereco do ci dos botões / 0 é posicao do botao
            "s2":["","","alimentacao"],
            "bpRetorno":["","","alimentacao"],

            #Inoculacao
            "temp":[0x24,0,"inoculacao"],
            "biRetorno":[0x24,1,"inoculacao"],
            "s3":[0x24,2,"inoculacao"],
            "at1open":[0x24,3,"inoculacao"],
            "at1close":[0x24,4,"inoculacao"],

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