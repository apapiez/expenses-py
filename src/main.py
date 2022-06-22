from select import select
import PySimpleGUI as sg
import sys
from classes import Transaction, select_db_window, Database, Sql, view_transaction_window, choose_attachment_window, FileOperations
from global_constants import *
import configparser
import os
import atexit





cfg_path = os.path.join(os.path.dirname(__file__), 'config.ini')
atexit.register(FileOperations.delete_temp_dir)



class MainWindow:
    def __init__(self):
        self._config_parser = configparser.ConfigParser()
        self._config_parser.read(cfg_path)
        print(self._config_parser.sections())
        self.db_path = self._config_parser['DATABASE']['db_path']
        Database.db_path = self.db_path
        self.temp_attachments = []
        self.transactions = []
        self.menu_def = [['&File', ['&Open database...::open_db_key']],]
        self.tab1_layout = [
            [sg.Text('Expenses')],
            [sg.Listbox(values=[], key='expenses', size=(50, 25))],
            [sg.Button('View', key=lambda values: self.view_transaction()), sg.Button('Delete', key=lambda values: self.delete_button_callback())]
        ]
        self.tab2_layout = [
            [sg.Text('New Expense')],
            [sg.Text('Name', size=SIZE_LHS), sg.InputText(key='name', justification='right')],
            [sg.Text('Amount', size=SIZE_LHS), sg.InputText(key='amount')],
            [sg.Text('Date', size=SIZE_LHS), sg.Push(), sg.CalendarButton(button_text='Pick Date', target='date', format="%d-%m-%Y"), sg.InputText(key='date', size=(15,))],
            [sg.Text('Attachments', size=SIZE_LHS), sg.Push(), sg.Listbox(values=self.temp_attachments, size=(40, 10), key='attachments')],
            [sg.Push(), sg.Button('Add', key=lambda values: self.choose_attachment(values)), sg.Button('Remove', key=lambda values: self.remove_attachment(v=values))],
            [sg.Text('Notes', size=SIZE_LHS), sg.Push(), sg.Multiline(key='notes', size=(40, 10))],
            [sg.Button('Add', key=lambda values: self.add_transaction_callback())],
            [sg.Button('Clear', key=lambda values: print(values))]
        ]
        self.layout = [
            [sg.Menu(self.menu_def)],
            [sg.TabGroup([[sg.Tab('View Expenses', self.tab1_layout), sg.Tab('New Expense', self.tab2_layout)]], background_color='black')],
            [sg.Button('Add test transaction', key=lambda values: self.add_test_transaction(values)), sg.Button('Exit')]
        ]
        
        self.window = sg.Window('Expense Tracker', self.layout)
        self.window.Finalize()

    def update_transactions(self):
        self.transactions = Database.get_all_transactions()
        self.window['expenses'].update(values=self.transactions)

    def update_temp_attachments(self):
        self.window['attachments'].update(values=self.temp_attachments)

    def add_test_transaction(self, *args, **kwargs):
        if Database.db_path in ['', None]:
            sg.Popup('Please open a database first')
            return
        test_transaction = Transaction()
        test_transaction.amount = 100
        test_transaction.date = '2020-01-01'
        test_transaction.name = 'test'
        test_transaction.notes = 'test'
        Database.add_transaction(test_transaction)
        self.update_transactions()

    def choose_attachment(self, *args, **kwargs):
        w = choose_attachment_window(self)
        self.window.Hide()
        w.run()
        self.update_temp_attachments()
        self.window.UnHide()

    def remove_attachment(self, *args, **kwargs):
        self.temp_attachments.remove(self.values['attachments'][0])
        self.update_temp_attachments()

    def view_transaction(self, *args, **kwargs):
        if Database.db_path in ['', None]:
            sg.Popup('Please open a database first')
            return
        if len(self.values['expenses']) == 0:
            sg.Popup('Please select a transaction')
            return
        self.window.Hide()
        w = view_transaction_window(self, transaction=self.values['expenses'][0])
        w.run()
        self.window.UnHide()

    def delete_button_callback(self, *args, **kwargs):
        if Database.db_path in ['', None]:
            sg.Popup('Please open a database first')
            return
        if len(self.values['expenses']) == 0:
            sg.Popup('Please select a transaction')
            return
        selected_transaction : Transaction = self.values['expenses'][0]
        Database.delete_transaction(selected_transaction.id)
        self.update_transactions()

    def add_transaction_callback(self, *args, **kwargs):
        if Database.db_path in ['', None]:
            sg.Popup('Please open a database first')
            return
        transaction = Transaction()
        transaction.amount = self.values['amount']
        transaction.date = self.values['date']
        transaction.name = self.values['name']
        transaction.notes = self.values['notes']
        transaction.attachments = self.temp_attachments
        Database.add_transaction(transaction)
        self.update_transactions()
        self.temp_attachments = []
        self.update_temp_attachments()  
        self.window['name'].update('')
        self.window['amount'].update('')
        self.window['date'].update('')
        self.window['notes'].update('')
        




    def start(self):
        if self.db_path not in ['', None]:
            self.update_transactions()
        while True:
            event, values = self.window.read()
            self.event, self.values = event, values #hack becuase I need to refactor
            if event == 'Exit':
                break
            elif not callable(event) and event != None and 'open_db_key' in event :
                self.window.Hide()
                w = select_db_window(self)
                w.run()
                self._config_parser['DATABASE']['db_path'] = Database.db_path
                with open(cfg_path, 'w') as configfile:
                    self._config_parser.write(configfile)
                self.update_transactions()
                self.window.UnHide()                
            elif event == sg.WIN_CLOSED:
                break
            elif callable(event):
                event(values)

    def dance(self):
        print('dance')
        

if __name__ == '__main__':
    window = MainWindow()
    window.start()
            
