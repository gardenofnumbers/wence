import json
from functools import wraps
from collections import defaultdict 
from itertools import chain
from pprint import PrettyPrinter; pp = PrettyPrinter().pprint
import code; 
DEBUG_WALKER = False
DEBUG_DOT = False
DEBUG_FOLD = True

RENDER_CLUSTERS = True
"""
    First effort at dot based frontend. Transforms the dict tree into a node based cyclic digraph, and emits DOT.
"""

class WenceNode(object):
    def __init__(self, node):
        self.node = node;
        self.id = node['id']; 
        self.nid = node['nid'];
        if "value" in node:
            self.value = node['value'];
        else:
            self.value = None
        
        self.in_block = node['in_block'] if 'in_block' in node else None;
        
        if 0 in node:
            #recurse structural descendants
            traverse  = lambda node: [x for xs in ([traverse (node[x]) for x in node if type(node[x]) == dict and type(x) == int and x != 9090] if 0 in node else [[node['nid']]]) for x in xs]    
            self.subgraph = traverse (node)
            if DEBUG_FOLD:
                print(node['nid'], "\n", self.subgraph)
        else:
            self.subgraph = []

        self.data = [ node[x]['nid'] for x in node if type(node[x]) == dict and type(x) == int and x != 9090 ]
        self.flow = [ node[x]['nid'] for x in node if type(node[x]) == dict and type(x) == int and x == 9090 ]

        if DEBUG_DOT:
            print(f"{self.id} {self.nid} {self.data} -> {self.flow}")
       

    def emit(self, blockmap, flowmap, nodelist):
        label   = f"{self.id}\nnid={self.nid}"
        
        #default, debug values (to be removed or used elsewhere)
        if self.value is not None:
            label += f"\nvalue= '{self.value}'"
        match self.id:
            case "BLOCK":
                label += f"\nblock_id={self.node['block_id']}"

        if self.in_block is None:
            node = f'n{self.nid} [label="{label}"]\n'
        else:
            node = f'n{self.nid} [label="{label}" ]\n'

        edges = ""
        #build output edges
        for d in self.flow:
            edges += f'n{self.nid} -> n{d} [label=flow color=green]\n'
            self.subgraph.append(d)

        #build data edges - these can go away as compilation improves
        if len(self.data):
            for d in self.data:
                edges += f'n{self.nid} -> n{d} [color=grey]\n'
        #handle special edges;
        match self.id:
            case 'BLOCK_REF':
                edges += f"n{self.nid} -> n{blockmap[self.value]} [label=block color=purple]\n"         
                
                traverse  = lambda node: [x for xs in ([traverse (node[x]) for x in node if type(node[x]) == dict and type(x) == int] if 0 in node else [[node['nid']]]) for x in xs]    
                for n in nodelist:
                    if n.nid == blockmap[self.value]:
                        self.subgraph = traverse(n.node);
                        
                        
            case "FLOWPOINT":
                if "flow_to" in self.node:
                    edges += "\n".join([x for xs in [ [f'n{self.nid} -> n{v} [label="flow->{l}" color=red]' for v in f] for (l,f) in [ (l, flowmap[l]) for l in self.value ]] for x in xs])
                    
        return (self.nid, self.subgraph), node + edges
    
class WenceDotGen():

    def __init__(self, blocks):
        self.trace = ""
        self.blocks = blocks
        self.nid = 0
        self.types = set()
        self.output = ""
        self.blockmap = {} 
        self.flowmap  = defaultdict(lambda: set())

        self.node_list = []
        self.cur_block = None;

    def walk(self, node, depth = 0):
        #set node nid first
        node['nid'] = self.nid
        self.nid += 1

        #add our type to the list
        self.types.add(node['id'])

        #process blocks and flowpoints
        if self.cur_block is not None:
            node['in_block'] = self.cur_block;
        if node['id'] == "BLOCK":
            self.blockmap[node['block_id']] = node['nid']
            self.cur_block = node['block_id']
            if DEBUG_WALKER:
                print(f"processing block {self.cur_block}")
        if node['id'] == "FLOWPOINT":
            if DEBUG_WALKER:
                print("Lift flowpoint node")
                print(node)
            if 'flow_from' in node:
                for label in node['value']:
                    if DEBUG_WALKER:
                        print(f"add {label}->{node['nid']}")
                    self.flowmap[label].add(node['nid'])   
        #walk children
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int]
        if DEBUG_WALKER:
            print("\t"*depth + f"c: {node['id']} ({len(children)})")
            print("\t"*depth + json.dumps([c[1]['id'] for c in children]))
        self.trace += f" {node['id']}"
        for (idx, child) in children:
            self.walk(child, depth+1)

        self.node_list.append(WenceNode(node))
                
    def compile(self):
        for block in self.blocks:
            self.walk(block);
        if DEBUG_DOT:
            print(dict(self.flowmap))
        return self
    def emit(self):
        out = "digraph G {\n"
        subgraphs = {}
        for (nid, sg), v in [n.emit(self.blockmap, self.flowmap, self.node_list) for n in self.node_list]:
            if sg != []:
                subgraphs[nid] = sg;
            out += v;
        
        def transform(sgl, o={}):
            def fold(sgl):
                #warning: insane generator 
                def traverse(m):
                    assert type(m) == type([])
                    for i,v in enumerate(m):
                        assert (type(v) == type({}) or type(v) == type(0))
                        match v:
                            case dict():
                                j = list(v.keys())[0]
                                yield [j]
                                yield list(chain(*traverse(v[j])))
                            case int():
                                yield [v];
                ks = sorted(sgl.keys())[::-1]
                if len(ks) < 2:
                    return sgl
                m = sgl[ks[0]]
                z =  [x for xs in traverse(m) for x in xs]
                i = 1;
                while i < len(ks)-1:
                    t = sgl[ks[i]] 
                    if DEBUG_FOLD:
                        print(f"try {ks[0]}:{m}\n\tinto {ks[i]}:{t}")
                    if not any(_ in t for _ in z):
                        if ks[0] in t:
                            z = [ks[0]]
                            if DEBUG_FOLD:
                                print(f"\tyipi! fold   {ks[0]}:{m}\n\t\tinto {ks[i]}:{t}")  
                            break;
                        else:
                            if DEBUG_FOLD:
                                print(f"\tcan't fold {ks[0]}:{m}\n\tinto {ks[i]}:{t}")
                        i += 1
                    else:
                        if DEBUG_FOLD:
                            print(f"\tyipi! fold   {ks[0]}:{m}\n\t\tinto {ks[i]}:{t}")
                        break;
                        
                else:
                    return sgl
                sgl[ks[i]] = [_ for _ in t if _ not in z] + [{ ks[0] : m }] # 
                del sgl[ks[0]];
                return fold(sgl) 
            
            fold(sgl)
            ks = sorted(sgl.keys())[::-1] 
            o[ks[0]] = sgl[ks[0]] ; del sgl[ks[0]];
            
            return transform(sgl, o) if sgl != {} else o
        pp(subgraphs)
        sgl = transform(subgraphs)
        pp(sgl)
        
        #wow generators are kinda sexy ngl
        def emit_groups(sgl):    
            for gid,sg in [(gid,sgl[gid]) for gid in sgl]:
                if all(isinstance(_, int) for _ in sg):
                    yield f'subgraph cluster{gid} {{ label={gid} n{gid};{";".join(map(lambda n: f"n{n}", sg))} }}\n'
                else:
                    s = f'subgraph cluster{gid} {{ label={gid} n{gid}; {";".join([ f"n{_}" for _ in sg if isinstance(_, int) ])}\n'
                    z = list(chain(*[emit_groups(_) for _ in sg if not isinstance(_, int) ]))
                    yield s;
                    for _ in z:
                        yield _;
                    yield "}"
                    
        return out + "".join(list(emit_groups(sgl))) + "}"
            

        
    
        
        
