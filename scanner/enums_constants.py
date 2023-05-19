from enum import Enum


class TokenType(Enum):
    Symbol = 'SYMBOL'
    Id = 'ID'
    Keyword = 'KEYWORD'
    Num = 'NUM'
    Comment = 'COMMENT'
    Whitespace = 'WHITESPACE'
    KeywordId = 'KEYWORDID'
    Unknown = 'UNKNOWN'
    EOF = 'EOF'


class Error(Enum):
    InvalidNumber = 'Invalid number'
    InvalidInput = 'Invalid input'
    UnmatchedComment = 'Unmatched comment'
    UnclosedComment = 'Unclosed comment'


def get_keywords():
    return ['break', 'else', 'if', 'int', 'repeat', 'return', 'until', 'void']


def get_symbols():
    return [':', ';', '[', ',', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<']


def get_white_spaces():
    return ['\n', ' ', '\r', '\t', '\v', '\f']


def get_digits():
    return [str(i) for i in range(0, 10)]


def get_alphabets():
    return [str(chr(i + 65)) for i in range(0, 26)] + [str(chr(i + 97)) for i in range(0, 26)]


def get_comments():
    return ['/', '*']
