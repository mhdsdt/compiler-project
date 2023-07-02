import sys

from collections import namedtuple

MidLangDefaults = namedtuple('MidLangDefaults', 'WORD_SIZE DATA_ADDRESS TEMP_ADDRESS STACK_ADDRESS')
MID_LANG = MidLangDefaults(4, 500, 900, 1000)


class Assembler:
    def __init__(self):
        self.arg_dec = False
        self.set_exec = False
        self.arg_pointer = []
        self.data_pointer = 0
        self.temp_pointer = 0
        self.last_id = None
        self.temp_address = 0
        self.data_address = 0
        self.stack_address = 0
        self.program_block = []


class RegisterFile:
    def __init__(self, sp_address, fp_address, ra_address, rv_address):
        self.sp = sp_address
        self.fp = fp_address
        self.ra = ra_address
        self.rv = rv_address


class Layer:
    def __init__(self, assembler):
        self.assembler = assembler
        self.temp_stack = []
        self.data_stack = []
        self.jail = []

    def new_scope(self):
        self.temp_stack.append(self.assembler.temp_address)
        self.data_stack.append(self.assembler.data_address)
        self.jail.append("|")

    def del_scope(self):
        self.assembler.data_address = self.data_stack.pop()
        self.assembler.temp_address = self.temp_stack.pop()

        while self.jail[-1] != "|":  # scope delimiter
            self.prison_break()
        self.jail.pop()

    def prison_break(self):
        break_address = len(self.assembler.program_block)
        prisoner = self.jail.pop()
        self.assembler.program_block[prisoner] = f"(JP, {break_address}, , )"

    def prison(self):
        self.jail.append(len(self.assembler.program_block))
        self.assembler.program_block.append("(help step-programmer im stuck!)")


class ScopeManager:
    def __init__(self, assembler, stack):
        self.should_delete_scope = False
        self.stack = stack
        self.layers = {"t": Layer(assembler), "f": Layer(assembler), "c": Layer(assembler), "s": Layer(assembler)}
        self.scmod = []

    def push_scmod(self, mod):
        self.scmod.append(mod)
        if self.should_delete_scope:
            self.__del_scope()

    def prison(self):
        self.layers[self.scmod.pop()].prison()

    def prison_break(self):
        self.layers[self.scmod.pop()].prison_break()

    def new_scope(self):
        scmod = self.scmod.pop()
        self.layers[scmod].new_scope()
        if scmod == "f":
            self.stack.new_scope()

    def del_scope(self):
        self.should_delete_scope = True

    def __del_scope(self):
        self.should_delete_scope = False
        scmod = self.scmod.pop()
        self.layers[scmod].del_scope()
        if scmod == "f":
            self.stack.del_scope()


class StackManager:
    def __init__(self, program_block, register_file, MLD):
        self.MLD = MLD
        self.program_block = program_block
        self.rf = register_file

    def push(self, value):
        self.program_block.append(f"(ASSIGN, {value}, @{self.rf.sp}, )")
        self.program_block.append(f"(ADD, {self.rf.sp}, #{self.MLD.WORD_SIZE}, {self.rf.sp})")

    def pop(self, holder):
        self.program_block.append(f"(SUB, {self.rf.sp}, #{self.MLD.WORD_SIZE}, {self.rf.sp})")
        self.program_block.append(f"(ASSIGN, @{self.rf.sp}, {holder}, )")

    def new_scope(self):
        self.program_block.append("")
        self.push(self.rf.fp)
        self.program_block.append(f"(ASSIGN, {self.rf.sp}, {self.rf.fp}, )")

    def del_scope(self):
        self.program_block.append(f"(ASSIGN, {self.rf.fp}, {self.rf.sp}, )")
        self.pop(self.rf.fp)
        self.program_block.append("")

    def reserve(self, chunk=1):
        self.program_block.append(f"(ADD, #{self.MLD.WORD_SIZE * chunk}, {self.rf.sp}, {self.rf.sp})")

    def debug(self):
        self.program_block.append(f"(PRINT, 500, , )")
        self.program_block.append(f"(PRINT, 504, , )")

    def store_registers(self):
        self.push(self.rf.sp)
        self.push(self.rf.fp)
        self.push(self.rf.ra)

    def load_registers(self):
        self.pop(self.rf.ra)
        self.pop(self.rf.fp)
        self.pop(self.rf.sp)


class CodeGen:

    def __init__(self, mid_lang_defaults=MID_LANG):
        self.semantic_stack = []
        self.jail = []

        self.MLD = mid_lang_defaults
        self.assembler = Assembler()
        self.assembler.data_address = self.MLD.DATA_ADDRESS
        self.assembler.stack_address = self.MLD.STACK_ADDRESS
        self.assembler.temp_address = self.MLD.TEMP_ADDRESS

        self.rf = RegisterFile(self.get_data_var(), self.get_data_var(), self.get_data_var(), self.get_data_var())
        self.stack = StackManager(self.assembler.program_block, self.rf, self.MLD)
        self.scope = ScopeManager(self.assembler, self.stack)

        self.apply_template()

        self.routines = {"#pnum": self.pnum,
                         "#pid": self.pid,
                         "#parr": self.parr,
                         "#pzero": self.pzero,
                         "#prv": self.prv,
                         "#op_push": self.op_push,
                         "#pop": self.pop,

                         "#declare": self.declare,
                         "#declare_id": self.declare_id,
                         "#declare_arr": self.declare_arr,
                         "#declare_func": self.declare_func,

                         "#arg_init": self.arg_init,
                         "#arg_finish": self.arg_finish,
                         "#arg_pass": self.arg_pass,

                         "#assign": self.assign,
                         "#op_exec": self.op_exec,
                         "#decide": self.decide,
                         "#case": self.case,

                         "#hold": self.hold,
                         "#label": self.label,

                         "#prison_break": self.prison_break,
                         "#prison": self.prison,
                         "#jump_while": self.jump_while,

                         "#output": self.output,
                         "#call": self.func_call,
                         "#return": self.func_return,

                         "#scmod_f": self.scmod_f,
                         "#scmod_c": self.scmod_c,
                         "#scmod_s": self.scmod_s,
                         "#scmod_t": self.scmod_t,

                         "#sc_start": self.scope_start,
                         "#sc_stop": self.scope_stop,

                         "#set_exec": self.set_exec,
                         }

    def call(self, routine, token=None):
        try:
            self.routines[routine](token)
            # uncomment the line below for debugging , gives you a step by step view!
            # self.export("output.txt")
        except:
            sys.stderr.write(f"error during generating code for token {token.lexeme} and routine {routine}\n")

    def pid(self, token):
        self.semantic_stack.append(self.find_var(token.lexeme).address)

    def pnum(self, token):
        self.semantic_stack.append(f"#{token.lexeme}")

    def pzero(self, token=None):
        self.semantic_stack.append(f"#0")

    def prv(self, token=None):
        self.semantic_stack.append(self.rf.rv)

    def parr(self, token=None):
        offset = self.semantic_stack.pop()
        temp = self.get_temp_var()
        self.assembler.program_block.append(f"(MULT, #{self.MLD.WORD_SIZE}, {offset}, {temp})")
        self.assembler.program_block.append(f"(ADD, {self.semantic_stack.pop()}, {temp}, {temp})")
        self.semantic_stack.append(f"@{temp}")

    def pop(self, token=None):
        self.semantic_stack.pop()

    def declare_arr(self, token=None):
        self.assembler.program_block.append(f"(ASSIGN, {self.rf.sp}, {self.semantic_stack[-2]}, )")
        self.stack.reserve(int(self.semantic_stack.pop()[1:]))

    def declare_func(self, token=None):
        self.assembler.data_pointer = self.assembler.data_address
        self.assembler.temp_pointer = self.assembler.temp_address

        # only when zero init is activated
        self.assembler.program_block[-1] = ""

        id_record = self.find_var(self.assembler.last_id.lexeme)
        id_record.address = len(self.assembler.program_block)

    def declare_id(self, token):
        id_record = self.find_var(token.lexeme)
        id_record.address = self.get_data_var()

        self.assembler.last_id = token

        if self.assembler.arg_dec:
            self.arg_assign(id_record.address)
        else:
            self.assembler.program_block.append(f"(ASSIGN, #0, {id_record.address}, )")
            pass

    # @staticmethod
    # def declare(Token=None):
    #     tables.get_symbol_table().set_declaration(True)

    def assign(self, token=None):
        self.assembler.program_block.append(f"(ASSIGN, {self.semantic_stack.pop()}, {self.semantic_stack[-1]}, )")

    def op_exec(self, token=None):
        second = self.semantic_stack.pop()
        operand = self.semantic_stack.pop()
        first = self.semantic_stack.pop()
        result = self.get_temp_var()
        self.assembler.program_block.append(f"({operand}, {first}, {second}, {result})")
        self.semantic_stack.append(result)

    operands = {'+': 'ADD', '-': 'SUB', '*': 'MULT', '<': 'LT', '==': 'EQ'}

    def op_push(self, token):
        self.semantic_stack.append(self.operands[token.lexeme])

    def hold(self, token=None):
        self.label()
        self.assembler.program_block.append("(new you see me!)")

    def label(self, token=None):
        self.semantic_stack.append(len(self.assembler.program_block))

    def decide(self, token=None):
        address = self.semantic_stack.pop()
        self.assembler.program_block[
            address] = f"(JPF, {self.semantic_stack.pop()}, {len(self.assembler.program_block)}, )"

    def case(self, token=None):
        result = self.get_temp_var()
        self.assembler.program_block.append(f"(EQ, {self.semantic_stack.pop()}, {self.semantic_stack[-1]}, {result})")
        self.semantic_stack.append(result)

    def jump_while(self, token=None):
        head1 = self.semantic_stack.pop()
        head2 = self.semantic_stack.pop()
        self.assembler.program_block.append(f"(JP, {self.semantic_stack.pop()}, , )")
        self.semantic_stack.append(head2)
        self.semantic_stack.append(head1)

    def output(self, token=None):
        self.assembler.program_block.append(f"(PRINT, {self.semantic_stack.pop()}, , )")

    def get_temp_var(self):
        self.assembler.temp_address += self.MLD.WORD_SIZE
        return self.assembler.temp_address - self.MLD.WORD_SIZE

    def get_data_var(self, chunk_size=1):
        self.assembler.data_address += self.MLD.WORD_SIZE * chunk_size
        return self.assembler.data_address - self.MLD.WORD_SIZE * chunk_size

    def store(self):
        # storing data
        for data in range(self.assembler.data_pointer, self.assembler.data_address, self.MLD.WORD_SIZE):
            self.stack.push(data)
        # storing temp
        for temp in range(self.assembler.temp_pointer, self.assembler.temp_address, self.MLD.WORD_SIZE):
            self.stack.push(temp)
        # storing registers
        self.stack.store_registers()

    def restore(self):
        # loading registers
        self.stack.load_registers()
        # loading temps
        for temp in range(self.assembler.temp_address, self.assembler.temp_pointer, -self.MLD.WORD_SIZE):
            self.stack.pop(temp - self.MLD.WORD_SIZE)
        # loading data
        for data in range(self.assembler.data_address, self.assembler.data_pointer, -self.MLD.WORD_SIZE):
            self.stack.pop(data - self.MLD.WORD_SIZE)

    def collect(self):
        # collect
        result = self.get_temp_var()
        self.assembler.program_block.append(f"(ASSIGN, {self.rf.rv}, {result}, )")
        self.semantic_stack.append(result)

    def push_args(self):
        # arg pass
        for arg in range(self.assembler.arg_pointer.pop(), len(self.semantic_stack)):
            self.stack.push(self.semantic_stack.pop())

    def func_call(self, token=None):
        self.store()
        self.push_args()
        # setting registers
        self.assembler.program_block.append(f"(ASSIGN, #{len(self.assembler.program_block) + 2}, {self.rf.ra}, )")
        # call!
        self.assembler.program_block.append(f"(JP, {self.semantic_stack.pop()}, , )")
        self.restore()
        self.collect()

    def func_return(self, token=None):
        self.assembler.program_block.append(f"(JP, @{self.rf.ra}, , )")

    # argument management
    def arg_init(self, token=None):
        self.assembler.arg_dec = True

    def arg_finish(self, token=None):
        self.assembler.arg_dec = False

    def arg_assign(self, address):
        self.stack.pop(address)

    def arg_pass(self, token=None):
        self.assembler.arg_pointer.append(len(self.semantic_stack))

    # scope
    def scmod_f(self, token=None):
        self.scope.push_scmod("f")  # function

    def scmod_c(self, token=None):
        self.scope.push_scmod("c")  # container

    def scmod_s(self, token=None):
        self.scope.push_scmod("s")  # simple

    def scmod_t(self, token=None):
        self.scope.push_scmod("t")  # temporary

    # def scope_start(self, token=None):
    #     tables.get_symbol_table().new_scope()
    #     self.scope.new_scope()

    # def scope_stop(self, token=None):
    #     tables.get_symbol_table().remove_scope()
    #     self.scope.del_scope()

    def prison(self, token=None):
        self.scope.prison()

    def prison_break(self, token=None):
        self.scope.prison_break()

    # @staticmethod
    # def find_var(id):
    #     return tables.get_symbol_table().fetch(id)

    def export(self, path):
        with open(path, "w") as f:
            for i, l in enumerate(self.assembler.program_block):
                f.write(f"{i}\t{l}\n")

    def apply_template(self):
        self.assembler.program_block.append(f"(ASSIGN, #{self.MLD.STACK_ADDRESS}, {self.rf.sp}, )")
        self.assembler.program_block.append(f"(ASSIGN, #{self.MLD.STACK_ADDRESS}, {self.rf.fp}, )")

        self.assembler.program_block.append(f"(ASSIGN, #9999, {self.rf.ra}, )")
        self.assembler.program_block.append(f"(ASSIGN, #9999, {self.rf.rv}, )")

        self.assembler.program_block.append(f"(JP, 9, , )")
        self.stack.pop(self.rf.rv)
        self.assembler.program_block.append(f"(PRINT, {self.rf.rv}, , )")
        self.assembler.program_block.append(f"(JP, @{self.rf.ra}, , )")
        self.get_data_var()

    def set_exec(self, token=None):
        if not self.assembler.set_exec:
            self.assembler.set_exec = True
            func = self.semantic_stack.pop()
            self.assembler.program_block.pop()
            self.hold()
            self.semantic_stack.append(func)

    def execute_from(self, func_name):
        try:
            id_record = self.find_var(func_name)
            self.assembler.program_block[self.semantic_stack.pop()] = f"(JP, {id_record.address}, , )"
        except:
            sys.stderr.write(f"couldn't set the executable path")
