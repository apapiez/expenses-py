from select import select
import PySimpleGUI as sg
import sys
from classes import Transaction, select_db_window, Database, Sql, view_transaction_window
from global_constants import *

class MainWindow:
    def __init__(self):
        self.db_path = None
        self.temp_attachments = []
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
            [sg.Button('Add', key=lambda values: self.dance(values))],
            [sg.Button('Clear', key=lambda values: print(values))]
        ]
        self.layout = [
            [sg.Menu(self.menu_def)],
            [sg.TabGroup([[sg.Tab('View Expenses', self.tab1_layout), sg.Tab('New Expense', self.tab2_layout)]], background_color='black')],
            [sg.Button('Add test transaction', key=lambda values: self.add_test_transaction(values)), sg.Button('Exit')]
        ]
        
        self.window = sg.Window('Expense Tracker', self.layout)

    def update_transactions(self):
        self.window['expenses'].update(values=Database.get_all_transactions())

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
        CLOSE = False

        def attachment_chosen(*args, **kwargs):
            self.temp_attachments.append(values['attachment_path'])
            self.window['attachments'].update(values=self.temp_attachments)
            nonlocal CLOSE
            CLOSE = True

        def attachment_cancelled(*args, **kwargs):
            nonlocal CLOSE
            CLOSE = True


        layout = [
            [sg.Text("Choose an attachment"), sg.InputText(key='attachment_path'), sg.FileBrowse(target='attachment_path')],
            [sg.Button('Add', key=lambda values: attachment_chosen(values)), sg.Button('Cancel', key = lambda values: attachment_cancelled(values))]
            ]

        window = sg.Window('Choose an attachment', layout)

        while CLOSE == False:
            event, values = window.read()
            if event == 'Exit':
                break
            elif event == sg.WIN_CLOSED:
                break
            elif callable(event):
                event(values)
        
        if CLOSE == True:
            window.close()
    

    def remove_attachment(self, *args, **kwargs):
        if ('v' in kwargs):
            print(kwargs['v'])

    def view_transaction(self, *args, **kwargs):
        if Database.db_path in ['', None]:
            sg.Popup('Please open a database first')
            return
        if len(self.values['expenses']) == 0:
            sg.Popup('Please select a transaction')
            return
        if len(self.window['expenses'].values) == 0:
            sg.Popup('There are no transactions to view!')
            return
        self.window.Hide()
        w = view_transaction_window(self, transaction=self.values['expenses'][0])
        w.run()
        self.window.UnHide()

    def delete_button_callback(self, *args, **kwargs):
        selected_transaction : Transaction = self.values['expenses'][0]
        Database.delete_transaction(selected_transaction.id)
        self.update_transactions()



    def start(self):
        while True:
            event, values = self.window.read()
            self.event, self.values = event, values #hack becuase I need to refactor
            if event == 'Exit':
                break
            elif not callable(event) and event != None and 'open_db_key' in event :
                self.window.Hide()
                w = select_db_window(self)
                w.run()
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
            
