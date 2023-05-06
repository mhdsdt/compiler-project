from scanner.enums_constants import *


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
        if self.dfa_node.token_type == TokenType.Num.value:
            return self.lexeme, Error.InvalidNumber.value
        if self.lexeme.startswith("/*"):
            if len(self.lexeme) < 8:
                return self.lexeme, Error.UnclosedComment.value
            return self.lexeme[0:7] + "...", Error.UnclosedComment.value
        if self.lexeme == "*/":
            return self.lexeme, Error.UnmatchedComment.value
        if self.lexeme[0] == '/' and self.lexeme[1] != '#':
            self.dfa_node.roll_back = True
        return self.lexeme, Error.InvalidInput.value


class RegexEdge:

    def __init__(self):
        self.accepted_range = []
        self.rejected_range = []

    def accept(self, start, end=None):
        if not end:
            end = start
        self.accepted_range.append((start, end))
        return self

    def reject(self, start, end=None):
        if not end:
            end = start
        self.rejected_range.append((start, end))
        return self

    def is_in_accepted(self, char):
        for start, end in self.accepted_range:
            if start <= char <= end:
                return True
        return False

    def is_not_in_rejected(self, char):
        for start, end in self.rejected_range:
            if start <= char <= end:
                return False
        return True

    def can_accept(self, char):
        if len(self.rejected_range) == 0:
            return self.is_in_accepted(char)
        elif len(self.accepted_range) == 0:
            return self.is_not_in_rejected(char)
        else:
            return self.is_in_accepted(char) and self.is_not_in_rejected(char)

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
