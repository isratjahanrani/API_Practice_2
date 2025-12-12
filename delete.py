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

def delete_teacher_from_db(teacher_id):
    sql = "DELETE FROM section_details WHERE id = %s"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (teacher_id,))
        conn.commit()
        deleted_rows = teacher_id
        cursor.close()
        return deleted_rows
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
    
    def do_DELETE(self):
        if not self.authenticate():
            return

        parsed = urlparse(self.path)
        teacher_id = parsed.query.split('=')[1]
        if parsed.path == "/teacher":
            
            deleted_rows = delete_teacher_from_db(int(teacher_id))
                    
            result = {
                    "message": "Section detais deleted successfully",
                    "deleted_rows": deleted_rows
                }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()  
            self.wfile.write(json.dumps(result).encode())



server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()
    