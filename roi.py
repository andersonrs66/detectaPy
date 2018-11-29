__doc__ = '''
DetectaPy > roi.py
Author: Anderson Rodriguez <anderson_f_r@hotmail.com>

primeira segmentacao da imagem

modulo detecta face e olhos
'''

#Import the OpenCV and dlib libraries
import cv2
import numpy as np
import dlib


#Initialize a face cascade using the frontal face haar cascade provided with
#the OpenCV library

class Detect:
    def __init__(self):
        self.faceCascade = cv2.CascadeClassifier('recursos/haarcascade_frontalface_default.xml')
        self.eyeCascade = cv2.CascadeClassifier('recursos/haarcascade_eye.xml')
        self.trackingFace = 0
        self.trackingEye = 0
        self.rectangleColor = (0,165,255)
        self.faceTracker = dlib.correlation_tracker()
        self.eyeTracker = dlib.correlation_tracker()
        self.frameAtual = {}
        self.frameAnterior= {}
        self.lastTrackPos = (0, 0, 0, 0)
        self.lastEyeTrackPos = (0, 0, 0, 0)

    def detectar(self, **frame):
        # o frame recebido tem que ser um dict com
        # a imagem 'original' e 'gray'
        self.frameAtual = frame.copy()
        if not self.trackingFace:
            self.detectFace()
        else:
            self.trackFace()
        if not self.trackingEye:
            self.detectEye()
        else:
            self.trackEye()
        if 'roi_face' in self.frameAtual.keys():
            self.frameAtual['roi_face'] = self.image_resize(self.frameAtual['roi_face'], width = 250)
        if 'roi_eyes' in self.frameAtual.keys():
            self.frameAtual['roi_eyes'] = self.image_resize(self.frameAtual['roi_eyes'], width = 210)
        if 'roi_eye' in self.frameAtual.keys():
            self.frameAtual['roi_eye'] = self.image_resize(self.frameAtual['roi_eye'], width = 200, height = 200)
        return self.frameAtual


    def detectFace(self):
        # detecta a face pelo metodo viola & jones
        # e se encontrar uma face, comeca a ratrear
        # com 'dlib.correlation_tracker'
        faces = self.faceCascade.detectMultiScale(self.frameAtual['gray'], 1.3, 5)
        maxArea = 0
        x = 0
        y = 0
        w = 0
        h = 0
        for (_x,_y,_w,_h) in faces:
            if  _w*_h > maxArea:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
                maxArea = w*h
            if maxArea > 0 :
                #Initialize the tracker
                self.lastTrackPos = (x, y, w, h)
                self.faceTracker.start_track(self.frameAtual['gray'], dlib.rectangle( x, y, x+w, y+h))
                #Set the indicator variable such that we know the
                #tracker is tracking a region in the image
                self.trackingFace = 1

    def trackFace(self):
        # rastreia a face com o metodo presente na biblioteca dlib
        # creditos:
        # https://github.com/gdiepen/face-recognition/blob/master/face%20detect%20and%20track/demo%20-%20detect%20and%20track.py
        if self.trackingFace:
            trackingQuality = self.faceTracker.update(self.frameAtual['gray'])
            #print trackingQuality
            if trackingQuality >= 10:
                tracked_position =  self.faceTracker.get_position()
                #print tracked_position
                t_x = int(tracked_position.left())
                t_y = int(tracked_position.top())
                t_w = int(tracked_position.width())
                t_h = int(tracked_position.height())
                if (t_x < 10) or (t_y < 10):
                    self.trackingFace = 0
                    self.trackingEye = 0
                    try:
                        del self.frameAtual['roi_eyes']
                        del self.frameAtual['roi_eye']
                        del self.frameAtual['roi_face']
                        print self.frameAtual.keys()
                    except KeyError:
                        pass
                    return
                limiar = 25
                if abs(t_x - self.lastTrackPos[0]) <= limiar:
                    t_x = self.lastTrackPos[0]
                if abs(t_y - self.lastTrackPos[1]) <= limiar:
                    t_y = self.lastTrackPos[1]
                if abs(t_w - self.lastTrackPos[2]) <= limiar:
                    t_w = self.lastTrackPos[2]
                if abs(t_h - self.lastTrackPos[3]) <= limiar:
                    t_h = self.lastTrackPos[3]
                #roi da face
                cv2.rectangle(self.frameAtual['original'], (t_x, t_y), (t_x+t_w , t_y+t_h), (255,0,0) ,2)
                face = self.frameAtual['gray'].copy()
                #self.frameAtual['roi_face'] = face[t_y:t_y+t_h, t_x:t_x+t_w]
                self.frameAtual['roi_face'] = face[int(t_y+(t_h/7)):int(t_y+t_h-(t_h/10)), int(t_x+(t_w/9)):int(t_x+t_w-(t_w/9))]
                #roi_frame = (t_x, t_y, t_w, t_h)
                #roi dos olhos
                cv2.rectangle(self.frameAtual['original'], ( int(t_x+(t_w/9)), int(t_y+(t_h/7)) ),
                                                        ( int(t_x+t_w-(t_w/9)) , int(t_y+t_h/2)), (255,0,0) ,2)
                self.frameAtual['roi_eyes'] = self.frameAtual['gray'][ int(t_y+(t_h/7)):int(t_y+(t_h*0.6)), int(t_x+(t_w/9)):int(t_x+t_w-(t_w/9))]
                #self.frameAtual['roi_eyes'] = self.frameAtual['gray'][t_y+(t_h/7):t_y+t_h-(t_h/10), t_x+(t_w/9):t_x+t_w-(t_w/9)]

            else:
                #If the quality of the tracking update is not
                #sufficient (e.g. the tracked region moved out of the
                #screen) we stop the tracking of the face and in the
                #next loop we will find the largest face in the image
                #again
                self.trackingFace = 0
                self.trackingEye = 0
                try:
                    del self.frameAtual['roi_eyes']
                    del self.frameAtual['roi_eye']
                    del self.frameAtual['roi_face']
                    print self.frameAtual.keys()
                except KeyError:
                    pass


    def detectEye(self):
        # detecta olhos pelo metodo viola & jones
        # e se encontrar um olho, comeca a ratrear
        if 'roi_eyes' not in self.frameAtual.keys():
            return
        eyes = self.eyeCascade.detectMultiScale(self.frameAtual['roi_eyes'], 1.3, 5)
        maxArea = 0
        x = 0
        y = 0
        w = 0
        h = 0
        for (_x,_y,_w,_h) in eyes:
            if  _w*_h > maxArea:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)
                maxArea = w*h
            if maxArea > 0 :
                #Initialize the tracker
                self.eyeTracker.start_track(self.frameAtual['roi_eyes'], dlib.rectangle( x, y, x+w, y+h))
                self.lastEyeTrackPos = (x, y, w, h)
                #Set the indicator variable such that we know the
                #tracker is tracking a region in the image
                self.trackingEye = 1

    def trackEye(self):
        # rastreia a camera com o metodo presente na biblioteca dlib
        # creditos:
        # https://github.com/gdiepen/face-recognition/blob/master/face%20detect%20and%20track/demo%20-%20detect%20and%20track.py
        if self.trackingEye:
            trackingQuality = self.eyeTracker.update(self.frameAtual['roi_eyes'])
            #print 'eye' , trackingQuality
            if trackingQuality >= 5.5:
                tracked_position =  self.eyeTracker.get_position()
                t_x = int(tracked_position.left())
                t_y = int(tracked_position.top())
                t_w = int(tracked_position.width())
                t_h = int(tracked_position.height())
                #tentativa de evitar o flicker
                limiar = 10
                if abs(t_x - self.lastEyeTrackPos[0]) <= limiar:
                    t_x = self.lastEyeTrackPos[0]
                if abs(t_y - self.lastEyeTrackPos[1]) <= limiar:
                    t_y = self.lastEyeTrackPos[1]
                if abs(t_w - self.lastEyeTrackPos[2]) <= limiar:
                    t_w = self.lastEyeTrackPos[2]
                if abs(t_h - self.lastEyeTrackPos[3]) <= limiar:
                    t_h = self.lastEyeTrackPos[3]
                #roi da face
                cv2.rectangle(self.frameAtual['roi_eyes'], (t_x, t_y), (t_x+t_w , t_y+t_h), (255,0,0) ,2)
                roi_frame = (t_x, t_y, t_w, t_h)
                #roi dos olhos
                self.frameAtual['roi_eye'] = self.frameAtual['roi_eyes'][t_y:t_y+t_h, t_x:t_x+t_w]
                # testando aqui
                blur, self.frameAtual['roi_eye'] = cv2.threshold(self.frameAtual['roi_eye'],50,220,cv2.THRESH_BINARY_INV)
                kernel = np.ones((5,5),np.uint8)
                self.frameAtual['roi_eye'] = cv2.GaussianBlur(self.frameAtual['roi_eye'],(7,7),0)
                #self.frameAtual['roi_eye'] = cv2.dilate(self.frameAtual['roi_eye'],kernel,iterations = 1)
                #self.frameAtual['roi_eye'] = cv2.erode(self.frameAtual['roi_eye'],kernel,iterations = 2)

            else:
                #If the quality of the tracking update is not
                #sufficient (e.g. the tracked region moved out of the
                #screen) we stop the tracking of the face and in the
                #next loop we will find the largest face in the image
                #again
                self.trackingEye = 0
                try:
                    del self.frameAtual['roi_eye']
                    print self.frameAtual.keys()
                except KeyError:
                    pass

    def image_resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        dim = None
        (h, w) = image.shape[:2]

        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image

        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)

        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # resize the image
        resized = cv2.resize(image, dim, interpolation = inter)

        # return the resized image
        return resized
if __name__ == '__main__':
    pass
