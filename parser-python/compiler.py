import sys
from enum import Enum

from lib.translate import translate

class NodeType(Enum):
    Program = 10
    Block = 20
    If = 22
    For = 23
    While = 24
    Return = 25
    Plus = 30
    Minus = 40
    Multiply = 50
    Divide = 60
    UnaryMinus = 65
    DeclList  = 70
    FunDecl = 80
    Statement = 90
    VarDecl = 100
    Expression = 110
    Assignament = 120
    Identifier = 130
    Constant = 140
    FunCall = 150
    FunCallArg = 160
    BoolAnd = 200
    BoolOr = 201
    BoolNot = 202
    BoolEqual = 203
    BoolNotEqual = 204
    BoolGt = 205
    BoolGte = 206
    BoolLt = 207
    BoolLte = 208


ch = '\n'
token = ""
tokens = ['head']
tokenpos = 0
op_debug = False
op_ast = False
op_translate = False


class AstNode:
    def __init__(self, ty: NodeType, 
                 lnode = None, rnode = None, 
                 other = None, other2 = None, 
                 value1 = None , value2 = None):
        self.ty = ty
        self.lhs = lnode
        self.rhs = rnode
        self.oth = other
        self.oth2 = other2
        self.v1 = value1
        self.v2 = value2

    def __str__(self) -> str:
        def ppty(v):
            if not v:
                return ""
            else:
                return str(v)

        return " ".join([
            self.ty.name,
            ppty(self.v1),
            "(tail)" if self.lhs == None and self.v1 == None else ""])

    def __repr__(self) -> str:
        return self.__str__()

def newnode(ntype: NodeType) -> AstNode:
    return AstNode(ty = ntype)


def readch():
    c = sys.stdin.read(1)
    return c


def is_white(c):
    return c == ' '

def is_newline(c):
    return c == '\n'

def lex():
    global tokenpos, tokens 

    if tokenpos + 1 >= len(tokens):
        return ""

    tokenpos += 1
    tk = tokens[tokenpos]
    return tk

def lex_peek(n = 0):
    if tokenpos + n >= len(tokens):
        return ""

    return tokens[tokenpos + n]


def skip_line():
    global ch

    while ch != '\n' and ch != '':
        ch = readch()


def read_lex():
    global ch

    tk = ""
    while ch != "":
        if is_white(ch) or is_newline(ch):
            ch = readch()
            continue

        if ch in [";", ",", "[", "{", "(", "]", "}", ")", "*", "/"]:
            tk = ch
            ch = readch()
            if tk == '-' and ch == '-':
                tk += ch
                ch = readch()
            break

        #if ch == '/':
        #    tk = ch
        #    ch = readch()
        #    if ch == '/': # a comment?
        #        skip_line()
        #        ch = readch()
        #    break

        if ch == '+':
            tk = ch
            ch = readch()
            if ch == '+':
                tk += ch
                ch = readch()
            break

        if ch == '-':
            tk = ch
            ch = readch()
            if ch == '-':
                tk += ch
                ch = readch()
            break

        if ch == '<':
            tk = ch
            ch = readch()
            if ch == '=':
                tk += ch
                ch = readch()
            break

        if ch == '>':
            tk = ch
            ch = readch()
            if ch == '=':
               tk += ch
               ch = readch()
            break

        if ch == '=':
            tk = ch
            ch = readch()
            if ch == '=':
                tk += ch
                ch = readch()
            break
        
        if ch == '&':
            tk = ch
            ch = readch()
            if ch == '&':
                tk += ch
                ch = readch()
            else:
                error("lexer: unexpected character: '" + ch + "'")
            break

        if ch == '|':
            tk = ch
            ch = readch()
            if ch == '|':
                tk += ch
                ch = readch()
            else:
                error("lexer: unexpected character: '" + ch + "'")
            break

        if ch == '!':
            tk = ch
            ch = readch()
            if ch == '=':
                tk += ch
                ch = readch()
            break

        if ch in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            while ch.isdigit():
                tk += ch
                ch = readch()

            if ch == '.':
                tk += ch
                ch = readch()
                while ch.isdigit():
                    tk += ch
                    ch = readch()
            break

        if ch.isalpha():
            while ch.isalnum():
                tk += ch
                ch = readch()
            break

        error("lexer: unexpected character: '" + ch + "'")

    if ch == "":
        tk = "eof"

    return tk


def error(msg):
    print(msg)
    sys.exit(-1)


def debug(line, op1="", op2=""):
    if op_debug:
        print(line, op1, op2)


def eq_constant(tok):
    for c in tok:
        if not c.isdigit() and not c == '.':
            return False
    return True


# <identifier> ::= <identifier> <letterordigit> | <letter>
# EBNF: identifier = letter { letterordigit }
def eq_identifier(tok):
    if tok and not tok[0].isalpha():
        return False

    for c in tok[1:]:
        if not c.isalnum():
            return False

    return True

def eq_multop(tok):
    if tok == "*" or tok == "/":
        return True
    return False


def eq_addingop_old(tok):
    if tok == "+" or tok == "-" or tok == '&&' or tok == '||':
        return True
    return False

def eq_addingop(tok):
    if tok in [
            "+", "-",
            ">", ">=", "<", "<=", 
            "==", "!==",
            "&&", "||"]:
        return True
    return False

def is_type(tok):
    if tok == "int" or tok == "float":
        return True
    return False


# fun_decl == identifier identifier (
def eq_fun_decl(tok):
    if not eq_identifier(tok):
        return False
    if not eq_identifier(lex_peek(1)):
        return False
    if not lex_peek(2) == "(":
        return False

    return True


def print_ast(node, ident=0, prefix=""):
    if not node:
        return

    print((" " * ident) + prefix, end="")

    # unary nodes
    if node.ty in [
            NodeType.Program,
            NodeType.FunDecl,
            NodeType.VarDecl,
            NodeType.Block,
            NodeType.Return,
            NodeType.FunCall,
            NodeType.UnaryMinus,
            NodeType.BoolNot]:
        print(node)
        print_ast(node.lhs, ident + 4)

    # list nodes
    elif node.ty in [
            NodeType.Statement,
            NodeType.DeclList,
            NodeType.FunCallArg]:
        print(node)
        print_ast(node.rhs, ident + 4)
        print_ast(node.lhs, ident)

    # binary operands
    elif node.ty in [
            NodeType.Assignament,
            NodeType.Plus, 
            NodeType.Minus, 
            NodeType.Multiply, 
            NodeType.Divide,
            NodeType.BoolAnd,
            NodeType.BoolOr,
            NodeType.BoolNotEqual,
            NodeType.BoolEqual,
            NodeType.BoolGt,
            NodeType.BoolGte,
            NodeType.BoolLt,
            NodeType.BoolLte]:
        print(node)
        print_ast(node.lhs, ident + 4, prefix="left: ")
        print_ast(node.rhs, ident + 4, prefix="right: ")

    # while statement
    elif node.ty == NodeType.While:
        print(node)
        print_ast(node.lhs, ident + 4, prefix="left(pred): ")
        print_ast(node.rhs, ident + 4, prefix="right(loop): ")

    # if statement
    elif node.ty == NodeType.If:
        print(node)
        print_ast(node.lhs, ident + 4, prefix="left(pred): ")
        print_ast(node.rhs, ident + 4, prefix="right(true): ")
        print_ast(node.oth, ident + 4, prefix="other(false): ")

    # for statement
    elif node.ty == NodeType.For:
        print(node)
        print_ast(node.lhs, ident + 4, prefix="left(init): ")
        print_ast(node.rhs, ident + 4, prefix="right(blok): ")
        print_ast(node.oth, ident + 4, prefix="other(cond): ")
        print_ast(node.oth2, ident + 4, prefix="other2(iter): ")

    else:
        print(node)


# ident = leter { leter_or_digit }
def identifier():
    global token
    debug("<identifier>")

    ident = AstNode(NodeType.Identifier, value1=token)
    token = lex()

    debug(f"<identifier {token}>")
    return ident

# <assignment> ::= <identifier> = <expression>
#    | <identifier> [ <expression> ] = <expression>
def assignment():
    global token
    debug("<assignment>")

    ident = identifier()
    token = lex() # skip '='
    expr = expression()

    debug(f"</assignment>({ident})", [ident, expr])
    node = AstNode(NodeType.Assignament, ident, expr)
    return node


# <expression> ::= <expression> <addingop> <term> | <term> | <addingop> <term>
def expression():
    global token

    debug("<expression>")
    startingtoken = "+"

    if token in ["+", "-", "!"]:
        debug(f"<unary>({token})")
        startingtoken = token
        token = lex()

    nfirst = term()

    if startingtoken == "-":
        nfirst = AstNode(NodeType.UnaryMinus, nfirst)
    elif startingtoken == "!":
        nfirst = AstNode(NodeType.BoolNot, nfirst)

    while eq_addingop(token):
        debug(f"<addingop>({token})")
        if token == "+":
            nt = NodeType.Plus
        elif token == "-":
            nt = NodeType.Minus
        elif token == "==":
            nt = NodeType.BoolEqual
        elif token == "!=":
            nt = NodeType.BoolNotEqual
        elif token == ">":
            nt = NodeType.BoolGt
        elif token == ">=":
            nt = NodeType.BoolGte
        elif token == "<":
            nt = NodeType.BoolLt
        elif token == "<=":
            nt = NodeType.BoolLte
        elif token == "&&":
            nt = NodeType.BoolAnd
        elif token == "||":
            nt = NodeType.BoolOr
        else:
            return error(f"invalid token: {token} not allowed in expression")

        token = lex()
        nterm2 = term()
        nfirst = AstNode(nt, nfirst, nterm2)

    debug("</expression>")
    return nfirst

# term = factor { multop factor }
def term():
    global token

    debug("<term>")
    nfirst = factor()

    while eq_multop(token):
        debug(f"<multop>({token})")
        if token == "*":
            nt = NodeType.Multiply
        else:
            nt = NodeType.Divide
        token = lex()
        nfactor = factor()
        nfirst = AstNode(nt, nfirst, nfactor)

    debug("</term>")
    return nfirst

# fun_call_arguments = expression { "," expression }
def fun_call_arguments():
    global token

    args = node = AstNode(NodeType.FunCallArg)
    node.rhs = expression()
    node.lhs = AstNode(NodeType.FunCallArg)
    node = node.lhs

    while token == ",":
        token = lex()
        node.lhs = AstNode(NodeType.FunCallArg)
        node.rhs = expression()
        node = node.lhs

    return args

# fun_call = identifier "(" [fun_call_arguments] ")"
def fun_call():
    global token
    debug("<fun_call>")

    fun_name = token
    token = lex()

    args = []
    if token == "(":
        token = lex()
        if token != ")":
            args = fun_call_arguments()
    else:
        return error(f"invalid token: {token} left parent expected")

    if token == ")":
        token = lex()
    else:
        return error(f"invalid token: {token} right parent expected")

    debug("</fun_call>", [fun_name, args])
    return AstNode(NodeType.FunCall, args, value1=[fun_name])


# <factor> ::= <constant> | identifier | ( <expression> ) | fun_call
#              | identifier '(' argument_list ')'
#              | identifier '[' expression ']'
#              | identifier '.' identifier 
#              | identifier '++'
#              | identifier '--'
def factor():
    global token
    debug("<factor>")
    
    if eq_constant(token):
        debug(f"<constant/>({token})")
        node = AstNode(NodeType.Constant, value1=[token])
        token = lex()
    elif eq_identifier(token):
        peek = lex_peek(1)
        if peek == "(":
            node = fun_call()
        elif peek == "[":
            debug(f"<postfix de ref array [")
            return error(f"invalid expresion, not implemented []")
        elif peek == "++":
            debug(f"<postfix ++ ")
            return error(f"invalid expresion, not implemented ++")
        elif peek == "--":
            debug(f"<postfix -- ")
            return error(f"invalid expresion, not implemented --")
        else:
            debug(f"<identifier/>({token})")
            node = AstNode(NodeType.Identifier, value1=[token])
            token = lex()
    elif token == "(":
        token = lex()
        node = expression()
        if token == ")":
            token = lex()
        else:
            error(f"invalid token: {token} rparent expected.")
    else:
        error(f"invalid token: {token} constant or lparent expected.")
   
    debug("</factor>")
    return node


# var_decl = type_ident identifier | type_ident identifier = expression
def var_decl():
    global token

    debug("<var_decl>")
    if eq_identifier(token):
        var_type = token
        token = lex()
    else:
        return error(f"invalid token {token}: type identifier expected")

    if eq_identifier(token):
        var_name = token
    else:
        return error(f"invalid token {token}: variable name identifier expected")

    ntoken = lex_peek(1)
    if ntoken == '=':
        assign = assignment()
    else:
        assign = None
        token = lex() # consume identifier lately

    node = AstNode(NodeType.VarDecl, lnode=assign, value1=[var_type, var_name])
    debug("</var_decl>", node.v1)
    return node


# if_statement = if ( bool_expression ) { block } else { block } | if ( bool_expression ) { block }
def if_stmt():
    global token
    debug("<if_stmt>")

    blk_false = None
    
    token = lex()
    if token == '(':
        token = lex()
        bool_expr = expression()
    else:
        error("invalid token: {token} '(' expected")
        
    token = lex()

    blk_true = block()

    if token == 'else':
        token = lex()
        blk_false = block()

    debug("</if_stmt>")
    node = AstNode(NodeType.If, lnode=bool_expr, rnode=blk_true, other=blk_false) 
    return node

# while_stmt = while ( expression )
def while_stmt():
    global token
    debug("<while_stmt>")

    cond = None
    blk = None

    token = lex()
    if token == '(':
        token = lex()
        cond = expression()
    else:
        error("invalid token: {token} '(' expected")

    if token == ')':
        token = lex()
    else:
        error("invalid token: {token} ')' expected")

    debug("token -------------------", token)
    blk = block()

    debug("</while_stmt>")
    node = AstNode(NodeType.While, lnode=cond, rnode=blk) 
    return node

# return_stmt = "return" expression
def return_stmt():
    global token
    debug("<return_stmt>")

    token = lex()
    expr = expression()
    
    debug("</return_stmt>")
    node = AstNode(NodeType.Return, lnode=expr) 
    return node


# for_statement = for ( var_decl | assignment ; expression ; assignment | assignment )
def for_stmt():
    global token
    debug("<for_stmt>")

    init = None
    cond = None
    assig = None
    blk = None

    token = lex()
    if token == '(':
        token = lex()
        if is_type(token):
            init = var_decl()
        else:
            init = assignment()
    else:
        error("invalid token: {token} '(' expected")

    if token == ';':
        token = lex()
        cond = expression()

    if token == ';':
        token = lex()
        assig = assignment()

    if token == ')':
        token = lex()
    else:
        error("invalid token: {token} ')' expected")

    if token == '{':
        blk = block()
    else:
        blk = statement()

    debug("</for>")
    node = AstNode(NodeType.For, lnode=init, rnode=blk, other=cond, other2=assig) 
    return node


# statement = assignment | expression
def statement():
    global token

    debug("<statement>", token)
    tknext = lex_peek(1)
    if tknext == "=":
        node = assignment()
    elif is_type(token):
        node = var_decl()
    elif token == "if":
        node = if_stmt()
    elif token == "for":
        node = for_stmt()
    elif token == "while":
        node = while_stmt()
    elif token == "return":
        node = return_stmt()
    else:
        node = expression()
        debug(token)

    stmt = AstNode(NodeType.Statement)
    stmt.rhs = node
    ## fix, check ';' for not block statements
    if token == ";":
        token = lex()

    debug("</statement>")
    return stmt


# block = statement | { statement* }
def block():
    global token
    debug("<block>")

    blk = AstNode(NodeType.Block)
    if token == "{":
        token = lex()

        blk.lhs = last = AstNode(NodeType.Statement)
        while token != "}" and token != "":
            tmp = statement()
            last.lhs = AstNode(NodeType.Statement)
            last.rhs = tmp.rhs
            last = last.lhs

        token = lex()
    else: # single statement
        stmt = statement()
        stmt.lhs = AstNode(NodeType.Statement)
        blk.lhs = stmt

    debug("</block>")
    return blk


def type_and_arg():
    global token

    type_ident = ""
    arg_ident = ""

    if eq_identifier(token):
        type_ident = token
        token = lex()
    else:
        return error(f"invalid token {token}: identifier expected")

    if eq_identifier(token):
       arg_ident = token
       token = lex()
    else:
        return error(f"invalid token {token}: identifier expected")

    return [type_ident, arg_ident]

# type_arg_list = type_and_arg | ("," type_and_arg)*
def type_and_arg_list():
    global token
    args = []

    args.append(type_and_arg())
    while token == ',':
        token = lex()
        args.append(type_and_arg())

    return args

# argument_list = '(' void | [ type_arg_list ] ')'
def fun_argument_list():
    global token

    args = []
    if token == "void":
        ## is a function without parameters
        token = lex()
        if token == ')':
            token = lex()
            return args
        else:
            return error(f"invalid token {token}: ')' expected")
    else:
        ## is a function with any parameters
        if token == ')':
            token = lex()
        else:
            ## is a function with this parameters
            args = type_and_arg_list()
            token = lex()

    return args

# fun_decl = identifier identifier "(" [ argument_list ] ")" block
def fun_decl():
    global token
    debug("<fun_decl>")

    if eq_identifier(token):
        fun_ret_type = token
        token = lex()
    else:
        return error("identifier expected")

    if eq_identifier(token):
        fun_name = token
        token = lex()
    else:
        return error("identifier expected")

    fun_args = []
    if token == "(":
        token = lex()
        fun_args = fun_argument_list()
    else:
        return error("identifier expected")

    blk = block()

    debug("</fun_decl> : ", [fun_ret_type, fun_name, fun_args])
    return AstNode(NodeType.FunDecl, value1=[fun_ret_type, fun_name, fun_args], lnode=blk)


def decl_list():
    global token
    debug("<fun_decl_list>")

    decls = node = AstNode(NodeType.DeclList)
    while eq_fun_decl(token):
        node.rhs = fun_decl()
        node.lhs = AstNode(NodeType.DeclList)
        node = node.lhs

    debug("</fun_decl_list>")
    return decls


def program() -> AstNode:
    debug("<program>")
    prog = AstNode(NodeType.Program)

    if token == "":
        debug("</program>")
    else:
        decls = decl_list()
        prog.lhs = decls

    return prog


def tokenize():
    tk = read_lex()
    while tk != "eof":
        tokens.append(tk)
        tk = read_lex()


def parse():
    global token
    token = lex()
    return program()


if "-d" in sys.argv:
    op_debug = True

if "-a" in sys.argv:
    op_ast = True

if "-t" in sys.argv:
    op_translate = True


tokenize()


ast = parse()
if op_ast:
    print_ast(ast)

if op_translate:
    translate(ast)

