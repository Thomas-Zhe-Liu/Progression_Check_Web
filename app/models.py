import sqlite3
from app import login_manager

class Users():

    def __init__(self, z_id, password, active=True):
        self.z_id = z_id
        self.password = password
        self.active = active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.z_id

    def add(self):
        connection = sqlite3.connect('Gradget.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user values(?, ?)", (self.z_id, self.password,))
        connection.commit()
        connection.close()

    def is_active(self):
        return self.active

    def is_authenticated(self):
        connection = sqlite3.connect('Gradget.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE z_id = ? AND password = ?", (self.z_id, self.password))
        data = cursor.fetchone()
        if data is None:
            return False
        return True

@login_manager.user_loader
def load_user(id):
    connection = sqlite3.connect('Gradget.db')
    cursor = connection.cursor()
    cursor.execute("SELECT z_id, password FROM user WHERE z_id = ?", (id,))
    data = cursor.fetchone()
    print(data,'is data')
    if data is not None:
        user = Users(data[0],data[1])
        return user
    return None