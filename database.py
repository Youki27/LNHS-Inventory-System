import mysql.connector

#db = Database(host='127.0.0.1',user='root',password='youkifubuki27*',database='LNHSIS')
class Database:
    def __init__ (self):
        self.host = '127.0.0.1'
        self.user = 'root'
        self.password = 'youkifubuki27*'
        self.database = 'lnhsis'



    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                create_db = Database.create_database_if_not_exists(self)
            else:
                print("Error:",err)
        return self.connection

    def create_database_if_not_exists(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )

        cursor = self.connection.cursor()

        try:
            #check if db exists
            cursor.execute("SHOW DATABASES")
            databases = [database[0] for database in cursor.fetchall()]

            if self.database.lower() not in databases:
                #create if non-existent
                cursor.execute(f"CREATE DATABASE {self.database};")
                cursor.execute(f" CREATE TABLE {self.database}.users (uid int primary key auto_increment not null, username varchar(255), password varchar(255));")
                cursor.execute(f"CREATE TABLE {self.database}.permissions (perm_id int primary key auto_increment not null, perm_val varchar(100), perm_user varchar(255));")
                cursor.execute(f"CREATE TABLE {self.database}.items (item_id int primary key auto_increment not null, item_name varchar(100),quality varchar(50), barcode varchar(50),date_added datetime, status int);")
                cursor.execute(f"CREATE TABLE {self.database}.borrowers (bid int primary key auto_increment not null, borrower_name varchar(100), borrower_address varchar(100), borrowed_item varchar(100), barcode varchar(50), purpose varchar(255), date_borrowed datetime, date_return_estimate datetime, date_returned datetime);")
                cursor.execute(f"CREATE TABLE {self.database}.logs (log_id int primary key auto_increment not null, user varchar(100), action varchar(255));")
                print(f"Database '{self.database}' created!")
                self.connection.commit()
        except mysql.connector.Error as err:
            print("Error", err)
            self.connection.rollback()

        try:
            cursor.execute(f"INSERT {self.database}.users (username, password) VALUES ('admin', 'changeme')")
            self.connection.commit()
        except mysql.connector.Error as err:
            print("ERROR", err)
            self.connection.rollback()

        try:
            cursor.execute(f"INSERT {self.database}.permissions (perm_val, perm_user) VALUES ('admin','admin')")
            self.connection.commit()
        except mysql.connector.Error as err:
            print("ERROR", err)
            self.connection.rollback()

    def delete_database(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        
        cursor = self.connection.cursor()

        try:
            #check if db exists
            cursor.execute("SHOW DATABASES")
            databases = [database[0] for database in cursor.fetchall()]

            if self.database.lower() in databases:
                #drop if exist
                cursor.execute("DROP DATABASE {}".format(self.database))
                print(f"Database '{self.database}' deleted!")
            else:
                print(f"Database doesn't exist!")
        except mysql.connector.Error as err:
            print("Error", err)

    def verify_login(self,given_cred):
        self.connection = mysql.connector.connect(
            host = self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

        username = given_cred[0]
        pw = given_cred[1]

        cursor = self.connection.cursor()

        try:
            cursor.execute(f"SELECT username,password FROM lnhsis.users WHERE username = '{username}'")
            result = cursor.fetchall()

            if not result:
                return False
            for row in result:
                pw_res = row[1]
                usrnm = row[0]
            if pw_res != pw:
                return False
            if usrnm != username:
                return False
            return True
        except mysql.connector.Error as err:
            print("ERROR", err)

    def close(self):
        if self.connection:
            self.connection.close()


    