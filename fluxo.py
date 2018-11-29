import numpy as np
import cv2
#import video
import time

help_message = '''
recebe o dicionario frame

tem que devolver o sentido do movimento apenas ou parado se erro
'''
class Fluxo:
    def __init__(self):
        self.score = 0
        self.totalscore = 0
        self.movimentos = []
        self.atual = np.zeros((200,200,3), np.uint8)
        self.atual = cv2.cvtColor(self.atual, cv2.COLOR_BGR2GRAY)
        self.anterior = self.atual.copy()


    def trata(self, frame):
        self.atual = frame
        #flow = cv2.calcOpticalFlowFarneback(self.anterior, self.atual, None, 0.5, 2, 10, 3, 5, 1.2, 0)
        flow = cv2.calcOpticalFlowFarneback(self.anterior, self.atual,
                                            None, pyr_scale=0.5,
                                            levels=1, winsize=15,
                                            iterations=3, poly_n=7,
                                            poly_sigma=1.5, flags=0	)
        self.anterior = self.atual.copy()
        mov = self.draw_flow(flow)
        self.movimentos.append(mov)
        return mov

    def placar(self, alvo):
        self.score = 0
        for passo in range(0, len(self.movimentos)):
            if alvo == self.movimentos[passo]:
                self.score += 1
        self.movimentos = []
        self.totalscore = self.totalscore + self.score
        if self.score == 0:
            self.totalscore = 0
        if self.totalscore >= 8:
            print 'usuario vivo'
            self.totalscore = 0
            return 'vivo'
        return self.score



    def draw_flow(self, flow, step=64):
        h, w = self.atual.shape[:2]
        y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
        fx, fy = flow[y,x].T
        lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
        lines = np.int32(lines + 0.5)
        #print 'linhas: ', lines[4]
        movX = lines[4][0][0] - lines[4][1][0]
        movY = lines[4][0][1] - lines[4][1][1]
        #lines[4][1][1] = 0
        #lines[4][1][0] = 0
        #print 'movX {} e movY {}'.format(movX, movY)

        movimento = ''
        if movX == 0:
            movimento = 'PARADO'
            if movY < 0:
                movimento = 'ABAIXO'
            if movY > 0:
                movimento = 'ACIMA'

        if movX > 0:
            movimento = 'ESQUERDA'
            if movY < 0:
                movimento = 'INF_ESQUERDO'
            if movY > 0:
                movimento = 'SUP_ESQUERDO'

        if movX < 0:
            movimento = 'DIREITA'
            if movY < 0:
                movimento = 'INF_DIREITO'
            if movY > 0:
                movimento = 'SUP_DIREITO'
        #print 'moveu: ', movimento
        return movimento


if __name__ == '__main__':
    import sys
    print help_message

    #cam = cv2.VideoCapture('recursos/eyes.mp4')
    cam = cv2.VideoCapture('saida/test.avi')
    ret, prev = cam.read()
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #cv2.calcOpticalFlowFarneback(prev,next,flow, pyr_scale, levels, winsize, iterations, poly_n, poly_sigma, flags[, flow])
        #flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray

        print len(flow)
        teste = flow[0,0]
        #print len(teste)
        #print len(teste[18])

        cv2.imshow('flow', draw_flow(gray, flow))
        time.sleep(1)


        ch = 0xFF & cv2.waitKey(5)
        if ch == 27:
            break

    cv2.destroyAllWindows()
