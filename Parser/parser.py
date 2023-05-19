from anytree import Node, RenderTree

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
    def get_first_set(symbols):
        first_set = set()
        for symbol in symbols:
            if isinstance(symbol, Terminal):
                first_set.add(symbol)
                break
            elif isinstance(symbol, NonTerminal):
                first_set |= set(symbol.first)
                if Terminal('EPSILON') not in symbol.first:
                    break
        return first_set

    def create_parse_table(self):
        for non_terminal in self.grammar.non_terminals:
            for terminal in self.grammar.terminals:
                self.table[(non_terminal, terminal)] = None

        for rule in self.grammar.product_rules:
            lhs = rule.lhs
            first_set = self.get_first_set(rule.rhs)

            for terminal in first_set:
                if terminal.name != 'EPSILON':
                    self.table[(lhs, terminal)] = rule

            if 'EPSILON' in [term.name for term in first_set]:
                follow_set = lhs.follow
                for terminal in follow_set:
                    self.table[(lhs, terminal)] = rule

    def get_rhs_from_table(self, top_of_stack):
        lexeme = self.last_token[1]
        print(top_of_stack, lexeme)
        return self.table.get((top_of_stack, lexeme))

    def _update_stack(self, ):
        last_stmt = self.stack.pop()
        while len(self.stack) and last_stmt.name == 'EPSILON':
            last_stmt = self.stack.pop()

        if isinstance(last_stmt, NonTerminal):
            rhs = self.get_rhs_from_table(last_stmt)
            if not rhs or rhs[0] == 'SYNCH':
                self.handle_panic(last_stmt)
            else:
                self.stack.append(Node(r, parent=last_stmt) for r in rhs)
        elif isinstance(last_stmt, Terminal):
            if last_stmt.name != self.last_token.token_type:
                self.errors.append((self.scanner.get_current_line(), f'syntax error, missing {self.last_token.lexeme}'))
            elif self.stack:
                self.last_token = self.get_next_token()

    def parse(self):
        self.stack.append(self.root)
        self.last_token = self.get_next_token()
        while self.stack:
            self._update_stack()

        self.export_parse_tree()
        self.export_syntax_errors()

    def export_parse_tree(self):
        with open(ROOT_DIR + 'parse_tree.txt', 'w') as f:
            for pre, _, node in RenderTree(self.root):
                f.write('%s%s\n' % (pre, node.name))

    def export_syntax_errors(self):
        errors_table = ErrorsTable(self.errors)
        errors_table.export_syntax_errors()

    def get_next_token(self):
        token = self.scanner.get_next_token()
        print('token:', token)
        return token

    def handle_panic(self, last_stmt):
        rhs = self.get_rhs_from_table(last_stmt)
        while not rhs:
            self.errors.append((self.scanner.get_current_line(), f'syntax error, illegal {self.last_token[1]}'))
            self.last_token = self.get_next_token()
            rhs = self.get_rhs_from_table(last_stmt)
            if self.last_token[0] == TokenType.EOF.value:
                break

        self.errors.append((self.scanner.get_current_line(), f'syntax error, missing {self.last_token[1]}'))
