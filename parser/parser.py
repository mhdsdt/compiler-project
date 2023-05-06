from anytree import Node, RenderTree

from utils.tables import ErrorsTable, ROOT_DIR


class TerminalNode(Node):
    pass


class NonTerminalNode(Node):
    pass


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.errors = []
        self.root = NonTerminalNode(name='')

    def parse(self):
        pass

    def export_parse_tree(self):
        with open(ROOT_DIR + 'lexical_errors.txt', 'w') as f:
            for pre, _, node in RenderTree(self.root):
                f.write("%s%s\n" % (pre, node.name))

    def export_syntax_errors(self):
        errors_table = ErrorsTable(self.errors)
        errors_table.export_syntax_errors()
