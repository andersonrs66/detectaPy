import numpy as np
import cv2
#from matplotlib import pyplot as plt

class FaceRecognition:
    def __init__(self):
        # cria SURF and detect/compute
        self.surf = cv2.xfeatures2d.SURF_create(500)

    def correct_gamma(self, img, correction):
        img = img/255.0
        img = cv2.pow(img, correction)
        return np.uint8(img*255)

    def process_image(self, imag):
        gr = self.correct_gamma(imag, 0.3)
        gr = cv2.equalizeHist(gr)
        return gr

    def preprocessa(self, frame):
        # preprocessador da imagem
        #normaliza histograma com clahe
        clahe = cv2.createCLAHE(clipLimit=1.7, tileGridSize=(5,5))
        frame = self.process_image(frame)
        #frame = clahe.apply(frame)
        #frame = cv2.blur(frame,(3,3)) #blur nao sei se vai ainda

        return frame

    def recognite(self, queryImage, trainingImage):
        '''
        funcao que realiza o reconhecimento facial
        entrada:
            queryImage: imagem padrao
            trainingImage: imagem a ser testada
        saida: dicionario com os campos:
            'querykp' = (int) quant de keypoints da imagem base
            'trainKp' = (int) quant de keypoints da imagem teste
            'matchedKp' = (int) quant de keypoints correlacionados
            'resultImage' = np.array = imagem resultado com os keypoints
        '''
        retorno={}
        queryImage = self.preprocessa(queryImage)
        trainingImage = self.preprocessa(trainingImage)
        kp1, des1 = self.surf.detectAndCompute(queryImage, None)
        #print 'query image possui: ', len(kp1)
        retorno['queryKp'] = len(kp1)
        kp2, des2 = self.surf.detectAndCompute(trainingImage, None)
        #print 'training image possui: ', len(kp2)
        retorno['trainKp'] = len(kp2)

        # FLANN matcher parameters
        FLANN_INDEX_KDTREE = 0
        indexParams = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        searchParams = dict(checks=50) # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(indexParams,searchParams)
        matches = flann.knnMatch(des1,des2,k=2)
        pontos = 0
        # #teste com BFMATHCER
        # # create BFMatcher object
        # bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # # Match descriptors.
        # matches = bf.match(des1,des2)
        # # Sort them in the order of their distance.
        # matches = sorted(matches, key = lambda x:x.distance)
        # # Draw first 10 matches.
        # img3 = cv2.drawMatches(queryImage,kp1,trainingImage,kp2,matches[:10], flags=2)
        # prepare an empty mask to draw good matches
        matchesMask = [[0,0] for i in xrange(len(matches))]

        # David G. Lowe's ratio test, populate the mask
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.7*n.distance:
                matchesMask[i]=[1,0]
                pontos += 1

        retorno['matchedKp'] = pontos
        #print 'pontos encontrados: ', pontos
        drawParams = dict(matchColor = (0,255,0),
                            singlePointColor = (255,0,0),
                            matchesMask = matchesMask,
                            flags = 0)

        resultImage = cv2.drawMatchesKnn(queryImage,kp1,trainingImage,kp2,matches,
                                        None,**drawParams)
        retorno['resultImage'] = resultImage
        return retorno

def teste():
    #path1 = 'recursos/amostras/1.png'
    path1 = 'saida/5.png'
    print 'base: ', path1
    for x in range(1, 400):
        path2 = 'saida/'
        padrao = cv2.imread(path1, 0)
        path2 += '{}.png'.format(x)
        teste = cv2.imread(path2, 0)
        faceRec = FaceRecognition()
        result = faceRec.recognite(padrao, teste)
        print ' {} {} {} {}'.format(x,result['queryKp'],result['trainKp'], result['matchedKp'])
        cv2.imshow('resultado', result['resultImage'])
        cv2.waitKey(0)


if __name__ == '__main__':
    teste()
    # path1 = 'recursos/amostras/1.png'
    # path2 = 'recursos/amostras/'
    #
    # padrao = cv2.imread(path1, 0)
    # teste = cv2.imread(path2, 0)
    # faceRec = FaceRecognition()
    # result = faceRec.recognite(padrao, teste)
    # print '{}, {}, {}'.format(result['queryKp'],result['trainKp'], result['matchedKp'])
    # #cv2.imshow('resultado', result['resultImage'])
    # #cv2.waitKey(0)
