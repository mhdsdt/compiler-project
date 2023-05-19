from anytree import Node, RenderTree

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

    def create_parse_table(self):
        for rule in self.grammar.product_rules:
            self.table[rule.lhs.name] = dict()
            self.table[rule.lhs.name][rule.lhs.first.name] = [p.name for p in rule.rhs]

        for nt in self.grammar.non_terminals:
            for follow in nt.follow:
                if not self.table.get(nt.name).get(follow):
                    self.table[nt.name][follow.name] = ['SYNCH']

    def get_rhs_from_table(self, top_of_stack):
        lexeme = self.last_token[1]
        return self.table.get(top_of_stack).get(lexeme)

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
                self.last_token = self.scanner.get_next_token()

    def parse(self):
        self.stack.append(self.root)
        self.last_token = self.scanner.get_next_token()
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

    def handle_panic(self, last_stmt):
        rhs = self.get_rhs_from_table(last_stmt)
        while not rhs:
            self.errors.append((self.scanner.get_current_line(), f'syntax error, illegal {self.last_token.lexeme}'))
            self.last_token = self.scanner.get_next_token()
            rhs = self.get_rhs_from_table(last_stmt)

        self.errors.append((self.scanner.get_current_line(), f'syntax error, missing {self.last_token.lexeme}'))
