from scanner import Scanner

# Mahdi Saadatbakht     99105475
# Mohammad Mowlavi      99105753


class Compiler:
    def __init__(self, input_file):
        self.input_file = input_file

    def compile(self):
        scanner = Scanner(self.input_file)
        scanner.tokenize()


def main():
    compiler = Compiler('input.txt')
    compiler.compile()


if __name__ == '__main__':
    main()
