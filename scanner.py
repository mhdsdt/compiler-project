from utils.buffer import Buffer
from utils.tables import *
from regex_builder import get_default_dfa
from dfa_handler import DFANode, ErrorNode, NonTokenizableNode
from enums_constants import get_keywords
from enums_constants import TokenType


class Scanner:
    def __init__(self, input_file_name):
        self.buffer = Buffer(input_file_name)
        self.tokens = [[]]
        self.symbols = get_keywords()
        self.errors = []
        self.tokens_table, self.symbols_table, self.errors_table = None, None, None

    def get_current_line(self):
        return self.buffer.current_line

    def get_next_token(self):
        curr_state = get_default_dfa()
        lexeme = ''
        while True:
            next_char = self.buffer.get_next_char()
            if not next_char:
                return
            lexeme += next_char
            curr_state = curr_state.accept(lexeme)
            if isinstance(curr_state, NonTokenizableNode):
                curr_state = get_default_dfa()
                lexeme = ''
            elif isinstance(curr_state, DFANode) and curr_state.finished:
                if curr_state.roll_back:
                    self.buffer.rollback()
                    lexeme = lexeme[: -1]
                return curr_state.get_token(lexeme)
            elif isinstance(curr_state, ErrorNode):
                self.errors.append((self.get_current_line(), curr_state.handle_error()))
                curr_state = get_default_dfa()
                lexeme = ''

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

    def __create_tables(self):
        self.tokens_table = TokensTable(self.tokens)
        self.symbols_table = SymbolsTable(self.symbols)
        self.errors_table = ErrorsTable(self.errors)

    def __export_tables(self):
        self.tokens_table.export()
        self.symbols_table.export()
        self.errors_table.export()
