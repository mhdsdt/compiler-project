import os.path

ROOT_DIR = os.path.dirname(__file__) + '/../'


class TokensTable:
    def __init__(self, tokens: list):
        self.tokens = tokens

    def export(self):
        with open(ROOT_DIR + 'tokens.txt', 'w') as tokens_file:
            for i, line_tokens in enumerate(self.tokens):
                if line_tokens:
                    tokens_as_string = [f'({token[0]}, {token[1]})' for token in line_tokens]
                    tokens_file.write(f'{i + 1}.\t' + ' '.join(tokens_as_string) + ' \n')


class SymbolsTable:
    def __init__(self, symbols: list):
        self.symbols = symbols

    def export(self):
        with open(ROOT_DIR + 'symbol_table.txt', 'w') as symbols_file:
            for i, symbol in enumerate(self.symbols):
                symbols_file.write(f'{i + 1}.\t{symbol}\n')


class ErrorsTable:
    def __init__(self, errors: list):
        self.errors = {}
        for error in errors:
            line_num, error_str, message = error
            if self.errors.get(line_num):
                self.errors[line_num].append((error_str, message))
            else:
                self.errors[line_num] = [(error_str, message)]

    def export_lexical_errors(self):
        with open(ROOT_DIR + 'lexical_errors.txt', 'w') as errors_file:
            if not self.errors:
                return errors_file.write('There is no lexical error.')
            for line_num, errors in self.errors.items():
                errors_as_string = ' '.join([f'({error[0]}, {error[1]})' for error in errors])
                errors_file.write(f'{line_num}.\t{errors_as_string} \n')

    def export_syntax_errors(self):
        with open(ROOT_DIR + 'syntax_errors.txt', 'w') as f:
            if not self.errors:
                f.write("There is no syntax error.")
            for line_num, errors in self.errors.items():
                for error in errors:
                    f.write(f"#{line_num} : {error[1]} \n")
