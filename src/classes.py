import PySimpleGUI as sg
import sqlite3 as sql
from abc import ABC, abstractmethod
import os


class Sql:
    """
    Context manager for SQLite queries

    Attributes
    ----------
    db_path : str
        The path to the database file

    conn : sqlite3.connection
        Connection to the database

    cursor : sqlite3.connection.cursor
        Cursor for executing sqlite queries

    Methods
    --------
    __enter__ : None
        methods to execute when entering the context manager
        sets up the database connection and cursor
    
    __exit__ : None
        methods to execute when exiting the context manager
        commits any changes written to the db then closes the connection

    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        '''
        Executed on entering the context manager

        Returns:
            self.cursor (sqlite3.connection.cursor) : A cursor object to manipulate the current database. 

        '''
        self.conn = sql.connect(self.db_path)
        print("Connected to database")
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()
        print("Closed connection to database")


class Database(ABC):
    '''
    Abstract base class for a database
    '''
    db_path = ''

    @staticmethod
    def prepare_tables():
        '''
        Creates the required database tables if they aren't there
        
        Parameters:
            db_path (str) : the path to the database

        Returns:
            None
        '''
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    amount NUMBER,
                    date TEXT,
                    notes TEXT
                    )
                    '''
            )
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY,
                    transaction_id INTEGER,
                    name TEXT,
                    filepath TEXT
                    )'''
            )
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS filedata (
                    id INTEGER PRIMARY KEY,
                    fileID INTEGER,
                    data BLOB
                    )'''
            )
        print('Tables created')
        #print the current database schema
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                SELECT name, sql FROM sqlite_master WHERE type='table'
                '''
            )
            print(cursor.fetchall())
        print(Database.db_path)
    
            
    @staticmethod
    def add_transaction(transaction):
        '''
        Enters a new transaction into the transactions table
        Enters the associated attachments into the attachments table

        Parameters:
            db_path (str) : the path to the current database
            transaction (Transaction) : the transaction to add

        Returns:
            None
        '''


        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                INSERT INTO transactions (name, amount, date, notes)
                VALUES (?, ?, ?, ?)
                ''', (transaction.name, transaction.amount, transaction.date, transaction.notes))
            transaction_id = cursor.lastrowid
            for attachment in transaction.attachments:
                cursor.execute('''
                    INSERT INTO attachments (transaction_id, name, filepath)
                    VALUES (?, ?, ?)
                    ''', (transaction_id, attachment.name, attachment.filepath))

    @staticmethod
    def get_all_transactions():
        '''
        Gets all transactions currently in the transactions table

        Parameters:
            db_path (str) : the path to the current database

        Returns:
            transactions (list[Transaction]) : the list of transactions in the database
            Does not populate the attachments list for each transaction -> see get_attachments_for_transaction
        
        '''

        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                SELECT * FROM transactions
                '''
            )
            transactions = []
            for row in cursor.fetchall():
                transaction = Transaction()
                transaction.id = row[0]
                transaction.name = row[1]
                transaction.amount = row[2]
                transaction.date = row[3]
                transaction.notes = row[4]
                transactions.append(transaction)
            return transactions

    @staticmethod
    def get_attachments_for_transaction(transaction_id):
        '''
        Gets all the attachments associated with a given transaction

        Parameters:
            db_path (str) : the path to the current database
            transaction_id (int) : the id of the transaction to fetch attachments for
        
        Returns:
            attachments (list[Attachment]) : A list of attachment objects where the 
            transaction_id parameter in the table matches the transaction_id parameter

        '''
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                SELECT * FROM attachments
                WHERE transaction_id = ?
                ''', (transaction_id,))
            attachments = []
            for row in cursor.fetchall():
                attachment = Attachment(row[2], row[3])
                attachments.append(attachment)
            return attachments

    @staticmethod
    def add_attachments_to_transaction(transaction, attachments):
        for attachment in attachments:
            transaction.attachments.append(attachment)

    @staticmethod
    def delete_transaction(transaction_id):
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                DELETE FROM transactions
                WHERE id = ?
                ''', (transaction_id,))
            cursor.execute('''
                DELETE FROM attachments
                WHERE transaction_id = ?
                ''', (transaction_id,))
    
    @staticmethod
    def modify_transaction(transaction):
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                UPDATE transactions
                SET name = ?, amount = ?, date = ?, notes = ?
                WHERE id = ?
                ''', (transaction.name, transaction.amount, transaction.date, transaction.notes, transaction.id))
            for attachment in transaction.attachments:
                cursor.execute('''
                    INSERT INTO attachments (transaction_id, name, filepath)
                    VALUES (?, ?, ?)
                    ''', (transaction.id, attachment.name, attachment.filepath))    

    # a function that takes an attachment and reads the file data into a bytestring then inserts it into the filedata table
    @staticmethod
    def add_attachment_to_db(attachment):
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                INSERT INTO filedata (fileID, data)
                VALUES (?, ?)
                ''', (attachment.fileID, attachment.data))

    # a function that takes an attachment and retrieves the file data from the filedata table
    @staticmethod
    def get_attachment_from_db(attachment):
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                SELECT * FROM filedata
                WHERE fileID = ?
                ''', (attachment.fileID,))
            for row in cursor.fetchall():
                attachment.data = row[2]
    
    @staticmethod
    def get_next_transaction_id():
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                SELECT MAX(id) FROM transactions
                '''
            )
            if cursor.fetchone()[0] is None:
                return 1
            return cursor.fetchone()[0] + 1
    
    @staticmethod
    def get_next_attachment_id():
        with Sql(Database.db_path) as cursor:
            cursor.execute('''
                SELECT MAX(id) FROM attachments
                '''
            )
            if cursor.fetchone()[0] is None:
                return 1
            return cursor.fetchone()[0] + 1








class Transaction:
    """
    A class to represent a credit card transaction

    Attributes
    ----------
    id : int
        The id of the transaction

    name : str
        name of the person who made the transaction

    amount : float
        the amount of money associated with the transaction

    date : str
        the date of the transaction

    attachments : list[attachment]
        Any files associated with the transaction (e.g. receipt scans)

    notes : str
        Any commentary associated with the transaction

    Methods
    ------
    overridden str():
        returns a string representing the transaction in the form name, amount, date
        used to premit representation of the object in pysimplegui listbox        
    """

    def __init__(self):
        self.id = None
        self.name = ''
        self.amount = 0
        self.date = ''
        self.attachments = []
        self.notes = ''

    def __str__(self):
        return 'Name: {} ; £{} ; Date: {}'.format(self.name, self.amount, self.date)


class Attachment:
    '''
    A class to represent a file attached to a transaction
    
        Attributes
        ----------
        id : int
            the id of the file

        name : str
            name of the file

        path : str
            path to the file

        filetype : str
            the type of file (e.g. image, pdf, etc.)

        data : raw data
            raw data of the file

        Methods
        ------
        overridden str():
            returns a string representing the attachment in the form name, path

        file_to_blob(file):
            converts a file to blob data

        blob_to_file(blob, name, ):
            converts a blob data to a file

        get_file_type(path):
            returns the file type of a file

        get_file_name(path):
            returns the file name of a file

        get_raw_data():
            gets the raw data of the file from the database

        
    '''
    
    def __init__(self, filepath):
        self.id = Database.get_next_attachment_id()
        self.name, self.filetype = os.path.splitext(filepath)
        self.filepath = filepath
        self.data = ''
        print(f"attachment created, id: {self.id}, name: {self.name}, filetype: {self.filetype}, filepath: {self.filepath}")
    
    def __str__(self):
        return '{} {}'.format(self.name, self.filepath)

    def file_to_blob(self, file):
        '''
        converts a file to blob data
        '''
        with open(file, 'rb') as f:
            self.data = f.read()

    def blob_to_file(self, blob, name):
        '''
        converts a blob data to a file
        '''
        with open(name, 'wb') as f:
            f.write(blob)

    def get_file_type(self, path):
        '''
        returns the file type of a file
        '''
        return path.split('.')[-1]

    def get_file_name(self, path):
        '''
        returns the file name of a file
        '''
        return path.split('/')[-1]

    def get_raw_data(self):
        '''
        gets the raw data of the file from the database
        '''
        data = get_attachment_from_db(self.id)
        self.data = data[0]


        

    


        


class select_db_window:
    """
    Builds a window whereby the user can select a database file for the programme to operate with

    Attributes
    ----------
    _parent : MainWindow
         The parent window which created the current window
    layout : list[list]
        The layout of the window
    window : sg.Window
        The window object

    Methods
    -------
    _create_layout : list[list]
        Builds the window layout and returns it to the caller

    ok_button_callback : None
        Sets the db_path variable on the parent window equal to the path value entered into the textbox
        in the current window

    
    run : None
        The mainloop of the window

    """
    def __init__(self, parent):
        self.close_window = False
        self._parent = parent
        self.layout = self._create_layout()
        self.window = sg.Window("Select a database file", layout = self.layout)

    def _create_layout(self):
        '''
        Returns layout for the window
        '''
        layout = [
            [sg.Text('Select database')],
            [sg.InputText(key='db_path'), sg.FileBrowse(target='db_path')],
        [sg.Button('OK', key=lambda: self.ok_button_callback()), sg.Button('Cancel', key='-CANCEL-')]
        ]
        return layout   

    def ok_button_callback(self):
        '''
        Sets the db_path variable on the parent window equal to the path value entered into the textbox
        in the current window
        '''
        Database.db_path = self.values['db_path']
        Database.prepare_tables()
        self.close_window = True

    def run(self):
        '''
        Mainloop for the window
        '''
        while True:
            self.event, self.values = self.window.Read()
            if callable(self.event):
                self.event()
                if self.close_window:
                    self.window.Close()
                    break
            elif self.event == '-CANCEL-':
                self.window.close()
                break
            elif self.event == sg.WIN_CLOSED:
                self.window.close()
                break


class view_transaction_window:
    """
    A window to view a transaction
    
        Attributes
        ----------
        _parent : MainWindow
            The parent window which created the current window
        
        layout : list[list]
            The layout of the window

        window : sg.Window
            The window object

        transaction : Transaction
            The transaction to be viewed

        Methods
        -------
        _create_layout : list[list]
            Builds the window layout and returns it to the caller

        ok_button_callback : None   
            Closes the window

        run : None
            The mainloop of the window

    """
    def __init__(self, parent, transaction):
        self.close_window = False
        self._parent = parent
        self.layout = self._create_layout(transaction)
        self.window = sg.Window("View transaction", layout = self.layout)
        self.transaction = transaction

    def _create_layout(self, transaction):
        '''
        Returns layout for the window
        '''
        layout = [
            [sg.Text('Name: {}'.format(transaction.name))],
            [sg.Text('Amount: {}'.format(transaction.amount))],
            [sg.Text('Date: {}'.format(transaction.date))],
            [sg.Text('Notes')],
            [sg.Multiline(transaction.notes, size=(40, 10))],
            [sg.Text('Attachments')],
            [sg.Listbox(values=Database.get_attachments_for_transaction(transaction.id), size=(40, 10))],
            [sg.Button('View attachment', key=lambda: self.view_attachment_callback())],
            [sg.Button('OK', key=lambda: self.ok_button_callback())]
        ]
        return layout

    def view_attachment_callback(self):
        pass

    def ok_button_callback(self):
        '''
        Closes the window
        '''
        self.close_window = True
    
    def run(self):
        '''
        Mainloop for the window
        '''
        while True:
            self.event, self.values = self.window.Read()
            if callable(self.event):
                self.event()
                if self.close_window:
                    self.window.Close()
                    break
            elif self.event == sg.WIN_CLOSED:
                self.window.close()
                break

class choose_attachment_window:
    """
    A window to choose an attachment to add to a transaction
    
        Attributes
        ----------
        _parent : MainWindow
            The parent window which created the current window
        
        layout : list[list]
            The layout of the window

        window : sg.Window
            The window object

        Methods
        -------
        _create_layout : list[list]
            Builds the window layout and returns it to the caller

        ok_button_callback : None   
            Closes the window

        run : None
            The mainloop of the window

    """
    def __init__(self, parent):
        self.close_window = False
        self.parent = parent
        self.layout = self._create_layout()
        self.window = sg.Window("Choose attachment", layout = self.layout)

    def _create_layout(self):
        '''
        Returns layout for the window
        '''
        layout = [
            [sg.Text('Select attachment')],
            [sg.InputText(key='attachment_path'), sg.FileBrowse(target='attachment_path')],
            [sg.Button('OK', key=lambda: self.ok_button_callback())],
            [sg.Button('Cancel', key='-CANCEL-')]
        ]
        return layout

    def ok_button_callback(self):
        attachment = Attachment(self.values['attachment_path'])
        self.parent.temp_attachments.append(attachment)
        self.close_window = True

    def run(self):
        '''
        Mainloop for the window
        '''
        while True:
            self.event, self.values = self.window.Read()
            if callable(self.event):
                self.event()
                if self.close_window:
                    self.window.Close()
                    break
            elif self.event == sg.WIN_CLOSED:
                self.window.close()
                break

