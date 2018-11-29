import cv2
import numpy as np
import roi
from camera import Camera
from face_recognition import FaceRecognition
import drawObj
import time
import fluxo


__doc__ = '''
o dicionario frame composto por:
    frame[
    'original'
    'gray'
    'roi_face' < marca no original
    'roi_olhos' < marca no original
    ]
    cam:(pronto)
        recebe nada
        responde 'original' e 'gray'

    facetrack e eyetrack:
        recebe 'original' e 'gray'
        responde 'original'.(com face marcada), 'gray', 'roi_face'
        responde 'oringinal'.(com olhos marcados), 'gray', 'roi_face', 'roi_eye'

    vitalidade:
        recebe: 'original', 'roi_eye'
        responde 'original'.(com alvo), 'movimento_alvo', 'movimento_olhos'

    recoon:
        recebe: 'roi_face'

'''


if __name__ == '__main__':

    #classe que cria os alvos
    tempo = time.time()
    alvo = drawObj.Alvo()
    # conta quadros para desenhar novo alvo
    alvoQuadrosCount = 0
    # classe detecta fluxo optico
    fluxo = fluxo.Fluxo()
    # guarda estado atual da aplicacao
    estado = 0
    salvo = 'user.png'
    user1 = cv2.imread(salvo, 0)
    cam = Camera(1)
    faceTracker = roi.Detect()
    recon = FaceRecognition()
    contador = 0
    while True:
        #print 'estdo = ', estado
        # captura frame
        frame = cam.preprocessa()
        # detecta faces
        frame = faceTracker.detectar(**frame)
        #if 'gray' in frame.keys():
        #    cv2.imshow('gray', frame['gray'])
        #if 'roi_face' in frame.keys():
        #    cv2.imshow('roi_face', frame['roi_face'])
        if 'roi_eyes' in frame.keys():
            #cv2.imshow('roi_eyes', frame['roi_eyes'])
            estado = 1
        key = cv2.waitKey(10)
        if key & 0xFF == ord('q'):
            #sair
            break
        if key & 0xFF == ord('2'):
            # "cadastrar" face
            if 'roi_face' in frame.keys():
                cv2.imwrite('user.png', frame['roi_face'])
                user1 = cv2.imread(salvo, 0)
                print 'usuario cadastrado'
        if key & 0xFF == ord('1'):
            # tentar login
            if 'roi_face' in frame.keys():
                result = recon.recognite(user1, frame['roi_face'])
                print '{} {} {}'.format(result['queryKp'],result['trainKp'], result['matchedKp'])
                cv2.imshow('resultado', result['resultImage'])
        if estado == 1:
            if 'roi_eye' in frame.keys():
                alvo.show(frame['original'])
                saida = 'saida/{}.png'.format(contador)
                contador += 1
                cv2.imshow('roi eyes', frame['roi_eyes'])
                cv2.imshow('roi eye', frame['roi_eye'])
                #cv2.imwrite(saida, frame['roi_eye'])
                estado = 2
            else:
                estado = 0
        if estado == 2:
            if 'roi_eye' in frame.keys():
                frame['fluxoOlho'] = fluxo.trata(frame['roi_eye'])
                if 'roi_eye' in frame.keys() and alvoQuadrosCount >= 15:
                    frame['movimentoAlvo'] = alvo.movimentaAleatorio(frame['original'])
                    retorno = fluxo.placar(frame['movimentoAlvo'])
                    if retorno == 'vivo':
                        result = recon.recognite(user1, frame['roi_face'])
                        print '{} {} {}'.format(result['queryKp'],result['trainKp'], result['matchedKp'])
                        cv2.imshow('resultado', result['resultImage'])
                        if result['matchedKp'] >= 15:
                            demorou = time.time() - tempo
                            print 'usuario autenticado com sucesso com {} segundos'.format(demorou)
                            estado = 4
                    else:
                        print retorno
                    #print 'alvo = {} user = {}'.format(frame['movimentoAlvo'], frame['fluxoOlho'])
                    alvoQuadrosCount = 0
                else:
                    alvoQuadrosCount += 1
                    #print 'user = {}'.format(frame['fluxoOlho'])
        cv2.imshow('teste01', frame['original'])
        if estado == 4:
            cv2.waitKey(0)
            break

    cv2.destroyAllWindows()
