import os
import subprocess
import shutil
import filecmp


ROOT_DIR = '../../'
OUTPUT_FILES = {'lexical_errors.txt': 0, 'symbol_table.txt': 0, 'tokens.txt': 0}


class Color:
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def get_number_of_tests():
    return len(next(os.walk('./testcases/'))[1])


def is_output_correct(i):
    print(f'---------- T{i:02} ------------')
    result = True
    for file in OUTPUT_FILES.keys():
        dst = f'./testcases/T{i:02}/{file}'
        is_identical = filecmp.cmp(ROOT_DIR + file, dst)
        if is_identical:
            OUTPUT_FILES[file] += 1
            string_to_print = f'{Color.GREEN}PASSED{Color.END}'
        else:
            string_to_print = f'{Color.RED}FAILED{Color.END}'
        print(f'{file.split(".")[0]}: {string_to_print}')
        result = is_identical and result

    return result


def remove_output_files():
    for file in OUTPUT_FILES.keys():
        os.remove(ROOT_DIR + file)


def main():
    num_tests = get_number_of_tests()
    num_passed_tests = 0
    for i in range(1, num_tests + 1):
        src = f'./testcases/T{i:02}/input.txt'
        dst = ROOT_DIR + 'input.txt'
        shutil.copyfile(src, dst)
        subprocess.run(['python', 'compiler.py'], cwd=ROOT_DIR)
        if is_output_correct(i):
            string_to_print = f'{Color.GREEN}{Color.BOLD}PASSED!{Color.END}'
            num_passed_tests += 1
        else:
            string_to_print = f'{Color.RED}{Color.BOLD}FAILED!{Color.END}'
        print(f'******* T{i:02} {string_to_print} *******\n')
        # os.remove(dst)
        # remove_output_files()

    for file, num_passed in OUTPUT_FILES.items():
        print(f'{file.split(".")[0]}: {num_passed} / {num_tests}')
    print(f'{Color.BOLD}TOTAL: {num_passed_tests} / {num_tests}{Color.END}')


if __name__ == '__main__':
    main()
