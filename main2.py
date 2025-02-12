import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QComboBox
from PyQt5.QtWidgets import QLabel, QGroupBox, QGridLayout, QLineEdit, QPushButton, QProgressBar
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFormLayout, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QTabWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
import shutil, os, subprocess
import pickle
import cv2
import os, time
import numpy as np
import csv
import pandas as pd
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

from lib.mysql_connector import MySQLConnectionPool, AttendanceDB

from utils import get_image_paths
from utils import face_encodings
from utils import face_rects
from utils import face_encodings
from utils import nb_of_matches

from datetime import datetime

##################################### 1 baris
import serial.tools.list_ports

import pickle

from thread import *

with open("{}/encodings.pickle".format(current_directory), "rb") as f:
    name_encodings_dict = pickle.load(f)
threshold = 0.5

from deepface import DeepFace

pool = MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    port=3306,
    database="attendanceDB",
    user="root",
    password=""
)

attendance_db = AttendanceDB(pool)

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.judul = "SISTEM PENGENALAN WAJAH"
        self.display_width, self.display_height = 640, 480
        self.captured_images = []
        self.files = []
        self.initUI()

    def initUI(self):
        # Widget utama
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.main_tab = QWidget()
        self.data_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.data_tab, "Data")

        main_layout = QGridLayout()

        self.main_tab.setLayout(main_layout)

        data_layout = QGridLayout()
        self.data_tab.setLayout(data_layout)


        ################################################

        # title_label = QLabel(self.judul)
        # title_label.setAlignment(Qt.AlignCenter)
        # main_layout.addWidget(title_label, 0, 0, 1, 2)

        gbVid = QGroupBox("Camera Stream 1")
        image_layout = QVBoxLayout()
        self.vid_label = QLabel()
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        self.vid_label.setPixmap(pixmap)
        image_layout.addWidget(self.vid_label, alignment=Qt.AlignCenter)
        gbVid.setLayout(image_layout)
        main_layout.addWidget(gbVid, 0, 0, 2, 1)

        gbVid2 = QGroupBox("Camera Stream 2")
        image_layout2 = QVBoxLayout()
        self.vid_label3 = QLabel()
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        self.vid_label3.setPixmap(pixmap)
        image_layout2.addWidget(self.vid_label3, alignment=Qt.AlignCenter)
        gbVid2.setLayout(image_layout2)
        main_layout.addWidget(gbVid2, 2, 0, 2, 1)

        gbDeteksi = QGroupBox("Deteksi")
        det_layout = QHBoxLayout()
        self.img_label = QLabel()
        self.img_label2 = QLabel()
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        self.img_label.setPixmap(pixmap)
        self.img_label2.setPixmap(pixmap)
        det_layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        # det_layout.addWidget(self.img_label2, alignment=Qt.AlignCenter)
        gbDeteksi.setLayout(det_layout)
        main_layout.addWidget(gbDeteksi, 0, 2)

        status_deteksi_box = QGroupBox("Status Deteksi")
        status_deteksi_layout = QVBoxLayout()
        self.status_deteksi_label = QLabel("-")
        status_deteksi_layout.addWidget(self.status_deteksi_label)
        status_deteksi_box.setLayout(status_deteksi_layout)
        main_layout.addWidget(status_deteksi_box, 1, 2)

        hasil_deteksi_box = QGroupBox("Hasil Deteksi")
        hasil_deteksi_layout = QVBoxLayout()
        self.label_nama    = QLabel("Nama    : -")
        self.label_tanggal = QLabel("Tanggal : -")
        self.label_waktu   = QLabel("Waktu Masuk   : -")
        self.label_waktu2   = QLabel("Waktu Keluar  : -")
        self.label_conf    = QLabel("Conf    : -")
        self.label_pred_time = QLabel("Waktu Prediksi    : -")
        hasil_deteksi_labels = [self.label_nama, self.label_tanggal, self.label_waktu, self.label_waktu2, self.label_conf, self.label_pred_time]

        for label in hasil_deteksi_labels:
            hasil_deteksi_layout.addWidget(label)

        hasil_deteksi_box.setLayout(hasil_deteksi_layout)
        main_layout.addWidget(hasil_deteksi_box, 2, 2)

        # Status Serial GroupBox
        status_serial_box = QGroupBox("Status Serial")
        status_serial_layout = QVBoxLayout()
        self.status_serial_label = QLabel("-")
        status_serial_layout.addWidget(self.status_serial_label)
        status_serial_box.setLayout(status_serial_layout)
        main_layout.addWidget(status_serial_box, 3, 2)

        ####################################

        gbDt = QGroupBox("Data")
        dt_layout = QVBoxLayout()
        self.table = QTableWidget()
        dt_layout.addWidget(self.table)
        gbDt.setLayout(dt_layout)
        data_layout.addWidget(gbDt, 0, 0, 2, 1)

        # Grup Box untuk tampilan kamera
        camera_groupbox = QGroupBox("Camera")
        camera_layout = QVBoxLayout()
        self.vid_label2 = QLabel()
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.vid_label2.setPixmap(pixmap)
        camera_layout.addWidget(self.vid_label2)
        camera_groupbox.setLayout(camera_layout)
        data_layout.addWidget(camera_groupbox, 0, 1, 3, 1)


        gbForm = QGroupBox("Form")
        group_layout = QVBoxLayout()
        self.name_label = QLabel("Nama:")
        self.name_edit = QLineEdit()
        self.file_label = QLabel("File gambar:")
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        group_layout.addWidget(self.name_label)
        group_layout.addWidget(self.name_edit)
        group_layout.addWidget(self.file_label)
        group_layout.addWidget(self.file_edit)
        self.file_button = QPushButton("Pilih Gambar dari File")
        self.file_button.clicked.connect(self.select_files)
        self.file_button2 = QPushButton("Ambil Gambar dari Kamera")
        self.file_button2.clicked.connect(self.take_5picts)
        group_layout2 = QHBoxLayout()
        group_layout2.addWidget(self.file_button)
        group_layout2.addWidget(self.file_button2)
        group_layout.addLayout(group_layout2)
        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.save_data)
        group_layout.addWidget(self.save_button)
        gbForm.setLayout(group_layout)
        data_layout.addWidget(gbForm, 2, 0, 2, 1)

        gbAct = QGroupBox("Training")
        act_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.btn_train = QPushButton('Training Model')
        self.btn_train.clicked.connect(self.train_model)
        # self.btn_database = QPushButton('Database')
        # self.btn_database.clicked.connect(self.database)
        # act_layout.addWidget(self.btn_database)
        act_layout.addWidget(self.progress_bar)
        act_layout.addWidget(self.btn_train)
        gbAct.setLayout(act_layout)
        data_layout.addWidget(gbAct, 4, 0)

        # Grup Box untuk tampilan kamera
        preview_groupbox = QGroupBox("Preview")
        self.preview_layout = QHBoxLayout()
        # self.image_label2 = QLabel()
        # pixmap2 = QPixmap("{}/no-image.jpg".format(current_directory))
        # self.image_label2.setPixmap(pixmap2)
        # self.preview_layout.addWidget(self.image_label2)
        preview_groupbox.setLayout(self.preview_layout)
        data_layout.addWidget(preview_groupbox, 3, 1, 2, 1)


        self.tabs.currentChanged.connect(self.tab_changed)
        self.setWindowTitle(self.judul)

        self.image_thread = ImageThread(index=[0, 1])
        self.image_thread.change_pixmap_signal.connect(self.update_image)
        self.image_thread.change_pixmap_signal2.connect(self.update_image2)
        self.image_thread.change_status_signal.connect(self.update_status_deteksi)
        self.image_thread.change_hasil_signal.connect(self.update_status_hasil)
        self.image_thread.start()

        self.serial_thread = SerialThread()
        # self.image_thread.change_pixmap_signal.connect(self.update_image)
        # self.image_thread.change_pixmap_signal2.connect(self.update_image2)
        self.serial_thread.change_status_signal.connect(self.update_status_serial)
        # self.image_thread.change_hasil_signal.connect(self.update_status_hasil)
        self.serial_thread.start()

    def tab_changed(self, index):
        if index == 1:
            self.captured_images = []
            self.files = []
            self.image_thread.stop()
            self.update_table()
            pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
            self.vid_label.setPixmap(pixmap)
            self.vid_label3.setPixmap(pixmap)
            self.img_label.setPixmap(pixmap)
        elif index == 0:
            self.image_thread = ImageThread(index=[0, 1])
            self.image_thread.change_pixmap_signal.connect(self.update_image)
            self.image_thread.change_pixmap_signal2.connect(self.update_image2)
            self.image_thread.change_status_signal.connect(self.update_status_deteksi)
            self.image_thread.change_hasil_signal.connect(self.update_status_hasil)
            self.image_thread.start()
            QApplication.processEvents()

    def take_5picts(self):
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        self.image_thread2 = ImageThread2()
        self.image_thread2.change_pixmap_signal.connect(self.update_imageA)
        self.image_thread2.change_pixmap_signal2.connect(self.update_imageA2)
        self.image_thread2.stop_signal.connect(self.stop_thread)
        self.image_thread2.start()

    def stop_thread(self):
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.vid_label2.setPixmap(pixmap)

    def select_files(self):
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        self.files = file_dialog.getOpenFileNames(self, "Pilih Berkas Gambar", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")[0]
        print("Berkas yang dipilih:", self.files[:5])  # Ambil lima berkas pertama
        fileTxt = []
        for f in self.files:
            f = f.split("/")[-1]
            fileTxt.append(f)
        result = ', '.join(fileTxt)
        # print(result)
        self.file_edit.setText(result)

        for f in self.files:
            image = QPixmap(f)
            image = image.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(image)
            self.preview_layout.addWidget(image_label)

    def save_data(self):
        # self.captured_images = []
        # self.files = []
        name = self.name_edit.text()
        if name != "":
            if len(self.files) > 0:
                folder_path = "dataset/train/{}".format(name)
                folder_path = os.path.join(current_directory, folder_path)
                try:
                    # Menghapus folder beserta seluruh isinya
                    shutil.rmtree(folder_path)
                    print(f"Folder {folder_path} berhasil dihapus.")
                except FileNotFoundError:
                    print(f"Folder {folder_path} tidak ditemukan.")
                except Exception as e:
                    print(f"Terjadi kesalahan saat menghapus folder: {e}")

                dest = "{}/dataset/train/{}".format(current_directory, name)
                os.mkdir(dest)
                for f in self.files:
                    print(f)
                    shutil.copy(f, dest)
                print("Nama yang disimpan:", name)
                QMessageBox.information(self, "Information", "Gambar berhasil disimpan")
            elif len(self.captured_images) > 0:
                # print("kkkkkkk")
                folder_path = "dataset/train/{}".format(name)
                folder_path = os.path.join(current_directory, folder_path)
                try:
                    # Menghapus folder beserta seluruh isinya
                    shutil.rmtree(folder_path)
                    print(f"Folder {folder_path} berhasil dihapus.")
                except FileNotFoundError:
                    print(f"Folder {folder_path} tidak ditemukan.")
                except Exception as e:
                    print(f"Terjadi kesalahan saat menghapus folder: {e}")

                dest = "{}/dataset/train/{}".format(current_directory, name)
                os.mkdir(dest)
                for i, image in enumerate(self.captured_images):
                    # print(i)
                    image.save(f"{folder_path}/captured_image_{i}.png")
                QMessageBox.information(self, "Information", "Gambar berhasil disimpan")
            self.update_table()
            self.name_edit.setText("")
            self.file_edit.setText("")

            self.files = []
            self.captured_images = []
            while self.preview_layout.count():
                item = self.preview_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                    

    def edit_data(self, row):
        name_item = self.table.item(row, 0)
        if name_item:
            name = name_item.text()
            print(f"Edit data: {name}")
            self.name_edit.setText(name)
        self.file_edit.setText("")


    def delete_data(self, row):
        # self.table.removeRow(row)
        name_item = self.table.item(row, 0)
        if name_item:
            name = name_item.text()
            print(f"Hapus data: {name}")
            folder_path = "dataset/train/{}".format(name)
            folder_path = os.path.join(current_directory, folder_path)
            try:
                # Menghapus folder beserta seluruh isinya
                shutil.rmtree(folder_path)
                print(f"Folder {folder_path} berhasil dihapus.")
            except FileNotFoundError:
                print(f"Folder {folder_path} tidak ditemukan.")
            except Exception as e:
                print(f"Terjadi kesalahan saat menghapus folder: {e}")
        print("Data dihapus.")
        self.update_table()

    def update_table(self):
        self.table.setRowCount(0)
        folder_name = "dataset/train"
        dataset_folder_path = os.path.join(current_directory, folder_name)

        folders_inside_dataset = []

        for name in os.listdir(dataset_folder_path):
            if os.path.isdir(os.path.join(dataset_folder_path, name)):
                if os.listdir(os.path.join(dataset_folder_path, name)):
                    folders_inside_dataset.append(name)
                else:
                    shutil.rmtree(os.path.join(dataset_folder_path, name))

        self.table.setColumnCount(2)
        # self.table.setRowCount(len(folders_inside_dataset))
        self.table.setHorizontalHeaderLabels(["Nama", "Aksi"])

        current_row = self.table.rowCount()
        for name in folders_inside_dataset:
            self.table.insertRow(current_row)
            self.table.setItem(current_row, 0, QTableWidgetItem(name))
            # self.table.setItem(current_row, 1, QTableWidgetItem(""))  # Kolom usia dikosongkan

            # Tambahkan tombol edit dan hapus
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Hapus")

            edit_button.clicked.connect(lambda _, row=current_row: self.edit_data(row))
            delete_button.clicked.connect(lambda _, row=current_row: self.delete_data(row))

            cell_widget = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(edit_button)
            layout.addWidget(delete_button)
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)

            self.table.setCellWidget(current_row, 1, cell_widget)
            current_row += 1

    @pyqtSlot(list)#np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img[1])
        if cv_img[0] == 0:
            self.vid_label.setPixmap(qt_img)
        if cv_img[0] ==1:
            self.vid_label3.setPixmap(qt_img)

    @pyqtSlot(np.ndarray)
    def update_image3(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.vid_label3.setPixmap(qt_img)

    @pyqtSlot(np.ndarray)
    def update_imageA(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.vid_label2.setPixmap(qt_img)

    def addLog(self, text):
        file_path = "{}/log.txt".format(current_directory)
        with open(file_path, "a") as file:
            file.write(text+"\n")

    @pyqtSlot(list)#np.ndarray)
    def update_image2(self, cv_img):
        # print(cv_img)
        global name_encodings_dict
        try:
            qt_img = self.convert_cv_qt2(cv_img[1])
            self.img_label.setPixmap(qt_img)
        except:
            pass
        self.addLog("sedang di proses")
        self.update_status_deteksi("Sedang diproses")

        try:
            self.addLog("start anti spoofing")
            self.addLog('{}/temp/pic{}.png'.format(current_directory, cv_img[0]))
            res = DeepFace.extract_faces(
              img_path='{}/temp/pic{}.png'.format(current_directory, cv_img[0]),
              anti_spoofing = True
            )
            self.addLog("done anti spoofing")
            print(res[0].get("facial_area"))
            print(res[0].get("is_real"))
            self.addLog("result anti spoofing : {}".format(res[0].get("is_real")))
            start_time = datetime.now().timestamp()

            if res[0].get("is_real") == True:
                print("================asdasdas====================")
                self.addLog("start face recognition")
                frame = cv2.imread('{}/temp/pic{}.png'.format(current_directory, cv_img[0]))
                encodings, rects = face_encodings(frame)

                name = ""
                names = []
                confs = [] 
                self.addLog("1")
                for encoding in encodings:
                    counts = {}
                    for (name, encodings) in name_encodings_dict.items():
                        print(name, len(encodings), len(encoding))
                        _, counts[name] = nb_of_matches(encodings, encoding)
                    print("--------------", counts, "ini")
                    if all(count == 0 for count in counts.values()):
                        name = "Unknown"
                        confs.append(" ")
                    else:
                        name = max(counts, key=counts.get)
                        if counts[name] < threshold:
                            name = "Unknown"
                            confs.append(" ")
                        else:
                            confs.append(counts[name])
                    names.append(name)
                self.addLog("2")
                nama = ""
                conf = ""
                rect = ""
                for n, name in enumerate(names):
                    nama = name
                    conf = confs[n]
                    rect = rects[n]
                    print("{} : {} {}".format(name, confs[n], rects[n]))
                self.addLog("result = {} : {} {}".format(name, confs[n], rects[n]))
                self.addLog("3")
                tgl = datetime.now().strftime("%d-%m-%Y")  
                waktu = datetime.now().strftime("%H:%M:%S")

                # print("Current Date:", tgl)
                # print("Current Time:", waktu)
                try:
                    # x, y, w, h = rect.left(), rect.top(), rect.width(), rect.height()
                    # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
                    # cv2.putText(frame, "{} {:.2f}".format(nama, conf), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

                    # cv2.imwrite("ini.png", frame)
                    # self.update_image(frame)
                    end_time = int(datetime.now().timestamp()*1000 - start_time*1000)
                    self.image_thread.update_name(cv_img[0], nama, conf, end_time)
                except:
                    pass
                end_time = int(datetime.now().timestamp()*1000 - start_time*1000)
                self.addLog("4")
                self.update_status_hasil([cv_img[0], "{}/{}/{}/{}/{}".format(str(nama), str(tgl), str(waktu), str(conf), str(end_time))])
                self.addLog("5")
                if nama == "" or nama.lower() == "unknown":
                    self.serial_thread.send("1\n")
                else:
                    if cv_img[0] == 0:
                        self.serial_thread.send("2\n")
                    if cv_img[0] == 1:
                        self.serial_thread.send("3\n")
                self.addLog("6")
            else:
                self.update_status_deteksi("BUKAN WAJAH ASLI")
                self.update_status_hasil([cv_img[0], "BUKAN WAJAH ASLI/-/-/-/-"])
        except Exception as e:
            error_msg = f"Error : {e}"
            self.addLog(error_msg)
            pass

    @pyqtSlot(np.ndarray)
    def update_imageA2(self, cv_img):
        image = self.convert_cv_qt(cv_img)
        image = image.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(image)
        self.preview_layout.addWidget(image_label)

        # Simpan gambar ke daftar gambar yang telah di-capture
        self.captured_images.append(image)

    def add_or_edit_data(self, nama, tanggal, jam_masuk=None, jam_keluar=None, predict_time=None, image_path=''):
        filename = '{}/output/data.csv'.format(current_directory)
        # Cek apakah file sudah ada
        if os.path.exists(filename):
            # Jika file ada, baca file tersebut
            df = pd.read_csv(filename)
        else:
            # Jika file tidak ada, buat DataFrame baru dengan kolom yang sesuai
            df = pd.DataFrame(columns=['no', 'nama', 'tanggal', 'jam masuk', 'jam keluar'])
        
        # Cek apakah ada data dengan nama dan tanggal yang sama
        existing_data = df[(df['nama'] == nama) & (df['tanggal'] == tanggal)]
        
        if not existing_data.empty:
            # Jika data ada, update data tersebut
            index = existing_data.index[0]
            if jam_masuk != None:
                df.at[index, 'jam masuk'] = jam_masuk

                formatted_tanggal = str(tanggal).split('-')
                formatted_tanggal = f'{formatted_tanggal[2]}-{formatted_tanggal[1]}-{formatted_tanggal[0]}'

                attendance_db.update_hours_in(
                    (jam_masuk, predict_time, image_path, nama, formatted_tanggal)
                )

            if jam_keluar != None:

                formatted_tanggal = str(tanggal).split('-')
                formatted_tanggal = f'{formatted_tanggal[2]}-{formatted_tanggal[1]}-{formatted_tanggal[0]}'

                attendance_db.update_hours_out(
                    (jam_keluar, predict_time, nama, image_path, formatted_tanggal)
                )

                df.at[index, 'jam keluar'] = jam_keluar
            print(f"Data untuk {nama} pada tanggal {tanggal} berhasil diupdate.")
        else:
            # Jika data tidak ada, tambahkan data baru
            if df.empty:
                new_no = 1
            else:
                new_no = df['no'].max() + 1
            
            new_data = {
                'no': new_no,
                'nama': nama,
                'tanggal': tanggal,
                'jam masuk': jam_masuk,
                'jam keluar': jam_keluar
            }

            formatted_tanggal = str(tanggal).split('-')
            formatted_tanggal = f'{formatted_tanggal[2]}-{formatted_tanggal[1]}-{formatted_tanggal[0]}'

            attendance_db.insert_data(
                (nama, str(formatted_tanggal), str(jam_masuk), str(jam_keluar), predict_time, image_path)
            )
            print(new_data)
            
            df = df.append(new_data, ignore_index=True)
            print(f"Data baru untuk {nama} pada tanggal {tanggal} berhasil ditambahkan dengan no {new_no}.")

        # Simpan kembali DataFrame ke file CSV
        df.to_csv(filename, index=False)

    @pyqtSlot(list)
    def update_status_hasil(self, ll):
        cam, text = ll
        nama = text.split("/")[0]
        # print(nama)
        tgl = text.split("/")[1]
        waktu = text.split("/")[2]
        conf = text.split("/")[3]

        try:
            pred_time = text.split("/")[4]
        except:
            pred_time = 0

        if nama != "BUKAN WAJAH ASLI":
            nama =  ''.join(char for char in nama if char.isalpha())

        self.label_nama.setText(    "Nama    : {}".format(nama))
        self.label_tanggal.setText( "Tanggal : {}".format(tgl))
        # self.label_waktu.setText(   "Waktu   : {}".format(waktu))
        self.label_conf.setText(    "Conf    : {}".format(conf))
        self.label_pred_time.setText("Waktu Prediksi    : {}".format(pred_time))

        if nama == "BUKAN WAJAH ASLI":
            nama = "-"

        if nama != "" and nama != "-":
            # Example usage
            source_file = '{}/temp/pic{}.png'.format(current_directory, cam)
            destination_file = 'output/{}_{}_{}.png'.format(tgl, waktu, nama)

            destination_file = destination_file.replace(":", "")
            destination_file = destination_file.replace("-", "")
            destination_file = "{}/{}".format(current_directory, destination_file)
            self.copy_and_rename_file(source_file, destination_file)
            # self.serial_thread.send("~{}!{}@{}#\n".format(nama, tgl, waktu))

            if str(cam) == "0":
                print("masuk======================")
                new_row_data = [nama, waktu, "-"]
                # self.add_row_to_csv(file_path, new_row_data)
                self.add_or_edit_data(nama, tgl, jam_masuk=waktu, predict_time=pred_time, image_path=destination_file)
                self.label_waktu.setText(   "Waktu Masuk    : {}".format(waktu))
                self.label_waktu2.setText(   "Waktu Keluar   : -")
            else:
                self.add_or_edit_data(nama, tgl, jam_keluar=waktu, predict_time=pred_time, image_path=destination_file)
                self.label_waktu2.setText(   "Waktu Keluar   : {}".format(waktu))
                filename = '{}/output/data.csv'.format(current_directory)
                # Cek apakah file sudah ada
                if os.path.exists(filename):
                    # Jika file ada, baca file tersebut
                    df = pd.read_csv(filename)
                else:
                    # Jika file tidak ada, buat DataFrame baru dengan kolom yang sesuai
                    df = pd.DataFrame(columns=['no', 'nama', 'tanggal', 'jam masuk', 'jam keluar'])
                
                # Cek apakah ada data dengan nama dan tanggal yang sama
                existing_data = df[(df['nama'] == nama) & (df['tanggal'] == tgl)]
                
                if not existing_data.empty:
                    # Jika data ada, update data tersebut
                    index = existing_data.index[0]
                    waktu = df.at[index, 'jam masuk']
                    self.label_waktu.setText(   "Waktu Masuk    : {}".format(waktu))
            

        else:
            self.label_waktu.setText(   "Waktu Masuk    : -")
            self.label_waktu2.setText(   "Waktu Keluar   : -")    
    def copy_and_rename_file(self, src_file, dst_file):
        shutil.copy(src_file, dst_file)

    def add_row_to_csv(self, file_path, data):
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

    @pyqtSlot(str)
    def update_status_deteksi(self, status):
        self.status_deteksi_label.setText(status)

    @pyqtSlot(str)
    def update_status_serial(self, status):
        self.status_serial_label.setText(status)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width/2, self.display_height/2, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def convert_cv_qt2(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(int(self.display_width/4), int(self.display_height/4), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def train_model(self):
        global name_encodings_dict
        self.image_thread.stop()
        root_dir = "{}/dataset/train".format(current_directory)
        class_names = os.listdir(root_dir)

        image_paths = get_image_paths(root_dir, class_names)
        name_encodings_dict = {}

        nb_current_image = 1

        for n, image_path in enumerate(image_paths):
            try:
                print(f"Image processed {nb_current_image}/{len(image_paths)}")
                print(image_path)
                image = cv2.imread(image_path)
                encodings, _ = face_encodings(image)
                name = image_path.split(os.path.sep)[-2]
                e = name_encodings_dict.get(name, [])
                e.extend(encodings)
                name_encodings_dict[name] = e
                nb_current_image += 1

                progres = int(n/len(image_paths) * 100)
                self.progress_bar.setValue(progres)
                QApplication.processEvents()
            except:
                print("Fail {}".format(image_path))

        with open("{}/encodings.pickle".format(current_directory), "wb") as f:
            pickle.dump(name_encodings_dict, f)

        with open("{}/encodings.pickle".format(current_directory), "rb") as f:
            name_encodings_dict = pickle.load(f)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Information", "Training Berhasil")

        # self.image_thread = ImageThread()
        # self.image_thread.change_pixmap_signal.connect(self.update_image)
        # self.image_thread.change_pixmap_signal2.connect(self.update_image2)
        # self.image_thread.change_status_signal.connect(self.update_status_deteksi)
        # self.image_thread.change_hasil_signal.connect(self.update_status_hasil)
        # self.image_thread.start()
        QApplication.processEvents()

    # def closeEvent(self, event):
    #     self.conn.close()
    #     # self.threadCamera1.stop()
    #     # self.threadCamera2.stop()
    #     # event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_gui = MyApp()
    # my_gui.showMaximized()
    my_gui.show()
    sys.exit(app.exec_())





