from tests import tester
OUTPUT_FILES = {'lexical_errors.txt': 0, 'symbol_table.txt': 0, 'tokens.txt': 0}


if __name__ == '__main__':
    tester.test(output_files=OUTPUT_FILES, tests_path='scanner/testcases')
