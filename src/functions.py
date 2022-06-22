import sqlite3 as sql
import PySimpleGUI as sg
from classes import Transaction
Attachment = lambda name, filepath: (name, filepath)

#context manager for sqlite3
class Sql:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sql.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

#prepare tables
def prepare_tables(db_path):
    with Sql(db_path) as cursor:
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

def add_transaction(db_path, transaction):
    with Sql(db_path) as cursor:
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

def get_all_transactions(db_path):
    with Sql(db_path) as cursor:
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

def get_attachments_for_transaction(db_path, transaction_id):
    with Sql(db_path) as cursor:
        cursor.execute('''
            SELECT * FROM attachments
            WHERE transaction_id = ?
            ''', (transaction_id,))
        attachments = []
        for row in cursor.fetchall():
            attachment = Attachment(row[2], row[3])
            attachments.append(attachment)
        return attachments

def add_attachments_to_transaction(transaction, attachments):
    for attachment in attachments:
        transaction.attachments.append(attachment)

def delete_transaction(db_path, transaction_id):
    with Sql(db_path) as cursor:
        cursor.execute('''
            DELETE FROM transactions
            WHERE id = ?
            ''', (transaction_id,))
        cursor.execute('''
            DELETE FROM attachments
            WHERE transaction_id = ?
            ''', (transaction_id,))

def modify_transaction(db_path, transaction):
    with Sql(db_path) as cursor:
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

def select_db():
    CLOSE = False

    def close_window():
        nonlocal CLOSE
        CLOSE = True

    layout = [
        [sg.Text('Select database')],
        [sg.InputText(key='db_path'), sg.FileBrowse(target='db_path')],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]
    window = sg.Window('Select database', layout)
    
    while CLOSE == False:
        event, values = window.read()
        if event == 'OK':
            close_window()
            return values['db_path']
        elif event == 'Cancel':
            close_window()
            return None

        



    

