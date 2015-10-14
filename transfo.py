import cnorm
from decl_keeper import *

def moduleTransfo(ast):
    for mod in DeclKeeper.instance().modules:
        if DeclKeeper.instance().modules[mod].recurs == False:
            for decl in DeclKeeper.instance().modules[mod].decls:
                ast.body.append(DeclKeeper.instance().modules[mod].decls[decl])

    for class_name in DeclKeeper.instance().implementations:
        imp = DeclKeeper().instance().implementations[class_name]
        for i in imp.imps:
            ast.body.append(imp.imps[i])
        ast.body.extend(imp.virtuals)


def add_include(ast):
    raw = cnorm.nodes.Raw('#include \".h\"\n')
    ast.body.insert(0, raw)


def add_defines(ast, file_name):
    file_name = file_name[file_name.rfind('/') + 1:]
    define = file_name.replace('.', '_').upper()
    ast.body.insert(0, cnorm.nodes.Raw('#ifndef %s\n' % define))
    ast.body.insert(1, cnorm.nodes.Raw('#define %s\n' % define))
    ast.body.append(cnorm.nodes.Raw('#endif\n'))
