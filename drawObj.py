import numpy as np
import cv2


class Alvo:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.r = 40
        self.cor = (0,255,255)
        self.corMove = (100,100,100)

    def show(self, frame):
        #pega tamanho do frame e se
        #coord nao existir, fixa no canto
        height, width = frame.shape[:2]
        if self.x > width:
            self.x = width
        if self.y > height:
            self.y = height
        #desenha circulo com cruz no centro
        cv2.circle(frame,(self.x, self.y), self.r, self.cor, thickness=6)
        cv2.line(frame,(self.x+(self.r/2),self.y),(self.x-(self.r/2),self.y),self.cor,thickness=5)
        cv2.line(frame,(self.x,self.y+(self.r/2)),(self.x,self.y-(self.r/2)),self.cor,thickness=5)

    def movimentaAleatorio(self, frame):
        #seta valores aleatorios para x, y e movimenta
        import random
        height, width = frame.shape[:2]
        x = random.randint(100, (width-40))
        y = random.randint(100, (height-40))
        ret = self.movimenta(frame, x, y)
        return ret

    def movimenta(self, frame, x, y):
        if abs(x - self.x) < 60:
            x = self.x
        if abs(y - self.y) < 60:
            y = self.y
        #desenha o movimento
        cv2.line(frame,(x,y),(self.x,self.y),self.corMove,thickness=5)

        #guarda movimento
        movX = self.x - x
        movY = self.y - y

        #salva nova coordenada
        self.x = x
        self.y = y
        self.show(frame)

        if movX == 0:
            movimento = 'PARADO'
            if movY < 0:
                movimento = 'ABAIXO'
            if movY > 0:
                movimento = 'ACIMA'
            return movimento

        if movX > 0:
            movimento = 'ESQUERDA'
            if movY < 0:
                movimento = 'INF_ESQUERDO'
            if movY > 0:
                movimento = 'SUP_ESQUERDO'
            return movimento

        if movX < 0:
            movimento = 'DIREITA'
            if movY < 0:
                movimento = 'INF_DIREITO'
            if movY > 0:
                movimento = 'SUP_DIREITO'
            return movimento


# Create a black image
if __name__ == '__main__':

    img = np.zeros((512,512,3), np.uint8)
    alvo = Alvo(250,250)
    alvo.show(img)
    cv2.imshow('Log-in', img)
    cv2.waitKey(0)

    while True:
        img = np.zeros((512,512,3), np.uint8)
        ret = alvo.movimentaAleatorio(img)
        print ret
        cv2.imshow('Log-in', img)
        key = cv2.waitKey(0)
        if key & 0xFF == ord('q'):
            break
