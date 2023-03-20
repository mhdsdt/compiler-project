from utils.buffer import Buffer
from utils.tables import *


class Scanner:
    def __init__(self, input_file_name):
        self.buffer = Buffer(input_file_name)
        self.tokens = [[]]
        self.symbols = ['break', 'else', 'if', 'int', 'repeat', 'return', 'until', 'void']
        self.errors = []
        self.tokens_table, self.symbols_table, self.errors_table = None, None, None

    def get_current_line(self):
        return self.buffer.current_line

    def get_next_token(self):
        pass

    def tokenize(self):
        while True:
            tmp_current_line = self.get_current_line()
            token = self.get_next_token()
            if token is None:
                break
            if self.get_current_line() > tmp_current_line:
                self.tokens.append([])
            self.tokens[-1].append(token)

        self.__create_tables()
        self.__export_tables()

    def handle_errors(self):
        pass

    def __create_tables(self):
        self.tokens_table = TokensTable(self.tokens)
        self.symbols_table = SymbolsTable(self.symbols)
        self.errors_table = ErrorsTable(self.errors)

    def __export_tables(self):
        self.tokens_table.export()
        self.symbols_table.export()
        self.errors_table.export()
