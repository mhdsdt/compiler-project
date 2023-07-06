symbol_table = {'KEYWORD': ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'],
                'ID': []}


def search_in_symbol_table(item, scope_num=0):
    for i in symbol_table['ID'][::-1]:
        if item == i[0] and i[3] <= scope_num:
            return True
    return False


class CodeGen:
    def __init__(self):
        self.SS = list()
        self.PB = dict()
        self.break_stack = list()
        self.current_scope = 0
        self.return_stack = list()
        self.index = 0
        self.temp_address = 500
        self.semantic_errors = []
        self.operations_dict = {'+': 'ADD', '-': 'SUB', '<': 'LT', '==': 'EQ'}
        self.id_type = 'void'
        self.isLoop = []
        self.isMult = False

    def find_address(item):
        if item == 'output':
            return item
        for i in symbol_table['ID'][::-1]:
            if item == i[0]:
                return i[2]

    def call(self, name, lookahead):
        self.__getattribute__(name[1:])(lookahead)
        self.export('')

    def export(self, path):
        with open('output1.txt', "a") as f:
            # for i in sorted(self.PB.keys()):
            f.write(f'{self.__dict__}\n')
            f.write('==================================\n')

    def insert_code(self, a, b, c='', d=''):
        self.PB[self.index] = f'({a}, {b}, {c}, {d})'
        self.index += 1

    def get_temp(self, count=1):
        address = str(self.temp_address)
        for _ in range(count):
            self.insert_code('ASSIGN', '#0', str(self.temp_address))
            self.temp_address += 4
        return address

    def define_variable(self, lookahead):

        var_id = self.SS.pop()

        self.void_check(var_id)
        address = self.get_temp()
        symbol_table['ID'].append((var_id, 'int', address, self.current_scope))

    def define_array(self, lookahead):
        array_size, array_id = int(self.SS.pop()[1:]), self.SS.pop()

        self.void_check(array_id)
        address = self.get_temp()
        array_space = self.get_temp(array_size)
        self.insert_code('ASSIGN', f'#{array_space}', address)
        symbol_table['ID'].append((array_id, 'int*', address, self.current_scope))

    def get_id_type(self, lookahead):
        self.id_type = lookahead

    def push_id(self, lookahead):
        self.SS.append(lookahead[2])

    def get_id(self, lookahead):
        self.scope_check(lookahead)
        self.SS.append(CodeGen.find_address(lookahead[2]))

    def push_num(self, lookahead):
        self.SS.append(f'#{lookahead[2]}')

    def push_operator(self, lookahead):
        self.SS.append(lookahead[2])

    def make_op(self, lookahead):
        operand_2 = self.SS.pop()
        operator = self.SS.pop()
        operand_1 = self.SS.pop()
        self.type_mismatch(lookahead, operand_1, operand_2)
        address = self.get_temp()
        self.insert_code(self.operations_dict[operator], operand_1, operand_2, address)
        self.SS.append(address)

    def assign_operation(self, lookahead):
        self.insert_code('ASSIGN', self.SS[-1], self.SS[-2])
        self.SS.pop()

    def multiply(self, lookahead):
        res = self.get_temp()
        self.isMult = True
        self.type_mismatch(lookahead, self.SS[-2], self.SS[-1])
        self.isMult = False
        self.insert_code('MULT', self.SS[-1], self.SS[-2], res)
        self.SS.pop()
        self.SS.pop()
        self.SS.append(res)

    def define_array_argument(self, lookahead):

        temp = symbol_table['ID'][-1]
        del symbol_table['ID'][-1]

        symbol_table['ID'].append((temp[0], 'int*', temp[2], temp[3]))

    def array_index(self, lookahead):
        idx, array_address = self.SS.pop(), self.SS.pop()
        temp, result = self.get_temp(), self.get_temp()
        self.insert_code('MULT', '#4', idx, temp)
        self.insert_code('ASSIGN', f'{array_address}', result)
        self.insert_code('ADD', result, temp, result)
        self.SS.append(f'@{result}')

    def implicit_output(self, lookahead):
        if self.SS[-2] == 'output':
            self.insert_code('PRINT', self.SS.pop())

    def save(self, lookahead):
        self.SS.append(self.index)
        self.index += 1

    def label(self, lookahead):
        self.SS.append(self.index)

    def jpf_save(self, lookahead):
        dest = self.SS.pop()
        src = self.SS.pop()
        self.PB[dest] = f'(JPF, {src}, {self.index + 1}, )'
        self.SS.append(self.index)
        self.index += 1

    def jump(self, lookahead):
        dest = int(self.SS.pop())
        self.PB[dest] = f'(JP, {self.index}, , )'

    def repeat(self, lookahead):
        self.PB[int(self.SS[-1])] = f'(JPF, {self.SS[-2]},{self.SS[-3]}, )'
        self.PB[self.index] = f'(JP,  {self.index + 1}, , )'
        self.index += 1
        self.SS.pop(), self.SS.pop(), self.SS.pop()

    def start_loop(self, lookahead):
        self.isLoop.append(1)
        self.break_stack.append('b')

    def end_loop(self, lookahead):
        latest_block = len(self.break_stack) - self.break_stack[::-1].index('b') - 1
        for item in self.break_stack[latest_block + 1:]:
            self.PB[item] = f'(JP, {self.index}, , )'
        self.break_stack = self.break_stack[:latest_block]
        self.isLoop.pop()

    def break_loop(self, lookahead):
        self.break_check(lookahead)
        self.break_stack.append(self.index)
        self.index += 1

    def clean_up(self, lookahead):
        self.SS.pop()

    def end_function(self, lookahead):
        self.SS.pop(), self.SS.pop(), self.SS.pop()
        for item in symbol_table['ID'][::-1]:
            if item[1] == 'function':
                if item[0] == 'main':
                    self.PB[self.SS.pop()] = f'(ASSIGN, #0, {self.get_temp()}, )'
                    return
                break
        self.PB[self.SS.pop()] = f'(JP, {self.index}, , )'

    def call_function(self, lookahead):
        if self.SS[-1] != 'output':
            args, attributes = [], []
            for i in self.SS[::-1]:
                if isinstance(i, list):
                    attributes = i
                    break
                args = [i] + args
            self.parameter_num_matching(lookahead, args, attributes)
            for var, arg in zip(attributes[1], args):
                self.parameter_type_matching(lookahead, var, arg, attributes[1].index(var) + 1)
                self.insert_code('ASSIGN', arg, var[2])
                self.SS.pop()
            for i in range(len(args) - len(attributes[1])):
                self.SS.pop()
            self.SS.pop()
            self.insert_code('ASSIGN', f'#{self.index + 2}', attributes[2])
            self.insert_code('JP', attributes[-1])
            result = self.get_temp()
            self.insert_code('ASSIGN', attributes[0], result)
            self.SS.append(result)

    def start_params(self, lookahead):
        func_name = self.SS.pop()
        self.SS.append(self.index)
        self.index += 1
        self.SS.append(func_name)
        symbol_table['ID'].append('s')

    def push_index(self, lookahead):
        self.SS.append(f'#{self.index}')

    def start_func(self, lookahead):
        return_address = self.get_temp()
        current_index = self.index
        return_value = self.get_temp()
        self.SS.append(return_value)
        self.SS.append(return_address)
        func_name = self.SS[-3]
        print(return_value, return_address)
        args_start_idx = symbol_table['ID'].index('s')
        func_args = symbol_table['ID'][args_start_idx + 1:]
        symbol_table['ID'].pop(args_start_idx)
        symbol_table['ID'].append(
            (func_name, 'function', [return_value, func_args, return_address, current_index], self.current_scope))

    def new_return(self, lookahead):
        self.return_stack.append('b')

    def save_return(self, lookahead):
        self.return_stack.append((self.index, self.SS[-1]))
        self.SS.pop()
        self.index += 2

    def return_anyway(self, lookahead):
        if self.SS[-3] != 'main':
            return_address = self.SS[-1]
            self.insert_code('JP', f'@{return_address}')

    def end_return(self, lookahead):
        latest_func = len(self.return_stack) - self.return_stack[::-1].index('b') - 1
        return_value = self.SS[-2]
        return_address = self.SS[-1]
        for item in self.return_stack[latest_func + 1:]:
            self.PB[item[0]] = f'(ASSIGN, {item[1]}, {return_value}, )'
            self.PB[item[0] + 1] = f'(JP, @{return_address}, , )'

        self.return_stack = self.return_stack[:latest_func]

    def scope_check(self, lookahead):
        if search_in_symbol_table(lookahead[2], self.current_scope) or lookahead[2] == 'output':
            return
        self.semantic_errors.append(f'#{lookahead[0]}: Semantic Error! \'{lookahead[2]}\' is not defined.')

    def void_check(self, var_id):
        if self.id_type[2] == 'void':
            self.semantic_errors.append(f'#{self.id_type[0]}: Semantic Error! Illegal type of void for \'{var_id}\'.')

    def break_check(self, lookahead):
        if len(self.isLoop) > 0:
            return
        self.semantic_errors.append(
            f'#{lookahead[0]}: Semantic Error! No \'repeat ... until\' found for \'break\'.')

    def type_mismatch(self, lookahead, operand_1, operand_2):
        if operand_2 is None or operand_1 is None:
            return
        operand_2_type = 'int'
        operand_1_type = 'int'
        if not operand_1.startswith('#'):
            for s in symbol_table['ID']:
                if s[2] == operand_1:
                    operand_1_type = s[1]
                    break
        if not operand_2.startswith('#'):
            for s in symbol_table['ID']:
                if s[2] == operand_2:
                    operand_2_type = s[1]
                    break

        if operand_2_type != operand_1_type:
            operand_1_type = 'array' if operand_1_type == 'int*' else operand_1_type
            operand_2_type = 'array' if operand_2_type == 'int*' else operand_2_type
            if self.isMult:
                self.semantic_errors.append(
                    f'#{lookahead[0]}: Semantic Error! Type mismatch in operands, Got array instead of int.')
            else:
                self.semantic_errors.append(
                    f'#{lookahead[0]}: Semantic Error! Type mismatch in operands, Got {operand_2_type} instead of {operand_1_type}.')

    def parameter_num_matching(self, lookahead, args, attributes):
        func_name = ''
        for i in symbol_table['ID']:
            if i[2] == attributes:
                func_name = i[0]
        func_args = []
        for i in attributes:
            if isinstance(i, list):
                func_args = i
        if len(func_args) != len(args):
            self.semantic_errors.append(
                f'#{lookahead[0]}: Semantic Error! Mismatch in numbers of arguments of \'{func_name}\'.')

    def parameter_type_matching(self, lookahead, var, arg, num):
        if arg.startswith('#'):
            if var[1] != 'int':
                var_type = 'array' if var[1] == 'int*' else var[1]
                self.semantic_errors.append(
                    f'#{lookahead[0]}: Semantic Error! Mismatch in type of argument {num} of \'{self.get_func_name(var)}\'. Expected \'{var_type}\' but got \'int\' instead.')
        else:
            for rec in symbol_table['ID']:
                if rec[2] == arg and rec[1] != var[1]:
                    type = 'array' if rec[1] == 'int*' else rec[1]
                    var_type = 'array' if var[1] == 'int*' else var[1]
                    self.semantic_errors.append(
                        f'#{lookahead[0]}: Semantic Error! Mismatch in type of argument {num} of \'{self.get_func_name(var)}\'. Expected \'{var_type}\' but got \'{type}\' instead.')

    def get_func_name(self, var):
        for rec in symbol_table['ID']:
            if rec[1] == 'function':
                for arg in rec[2][1]:
                    if arg[2] == var[2]:
                        return rec[0]

    def push_scope(self, lookahead):
        self.current_scope += 1

    def pop_scope(self, lookahead):
        for record in symbol_table['ID'][::-1]:
            if record[3] == self.current_scope:
                del symbol_table['ID'][-1]
        self.current_scope -= 1
