from anytree import Node, RenderTree

from scanner.dfa_handler import DFANode
from utils.tables import ErrorsTable, ROOT_DIR


class TerminalNode(Node):
    pass


class NonTerminalNode(Node):
    pass


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.errors = []
        self.root = NonTerminalNode(name='Program')
        self.stack = []
        self.table = []
        self.last_token = None

    def get_right_hand_side_from_table(self, top_of_stack):
        return []

    # def add_error(self, top_of_stack, token):
    #     self.errors.append((self.scanner.get_current_line(), 'syntax error, missing ]'))

    def _update_stack(self,):
        last_stmt = self.stack.pop()
        while len(self.stack) and last_stmt.name == "EPSILON":
            last_stmt = self.stack.pop()

        if isinstance(last_stmt, NonTerminalNode):
            right_hand_side = self.get_right_hand_side_from_table(last_stmt)
            if not right_hand_side or right_hand_side[0] == 'SYNCH':
                self.handle_panic(last_stmt)
            else:
                self.stack.append(Node(r, parent=last_stmt) for r in right_hand_side)
        elif isinstance(last_stmt, TerminalNode):
            if last_stmt.name != self.last_token.token_type:
                self.errors.append((self.scanner.get_current_line(), f"syntax error, missing {self.last_token.lexeme}"))
                self.remove_stmts(last_stmt)
            elif self.stack:
                self.last_token = self.scanner.get_next_token()

    def parse(self):
        self.stack.append(self.root)
        self.last_token = self.scanner.get_next_token()
        while self.stack:
            self._update_stack()

    def export_parse_tree(self):
        with open(ROOT_DIR + 'lexical_errors.txt', 'w') as f:
            for pre, _, node in RenderTree(self.root):
                f.write("%s%s\n" % (pre, node.name))

    def export_syntax_errors(self):
        errors_table = ErrorsTable(self.errors)
        errors_table.export_syntax_errors()

    def handle_panic(self, last_stmt):
        right_hand_side = self.get_right_hand_side_from_table(last_stmt)
        while not right_hand_side:
            self.errors.append((self.scanner.get_current_line(), f"syntax error, illegal {self.last_token.lexeme}"))
            self.last_token = self.scanner.get_next_token()
            right_hand_side = self.get_right_hand_side_from_table(last_stmt)

        self.errors.append((self.scanner.get_current_line(), f"syntax error, missing {self.last_token.lexeme}"))
        self.remove_stmts(right_hand_side[0])

    def remove_stmts(self, stmt):
        if stmt.parent:
            children = list(stmt.parent.children)
            children.remove(stmt)
            stmt.parent.children = tuple(children)
