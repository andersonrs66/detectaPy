__doc__ = '''
DetectaPy > camera.py
Author: Anderson Rodriguez <anderson_f_r@hotmail.com>

classe Camera:
    inicializa a camera, configura, captura frames
    e realiza o preprocessamento

comando para configurar a camera:
#desligar autofocus
uvcdynctrl -v -d video1 --set='Focus, Auto' 0
uvcdynctrl -v -d video0 --set='White Balance Temperature, Auto' 0
uvcdynctrl -v -d video0 --set='White Balance Temperature' 2800
#carregar arquivo de conf
uvcdynctrl -v -d video1 --load=filename
#salvar arquivo de conf
uvcdynctrl -v -d video1 --save=filename
'''

import cv2
import numpy as np

from subprocess import call

class Camera:
    def __init__(self, vidInput=0,):
        #construtor da classe Camera
        #inicializa a camera e algumas variaveis
        self._vidInput = vidInput
        self.cam = cv2.VideoCapture(self._vidInput)
        comando = " -v -d video{} --load=confWebcam.txt".format(vidInput)
        print comando
        call(["uvcdynctrl", comando ])
        print 'iniciando webcam'

    def __del__(self):
        #destrutor da classe Camera
        #ao fechar o programa sempre tem que liberar a camera
        print 'encerrando webcam'
        self.cam.release()

    def configCam(self, width=640, height=480, brightness=4.5,
                    contrast=5.0, saturation=5.0):
        # funcao configura parametros da camera
        self.cam.set(3, width)
        self.cam.set(4, height)
        self.cam.set(10, brightness)
        self.cam.set(11, contrast)
        self.cam.set(12, saturation)

    def preprocessa(self):
        # preprocessador da imagem
        # etapas:
        # converte para gray > equaliza histograma com clahe
        #   retorna dicionario contendo:
        #   'original' = imagem original espelhada
        #   'gray' = imagem em grayscale tratada
        retorno = {}
        self.clahe = cv2.createCLAHE(clipLimit=1.7, tileGridSize=(5,5))
        ret, frame = self.cam.read()
        frame = cv2.flip(frame, 1)
        retorno['original'] = frame.copy()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = self.clahe.apply(frame)
            retorno['gray'] = frame.copy()
            #frame = cv2.blur(frame,(5,5)) #blur nao sei se vai ainda
        return retorno

if __name__ == '__main__':
    cam = Camera(0)
    while True:
        frame = cam.preprocessa()
        cv2.imshow('teste01', frame['original'])
        cv2.imshow('gray', frame['gray'])

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


# if __name__ == '__main__':
#     #obtem um frame preprocessado com a classe Camera
#     #faz o rastreio da face com a classe face_detect
#     cam = Camera(0)
#     faceTracker = roi.FaceDetect()
#     eyeTracker = roi.EyeDetect()
#     while True:
#         img = cam.preprocessa()
#         imagens = faceTracker.seekAndDeploy(img)
#         if imagens:
#             img = imagens[0]
#             olhos = eyeTracker.seekAndDeploy(imagens[1])
#             if olhos:
#                 olhos_rast = vitalidade.erosao(olhos[1])
#                 cv2.imshow('olhos', olhos[0])
#                 cv2.imshow('eyetrack', olhos_rast)
#             cv2.imshow('ROI - face e olhos', img)
#             #cv2.imshow('olhos', imagens[1])
#         else:
#             cv2.imshow('ROI - face e olhos', img)
#         if cv2.waitKey(10) & 0xFF == ord('q'):
#             break
#     cv2.destroyAllWindows()
