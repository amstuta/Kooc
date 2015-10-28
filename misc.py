import cnorm
import os
from os.path import isfile
from sys import argv
import decl_keeper
from kooc_class import Kooc

execPath = os.getcwd()
filePath = os.path.realpath(os.path.dirname(__file__))

def moduleTransfo(ast):
    for mod in decl_keeper.modules:
        if decl_keeper.modules[mod].recurs == False:
            for decl in decl_keeper.modules[mod].decls:
                ast.body.append(decl)
    for imp in decl_keeper.implementations:
        for i in imp.imps:
            ast.body.append(i)
        ast.body.extend(imp.virtuals)


def add_include(ast):
    raw = cnorm.nodes.Raw('#include \"kooc.h\"\n')
    ast.body.insert(0, raw)


def add_defines(ast, file_name):
    file_name = file_name[file_name.rfind('/') + 1:]
    define = file_name.replace('.', '_').upper()
    ast.body.insert(0, cnorm.nodes.Raw('#ifndef %s\n' % define))
    ast.body.insert(1, cnorm.nodes.Raw('#define %s\n' % define))
    ast.body.append(cnorm.nodes.Raw('#endif\n'))


def write_file_out(file_name, ast):
    fd = open(file_name, 'w+')
    fd.write(str(ast.to_c()))
    fd.close()


def check_argv():
    if len(argv) != 2:
        print('Only one parameter required')
        exit(1)
    inFile = os.path.realpath(argv[1])
    outFile = ''
    if not isfile(inFile):
        print('Given file doesn\'t exist')
        exit(1)
    if inFile.endswith('.kc'):
        outFile = inFile.replace('.kc', '.c')
    elif inFile.endswith('.kh'):
        outFile = inFile.replace('.kh', '.h')
    else:
        print('Bad format for input file')
        exit(1)
    if outFile.rfind('/') != -1:
        outFile = outFile[outFile.rfind('/') + 1:]
    outFile = execPath + '/' + outFile
    return inFile, outFile


def create_header():
    a = Kooc()
    res_h = a.parse_file(filePath + '/kooc.kh')
    res_h.body.insert(0, cnorm.nodes.Raw('#ifndef KOOC_H\n#define KOOC_H\n'))
    moduleTransfo(res_h)
    decl_keeper.create_typedef_vt()
    res_h.body.append(cnorm.nodes.Raw('#endif\n'))
    res_h.body.insert(3, decl_keeper.typedef_vt_object)
    outFile = execPath + '/kooc.h'
    write_file_out(outFile, res_h)

    res_c = a.parse_file(filePath + '/kooc.kc')
    res_c.body.append(decl_keeper.instanciate_vtable())
    res_c.body.pop(0)
    res_c.body.extend(decl_keeper.implementations[0].imps)
    outFile = execPath + '/kooc.c'
    write_file_out(outFile, res_c)

    decl_keeper.clean_implementations()
