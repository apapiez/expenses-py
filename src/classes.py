class Transaction:
    def __init__(self):
        self.name = ''
        self.amount = 0
        self.date = ''
        self.attachments = []
        self.notes = ''

    def __str__(self):
        return '{} {} {}'.format(self.name, self.amount, self.date)

