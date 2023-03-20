from util.buffer import Buffer


class Scanner:
    def __init__(self, input_file_name):
        self.buffer = Buffer(input_file_name)
        self.tokens = [[]]
        self.symbol_table = ['break', 'else', 'if', 'int', 'repeat', 'return', 'until', 'void']
        self.errors = []

    def _write_to_tokens_file(self):
        with open('tokens.txt', 'w') as tokens_file:
            for i, line_tokens in enumerate(self.tokens):
                tokens_as_string = [f'({token[0]}, {token[1]})' for token in line_tokens]
                tokens_file.write(f'{i + 1}.\t' + ' '.join(tokens_as_string))

    def _write_to_symbols_file(self):
        with open('symbol_table.txt', 'w') as symbols_file:
            for i, symbol in enumerate(self.symbol_table):
                symbols_file.write(f'{i + 1}.\t {symbol}\n')

    def _write_to_errors_file(self):
        with open('lexical_errors.txt', 'w') as errors_file:
            if not self.errors:
                return errors_file.write('There is no lexical error.\n')
            for error in self.errors:
                line_num, error_str, message = error
                errors_file.write(f'{line_num}.\t {error_str} - {message}\n')

    def _handle_errors(self):
        pass

    def get_next_token(self):
        pass

    def tokenize(self):
        self._write_to_tokens_file()
        self._write_to_symbols_file()
        self._write_to_errors_file()
