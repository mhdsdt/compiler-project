from scanner.scanner import Scanner
from Parser.parser import Parser

from Parser.grammar import create_grammar

# Mahdi Saadatbakht     99105475
# Mohammad Mowlavi      99105753


class Compiler:
    def __init__(self, input_file):
        self.input_file = input_file

    def compile(self):
        parser = Parser(Scanner(self.input_file), create_grammar())
        parser.parse()


def main():
    compiler = Compiler('input.txt')
    compiler.compile()


if __name__ == '__main__':
    main()
