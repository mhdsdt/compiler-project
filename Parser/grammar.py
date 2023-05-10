class Terminal:
    def __init__(self, name):
        self.name = name.lower()
        self.first = [name]

    def __str__(self):
        return self.name


class NonTerminal:
    def __init__(self, name, first=None, follow=None):
        if first is None:
            first = []
        if follow is None:
            follow = []
        self.name = name.upper()
        self.first = first
        self.follow = follow

    def __str__(self):
        return self.name


class ProductRule:
    def __init__(self, lhs: NonTerminal, rhs: list):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return f'{self.lhs} -> {self.rhs}'


class Grammar:
    def __init__(self, terminals: list, non_terminals: list):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.product_rules = []

    def add_product_rule(self, rule):
        self.product_rules.append(rule)

    def get_term_by_name(self, name):
        for non_terminal in self.non_terminals:
            if non_terminal.name == name:
                return non_terminal
        for terminal in self.terminals:
            if terminal.name == name:
                return terminal

    def import_firsts(self):
        with open('firsts.txt', encoding='utf-8') as f:
            for line in f.readlines():
                split_line = line.strip('\n').split()
                non_terminal = self.get_term_by_name(split_line[0])
                non_terminal.first = [self.get_term_by_name(term) for term in split_line[1:]]

    def import_follows(self):
        with open('follows.txt.txt', encoding='utf-8') as f:
            for line in f.readlines():
                split_line = line.strip('\n').split()
                non_terminal = self.get_term_by_name(split_line[0])
                non_terminal.follow = [self.get_term_by_name(term) for term in split_line[1:]]

    def import_product_rules(self):
        with open('grammar.txt', encoding='utf-8') as f:
            for line in f.readlines():
                lhs_as_str, rhs_as_str = line.strip('\n').split('->')
                lhs = self.get_term_by_name(lhs_as_str)
                for rule in rhs_as_str.split('|'):
                    terms = [self.get_term_by_name(term) for term in rule.split()]
                    self.add_product_rule(ProductRule(lhs, terms))


def create_terminals():
    return [Terminal('$'), Terminal('EPSILON'), Terminal('ID'), Terminal(';'), Terminal('['), Terminal('NUM'),
            Terminal(']'), Terminal('('), Terminal(')'), Terminal('int'), Terminal('void'), Terminal(','),
            Terminal('{'), Terminal('}'), Terminal('break'), Terminal('if'), Terminal('else'), Terminal('while'),
            Terminal('return'), Terminal('switch'), Terminal('case'), Terminal('default'), Terminal(':'),
            Terminal('='), Terminal('<'), Terminal('=='), Terminal('+'), Terminal('-'), Terminal('*')]


def create_non_terminals():
    return [NonTerminal('Program'), NonTerminal('Declaration-list'), NonTerminal('Declaration'),
            NonTerminal('Declaration-initial'), NonTerminal('Declaration-prime'),
            NonTerminal('Var-declaration-prime'),
            NonTerminal('Fun-declaration-prime'), NonTerminal('Type-specifier'), NonTerminal('Params'),
            NonTerminal('Param-list-void-abtar'), NonTerminal('Param-list'), NonTerminal('Param'),
            NonTerminal('Param-prime'), NonTerminal('Compound-stmt'), NonTerminal('Statement-list'),
            NonTerminal('Statement'), NonTerminal('Expression-stmt'), NonTerminal('Selection-stmt'),
            NonTerminal('Iteration-stmt'), NonTerminal('Return-stmt'), NonTerminal('Return-stmt-prime'),
            NonTerminal('Switch-stmt'), NonTerminal('Case-stmts'), NonTerminal('Case-stmt'),
            NonTerminal('Default-stmt'), NonTerminal('Expression'), NonTerminal('B'), NonTerminal('H'),
            NonTerminal('Simple-expression-zegond'), NonTerminal('Simple-expression-prime'), NonTerminal('C'),
            NonTerminal('Relop'), NonTerminal('Additive-expression'), NonTerminal('Additive-expression-prime'),
            NonTerminal('Additive-expression-zegond'), NonTerminal('D'), NonTerminal('Addop'),
            NonTerminal('Term'), NonTerminal('Term-prime'), NonTerminal('Term-zegond'), NonTerminal('G'),
            NonTerminal('Signed-factor'), NonTerminal('Signed-factor-prime'), NonTerminal('Signed-factor-zegond'),
            NonTerminal('Factor'), NonTerminal('Var-call-prime'), NonTerminal('Var-prime'),
            NonTerminal('Factor-prime'), NonTerminal('Factor-zegond'), NonTerminal('Args'),
            NonTerminal('Arg-list'), NonTerminal('Arg-list-prime')]


def create_grammar():
    grammar = Grammar(create_non_terminals(), create_terminals())
    grammar.import_firsts()
    grammar.import_follows()
    grammar.import_product_rules()
    return grammar
