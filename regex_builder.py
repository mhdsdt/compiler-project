from dfa_handler import DFANode, RegexEdge, NonTokenizableNode
from enums_constants import TokenType


def get_default_dfa():
    start_dfa_node = DFANode(token_type=TokenType.Unknown.value)

    digit_dfa = DFANode(token_type=TokenType.Num.value)
    finish_digit_dfa = DFANode(finished=True, roll_back=True, token_type=TokenType.Num.value)
    digit_start_edge = RegexEdge().accept_digits()
    digit_middle_edge = RegexEdge().accept_digits()
    digit_final_edge = RegexEdge().accept_white_spaces().accept_symbols().accept_comments()
    start_dfa_node.add_next_node(edge=digit_start_edge, next_node=digit_dfa)
    digit_dfa.add_next_node(edge=digit_middle_edge, next_node=digit_dfa)
    digit_dfa.add_next_node(edge=digit_final_edge, next_node=finish_digit_dfa)

    id_keyword_start_dfa = DFANode(token_type=TokenType.KeywordId.value)
    id_keyword_middle_dfa = DFANode(token_type=TokenType.KeywordId.value)
    id_keyword_finish_dfa = DFANode(finished=True, roll_back=True, token_type=TokenType.KeywordId.value)
    id_keyword_start_edge = RegexEdge().accept_alphabets()
    id_keyword_middle_edge = RegexEdge().accept_digits().accept_alphabets()
    id_keyword_final_edge = RegexEdge().accept_symbols().accept_comments().accept_white_spaces()
    start_dfa_node.add_next_node(edge=id_keyword_start_edge, next_node=id_keyword_start_dfa)
    id_keyword_start_dfa.add_next_node(edge=id_keyword_middle_edge, next_node=id_keyword_middle_dfa)
    id_keyword_start_dfa.add_next_node(edge=id_keyword_final_edge, next_node=id_keyword_finish_dfa)
    id_keyword_middle_dfa.add_next_node(edge=id_keyword_middle_edge, next_node=id_keyword_middle_dfa)
    id_keyword_middle_dfa.add_next_node(edge=id_keyword_final_edge, next_node=id_keyword_finish_dfa)

    symbol_start_dfa_without_equals = DFANode(finished=True, token_type=TokenType.Symbol.value)
    symbol_start_equal_dfa = DFANode(token_type=TokenType.Symbol.value)
    equal_dfa_finisher = DFANode(finished=True, roll_back=True, token_type=TokenType.Symbol.value)
    symbol_double_equals_dfa = DFANode(finished=True, token_type=TokenType.Symbol.value)
    symbol_start_edge_without_equals = RegexEdge().accept_symbols().reject('=')
    equals_edge = RegexEdge().accept('=')
    equals_edge_finisher = RegexEdge().accept_digits().accept_white_spaces().accept_comments().accept_alphabets()
    start_dfa_node.add_next_node(edge=symbol_start_edge_without_equals, next_node=symbol_start_dfa_without_equals)
    start_dfa_node.add_next_node(edge=equals_edge, next_node=symbol_start_equal_dfa)
    symbol_start_equal_dfa.add_next_node(edge=equals_edge, next_node=symbol_double_equals_dfa)
    symbol_start_equal_dfa.add_next_node(edge=equals_edge_finisher, next_node=equal_dfa_finisher)

    white_space_dfa = NonTokenizableNode(finished=True, token_type=TokenType.Whitespace.value)
    white_space_start_edge = RegexEdge().accept_white_spaces()
    start_dfa_node.add_next_node(edge=white_space_start_edge, next_node=white_space_dfa)

    comment_start_dfa = DFANode(token_type=TokenType.Comment.value)
    comment_second_dfa = DFANode(token_type=TokenType.Comment.value)
    comment_middle_dfa = DFANode(token_type=TokenType.Comment.value)
    comment_2_pre_final_dfa = DFANode(token_type=TokenType.Comment.value)
    comment_pre_final_dfa = NonTokenizableNode(finished=True, token_type=TokenType.Comment.value)
    comment_start_edge = RegexEdge().accept('/')
    comment_second_edge = RegexEdge().accept('*')
    comment_middle_edge = RegexEdge().accept_digits().accept_alphabets().accept_symbols().accept_white_spaces()
    comment_2_pre_final_edge = RegexEdge().accept('*')
    comment_pre_final_edge = RegexEdge().accept('/')

    start_dfa_node.add_next_node(edge=comment_start_edge, next_node=comment_start_dfa)
    comment_start_dfa.add_next_node(edge=comment_second_edge, next_node=comment_second_dfa)
    comment_second_dfa.add_next_node(edge=comment_middle_edge, next_node=comment_middle_dfa)
    comment_middle_dfa.add_next_node(edge=comment_middle_edge, next_node=comment_middle_dfa)
    comment_middle_dfa.add_next_node(edge=comment_2_pre_final_edge, next_node=comment_2_pre_final_edge)
    comment_second_dfa.add_next_node(edge=comment_2_pre_final_edge, next_node=comment_2_pre_final_dfa)
    comment_2_pre_final_dfa.add_next_node(edge=comment_pre_final_edge, next_node=comment_pre_final_dfa)
    comment_2_pre_final_dfa.add_next_node(edge=comment_middle_edge, next_node=comment_middle_dfa)

    return start_dfa_node
