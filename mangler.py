import cnorm    

inst = None
speci = {4 : "L",
         5 : "LL",
         6 : "S"}

    
def changeClass(proto, newClassy, oldClassy):
    return proto.replace(oldClassy, newClassy)


def muckFangle(proto, module):
    res = ""
    if isinstance(proto._ctype, cnorm.nodes.FuncType):
        res += "Func"
    else:
        res += "Var"
    res += '$'
    res += module + '$'
    res += proto._name
    res += muckFimpleSangle(proto._ctype._decltype, False)
    #pointerR = proto._ctype._decltype
    #while pointerR != None:
     #   if isinstance(pointerR, cnorm.nodes.PointerType):
      #      res += 'P'
       # elif isinstance(pointerR, cnorm.nodes.ArrayType):
        #    res += 'A'
        #pointerR = pointerR._decltype
    if proto._ctype._specifier in range(4,7):
        res += Mangler.speci[proto._ctype._specifier]
    res += '$' + proto._ctype._identifier
    if isinstance(proto._ctype, cnorm.nodes.FuncType):
        for par in proto._ctype.params:
            res += muckFimpleSangle(par._ctype._decltype, False)
            #pointer = par._ctype._decltype
            #res += '$'
            #while pointer != None:
            #    if isinstance(pointer, cnorm.nodes.PointerType):
            #        res += 'P'
            #    elif isinstance(pointer, cnorm.nodes.ArrayType):
            #        res += 'A'
            #    pointer = pointer._decltype
            if par._ctype._specifier in range(4,7):
                res += Mangler.speci[par._ctype._specifier]
            res += '$' + par._ctype._identifier
    return res

    
def mimpleSangle(proto):
    res = ""
    res += proto._name
    """pointerR = proto._ctype._decltype
    while pointerR != None:
    if isinstance(pointerR, cnorm.nodes.PointerType):
    res += 'P'
    elif isinstance(pointerR, cnorm.nodes.ArrayType):
    res += 'A'
    pointerR = pointerR._decltype
    if proto._ctype._specifier in range(4,7):
    res += Mangler.speci[proto._ctype._specifier]
    res += '$' + proto._ctype._identifier"""
    res += muckFimpleSangle(proto._ctype._decltype, True)
    if proto._ctype._specifier in range(4,7):
        res += Mangler.speci[proto._ctype._specifier]
    res += "$" + proto._ctype._identifier
    #if hasattr(proto._ctype._decltype._decltype, "_params"):
    if isinstance(proto._ctype, cnorm.nodes.FuncType):
        for idx, par in enumerate(proto._ctype.params):
            if idx == 0 : continue
            res += muckFimpleSangle(par._ctype._decltype, True)
            #pointer = par._ctype._decltype
            #res += '$'
            #while pointer != None:
            #    if isinstance(pointer, cnorm.nodes.PointerType):
            #        res += 'P'
            #    elif isinstance(pointer, cnorm.nodes.ArrayType):
            #        res += 'A'
            #    pointer = pointer._decltype
            if par._ctype._specifier in range(4,7):
                res += Mangler.speci[par._ctype._specifier]
            res += '$' + par._ctype._identifier
    """for idx, par in enumerate(proto._ctype._decltype._decltype._params):
    print (par._ctype._identifier)
    if idx == 0: continue
    pointer = par._ctype._decltype
    res += '$'
    while pointer != None:
    if isinstance(pointer, cnorm.nodes.PointerType):
    res += 'P'
    elif isinstance(pointer, cnorm.nodes.ArrayType):
    res += 'A'
    pointer = pointer._decltype
    if par._ctype._specifier in range(4,7):
    res += Mangler.speci[par._ctype._specifier]
    res += '$' + par._ctype._identifier"""
    return res

def muckFimpleSangle(decltype, flag):
    res = "$"
    while decltype != None:
        if isinstance(decltype, cnorm.nodes.PointerType):
            res += 'P'
        elif isinstance(decltype, cnorm.nodes.ArrayType):
            res += 'A'
        elif isinstance(decltype, cnorm.nodes.ParenType):
            res += "Func"
            if hasattr(decltype, "_params"):
                res += SuckFimpleFangle(decltype._params, flag)
            else:
                res += SuckFimpleFangle(decltype.params, flag)
        decltype = decltype._decltype
    return res


def SuckFimpleFangle(para, flag):
    res = ""
    for idx, par in sorted(enumerate(para)):
        if idx == 0 and flag == True : continue
        res += '$'
        res += muckFimpleSangle(par._ctype._decltype, False)
        res += '$' + par._ctype._identifier
    return res


