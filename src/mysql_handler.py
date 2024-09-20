import mysql.connector
import yaml

class MYSQLHandler:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        self.conn = mysql.connector.connect(host = config['mysql']['host'],
        user = config['mysql']['user'],
        database = config['mysql']['database'])

        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        # Check if the table exists and create it if not
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                weight FLOAT,
                count INT,
                image_path VARCHAR(255)
            )
        """)
        self.conn.commit()

    def log_detection(self, timestamp, weight, count, image_path):
        sql = "INSERT INTO detection_logs (timestamp, weight, count, image_path) VALUES (%s, %s, %s, %s)"
        values = (timestamp, weight, count, image_path)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
        

        
    