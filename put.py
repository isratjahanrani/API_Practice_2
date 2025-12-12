#C:/Users/robiu/AppData/Local/Programs/Python/Python313/python.exe -m pip install --user mysql-connector-python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error

#http://localhost:5000/teacher?id=2

API_KEY = "mysecretkey123"
# DB config - update if your XAMPP uses different credentials
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",   # change if root has a password
    "database": "section_selection"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def update_teacher_in_db(teacher_id, course_name, course_code, department, faculty_name, section, day, course_credit):
    sql = "UPDATE section_details SET course_name = %s, course_code = %s, department = %s, faculty_name = %s, section = %s, day = %s, course_credit = %s WHERE id = %s"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (course_name, course_code, department, faculty_name, section, day, course_credit, teacher_id))
        conn.commit()
        updated_rows = teacher_id
        cursor.close()
        return updated_rows
    except Error:
        return None
    finally:
        if conn:
            conn.close()

class SimpleAPI(BaseHTTPRequestHandler):
    # AUTH CHECK
    def authenticate(self):
        """Check API key in request header"""
        key = self.headers.get("X-API-KEY")
        if key != API_KEY:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return False
        return True
    
    def do_PUT(self):
        if not self.authenticate():
            return
        parsed = urlparse(self.path)
        teacher_id = parsed.query.split('=')[1]
        if parsed.path == "/teacher":
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)
            course_name = data.get("course_name")
            course_code = data.get("course_code")
            department = data.get("department")
            faculty_name = data.get("faculty_name")
            section = data.get("section")
            day = data.get("day")
            course_credit = data.get("course_credit")
            updated_rows = update_teacher_in_db(int(teacher_id), course_name, course_code, department, faculty_name, section, day, course_credit)
            result = {
                    "message": "Section or Course updated successfully",
                    "updated_rows": updated_rows
                }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()

