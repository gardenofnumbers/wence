import json
from functools import wraps
from collections import defaultdict 
from itertools import chain
from pprint import PrettyPrinter; pp = PrettyPrinter().pprint
import code; 


import collections
DEBUG_ITER = False
_ = None;


class GraphIterException(Exception):
    def __init__(self, value): 
        self.value = value 


class Graph(dict): 
    # it's really two types at once but uhhhhhh sue me it's more fun this way
    @property
    def edges(self):
        return len(self.keys())

    def __getitem__(self,key):
        print("stop it dummy")
        return None
        assert isinstance(key,tuple) and len(key) == 4;
        # key, fn, v
        fn  = key[1]
        v   = key[2]
        key = key[0]
        assert callable(fn)
        n = dict.__getitem__(self,key)
        yield fn(n, v, self.G)      
    def __setitem__(self, key, value):
        print("stop it dummy")
        pass
    def __delitem__(self, key):
        pass
    def __init__(self, v=None):
        match v:
            case dict():
                g = v;
                self.G = self
                for i in g: 
                    dict.__setitem__(self,i,Graph((g[i], i)));
                for i in dict.__iter__(self):
                    n = dict.__getitem__(self, i)
                    n.G = self
                    n.N = i
                    for e in dict.__iter__(n):
                        if type(e) is not int:
                            continue
                        v = dict.__getitem__(self, e)
                        dict.__setitem__(n, e, v)
            case tuple():
                assert isinstance(v[0], dict) and isinstance(v[1], int)
                n,i = v;
                for v in n:
                    if isinstance(v, int):
                        dict.__setitem__(self,v,n[v])
                    else:
                        self.v = n[v]
            case _:
                print(type(v))
                assert v is None;
    def __call__(self, fn, v, s=set()):
        if DEBUG_ITER:
            print(f"d {self.N}")
        def _i(fn, v):
            for n in map(lambda i: dict.__getitem__(self,i), dict.__iter__(self)):    
                try:
                    if DEBUG_ITER:
                        print(f'd {self.N} -> {n.N}')
                    if n.N in s:
                        if DEBUG_ITER:
                            print(f"d $ {n.N}")
                        raise GraphIterException(0)
                    s.add(n.N)
                    r = []
                    i = fn(n,v,s)
                    list(map(r.append, i)) #lol
                except GraphIterException as e:
                    if DEBUG_ITER:
                        print(f"d ^ {n.N} {repr(e)}")
                    if e.value == 0:
                        continue
                    if e.value == 1:
                        if DEBUG_ITER:
                            print(F"d {n.N} <- {r}")
                        yield from r;
                        raise GraphIterException(1)
                if DEBUG_ITER:
                    print(F"d? {n.N} <- {r}")
                #yield from r
        return _i(fn, v);
g = {
    5  : { 6 : _ },
    6  : { 8: _ , 9 : _, 11 : _ },
    7  : { 8 : _, 9 : _, 10 : _ },
    8  : { },
    9  : { },
    10 : { 8 : _ },
    11 : { 5 : _, 7 : _ },
    12 : { 11 : _, 9 : _ },
}



def fn(n,v,s):
    t = v;
    yield n.N;
    if n.N == t:
        raise GraphIterException(1)
    if n.edges == 0:
        raise GraphIterException(0)
    r = [] #janky capture for concise use of the generator lmao
    try:
        list(map(r.append, n(fn, v, s))) #the list here is just `None, None ...` there's gotta be a better way
    except GraphIterException as e:
        print(f"f {n.N}: {repr(e)}")
        if e.value == 0:
            raise GraphIterException(0)
        elif e.value == 1:
            print(f"f {n.N} !! {r}")
            yield from r
            raise GraphIterException(1)
    

G = Graph(g)
n = dict.__getitem__(G, 12)
r = []
try:
    list(map(r.append, n(fn, 8)))
except Exception as e:
    print(repr(e))
    
print(r)
    

code.interact(local=locals())


