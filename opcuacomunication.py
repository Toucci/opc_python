"""Importando as bibliotecas que serão utilizadas"""
#importar opencv
import datetime
import cv2
#Biblioteca para realizar a leitura do código de barras utilizando uma webcam
from pyzbar.pyzbar import decode
#Importando as bibliotecas para realizar as conexões de servidores. 
import sys
from opcua import Client
from opcua import ua

#endereço do CLP URL
url = "opc.tcp://192.168.15.12:4840"

#Tenta encontrar a conexão com o endereço opc, caso contrário retorna erro e não realiza a conexão
try:
    client = Client(url)
    client.session_timeout = 30000

    client.connect()
    print("Conectado ao servidor")
except Exception as err:
    print("err",err)
    sys.exit(1)
    



#capturar video

captura = cv2.VideoCapture(0) #para ler camera

#criar loop

while True:

    #recuperar os frames
    ret,frame = captura.read() #ret e frames são variáveis que criamos - Ret é bool e retorna true caso seja possível ler alguma coisa da fonte de video, já a var frame é para armazenar a imagem
    
    
   
    #Definindo a janela da webcam, com cores, sizes e a importação da biblioteca openCV para visualização.

    frame = cv2.resize(frame,(640,480))
    frame =  cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    ret2,thres = cv2.threshold(frame,100,255,cv2.THRESH_BINARY)
    

    #Utiliza a função da biblioteca pyzbar para realizar a detectação do QR.
    detectedBarcodes = decode(thres) 
    
    if not detectedBarcodes: 
        print("código não detectado ou corrompido") 
        #speed = client.get_node("ns=4;s=|var|CODESYS Control Win V3.Application.OPC.speed").set_value(ua.Variant(0 , ua.VariantType.UInt16))
    else:
        for barcode in detectedBarcodes:   
            #(x, y, w, h) = barcode.rect
            #cv2.rectangle(frame , (x, y),(x + w, y + h), (255, 0, 0), 2) 

            if barcode.data!="": 

                print(barcode.data) 
                
                #print(barcode.type)

                
                #Realizando a leitura dos QR'S e seus títulos. Aqui lemos a variável importada do software Machine Expert e ativamos a funcionalidade.
                if str(barcode.data) == "b'TRUE'" :
                    enable = client.get_node("ns=2;s=Application.OPC.enable").set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
                    datavalue = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                    #enable.set_datavalue(datavalue)
                    print("ligar motor")
                    
                elif str(barcode.data) == "b'FALSE'":
                    disable = client.get_node("ns=2;s=Application.OPC.enable").set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
                    datavalue = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                    #disable.set_datavalue(datavalue)
                    print("desligar motor")

                elif str(barcode.data) == "b'HORARIO'":
                    fwd = client.get_node("ns=2;s=Application.OPC.fwd").set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
                    datavalue = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                    rev = client.get_node("ns=2;s=Application.OPC.rev").set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
                    datavalue = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                    #fwd.set_datavalue(datavalue)
                    print("reverte ok")

                elif str(barcode.data) == "b'REVERTE'":
                    rev = client.get_node("ns=2;s=Application.OPC.rev").set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
                    datavalue = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                    fwd = client.get_node("ns=2;s=Application.OPC.fwd").set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
                    datavalue = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))
                    #rev.set_datavalue(datavalue)
                    print("HORARIO OK")
                    
                elif str(barcode.data) == "b'RESET'":
                    reset = client.get_node("ns=2;s=Application.OPC.reset").set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
                    datavalue = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                    #reset.set_datavalue(datavalue)
                    print("reset")   
                
                else:
                    velocidade = int(barcode.data)
                    speed = client.get_node("ns=2;s=Application.OPC.speed")
                    datavalue = ua.DataValue(ua.Variant(velocidade, ua.VariantType.Int16))
                    speed.set_data_value(datavalue)
                    print ("velocidade gravada com sucesso")
            
                


    #Retorna as janelas de visualização da webcam.
    cv2.imshow("frame",frame)
    cv2.imshow("binaria",thres)


   # frame = []

    #guarda o botão que foi apertado na variavel key
    key = cv2.waitKey(300) #se usar 0 aguarda cada clique em qualquer tecla, qualquer outro numero vira delay em ms

    #Se pressionar a tecla Q o programa será finalizado.
    if key == ord("q"):
        break
#finally:
client.disconnect()
print("servidor desconectado")    


#fecha todos os popups que estiverem abertos pelo python
cv2.destroyAllWindows()
