#!/usr/bin/env python

import cnorm
from copy import copy, deepcopy
from cnorm.parsing.statement import Statement
from cnorm.parsing.declaration import Declaration
from cnorm.passes import to_c
from pyrser.grammar import Grammar
from pyrser import meta


class AspectC(Grammar, Declaration):
    entry = "translation_unit"
    grammar = """
    declaration = [Declaration.declaration | beg | end | callb]
    beg = ["@begin" '(' id :i ')' Statement.compound_statement :st #add_begin(current_block, i, st)]
    end = ["@end" '(' id :i ')' Statement.compound_statement :st #add_end(current_block, i, st)]
    callb = ["@callback" '(' id :i ')' ';' #add_callback(current_block, i)]
    """


class AtBegin:
    def __init__(self, ast, fname, body, idx):
        self.ast = ast
        self.fname = fname
        self.body = body
        self.idx = idx


class AtEnd:
    def __init__(self, ast, fname, body, idx):
        self.ast = ast
        self.fname = fname
        self.body = body
        self.idx = idx


class AtCallback:
    def __init__(self, ast, fname, idx):
        self.ast = ast
        self.fname = fname
        self.idx = idx

    def doTrans(self):
        decl = deepcopy(self.ast.func(self.fname))
        if hasattr(decl, 'body'):
            del decl.body
        decl._name = 'callback_' + self.fname
        decl._ctype._storage = cnorm.nodes.Storages.TYPEDEF
        internal = cnorm.nodes.ParenType()
        decl._ctype.push(internal)
        decl._ctype.push(cnorm.nodes.PointerType())
        internal._params = decl._ctype._params
        del decl._ctype._params
        decl._ctype.__class__ = cnorm.nodes.PrimaryType
        self.ast.body[self.idx] = decl




@meta.hook(AspectC)
def add_begin(self, block, idi, statement):
    topDoggyDog = AtBegin(block.ref, self.value(idi), statement.body, len(block.ref.body))
    block.ref.body.append(topDoggyDog)
    return True


@meta.hook(AspectC)
def add_end(self, block, idi, statement):
    topDoggyDog = AtEnd(block.ref, self.value(idi), statement.body, len(block.ref.body))
    block.ref.body.append(topDoggyDog)
    return True


@meta.hook(AspectC)
def add_callback(self, ast, idi):
    cb = AtCallback(ast.ref, self.value(idi), len(ast.ref.body))
    ast.ref.body.append(cb)
    ast.ref.types["callback_" + self.value(idi)] = None
    return True


def handleThen(bod, it):
    if type(bod.thencond) == cnorm.nodes.BlockStmt:
        blc = copy(bod.thencond)
        blc.body = []
        for i in bod.thencond.body:
            if type(i) == cnorm.nodes.If:
                handleThen(i, it)
                handleElse(i, it)
            elif type(i) == cnorm.nodes.Return:
                for val in it.body:
                    blc.body.append(val)
            blc.body.append(i)
        bod.thencond.body = blc.body

    elif type(bod.thencond) == cnorm.nodes.Return:
        blc = copy(it.body)
        blc.append(bod.thencond)
        nBlock = cnorm.nodes.BlockStmt(blc)
        bod.thencond = nBlock

    elif type(bod.thencond) == cnorm.nodes.If:
        handleThen(bod.thencond, it)
        handleElse(bod.thencond, it)



def handleElse(bod, it):
    if type(bod.elsecond) == cnorm.nodes.BlockStmt:
        blc = copy(bod.elsecond)
        blc.body = []
        for i in bod.elsecond.body:
            if type(i) == cnorm.nodes.If:
                handleThen(i, it)
                handleElse(i, it)
            elif type(i) == cnorm.nodes.Return:
                for val in it.body:
                    blc.body.append(val)
            blc.body.append(i)
        bod.elsecond.body = blc.body

    elif type(bod.elsecond) == cnorm.nodes.Return:
        blc = copy(it.body)
        blc.append(bod.elsecond)
        nBlock = cnorm.nodes.BlockStmt(blc)
        bod.elsecond = nBlock

    elif type(bod.elsecond) == cnorm.nodes.If:
        handleThen(bod.elsecond, it)
        handleElse(bod.elsecond, it)



def maSuperTransfo(ast):
    toPop = []
    for it in ast.body:
        if isinstance(it, AtBegin):
            toPop.append(it)
            for i in it.ast.body:
                if not isinstance(i, AtBegin) and not isinstance(i, AtEnd) and not isinstance(i, AtCallback):
                    if i._name == it.fname:
                        for idx, val in enumerate(it.body):
                            i.body.body.insert(idx, val)

        if isinstance(it, AtEnd):
            toPop.append(it)
            for i in it.ast.body:
                if not isinstance(i, AtBegin) and not isinstance(i, AtEnd) and not isinstance(i, AtCallback):
                    if i._name == it.fname:
                        blc = copy(i.body)
                        blc.body = []
                        for bod in i.body.body:
                            if type(bod) == cnorm.nodes.If:
                                handleThen(bod, it)
                                handleElse(bod, it)
                            
                            if type(bod) == cnorm.nodes.Return:
                                for val in it.body:
                                    blc.body.append(val)
                            if not isinstance(bod, AtBegin) and not isinstance(bod, AtEnd) and not isinstance(bod, AtCallback):
                                blc.body.append(bod)
                        i.body = blc

        if isinstance(it, AtCallback):
            it.doTrans()
                        
    for it in reversed(toPop):
        ast.body.pop(it.idx)




a = AspectC()
r = a.parse_file("./main.c")
maSuperTransfo(r)
print("\n")
print(r.to_c())
