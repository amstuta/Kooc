#!/usr/bin/env python

import os
import cnorm
from user_class import *
from module import *
from implementation import *
import decl_keeper
from kooc_call import *
from pyrser import meta
from pyrser.grammar import Grammar
from cnorm.parsing.statement import Statement
from cnorm.parsing.declaration import Declaration
from cnorm.passes import to_c
from pyrser import error

execPath = os.getcwd()
filePath = os.path.realpath(os.path.dirname(__file__))


class Kooc(Grammar, Declaration):
    entry = 'translation_unit'
    grammar = """

    primary_expression = [ 
      '(' expression:expr ')' #new_paren(_, expr) 
      | [ Literal.literal | identifier ]:>_ 
      | kooc_expression:>_
    ]

    kooc_expression = [
        [
            kooc_call:>_
            | kooc_cast:>_
        ]
    ]

    kooc_cast = [
      "@!" '(' type_name:t ')' '[' expression:e ']'
      #kooc_cast(_, t, e)
    ]

    kooc_call = [
            
        '['
            primary_expression:i #kooc_call(_, i)
            [
                [ '.' Base.id:mbr #kooc_call_member(_, mbr) ]
                |
                [
                    Base.id:func #kooc_call_func(_, func)
                    [ ':' assignement_expression:e #kooc_call_add_param(_, e) ]*
                    #kooc_end_call(_, current_block)
                ]
            ]
        ']'

    ]

    declaration = [Declaration.declaration | module | import | implementation | class]
    module = ["@module" id :i Statement.compound_statement :st #add_module(st, i)]
    import = ["@import" '"' [id ".kh"] :i '"' #add_import(current_block, i)]


    class_compound_statement = [
    '{'
    __scope__ :current_block #new_blockstmt(_,current_block)
    [
        ["@member"  [c_decl | Statement.compound_statement :st #add_block(_, st)] #add_member(_, current_block)]
      | ["@virtual" [c_decl | Statement.compound_statement] #add_virtual(_, current_block)]
      | c_decl
    ]*
    '}'
    ]

    class = [
      "@class" id :class_name #add_type(current_block, class_name)
      [':' id :parent_class #add_parent(class_name, parent_class) ]?
      class_compound_statement :st #add_class(current_block, class_name, st)
    ]

    implementation = ["@implementation" id :class_name imp_compound_st :st #add_implementation(class_name, st)]
    imp_compound_st = [
    '{'
    __scope__ :current_block #new_blockstmt(_, current_block)
    ["@member"? line_of_code]*
    '}'
    ]

    """
    imports = []
    types = None

    def __init__(self, flag=False):
        self.recurs = flag
        super(Kooc, self).__init__()



@meta.hook(Kooc)
def add_block(self, node, st):
    if not hasattr(node, 'body'):
        setattr(node, 'body', [])
    node.body.append(st)
    return True

@meta.hook(Kooc)
def kooc_cast(self, node, t, expr):
    node.set(KoocCast(t._ctype, expr))
    return True

@meta.hook(Kooc)
def kooc_call(self, node, i):
    node.set(KoocCall(i))
    return True

@meta.hook(Kooc)
def kooc_call_member(self, node, mbr):
    node.call = False
    node.member = self.value(mbr)
    return True

@meta.hook(Kooc)
def kooc_call_func(self, node, func):
    node.call = True
    node.member = self.value(func)
    node.params = []
    return True

@meta.hook(Kooc)
def kooc_call_add_param(self, node, expr):
    node.params.append(expr)
    return True

@meta.hook(Kooc)
def kooc_end_call(self, node, current_block):
    #detecter appel grace a une variable/un moduel directement
    return True

@meta.hook(Kooc)
def add_parent(self, class_name, parent_name):
    decl_keeper.inher[self.value(class_name)] = self.value(parent_name)
    return True


@meta.hook(Kooc)
def add_virtual(self, node, ast):
    if not hasattr(node, 'virtuals'):
        setattr(node, 'virtuals', [])
    node.virtuals.append(ast.ref.body[len(ast.ref.body) - 1])
    ast.ref.body.pop(len(ast.ref.body) - 1)
    return True


@meta.hook(Kooc)
def add_module(self, statement, ident):
    ident = self.value(ident)
    mod = Module(ident, statement, self.recurs)
    decl_keeper.modules[ident] = mod
    return True


@meta.hook(Kooc)
def add_member(self, node, ast):
    if not hasattr(node, 'members'):
        setattr(node, 'members', [])
    st = ast.ref.body[len(ast.ref.body) - 1]
    if hasattr(st, '_ctype') and hasattr(st._ctype, '_identifier') \
       and st._ctype._identifier in ast.ref.types:
        raise BaseException('Error during parsing: symbol \"%s\" redeclared differently' % st._ctype._identifier)
    node.members.append(ast.ref.body[len(ast.ref.body) - 1])
    ast.ref.body.pop(len(ast.ref.body) - 1)
    return True


@meta.hook(Kooc)
def add_type(self, ast, class_name):
    if Kooc.types == None:
        Kooc.types = ast.ref.types
    ast.ref.types[self.value(class_name)] = None
    Kooc.types[self.value(class_name)] = None
    return True


@meta.hook(Kooc)
def add_implementation(self, class_name, statement):
    if self.recurs:
        return True
    class_name = self.value(class_name)
    imp = Implementation(class_name, statement)
    decl_keeper.implementations.append(imp)
    return True


@meta.hook(Kooc)
def add_class(self, ast, class_name, statement):
    class_name = self.value(class_name)
    cl = Class(class_name, statement, self.recurs)
    decl_keeper.classes[class_name] = cl
    tpds = cl.register_typedefs()
    vt = cl.register_struct_vt()
    struct = cl.register_struct()
    non_mbrs = cl.register_non_members()
    inst = cl.instanciate_vt()
    ast.ref.body.extend(tpds)
    ast.ref.body.append(vt)
    ast.ref.body.append(struct)
    ast.ref.body.extend(cl.protos)
    ast.ref.body.extend(non_mbrs)
    ast.ref.body.append(inst)
    return True


@meta.hook(Kooc)
def add_import(self, ast, ident):
    mod_name = self.value(ident)
    if mod_name in Kooc.imports:
        return True
    if Kooc.types == None:
        Kooc.types = ast.ref.types
    a = Kooc(True)
    r = a.parse_file(execPath + '/' + mod_name)
    for elem in r.body:
        if type(elem) == cnorm.nodes.Decl:
            decl_keeper.ids.append(elem._name)
    if not mod_name.endswith('.kh'):
        return True
    inc_name = mod_name.replace('.kh', '.h')
    inc = "#include \"%s\"\n" % inc_name
    raw = cnorm.nodes.Raw(inc)
    ast.ref.body.append(raw)
    return True


from misc import *
