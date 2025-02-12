from lib.mysql_connector import MySQLConnectionPool, AttendanceDB

# Inisialisasi pool koneksi
pool = MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host="localhost",
    port=3306,
    database="attendanceDB",
    user="root",
    password=""
)

# Inisialisasi AttendanceDB dengan pool koneksi
attendance_db = AttendanceDB(pool)

attendance_data = [
    ('ula', '2024-06-20', '14:27:33', '14:29:14', 0, '')
]

attendance_db.insert_data(attendance_data[0])