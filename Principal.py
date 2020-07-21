import tfmini
import acelerometro
import lora
import wifi
import memoria
import time
import math
from machine import Pin

class Principal():
    # Las keys del dispositivo para lorawan
    dev = '019b5d32'
    nwk = '948d551dc8122ec00d0a39ebf4a21280'
    app = '16f9bcb07a7b9d7052d038eaa6b82e9b'


    LIMITE_TECHO = 600
    LIMITE_ACELERACION = 144
    TIEMPO_ENTRE_LECTURAS = 200
    SEGUNDOS_ENTRE_HOLAS_LORA = 300

    insideLedPin = "P21"
    hitLedPin = "P22"

    maximo_aceleracion = 0
    x = 0.0
    y = 0.0
    z = 0.0
    max_x = 0.0
    max_y = 0.0
    max_z = 0.0
    distancia_techo = 0

    insideLed = False
    golpeLed = False
    reset_var = False
    siguienteComprobacionTiempo = 0
    siguienteComprobacionHola = 0

    lenHistorial = 20
    posicionHistorial = 0
    historial = []
    tiempos = []
    i=0
    
    interiorAnterior = True
    golpeAnterior = False

    insidePin=None
    hitPin=None
    acel = None
    loraVar = None
    tfminiVar = None
    wifiVar = None
    
    num = 0

    def __init__(self):
        self.LIMITE_TECHO = memoria.lee_techo()
        self.LIMITE_ACELERACION = memoria.lee_aceleracion()
        self.maximo_aceleracion = 0
        self.insidePin = Pin(self.insideLedPin, mode=Pin.OUT)
        self.hitPin = Pin(self.hitLedPin, mode=Pin.OUT)

        self.golpeLed = memoria.lee_impacto()
        self.wifiVar = wifi.Wifi(self)
        #self.tfminiVar = tfmini.Tfmini()
        self.acel = acelerometro.Acelerometro()
        self.loraVar=lora.Lora(self.dev, self.nwk, self.app)
        


    def loop(self):
        self.wifiVar.setPral(self)
        self.tiempo = time.time() * 1000
        var = self.loraVar.lee()
        if(var != None): print(var)
        (max_accel,self.x,self.y,self.z) = self.acel.lee()
        self.maximo_aceleracion =  max(self.maximo_aceleracion, max_accel)
        if abs(self.max_x)>abs(self.x):
            self.max_x = self.max_x
        else:
            self.max_x = self.x
        if abs(self.max_y)>abs(self.y):
            self.max_y = self.max_y
        else:
            self.max_y = self.y
        if abs(self.max_z)>abs(self.z):
            self.max_z = self.max_z
        else:
            self.max_z = self.z
        if ( self.siguienteComprobacionTiempo <= self.tiempo) :
            self.siguienteComprobacionTiempo = self.tiempo + self.TIEMPO_ENTRE_LECTURAS
            self.distancia_techo = self.tfminiVar.lee()
            self.insideLed = self.distancia_techo < self.LIMITE_TECHO
            if not self.golpeLed:
                if not self.reset_var:
                    if self.maximo_aceleracion > self.LIMITE_ACELERACION:
                        self.golpeLed = True;
                        memoria.escribe_impacto(True)
                else:
                    self.reset_var = False
            else:
                if self.reset_var:
                    self.reset_var = False
                    self.golpeLed = False
                    memoria.escribe_impacto(True)
            self.max_x = 0.0
            self.max_y = 0.0
            self.max_z = 0.0
            self.maximo_aceleracion = 0
    
        (max_accel,self.x,self.y,self.z) = self.acel.lee()
        self.maximo_aceleracion =  max(self.maximo_aceleracion, max_accel)

        if self.maximo_aceleracion > self.LIMITE_ACELERACION:
            self.historico(self.maximo_aceleracion, time.time()*1000)
        
        if ( self.siguienteComprobacionHola <= self.tiempo) :
            self.siguienteComprobacionHola = self.tiempo + self.SEGUNDOS_ENTRE_HOLAS_LORA*1000
            self.enviaSenal(False, 0, 0, 0, 0, latitud = 39.98287491906364, longitud = -0.024847984313964847)

        time.sleep_ms(1)
        

    #Añade un nuevo golpe al histórico
    def historico(self, fuerza, tiempo):
        if self.posicionHistorial>0 and self.tiempos[self.posicionHistorial-1]!=tiempo//100 or self.posicionHistorial<=0:
            if self.posicionHistorial < self.lenHistorial: 
                self.historial.append(fuerza)
                self.tiempos.append(tiempo//100)
                self.posicionHistorial=self.posicionHistorial+1
            else:
                for i in range(self.lenHistorial-1):
                    self.historial[i] = self.historial[i+1]
                    self.tiempos[i] = self.tiempos[i+1]
                
                self.historial[self.lenHistorial-1] = fuerza
                self.tiempos[self.lenHistorial-1] = tiempo
            self.enviaSenal(True, self.max_x, self.max_y, self.max_z, math.sqrt(fuerza), latitud = 39.98287491906364, longitud = -0.024847984313964847)
        
    def enviaSenal(self, golpe, x, y, z, total, latitud, longitud):
        golpeado = "false"
        if golpe: golpeado = "true"

        cadena = '{"contador": %d, "uptime": %d, "golpe": %s, "data": { "x": %f, "y": %f, "z": %f, "total": %f  }, "gnss": { "lat": %f,  "long": %f } }' % (self.num,time.time(), golpeado, x, y, z, total, latitud, longitud)
        self.num = (self.num+1)%1000
        self.loraVar.envia(cadena)

    def enviaPorGolpeOInterior(self, interior, golpe):
        if interior != self.interiorAnterior or golpe != self.golpeAnterior:
            dato = "{\"posicion\":"
            if interior:
                dato = dato + "\"interior\",\"golpe\":"
            else:
                dato = dato + "\"exterior\",\"golpe\":"
            if golpe:
                dato = dato + "\"verdadero\"}"
            else:
                dato = dato + "\"falso\"}"
            self.loraVar.envia(dato)
        self.interiorAnterior = interior
        self.golpeAnterior = golpe
    
#principal = Principal()
#while True:
#    principal.loop()
