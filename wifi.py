from network import WLAN
from microWebSrv.microWebSrv import MicroWebSrv
import json
import memoria
import time

# ssid: 720tec-iot pass: ioniPRim65!
class Wifi():
    my_ssid = None
    my_pass = None
    mws = None
    wlan = None
    principal = None

    def __init__(self, pral):
        self.my_ssid = "720tec-iot"
        self.my_pass = "ioniPRim65!"
        self.mws = MicroWebSrv()
        self.wlan = WLAN()
        self._inicializa()
        self.setPral(pral)

    #Añade una copia del programa principal para recoger lod datos
    def setPral(self, pral):
        self.principal = pral

    #Crea un json a partir de los datos de principal para enviarlos al cliente
    def _jsonData(self):
        cadena ='{"acelerometro":{"x":%f,"y":%f,"z":%f,"modulo_cuadrado":%f,"limite_acel_cuadrado":%f},' %(self.principal.max_x, self.principal.max_y, self.principal.max_z, self.principal.maximo_aceleracion, self.principal.LIMITE_ACELERACION)
        cadena = cadena + '"distancia_techo":%d,"limite_techo":%d,' %(self.principal.distancia_techo, self.principal.LIMITE_TECHO)
        estadoInterior=0
        estadoImpacto =0
        if self.principal.insideLed: estadoInterior = 1
        if self.principal.golpeLed: estadoImpacto = 1
        cadena = cadena + '"estados":{"interior":%d,"impacto":%d},'%(estadoInterior, estadoImpacto)
        cadena = cadena + '"historial":['
        if (self.principal.posicionHistorial>0):
            for i in range(min(self.principal.lenHistorial, self.principal.posicionHistorial)):
                cadena = cadena + '{"fuerza":%f,"tiempo":%d}'%(self.principal.historial[i],(time.time()*10-self.principal.tiempos[i])/10)
                if i<min(self.principal.lenHistorial-1, self.principal.posicionHistorial-1): cadena = cadena + ","
        
        return cadena+"]}"

    #Envia los datos en forma de json
    def _acceptWebSocketCallback(self, webSocket, httpClient) :
        print("WIFI: Actualizando datos")
        httpClient.WriteResponseOk(
            headers = ({'Cache-Control': 'no-cache'}),
            contentType = 'text/event-stream',
            contentCharset = 'UTF-8',
            content = 'data: {0}\n\n'.format(self._jsonData())
            )

    #Recoje json del mensaje enviado desde el cliente. 
    def _handlerJson(self, webSocket, httpClient) :
        print("WIFI: Actualización recibida")
        contenido = webSocket.ReadRequestContent()
        httpClient.WriteResponseJSONOk()
        carga = json.loads(contenido)
        impacto, reset, techo  = [carga[k] for k in sorted(carga.keys())]
        self.principal.reset_var = (int(reset)==1)
        self.principal.LIMITE_ACELERACION = int(impacto)*int(impacto)/4
        self.principal.LIMITE_TECHO = int(techo) * 50
        memoria.escribe_aceleracion(self.principal.LIMITE_ACELERACION)
        memoria.escribe_techo(self.principal.LIMITE_TECHO)


    def _inicializa(self):
        self.wlan.init(mode=WLAN.AP, ssid=self.my_ssid, auth=(WLAN.WPA2, self.my_pass))
        routeHandlers = [ ( "/data", "GET",  self._acceptWebSocketCallback ), ( "/dato", "POST",  self._handlerJson ) ]
        self.mws = MicroWebSrv(routeHandlers=routeHandlers, webPath = "web/")
        self.mws.SetNotFoundPageUrl(url="index.html")
        self.mws.MaxWebSocketRecvLen     = 256
        self.mws.WebSocketThreaded		= True
        self.mws.Start(threaded=True)


