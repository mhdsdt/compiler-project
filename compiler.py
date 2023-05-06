from scanner.scanner import Scanner
from parser.parser import Parser

# Mahdi Saadatbakht     99105475
# Mohammad Mowlavi      99105753


class Compiler:
    def __init__(self, input_file):
        self.input_file = input_file

    def compile(self):
        parser = Parser(Scanner(self.input_file))
        parser.parse()


def main():
    compiler = Compiler('input.txt')
    compiler.compile()


if __name__ == '__main__':
    main()
