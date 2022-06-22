import PySimpleGUI as sg
from classes import Transaction, Sql
Attachment = lambda name, filepath: (name, filepath)




def prepare_tables(db_path):
    '''
    Creates the required database tables if they aren't there
    
    Parameters:
        db_path (str) : the path to the database

    Returns:
        None
    '''
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filedata (
                id INTEGER PRIMARY KEY,
                fileID INTEGER,
                data BLOB
                )'''
        )
            

def add_transaction(db_path, transaction):
    '''
    Enters a new transaction into the transactions table
    Enters the associated attachments into the attachments table

    Parameters:
        db_path (str) : the path to the current database
        transaction (Transaction) : the transaction to add

    Returns:
        None
    '''


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
    '''
    Gets all transactions currently in the transactions table

    Parameters:
        db_path (str) : the path to the current database

    Returns:
        transactions (list[Transaction]) : the list of transactions in the database
        Does not populate the attachments list for each transaction -> see get_attachments_for_transaction
    
    '''

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
    '''
    Gets all the attachments associated with a given transaction

    Parameters:
        db_path (str) : the path to the current database
        transaction_id (int) : the id of the transaction to fetch attachments for
    
    Returns:
        attachments (list[Attachment]) : A list of attachment objects where the 
        transaction_id parameter in the table matches the transaction_id parameter

    '''
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

# a function that takes an attachment and reads the file data into a bytestring then inserts it into the filedata table
def add_attachment_to_db(db_path, attachment):
    with Sql(db_path) as cursor:
        cursor.execute('''
            INSERT INTO filedata (fileID, data)
            VALUES (?, ?)
            ''', (attachment.fileID, attachment.data))

# a function that takes an attachment and retrieves the file data from the filedata table
def get_attachment_from_db(db_path, attachment):
    with Sql(db_path) as cursor:
        cursor.execute('''
            SELECT * FROM filedata
            WHERE fileID = ?
            ''', (attachment.fileID,))
        for row in cursor.fetchall():
            attachment.data = row[2]



        



    

