#from typing import Tuple, List, Dict, _GenericAlias
from collections import defaultdict
import collections
import enum
import inspect
import typing

class Nothing:
    pass

def constructtype(typename, typeargs=Nothing):
    """Construct type from typename and typeargs
    
    Parameters
    ----------
    typename : str
        Typename, ex. "List", "Tuple" in "typing" library
    typeargs : [type]
        Tuple or list of types, ex. [int, str] for tuple; (5, "five")

    Returns
    -------
    Type descriptor from typing -class. Ex. Tuple[int, str]
    """
    
    typeclass = typing.__dict__[typename]
    if typeargs is not Nothing:
        return typeclass[typeargs]
    else:
        return typeclass

def deeptype(var):
    _type = type(var)

    if _type == type or _type == typing._GenericAlias:
        return var
    
    return _type

# Compare types
# (List, List[int]) == 1
# (List, List) == True
# (List, list) == -1
# (List[int], list) == -1
# (List[int], Tuple[str, float]) == 0
class TypeComparison(enum.Enum):
    EQUAL = 0
    
    COMPATIBLE_LESS_DEFINITIVE = 1
    COMPATIBLE_MORE_DEFINITIVE = 2
    
    UNEQUAL = 3

typemap = {
    list: typing.List,
    tuple: typing.Tuple,
    dict: typing.Dict,
    str: typing.Text,
    int: int,

    # Experimental features, missing tests
    collections.deque: typing.Deque,
    set: typing.Set,
    collections.defaultdict: typing.DefaultDict,
    collections.Counter: typing.Counter,
    collections.ChainMap: typing.ChainMap,
}

def totypingtype(var):
    if var.__module__ == "builtins":
        return typemap[var]
    elif var.__module__ == "typing":
        return var
    else:
        raise Exception("var type is not in typemap:", var, type(var), var.__module__)

def comparetypes(a, b):
    if a.__module__ == "builtins" and b.__module__ == "builtins":
        if a == b:
            return TypeComparison.EQUAL
        else:
            return TypeComparison.UNEQUAL

    a = totypingtype(a)
    b = totypingtype(b)

    if a == b:
        return TypeComparison.EQUAL

    if a._name != b._name:
        return TypeComparison.UNEQUAL
    else:
        defaultargs = constructtype(a._name).__args__
        if a.__args__ == defaultargs:
            return TypeComparison.COMPATIBLE_LESS_DEFINITIVE
        elif b.__args__ == defaultargs:
            return TypeComparison.COMPATIBLE_MORE_DEFINITIVE
        else:
            raise Exception("Comparison seems to be more than t._name and t.__args__ as it passed a==b")

def checksignature(func, *args, **kwargs):
    sig = inspect.signature(func)
    
    try:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
    except TypeError:
        return False
    
    for index, (name, param) in enumerate(bound.signature.parameters.items()):
        if index == 0 and name == "self":
            continue
        comparison = comparetypes(deeptype(param.annotation), deeptype(bound.arguments[name]))
        if comparison != TypeComparison.EQUAL and comparison != TypeComparison.COMPATIBLE_MORE_DEFINITIVE:
            return False
    return True

def evalassertions(func, funcargs, funckwargs, decargs, deckwargs):
    # print("func:", func)
    # print("funcargs:", funcargs)
    # print("funckwargs:", funckwargs)
    # print("decargs:", decargs)
    # print("deckwargs:", deckwargs)
    # print("Only function:", decoratoronlyfunction(*decargs, **deckwargs))
    try:
        bound = inspect.signature(func).bind(*funcargs, **funckwargs)
        bound.apply_defaults()
        boundargs = bound.arguments
    except:
        return False
    
    for key, assertions in deckwargs.items():
        if type(assertions) != tuple and type(assertions) != list:
            assertions = [assertions]

        for assertion in assertions:
            res = assertion(boundargs[key])
            if not res:
                return False

    if not decoratoronlyfunction(*decargs, **deckwargs):
        for value in boundargs.values():
            for assertion in decargs:
                res = assertion(value)
                if not res:
                    return False

    return True
            

class OverloadArgumentError(ValueError):
    pass

def init(funcname=None):
    if "__pypatterndict__" not in globals().keys():
        globals()["__pypatterndict__"] = defaultdict(list)
    
    if funcname is not None:
        globals()["__pypatterndict__"][funcname] = []

def patternedwrapper(*args, **kwargs):
    if len(args) == 1 and callable(args[0]) and not args[0].__code__.co_name == "<lambda>":
        return patterned_(args[0])
    else:
        return patterned_

def patterned_(func):
    if "__pypatterndict__" not in globals().keys():
        globals()["__pypatterndict__"] = defaultdict(list)
    def wrapper(*args, **kwargs):
        def error(*args, **kwargs):
            raise OverloadArgumentError("Could not find matching function for arguments:", args, kwargs)
        matchingfunc = error
        for f in globals()["__pypatterndict__"][func.__name__]:
            if checksignature(f, *args, **kwargs):
                matchingfunc = f
                break
        return matchingfunc(*args, **kwargs)

    globals()["__pypatterndict__"][func.__name__].append(func)
    return wrapper

def decoratoronlyfunction(*args, **kwargs):
    return len(args) == 1 and callable(args[0]) and not args[0].__code__.co_name == "<lambda>"

def patterned(*dargs, **dkwargs):
    def functionwrapper(func):
        if "__pypatterndict__" not in globals().keys():
            globals()["__pypatterndict__"] = defaultdict(list)
        def wrapper(*args, **kwargs):
            matches = []
            matchingfunc = None
            for f in globals()["__pypatterndict__"][func.__name__]:
                if checksignature(f, *args, **kwargs):
                    if evalassertions(f, args, kwargs, dargs, dkwargs):
                        res = f(*args, **kwargs)
                        return res
            else:
                raise OverloadArgumentError("Could not find matching function for arguments:", args, kwargs)

            assertions_passed = True

            if assertions_passed:
                return matchingfunc(*args, **kwargs)
            else:
                raise Exception("returning none")
                return None
    
        globals()["__pypatterndict__"][func.__name__].append(func)
        return wrapper

    if len(dargs) == 1 and callable(dargs[0]) and not dargs[0].__code__.co_name == "<lambda>":
        return functionwrapper(dargs[0])
    else:
        return functionwrapper
