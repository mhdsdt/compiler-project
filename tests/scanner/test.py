import os
import subprocess
import shutil
import filecmp


ROOT_DIR = '../../'
OUTPUT_FILES = ['lexical_errors.txt', 'symbol_table.txt', 'tokens.txt']


def is_output_correct(i):
    print(f'---------- T{i:02} ------------')
    result = True
    for file in OUTPUT_FILES:
        dst = f'./testcases/T{i:02}/{file}'
        is_identical = filecmp.cmp(ROOT_DIR + file, dst)
        if is_identical:
            print(f'{file.split(".")[0]}: PASSED')
        else:
            print(f'{file.split(".")[0]}: FAILED')
        result = is_identical and result

    return result


def remove_output_files():
    for file in OUTPUT_FILES:
        os.remove(ROOT_DIR + file)


def main():
    for i in range(1, 11):
        src = f'./testcases/T{i:02}/input.txt'
        dst = ROOT_DIR + 'input.txt'
        shutil.copyfile(src, dst)
        subprocess.run(['python', 'compiler.py'], cwd=ROOT_DIR)
        if is_output_correct(i):
            print(f'******* T{i:02} PASSED! *******')
        else:
            print(f'******* T{i:02} FAILED! *******')
        os.remove(dst)
        remove_output_files()


if __name__ == '__main__':
    main()
