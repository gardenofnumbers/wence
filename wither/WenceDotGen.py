import json
from functools import wraps
DEBUG_WALKER = False
DEBUG_DOT = False
"""
    First effort at dot based frontend. Transforms the dict tree into a node based cyclic digraph, and emits DOT.
"""

class WenceNode(object):
    def __init__(self, node):
        self.id = node['id']; 
        self.nid = node['nid'];
        if "value" in node:
            self.value = node['value'];
        else:
            self.value = None

        self.data = [ node[x]['nid'] for x in node if type(node[x]) == dict and type(x) == int and x != 69]
        self.flow = [ node[x]['nid'] for x in node if type(node[x]) == dict and type(x) == int and x == 69]
        if DEBUG_DOT:
            print(f"{self.id} {self.nid} {self.data} -> {self.flow}")
       

    def emit(self, blockmap):
        label   = f"id={self.id}\nnid={self.nid}"
        if self.value is not None:
            label += f"\nvalue= '{self.value}'"

        node = f'n{self.nid} [label="{label}"]\n'
        

        #build value pairs for node:
        edges = ""
        #build output edges
        for d in self.flow:
            edges += f'n{self.nid} -> n{d} [label=flow]\n'
        #build data edges
        for d in self.data:
            edges += f'n{self.nid} -> n{d} [label=data]\n'
        
        #handle block flow:
        if self.id == 'BLOCK_REF':
            edges += f"n{self.nid} -> n{blockmap[self.value]} [label=block]"

        return node + edges
    
class WenceDotGen():

    def __init__(self, blocks):
        self.trace = ""
        self.blocks = blocks
        self.nid = 0
        self.types = set()
        self.output = ""
        self.blockmap = {} 
        self.node_list = []


    def walk(self, node, depth = 0):
        #set node nid first
        node['nid'] = self.nid
        self.nid += 1

        #add our type to the list
        self.types.add(node['id'])

        #walk children
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int]
        if DEBUG_WALKER:
            print("\t"*depth + f"c: {node['id']} ({len(children)})")
            print("\t"*depth + json.dumps([c[1]['id'] for c in children]))
        self.trace += f" {node['id']}"
        for (idx, child) in children:
            self.walk(child, depth+1)

        self.node_list.append(WenceNode(node))
        
        """
            Todo: Maybe refactor so that this block_id -> node id transformation doesn't need to happen. 
                  Worried about confusion down the line with this sort of opaque juggling
        """
        if node['id'] == "BLOCK":
            self.blockmap[node['block_id']] = node['nid']
        if node['id'] == "BLOCK_REF":
            pass #should BLOCK_REF:value should point at `block_id`, we build a translation map rather than manipulating here.

    def generate(self):
        for block in self.blocks:
            self.walk(block);
        z = "\n"
        return f"""digraph G {{
            {z.join([n.emit(self.blockmap) for n in self.node_list])}
        }}
        """
    
        
        
