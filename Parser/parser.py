from anytree import Node, RenderTree, PreOrderIter

from scanner.enums_constants import TokenType
from utils.tables import ErrorsTable, ROOT_DIR
from Parser.grammar import Terminal, NonTerminal


class Parser:
    def __init__(self, scanner, grammar):
        self.root = NonTerminal(name='Program')
        self.scanner = scanner
        self.grammar = grammar
        self.errors = []
        self.stack = []
        self.table = dict()
        self.last_token = None
        self.create_parse_table()

    @staticmethod
    def get_first_set(terms):
        first_set = set()
        for term in terms:
            if isinstance(term, Terminal):
                first_set.add(term)
                break
            elif isinstance(term, NonTerminal):
                first_set |= set(term.first)
                if 'EPSILON' not in [term.name for term in term.first]:
                    break
        return first_set

    def create_parse_table(self):
        for non_terminal in self.grammar.non_terminals:
            for terminal in self.grammar.terminals:
                self.table[(non_terminal.name, terminal.name)] = None

        for rule in self.grammar.product_rules:
            lhs = rule.lhs
            first_set = self.get_first_set(rule.rhs)

            for terminal in first_set:
                if terminal.name != 'EPSILON':
                    self.table[(lhs.name, terminal.name)] = rule.rhs

            if 'EPSILON' in [term.name for term in first_set]:
                for terminal in lhs.follow:
                    self.table[(lhs.name, terminal.name)] = rule.rhs

    def get_rhs_from_table(self, top_of_stack):
        if self.last_token[0] in [TokenType.Id.value, TokenType.Num.value]:
            lexeme = self.last_token[0]
        else:
            lexeme = self.last_token[1]
        return self.table[(top_of_stack.name, lexeme)]

    def _update_stack(self, ):
        last_stmt = self.stack.pop()
        while len(self.stack) and last_stmt.name == 'EPSILON':
            last_stmt = self.stack.pop()

        if isinstance(last_stmt, NonTerminal):
            rhs = self.get_rhs_from_table(last_stmt)
            if not rhs or rhs[0].name == 'SYNCH':
                self.handle_panic(last_stmt)
            else:
                self.extend_stack(last_stmt, rhs)
        elif isinstance(last_stmt, Terminal):
            if self.last_token[0] in [TokenType.Id.value, TokenType.Num.value]:
                lexeme = self.last_token[0]
            else:
                lexeme = self.last_token[1]
            if lexeme == '$':
                Terminal('$', parent=self.root)
            elif last_stmt.name != lexeme:
                self.errors.append((self.scanner.get_current_line(), '', f'syntax error, missing {lexeme}'))
            elif self.stack:
                last_stmt.name = self.last_token
                self.last_token = self.get_next_token()

    def parse(self):
        self.stack.append(self.root)
        self.last_token = self.get_next_token()
        while self.stack:
            self._update_stack()
        self.export_parse_tree()
        self.export_syntax_errors()

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

    def get_next_token(self):
        token = self.scanner.get_next_token()
        return token

    def handle_panic(self, last_stmt):
        print('handle panic ---->', last_stmt)
        rhs = self.get_rhs_from_table(last_stmt)
        in_empty = False
        while not rhs:
            in_empty = True
            self.errors.append((self.scanner.get_current_line(), '', f'syntax error, illegal {self.last_token[1]}'))
            self.last_token = self.get_next_token()
            rhs = self.get_rhs_from_table(last_stmt)
            if self.last_token[0] == TokenType.EOF.value:
                break

        if in_empty:
            self.stack.append(last_stmt)

        if rhs and rhs[0].name != 'SYNCH':
            self.extend_stack(last_stmt, rhs)

        self.errors.append((self.scanner.get_current_line(), '', f'syntax error, missing {self.last_token[1]}'))

    def extend_stack(self, last_stmt, rhs):
        temp_stack = []
        for r in rhs:
            if isinstance(r, NonTerminal):
                temp_stack.append(NonTerminal(r.name, parent=last_stmt))
            elif isinstance(r, Terminal):
                temp_stack.append(Terminal(r.name, parent=last_stmt))

        for r in temp_stack[::-1]:
            if isinstance(r, NonTerminal):
                self.stack.append(r)
            elif isinstance(r, Terminal):
                self.stack.append(r)
            else:
                raise Exception(f'r is not either Terminal Or NonTerminal. {type(r)}')
