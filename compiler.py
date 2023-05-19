from scanner.scanner import Scanner
from Parser.parser import Parser
from Parser.grammar import Grammar

# Mahdi Saadatbakht     99105475
# Mohammad Mowlavi      99105753


class Compiler:
    def __init__(self, input_file):
        self.input_file = input_file

    def compile(self):
        parser = Parser(Scanner(self.input_file), Grammar())
        parser.parse()


def main():
    compiler = Compiler('input.txt')
    compiler.compile()


if __name__ == '__main__':
    main()


# input_file = 'input.txt'
# from scanner.scanner import Scanner
# from Parser.parser import Parser
# from Parser.grammar import Grammar
# Parser(Scanner(input_file), Grammar())
# <Parser.parser.Parser at 0x179a964c490>
# parser = Parser(Scanner(input_file), Grammar())
# from Parser.grammar import NonTerminal
# from Parser.grammar import NonTerminal, Terminal
# parser.get_rhs_from_table(NonTerminal('Declaration-initial'), 'void')
