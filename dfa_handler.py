from regex_builder import *
from enums_constants import *


class DFANode:

    def __init__(self, token_type, finished=False, roll_back=False):
        self.finished = finished
        self.token_type = token_type
        self.roll_back = roll_back
        self.next_nodes = []

    def add_next_node(self, edge, next_node):
        self.next_nodes.append((next_node, edge))

    def accept(self, lexeme):
        for node, rexp_edge in self.next_nodes:
            if rexp_edge.can_accept(lexeme[-1]):
                return node
        return ErrorNode(self, lexeme)

    def get_token(self, lexeme):
        if self.token_type == TokenType.KeywordId.value:
            if lexeme in get_keywords():
                return TokenType.Keyword.value, lexeme
            return TokenType.Id.value, lexeme
        if self.token_type == TokenType.Num.value:
            return TokenType.Num.value, lexeme
        if self.token_type == TokenType.Comment.value:
            return TokenType.Comment.value, lexeme
        if self.token_type == TokenType.Whitespace.value:
            return TokenType.Whitespace.value, lexeme
        if self.token_type == TokenType.Symbol.value:
            return TokenType.Symbol.value, lexeme


class NonTokenizableNode(DFANode):
    def __init__(self, token_type, finished=False, roll_back=False):
        super(NonTokenizableNode, self).__init__(token_type, finished=finished, roll_back=roll_back)


class ErrorNode:

    def __init__(self, dfa_node, lexeme):
        self.dfa_node = dfa_node
        self.lexeme = lexeme

    def handle_error(self):
        if self.lexeme[-1] not in get_comments() + get_symbols() + get_digits() + get_alphabets() + get_white_spaces():
            return self.lexeme, Error.InvalidInput.value
        if self.dfa_node.token_type == TokenType.Num.value:
            return self.lexeme, Error.InvalidNumber.value
        if self.dfa_node.token_type == TokenType.Comment.value:
            if self.lexeme[0] == '/':
                return '/* comm…', Error.UnclosedComment.value
            return '*/', Error.UnmatchedComment.value


class Edge:

    def __init__(self, token_type):
        self.token_type = token_type
        self.char = None

    def set_char(self, char):
        self.char = char

    def get_token_type(self):
        return self.token_type


class RegexEdge(Edge):

    def __init__(self, token_type):
        super(RegexEdge, self).__init__(token_type)
        self.accepted_chars = []

    def accept(self, char):
        if char not in self.accepted_chars:
            self.accepted_chars.append(char)
        return self

    def reject(self, char):
        if char in self.accepted_chars:
            self.accepted_chars.remove(char)
        return self

    def can_accept(self, char):
        return char in self.accepted_chars

    def accept_digits(self):
        for d in get_digits():
            self.accept(d)
        return self

    def accept_alphabets(self):
        for a in get_alphabets():
            self.accept(a)
        return self

    def accept_symbols(self):
        for symbol in get_symbols():
            self.accept(symbol)
        return self

    def accept_white_spaces(self):
        for white_space in get_white_spaces():
            self.accept(white_space)
        return self

    def accept_comments(self):
        for c in get_comments():
            self.accept(c)
        return self
