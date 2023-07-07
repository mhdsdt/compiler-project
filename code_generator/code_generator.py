from scanner.enums_constants import get_keywords


class AddressManager:
    DEFAULT_WORD_SIZE = 4
    DEFAULT_INDEX_INCREMENT = 1

    def __init__(self):
        self.__index = 0
        self.__temp_address = 500
        self.__symbol_table = {'KEYWORD': get_keywords(), 'ID': []}

    def get_temp_address(self):
        return self.__temp_address

    def get_index(self):
        return self.__index

    def increase_temp_address(self, amount=None):
        if amount is None:
            amount = AddressManager.DEFAULT_WORD_SIZE
        self.__temp_address += amount

    def increase_index(self, amount=None):
        if amount is None:
            amount = AddressManager.DEFAULT_INDEX_INCREMENT
        self.__index += amount

    def is_in_symbol_table(self, item, scope_num=0):
        for i in self.__symbol_table['ID'][::-1]:
            if item == i[0] and i[3] <= scope_num:
                return True
        return False

    def find_symbol_address(self, symbol):
        if symbol == 'output':
            return symbol
        for i in self.__symbol_table['ID'][::-1]:
            if symbol == i[0]:
                return i[2]

    def extend_symbol_table(self, symbol_info):
        self.__symbol_table['ID'].append(symbol_info)

    def get_last_id_in_symbol_table(self):
        return self.__symbol_table['ID'][-1]

    def delete_last_id_in_symbol_table(self):
        del self.__symbol_table['ID'][-1]

    def get_ids_from_symbol_table(self):
        return self.__symbol_table['ID']


class CodeGen:
    def __init__(self):
        self.SS = list()
        self.PB = dict()
        self.break_stack = list()
        self.current_scope = 0
        self.return_stack = list()
        self.address_manager = AddressManager()
        self.semantic_errors = []
        self.id_type = 'void'
        self.is_loop = []
        self.is_mult = False
        self.methods = {
            '#get_id_type': self.get_id_type,
            '#push_id': self.push_id,
            '#define_variable': self.define_variable,
            '#push_num': self.push_num,
            '#define_array': self.define_array,
            '#start_params': self.start_params,
            '#start_func': self.start_func,
            "#new_return": self.new_return,
            "#end_return": self.end_return,
            "#return_anyway": self.return_anyway,
            "#end_function": self.end_function,
            '#define_array_argument': self.define_array_argument,
            '#push_scope': self.push_scope,
            '#pop_scope': self.pop_scope,
            '#clean_up': self.clean_up,
            '#break_loop': self.break_loop,
            '#save': self.save,
            '#jpf_save': self.jpf_save,
            '#jump': self.jump,
            '#label': self.label,
            '#start_loop': self.start_loop,
            '#repeat': self.repeat,
            '#end_loop': self.end_loop,
            '#save_return': self.save_return,
            '#push_index': self.push_index,
            '#get_id': self.get_id,
            '#assign_operation': self.assign_operation,
            '#push_operator': self.push_operator,
            '#make_op': self.make_op,
            '#multiply': self.multiply,
            '#implicit_output': self.implicit_output,
            '#call_function': self.call_function,
            '#array_index': self.array_index,
        }

    def call(self, action_symbol, token_line, token_name):
        self.methods[action_symbol](token_line, token_name)
        # self.export('')

    def export(self, path):
        with open('output1.txt', "a") as f:
            # for i in sorted(self.PB.keys()):
            f.write(f'{self.__dict__}\n')
            f.write('==================================\n')

    def insert_code(self, a, b, c='', d=''):
        self.PB[self.address_manager.get_index()] = f'({a}, {b}, {c}, {d})'
        self.address_manager.increase_index()

    def get_temp(self, count=1):
        begin_address = str(self.address_manager.get_temp_address())
        for _ in range(count):
            self.insert_code('ASSIGN', '#0', str(self.address_manager.get_temp_address()))
            self.address_manager.increase_temp_address()
        return begin_address

    def define_variable(self, token_name, token_line):
        var_id = self.SS.pop()
        self.void_check(var_id)
        address = self.get_temp()
        self.address_manager.extend_symbol_table((var_id, 'int', address, self.current_scope))

    def define_array(self, token_name, token_line):
        array_size, array_id = int(self.SS.pop()[1:]), self.SS.pop()

        self.void_check(array_id)
        address = self.get_temp()
        array_space = self.get_temp(array_size)
        self.insert_code('ASSIGN', f'#{array_space}', address)
        self.address_manager.extend_symbol_table((array_id, 'int*', address, self.current_scope))

    def get_id_type(self, token_line, token_name):
        self.id_type = (token_line, token_name)

    def push_id(self, token_line, token_name):
        self.SS.append(token_name)

    def get_id(self, token_line, token_name):
        self.scope_check((token_line, token_name))
        self.SS.append(self.address_manager.find_symbol_address(token_name))

    def push_num(self, token_line, token_name):
        self.SS.append(f'#{token_name}')

    def push_operator(self, token_line, token_name):
        self.SS.append(token_name)

    def get_equivalent_operator(self, operator):
        if operator == '+':
            return 'ADD'
        elif operator == '-':
            return 'SUB'
        elif operator == '<':
            return 'LT'
        elif operator == '==':
            return 'EQ'
        raise Exception(f"in get_equivalent_operator operator == {operator}, How this is possible?")

    def make_op(self, token_line, token_name):
        operand_2 = self.SS.pop()
        operator = self.SS.pop()
        operand_1 = self.SS.pop()
        self.type_mismatch((token_line, token_name), operand_1, operand_2)
        address = self.get_temp()
        self.insert_code(self.get_equivalent_operator(operator), operand_1, operand_2, address)
        self.SS.append(address)

    def assign_operation(self, token_name, token_line):
        self.insert_code('ASSIGN', self.SS[-1], self.SS[-2])
        self.SS.pop()

    def multiply(self, token_line, token_name):
        res = self.get_temp()
        self.is_mult = True
        self.type_mismatch((token_line, token_name), self.SS[-2], self.SS[-1])
        self.is_mult = False
        self.insert_code('MULT', self.SS[-1], self.SS[-2], res)
        self.SS.pop()
        self.SS.pop()
        self.SS.append(res)

    def define_array_argument(self, token_name, token_line):
        temp = self.address_manager.get_last_id_in_symbol_table()
        self.address_manager.delete_last_id_in_symbol_table()
        self.address_manager.extend_symbol_table((temp[0], 'int*', temp[2], temp[3]))

    def array_index(self, token_line, token_name):
        idx, array_address = self.SS.pop(), self.SS.pop()
        temp, result = self.get_temp(), self.get_temp()
        self.insert_code('MULT', '#4', idx, temp)
        self.insert_code('ASSIGN', f'{array_address}', result)
        self.insert_code('ADD', result, temp, result)
        self.SS.append(f'@{result}')

    def implicit_output(self, token_line, token_name):
        if self.SS[-2] == 'output':
            self.insert_code('PRINT', self.SS.pop())

    def save(self, token_name, token_line):
        self.SS.append(self.address_manager.get_index())
        self.address_manager.increase_index()

    def label(self, token_name, token_line):
        self.SS.append(self.address_manager.get_index())

    def jpf_save(self, token_name, token_line):
        dest = self.SS.pop()
        src = self.SS.pop()
        self.PB[dest] = f'(JPF, {src}, {self.address_manager.get_index() + 1}, )'
        self.SS.append(self.address_manager.get_index())
        self.address_manager.increase_index()

    def jump(self, token_name, token_line):
        dest = int(self.SS.pop())
        self.PB[dest] = f'(JP, {self.address_manager.get_index()}, , )'

    def repeat(self, token_name, token_line):
        self.PB[int(self.SS[-1])] = f'(JPF, {self.SS[-2]},{self.SS[-3]}, )'
        self.PB[self.address_manager.get_index()] = f'(JP,  {self.address_manager.get_index() + 1}, , )'
        self.address_manager.increase_index()
        self.SS.pop(), self.SS.pop(), self.SS.pop()

    def start_loop(self, token_name, token_line):
        self.is_loop.append(1)
        self.break_stack.append('b')

    def end_loop(self, token_name, token_line):
        latest_block = len(self.break_stack) - self.break_stack[::-1].index('b') - 1
        for item in self.break_stack[latest_block + 1:]:
            self.PB[item] = f'(JP, {self.address_manager.get_index()}, , )'
        self.break_stack = self.break_stack[:latest_block]
        self.is_loop.pop()

    def break_loop(self, token_line, token_name):
        self.break_check((token_line, token_name))
        self.break_stack.append(self.address_manager.get_index())
        self.address_manager.increase_index()

    def clean_up(self, token_name, token_line):
        self.SS.pop()

    def end_function(self, token_name, token_line):
        self.SS.pop(), self.SS.pop(), self.SS.pop()
        symbol_table_ids = self.address_manager.get_ids_from_symbol_table()
        for item in symbol_table_ids[::-1]:
            if item[1] == 'function':
                if item[0] == 'main':
                    self.PB[self.SS.pop()] = f'(ASSIGN, #0, {self.get_temp()}, )'
                    return
                break
        self.PB[self.SS.pop()] = f'(JP, {self.address_manager.get_index()}, , )'

    def call_function(self, token_line, token_name):
        if self.SS[-1] != 'output':
            args, attributes = [], []
            for i in self.SS[::-1]:
                if isinstance(i, list):
                    attributes = i
                    break
                args = [i] + args
            self.parameter_num_matching((token_line, token_name), args, attributes)
            for var, arg in zip(attributes[1], args):
                self.parameter_type_matching((token_line, token_name), var, arg, attributes[1].index(var) + 1)
                self.insert_code('ASSIGN', arg, var[2])
                self.SS.pop()
            for i in range(len(args) - len(attributes[1])):
                self.SS.pop()
            self.SS.pop()
            self.insert_code('ASSIGN', f'#{self.address_manager.get_index() + 2}', attributes[2])
            self.insert_code('JP', attributes[-1])
            result = self.get_temp()
            self.insert_code('ASSIGN', attributes[0], result)
            self.SS.append(result)

    def start_params(self, token_name, token_line):
        func_name = self.SS.pop()
        self.SS.append(self.address_manager.get_index())
        self.address_manager.increase_index()
        self.SS.append(func_name)
        self.address_manager.extend_symbol_table('s')

    def push_index(self, token_name, token_line):
        self.SS.append(f'#{self.address_manager.get_index()}')

    def start_func(self, token_name, token_line):
        return_address = self.get_temp()
        current_index = self.address_manager.get_index()
        return_value = self.get_temp()
        self.SS.append(return_value)
        self.SS.append(return_address)
        func_name = self.SS[-3]
        symbol_table_ids = self.address_manager.get_ids_from_symbol_table()
        args_start_idx = symbol_table_ids.index('s')
        func_args = symbol_table_ids[args_start_idx + 1:]
        symbol_table_ids.pop(args_start_idx)
        symbol_table_ids.append(
            (func_name, 'function', [return_value, func_args, return_address, current_index], self.current_scope))

    def new_return(self, token_name, token_line):
        self.return_stack.append('b')

    def save_return(self, token_name, token_line):
        self.return_stack.append((self.address_manager.get_index(), self.SS[-1]))
        self.SS.pop()
        self.address_manager.increase_index(2)

    def return_anyway(self, token_name, token_line):
        if self.SS[-3] != 'main':
            return_address = self.SS[-1]
            self.insert_code('JP', f'@{return_address}')

    def end_return(self, token_name, token_line):
        latest_func = len(self.return_stack) - self.return_stack[::-1].index('b') - 1
        return_value = self.SS[-2]
        return_address = self.SS[-1]
        for item in self.return_stack[latest_func + 1:]:
            self.PB[item[0]] = f'(ASSIGN, {item[1]}, {return_value}, )'
            self.PB[item[0] + 1] = f'(JP, @{return_address}, , )'

        self.return_stack = self.return_stack[:latest_func]

    def scope_check(self, lookahead):
        if self.address_manager.is_in_symbol_table(lookahead[1], self.current_scope) or lookahead[1] == 'output':
            return
        self.semantic_errors.append(f'#{lookahead[0]}: Semantic Error! \'{lookahead[1]}\' is not defined.')

    def void_check(self, var_id):
        if self.id_type[1] == 'void':
            self.semantic_errors.append(f'#{self.id_type[0]}: Semantic Error! Illegal type of void for \'{var_id}\'.')

    def break_check(self, lookahead):
        if len(self.is_loop) > 0:
            return
        self.semantic_errors.append(
            f'#{lookahead[0]}: Semantic Error! No \'repeat ... until\' found for \'break\'.')

    def type_mismatch(self, lookahead, operand_1, operand_2):
        if operand_2 is None or operand_1 is None:
            return
        operand_2_type = 'int'
        operand_1_type = 'int'
        symbol_table_ids = self.address_manager.get_ids_from_symbol_table()
        if not operand_1.startswith('#'):
            for s in symbol_table_ids:
                if s[2] == operand_1:
                    operand_1_type = s[1]
                    break
        if not operand_2.startswith('#'):
            for s in symbol_table_ids:
                if s[2] == operand_2:
                    operand_2_type = s[1]
                    break

        if operand_2_type != operand_1_type:
            operand_1_type = 'array' if operand_1_type == 'int*' else operand_1_type
            operand_2_type = 'array' if operand_2_type == 'int*' else operand_2_type
            if self.is_mult:
                self.semantic_errors.append(
                    f'#{lookahead[0]}: Semantic Error! Type mismatch in operands, Got array instead of int.')
            else:
                self.semantic_errors.append(
                    f'#{lookahead[0]}: Semantic Error! Type mismatch in operands, Got {operand_2_type} instead of {operand_1_type}.')

    def parameter_num_matching(self, lookahead, args, attributes):
        func_name = ''
        symbol_table_ids = self.address_manager.get_ids_from_symbol_table()
        for i in symbol_table_ids:
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
            for rec in self.address_manager.get_ids_from_symbol_table():
                if rec[2] == arg and rec[1] != var[1]:
                    type = 'array' if rec[1] == 'int*' else rec[1]
                    var_type = 'array' if var[1] == 'int*' else var[1]
                    self.semantic_errors.append(
                        f'#{lookahead[0]}: Semantic Error! Mismatch in type of argument {num} of \'{self.get_func_name(var)}\'. Expected \'{var_type}\' but got \'{type}\' instead.')

    def get_func_name(self, var):
        for rec in self.address_manager.get_ids_from_symbol_table():
            if rec[1] == 'function':
                for arg in rec[2][1]:
                    if arg[2] == var[2]:
                        return rec[0]

    def push_scope(self, token_name, token_line):
        self.current_scope += 1

    def pop_scope(self, token_name, token_line):
        symbol_table_ids = self.address_manager.get_ids_from_symbol_table()
        for record in symbol_table_ids[::-1]:
            if record[3] == self.current_scope:
                del symbol_table_ids[-1]
        self.current_scope -= 1
