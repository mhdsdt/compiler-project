import os.path

ROOT_DIR = os.path.dirname(__file__) + '/../'


class TokensTable:
    def __init__(self, tokens: list):
        self.tokens = tokens

    def export(self):
        with open(ROOT_DIR + 'tokens.txt', 'w') as tokens_file:
            for i, line_tokens in enumerate(self.tokens):
                tokens_as_string = [f'({token[0]}, {token[1]})' for token in line_tokens]
                tokens_file.write(f'{i + 1}.\t' + ' '.join(tokens_as_string))


class SymbolsTable:
    def __init__(self, symbols: list):
        self.symbols = symbols

    def export(self):
        with open(ROOT_DIR + 'symbol_table.txt', 'w') as symbols_file:
            for i, symbol in enumerate(self.symbols):
                symbols_file.write(f'{i + 1}.\t {symbol}\n')


class ErrorsTable:
    def __init__(self, errors: list):
        self.errors = errors

    def export(self):
        with open(ROOT_DIR + 'lexical_errors.txt', 'w') as errors_file:
            if not self.errors:
                return errors_file.write('There is no lexical error.\n')
            for error in self.errors:
                line_num, error_str, message = error
                errors_file.write(f'{line_num}.\t {error_str} - {message}\n')

