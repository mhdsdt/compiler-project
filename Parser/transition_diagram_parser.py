from anytree import PreOrderIter, RenderTree

from Parser.grammar import NonTerminal, Terminal
from scanner.enums_constants import TokenType, get_symbols, get_keywords
from utils.tables import ROOT_DIR, ErrorsTable


class TransitionDiagramParser:
    def __init__(self, scanner, grammar):
        self.scanner = scanner
        self.grammar = grammar
        self.root = NonTerminal('Program')
        self.current_token = None
        self.errors = []
        self.unexpected_eof_reached = False

    def get_next_token(self):
        token = self.scanner.get_next_token()
        return token

    def parse(self):
        self.current_token = self.get_next_token()

        self.procedure(self.root)
        if not self.unexpected_eof_reached:
            self.match(TokenType.EOF.value, self.root)

        self.export_parse_tree()
        self.export_syntax_errors()

    def procedure(self, non_terminal: NonTerminal):
        # print('--------------------------')
        # print('Procedure called!')
        for rule in self.grammar.get_rules_by_lhs(non_terminal.name):
            if self.current_token[1] in rule.predict_set or \
                    self.current_token[0] in rule.predict_set:
                # print(f'rule: {rule.lhs} -> {" ".join([str(term) for term in rule.rhs])}')
                # print(rule.predict_set)
                # print(self.current_token)
                self.call_rule(non_terminal, rule.rhs)
                break
        else:
            # print('alo')
            if self.current_token[1] in non_terminal.follow:
                if 'EPSILON' not in [term.name for term in non_terminal.first]:
                    self.errors.append(
                        (self.scanner.get_current_line(), '', f'syntax error, missing {non_terminal.name}'))
                non_terminal.parent = None
                return
            else:
                # print('alo2')
                if self.eof_reached():
                    # print('alo3')
                    self.errors.append((self.scanner.get_current_line(), '', 'syntax error, Unexpected EOF'))
                    self.unexpected_eof_reached = True
                    non_terminal.parent = None
                    return
                illegal_lookahead = self.current_token[1]
                if self.current_token[0] in ['NUM', 'ID']:
                    illegal_lookahead = self.current_token[0]
                self.errors.append((self.scanner.get_current_line(), '', f'syntax error, illegal {illegal_lookahead}'))
                self.current_token = self.get_next_token()
                self.procedure(non_terminal)

    def call_rule(self, parent, rhs: list):
        # print('--------------------------')
        # print(f'Rule called!')
        for term in rhs:
            # print(f'self.unexpected_eof_reached: {self.unexpected_eof_reached}')
            if self.unexpected_eof_reached:
                return
            elif isinstance(term, NonTerminal):
                self.procedure(NonTerminal(term.name, parent=parent))
            elif isinstance(term, Terminal):
                self.match(term.name, parent)

    def match(self, expected_token: str, parent):
        # print('--------------------------')
        # print(f'Match called! - {expected_token}, {parent}')
        correct = False
        if expected_token in ['NUM', 'ID']:
            correct = self.current_token[0] == expected_token
        elif (expected_token in get_keywords()) or (expected_token in get_symbols() or expected_token == '=='):
            correct = self.current_token[1] == expected_token

        if correct:
            Terminal(f'({self.current_token[0]}, {self.current_token[1]})', parent=parent)
            self.current_token = self.get_next_token()
        elif expected_token == 'EPSILON':
            Terminal('EPSILON', parent=parent)
        elif expected_token == TokenType.EOF.value:
            # print('mmd')
            Terminal('$', parent=parent)
        else:
            self.errors.append((self.scanner.get_current_line(), '', f'syntax error, missing {expected_token}'))

    def eof_reached(self):
        return self.current_token[0] == TokenType.EOF.value

    def export_parse_tree(self):
        for node in PreOrderIter(self.root):
            if node.name == 'EPSILON':
                node.name = 'epsilon'
            elif type(node.name) is tuple:
                node.name = f'({node.name[0]}, {node.name[1]})'
        with open(ROOT_DIR + 'parse_tree.txt', 'w', encoding='utf-8') as f:
            string = ''
            for pre, _, node in RenderTree(self.root):
                string += f'{pre}{node.name}\n'
            f.write(string[:-1])

    def export_syntax_errors(self):
        errors_table = ErrorsTable(self.errors)
        errors_table.export_syntax_errors()
