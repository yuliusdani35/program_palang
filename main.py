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

current_directory = os.path.dirname(os.path.abspath(__file__))

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

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.judul = "SISTEM PENGENALAN WAJAH"
        self.display_width, self.display_height = 640, 480
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

        gbVid = QGroupBox("Camera Stream")
        image_layout = QVBoxLayout()
        self.vid_label = QLabel()
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        self.vid_label.setPixmap(pixmap)
        image_layout.addWidget(self.vid_label, alignment=Qt.AlignCenter)
        gbVid.setLayout(image_layout)
        main_layout.addWidget(gbVid, 0, 0, 4, 1)

        gbDeteksi = QGroupBox("Deteksi")
        det_layout = QVBoxLayout()
        self.img_label = QLabel()
        pixmap = QPixmap("{}/no-image.jpg".format(current_directory))
        self.img_label.setPixmap(pixmap)
        det_layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        gbDeteksi.setLayout(det_layout)
        main_layout.addWidget(gbDeteksi, 0, 1)

        status_deteksi_box = QGroupBox("Status Deteksi")
        status_deteksi_layout = QVBoxLayout()
        self.status_deteksi_label = QLabel("-")
        status_deteksi_layout.addWidget(self.status_deteksi_label)
        status_deteksi_box.setLayout(status_deteksi_layout)
        main_layout.addWidget(status_deteksi_box, 1, 1)

        hasil_deteksi_box = QGroupBox("Hasil Deteksi")
        hasil_deteksi_layout = QVBoxLayout()
        self.label_nama    = QLabel("Nama    : -")
        self.label_tanggal = QLabel("Tanggal : -")
        self.label_waktu   = QLabel("Waktu   : -")
        self.label_conf    = QLabel("Conf    : -")
        hasil_deteksi_labels = [self.label_nama, self.label_tanggal, self.label_waktu, self.label_conf]

        for label in hasil_deteksi_labels:
            hasil_deteksi_layout.addWidget(label)

        hasil_deteksi_box.setLayout(hasil_deteksi_layout)
        main_layout.addWidget(hasil_deteksi_box, 2, 1)

        # Status Serial GroupBox
        status_serial_box = QGroupBox("Status Serial")
        status_serial_layout = QVBoxLayout()
        self.status_serial_label = QLabel("-")
        status_serial_layout.addWidget(self.status_serial_label)
        status_serial_box.setLayout(status_serial_layout)
        main_layout.addWidget(status_serial_box, 3, 1)

        ####################################

        gbAct = QGroupBox("Training")
        act_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.btn_train = QPushButton('Training Model')
        self.btn_train.clicked.connect(self.train_model)
        self.btn_database = QPushButton('Database')
        self.btn_database.clicked.connect(self.database)
        act_layout.addWidget(self.btn_database)
        act_layout.addWidget(self.progress_bar)
        act_layout.addWidget(self.btn_train)
        gbAct.setLayout(act_layout)
        data_layout.addWidget(gbAct, 1, 1)

        gbDt = QGroupBox("Data")
        dt_layout = QVBoxLayout()
        self.table = QTableWidget()
        # self.table.setColumnCount(3)
        # self.table.setRowCount(3)
        # self.table.setHorizontalHeaderLabels(["Kolom 1", "Kolom 2", "Kolom 3"])

        # for i in range(3):
        #     for j in range(3):
        #         item = QTableWidgetItem(f"Baris {i+1}, Kolom {j+1}")
        #         self.table.setItem(i, j, item)
        dt_layout.addWidget(self.table)
        gbDt.setLayout(dt_layout)
        data_layout.addWidget(gbDt, 0, 0, 1, 2)

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
        self.file_button = QPushButton("Pilih Gambar")
        self.file_button.clicked.connect(self.select_files)
        group_layout.addWidget(self.file_button)
        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.save_data)
        group_layout.addWidget(self.save_button)
        gbForm.setLayout(group_layout)
        data_layout.addWidget(gbForm, 1, 0)


        self.tabs.currentChanged.connect(self.tab_changed)
        self.setWindowTitle(self.judul)

        self.image_thread = ImageThread()
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
            self.files = []
            self.image_thread.stop()
            self.update_table()
        elif index == 0:
            self.image_thread = ImageThread()
            self.image_thread.change_pixmap_signal.connect(self.update_image)
            self.image_thread.change_pixmap_signal2.connect(self.update_image2)
            self.image_thread.change_status_signal.connect(self.update_status_deteksi)
            self.image_thread.change_hasil_signal.connect(self.update_status_hasil)
            self.image_thread.start()
            QApplication.processEvents()

    def select_files(self):
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

    def save_data(self):
        name = self.name_edit.text()

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
        self.update_table()
        self.name_edit.setText("")
        self.file_edit.setText("")

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

    def database(self):
        print("database")
        self.image_thread.stop()
        time.sleep(10)
        self.image_thread = ImageThread()
        self.image_thread.change_pixmap_signal.connect(self.update_image)
        self.image_thread.change_pixmap_signal2.connect(self.update_image2)
        self.image_thread.change_status_signal.connect(self.update_status_deteksi)
        self.image_thread.change_hasil_signal.connect(self.update_status_hasil)
        self.image_thread.start()
        QApplication.processEvents()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.vid_label.setPixmap(qt_img)

    @pyqtSlot(np.ndarray)
    def update_image2(self, cv_img):
        global name_encodings_dict
        try:
            qt_img = self.convert_cv_qt2(cv_img)
            self.img_label.setPixmap(qt_img)
        except:
            pass
        self.update_status_deteksi("Sedang diproses")

        frame = cv2.imread('{}/temp/pic.png'.format(current_directory))
        encodings, rects = face_encodings(frame)

        name = ""
        names = []
        confs = [] 

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
        nama = ""
        conf = ""
        rect = ""
        for n, name in enumerate(names):
            nama = name
            conf = confs[n]
            rect = rects[n]
            print("{} : {} {}".format(name, confs[n], rects[n]))
        
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
            self.image_thread.update_name(nama, conf)
        except:
            pass
        self.update_status_hasil("{}/{}/{}/{}".format(str(nama), str(tgl), str(waktu), str(conf)))

    @pyqtSlot(str)
    def update_status_hasil(self, text):
        nama = text.split("/")[0]
        # print(nama)
        tgl = text.split("/")[1]
        waktu = text.split("/")[2]
        conf = text.split("/")[3]

        nama =  ''.join(char for char in nama if char.isalpha())

        self.label_nama.setText(    "Nama    : {}".format(nama))
        self.label_tanggal.setText( "Tanggal : {}".format(tgl))
        self.label_waktu.setText(   "Waktu   : {}".format(waktu))
        self.label_conf.setText(    "Conf    : {}".format(conf))


        if nama != "":
            # Example usage
            file_path = '{}/output/data.csv'.format(current_directory)
            new_row_data = [tgl, waktu, nama]
            self.add_row_to_csv(file_path, new_row_data)

            # Example usage
            source_file = '{}/temp/pic.png'.format(current_directory)
            destination_file = 'output/{}_{}_{}.png'.format(tgl, waktu, nama)

            destination_file = destination_file.replace(":", "")
            destination_file = destination_file.replace("-", "")
            destination_file = "{}/{}".format(current_directory, destination_file)
            self.copy_and_rename_file(source_file, destination_file)
            # self.serial_thread.send("~{}!{}@{}#\n".format(nama, tgl, waktu))

        if nama == "" or nama.lower() == "unknown":
            self.serial_thread.send("1\n")
        else:
            self.serial_thread.send("2\n")
            
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
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
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





