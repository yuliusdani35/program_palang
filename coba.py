import cv2

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('haarcascade.xml')

# Initialize the video capture object to capture video from the default camera (usually the webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream from the camera.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image")
        break

    # Convert the frame to grayscale as the face detector expects gray images
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform face detection
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around the detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Display the resulting frame
    cv2.imshow('Face Recognition', frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close the window
cap.release()
cv2.destroyAllWindows()


# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QGroupBox, QLabel, QLineEdit, QFileDialog


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Aplikasi Form dan Pemilihan Berkas")

#         # Buat widget utama
#         main_widget = QWidget()
#         self.setCentralWidget(main_widget)

#         layout = QVBoxLayout()
#         main_widget.setLayout(layout)

#         # Buat groupbox
#         groupbox = QGroupBox("Form dan Pemilihan Berkas")
#         layout.addWidget(groupbox)

#         group_layout = QVBoxLayout()
#         groupbox.setLayout(group_layout)

#         # Form untuk memasukkan nama
#         self.name_label = QLabel("Nama:")
#         self.name_edit = QLineEdit()
#         group_layout.addWidget(self.name_label)
#         group_layout.addWidget(self.name_edit)

#         # Tombol untuk memilih berkas
#         self.file_button = QPushButton("Pilih Berkas")
#         self.file_button.clicked.connect(self.select_files)
#         group_layout.addWidget(self.file_button)

#         # Tombol untuk menyimpan
#         self.save_button = QPushButton("Simpan")
#         self.save_button.clicked.connect(self.save_data)
#         group_layout.addWidget(self.save_button)

#     def select_files(self):
#         file_dialog = QFileDialog()
#         file_dialog.setFileMode(QFileDialog.ExistingFiles)
#         files = file_dialog.getOpenFileNames(self, "Pilih Berkas", "", "All Files (*)")[0]
#         print("Berkas yang dipilih:", files[:5])  # Ambil lima berkas pertama

#     def save_data(self):
#         name = self.name_edit.text()
#         print("Nama yang disimpan:", name)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
