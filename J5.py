#!/usr/bin/env python

import cnorm
from cnorm.parsing.statement import Statement
from cnorm.parsing.declaration import Declaration
from cnorm.passes import to_c
from pyrser.grammar import Grammar
from pyrser import meta

class MaPremiereClasse(Grammar, Declaration):

    entry = "translation_unit"
    grammar = """
    declaration = [Declaration.declaration | beg]
    
    beg = ["@begin" '(' id :i ')' Statement.compound_statement :st #add_begin(current_block, i, st)]
    
    """


class AtBegin:
    def __init__(self, ast, fname, body, idx):
        self.ast = ast
        self.fname = fname
        self.body = body
        self.idx = idx

        
@meta.hook(MaPremiereClasse)
def add_begin(self, block, idi, statement):

    topDoggyDog = AtBegin(block.ref, self.value(idi), statement.body, len(block.ref.body))
    block.ref.body.append(topDoggyDog)
    return True



def maSuperTransfo(ast):
    maSuperListe = []
    for it in ast.body:
        if isinstance(it, AtBegin):
            maSuperListe.append(it)
            for i in it.ast.body:
                if not isinstance(i, AtBegin):
                    if i._name == it.fname:
                        for idx, val in enumerate(it.body):
                            i.body.body.insert(idx, val)
    for it in reversed(maSuperListe):
        ast.body.pop(it.idx)



        
a = MaPremiereClasse()
r = a.parse_file("./main.c")
maSuperTransfo(r)
print("\n")
print(r.to_c())
