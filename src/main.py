import PySimpleGUI as sg
import sys
from classes import Transaction
from global_constants import *
from functions import *

class MainWindow:
    def __init__(self):
        self.db_path = None
        self.temp_attachments = []
        self.menu_def = [['&File', ['&Open database...::open_db_key']],]
        self.tab1_layout = [
            [sg.Text('Expenses')],
            [sg.Listbox(values=[], key='expenses', size=(50, 25))],
            [sg.Button('View'), sg.Button('Delete')]
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

    def add_test_transaction(self, *args, **kwargs):
        test_transaction = Transaction()
        test_transaction.amount = 100
        test_transaction.date = '2020-01-01'
        test_transaction.name = 'test'
        test_transaction.notes = 'test'
        self.window['expenses'].update(values=[test_transaction])

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

    def start(self):
        while True:
            event, values = self.window.read()
            if event == 'Exit':
                break
            elif event != None and 'open_db_key' in event:
                self.db_path = select_db()
                
            elif event == sg.WIN_CLOSED:
                break
            elif callable(event):
                event(values)

    def dance(self):
        print('dance')

if __name__ == '__main__':
    window = MainWindow()
    window.start()
            
