import os
import subprocess
import shutil
import filecmp


FILES = ['lexical_errors.txt', 'symbol_table.txt', 'tokens.txt']


def is_output_correct(i):
    print(f'-------- T{i:02} ----------')
    result = True
    for file in FILES:
        dst = f'./testcases/T{i:02}/{file}'
        is_identical = filecmp.cmp(file, dst)
        if is_identical:
            print(f"{file.split('.')}: PASSED")
        else:
            print(f"{file.split('.')}: FAILED")
        result = is_identical and result

    return result


def remove_output_files():
    for file in FILES:
        os.remove(file)


def main():
    for i in range(1, 11):
        src = f'./testcases/T{i:02}/input.txt'
        dst = './input.txt'
        shutil.copyfile(src, dst)
        subprocess.run(["python", "compiler.py"])
        if is_output_correct(i):
            print(f'******* TEST {i:02} PASSED! *******')
        else:
            print(f'******* TEST {i:02} FAILED! *******')
        os.remove(dst)
        remove_output_files()


if __name__ == '__main__':
    main()
