import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QLabel, QRadioButton, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import cv2
import numpy as np
import threading
import serial.tools.list_ports
import serial
import time, os

current_directory = os.path.dirname(os.path.abspath(__file__))
face_cascade = cv2.CascadeClassifier('{}/haarcascade.xml'.format(current_directory))
faces = {}
jumlah_file = 5
class ImageThread(QThread):
    change_pixmap_signal = pyqtSignal(list)#np.ndarray)
    change_pixmap_signal2 = pyqtSignal(list)#np.ndarray)
    change_status_signal = pyqtSignal(str)
    change_hasil_signal = pyqtSignal(list)

    def __init__(self, parent=None, mode="video", index=0,  file=None):
        super().__init__(parent)
        self.index = index
        self.running = True
        self.mode = mode
        self.file = file
        self.num = {}
        self.statusProses = {}
        self.name, self.conf, self.pred_time = {}, {}, {}   

    def stop(self):
        self.running = False

    def restart(self):
        self.running = True

    def update_name(self, n, nama, conf, pred_time):
        self.name[n], self.conf[n], self.pred_time[n] = nama, conf, pred_time
        print("OKE===", n, self.name, self.conf)

    def run(self):
        input_file = self.file
        input_mode = self.mode

        cap = []
        for n, i in enumerate(self.index):
            cap.append(cv2.VideoCapture(i))
            self.num[n] = 0
            self.statusProses[n] = False
            self.name[n], self.conf[n], self.pred_time[n] = "", "", ""

        while self.running:
            ret, frame, faces, frame2, cropped_image = {}, {}, {}, {}, {}
            nn = 0
            # try:
            for n, i in enumerate(cap):
                ret[n], frame[n] = cap[n].read()

                if ret[n]:
                    frame2[n] = frame[n].copy()
                    self.change_pixmap_signal.emit([n, frame[n]])
                    self.num[n] += 1
                    gray_image = cv2.cvtColor(frame[n], cv2.COLOR_BGR2GRAY)
                    # faces[n] = face_cascade.detectMultiScale(gray_image, scaleFactor=1.2, minNeighbors=3, minSize=(30, 30))
                    faces[n] = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    
                    for (x, y, w, h) in faces[n]:
                        cropped_image[n] = frame2[n][y-int(0.2*h):y+int(1.2*h), x-int(0.2*w):x+int(1.2*w)]

                    nn += len(faces[n])

                    if len(faces[n])>0:
                        if not self.statusProses[n] and self.num[n]>=20:
                            self.statusProses[n] = True    
                            cv2.imwrite('{}/temp/pic{}.png'.format(current_directory, n), frame[n])
                            self.change_pixmap_signal2.emit([n, cropped_image[n]])
                            print("============================")
                        self.change_status_signal.emit("Terdeteksi")
                        # print("============================", self.index[n])
                    else:
                        self.statusProses[n] = False
                        self.num[n] = 0 
                        # self.change_status_signal.emit("Tidak Terdeteksi")
                        # self.change_hasil_signal.emit("-/-/-/-")
                        self.name[n], self.conf[n], self.pred_time[n] = "", "", ""
                    for (x, y, w, h) in faces[n]:
                        cv2.rectangle(frame[n], (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        try:
                            # print("try1")
                            if self.name[n] != "":
                                cv2.putText(frame[n], "{} {}% {}ms".format(self.name[n], self.conf[n]*100, self.pred_time[n]), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                            # print("try2")
                        except:
                            pass

                    self.change_pixmap_signal.emit([n, frame[n]])
            
            if nn == 0:    
                self.change_status_signal.emit("Tidak Terdeteksi")
                self.change_hasil_signal.emit([n, "-/-/-/-"])
                    # print(self.num)
            # except:
            #     pass
        for n, i in enumerate(cap):
            cap[n].release()

class ImageThread2(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    change_pixmap_signal2 = pyqtSignal(np.ndarray)
    stop_signal = pyqtSignal()

    def __init__(self, parent=None, mode="video", file=None):
        super().__init__(parent)
        self.running = True
        self.mode = mode
        self.file = file
        self.num = 0
        self.statusProses = False
        self.num2 = 0

    def stop(self):
        self.running = False

    def restart(self):
        self.running = True

    def run(self):
        input_file = self.file
        input_mode = self.mode

        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if ret:
                frame2 = frame.copy()
                self.num += 1
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.2, minNeighbors=3, minSize=(30, 30))
                
                for (x, y, w, h) in faces:
                    cropped_image = frame2[y-int(0.2*h):y+int(1.2*h), x-int(0.2*w):x+int(1.2*w)]

                if len(faces)>0:
                    if not self.statusProses and self.num>=30:
                        self.statusProses = True    
                        cv2.imwrite('{}/temp/pic.png'.format(current_directory), frame)
                        self.change_pixmap_signal2.emit(cropped_image)
                        # print("============================", self.num2)
                        self.num2 += 1
                else:
                    self.statusProses = False
                    self.num = 0 
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                self.change_pixmap_signal.emit(frame)
                
                if self.num2 >= jumlah_file:
                    self.running = False
                    self.stop_signal.emit()
                    # print("STOP=============================")
                    break
                # print(self.num)
        cap.release()

class SerialThread(QThread):
    # change_pixmap_signal = pyqtSignal(np.ndarray)
    # change_pixmap_signal2 = pyqtSignal(np.ndarray)
    change_status_signal = pyqtSignal(str)
    # change_hasil_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.port = None
        self.baudrate = 9600
        self.ser = None
        self.data = ""
        self.statusProses = True
        # self.num = 0
        # self.statusProses = False

    def run(self):
        # input_file = self.file
        # input_mode = self.mode
        while self.running:
            try:
                portss = []
                descss = []
                ports = serial.tools.list_ports.comports()
                for port, desc, hwid in sorted(ports):
                    # print(f"Port: {port}, Description: {desc}, Hardware ID: {hwid}")
                    portss.append(port)
                    descss.append(desc)
                # print(portss)
                n = 0
                for i, p in enumerate(descss):
                    if "Arduino" in p or "USB" in p:
                        self.port = portss[i]
                        self.change_status_signal.emit("Terhubung")
                        n+=1
                # print(n)
                if n == 0:
                    self.change_status_signal.emit("Tidak terhubung")
                    self.ser = None
                
                try:
                    if self.ser == None and self.port != None:
                        self.ser = serial.Serial(self.port, self.baudrate)
                        print(self.ser)
                except:
                    pass
            except:
                pass
    
    def send(self, string):
        if string != self.data:
            try:
                # print(string)
                self.ser.write(string.encode())
                self.data = string
                print("success++++++++++++++++++++")
            except:
                # print("fail==============")
                pass
        # time.sleep(0.5)




            