#!/usr/bin/env python

from copy import copy
import cnorm
from cnorm.parsing.statement import Statement
from cnorm.parsing.declaration import Declaration
from cnorm.passes import to_c
from pyrser.grammar import Grammar
from pyrser import meta

class AspectC(Grammar, Declaration):

    entry = "translation_unit"
    grammar = """
    declaration = [Declaration.declaration | beg | end]
    beg = ["@begin" '(' id :i ')' Statement.compound_statement :st #add_begin(current_block, i, st)]
    end = ["@end" '(' id :i ')' Statement.compound_statement :st #add_end(current_block, i, st)]
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


def maSuperTransfo(ast):
    maSuperListe = []
    for it in ast.body:
        if isinstance(it, AtBegin):
            maSuperListe.append(it)
            for i in it.ast.body:
                if not isinstance(i, AtBegin) and not isinstance(i, AtEnd):
                    if i._name == it.fname:
                        for idx, val in enumerate(it.body):
                            i.body.body.insert(idx, val)


        if isinstance(it, AtEnd):
            maSuperListe.append(it)
            for i in it.ast.body:
                if not isinstance(i, AtBegin) and not isinstance(i, AtEnd):
                    if i._name == it.fname:
                        blc = copy(i.body)
                        blc.body = []
                        for bod in i.body.body:
                            if type(bod) == cnorm.nodes.Return:
                                for val in it.body:
                                    blc.body.append(val)
                            if not isinstance(bod, AtBegin) and not isinstance(bod, AtEnd):
                                blc.body.append(bod)    
                                                    
                        i.body = blc             
    for it in reversed(maSuperListe):
        ast.body.pop(it.idx)



        
a = AspectC()
r = a.parse_file("./main.c")
maSuperTransfo(r)
print("\n")
print(r.to_c())
