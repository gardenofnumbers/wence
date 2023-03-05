import json
from functools import wraps
DEBUG_WALKER = False

class WenceCodeGen():
    def __init__(self, ast):
        self.trace = ""
        self.ast = ast
        self.nid = 0
        self.types = set()
        self.output = ""

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
        
        #struct string
        #TODO XXX FIXME val stuff is so scuffed
        val = [node[x] for x in node if type(node[x]) != dict and type(x) == int]
        if len(val) > 1:
            raise Exception("Damnit, hoping we wouldn't hit this. too many values on node")
        val = val[0] if len(val) > 0 else "NULL";
        if type(val) == int or val == "NULL":
            val = f"""(uintptr_t){val}|~(-1ull >> 1)"""
        else:
            val = f"""(uintptr_t)\"{val}\""""
        
        res = f"""const wence_node_t node_{node['nid']} = {{{node['id']}, {val}, {{{"".join([f"&node_{c['nid']}," for (i,c) in children])} NULL}}}};\n"""
        self.output += (res)
    def generate(self):
        #process top level code
        self.walk(self.ast);
        #process blocks
        #blocks = self.ast['blocks']
        #for block in [blocks[x] for x in blocks if type(blocks[x]) == dict and type(x) == int]:
        #    print(block)
        #    self.walk(block)
        self.walk(self.ast['blocks'])
        self.output = f"""
typedef enum WENCE_NODE_TYPE {{
    {",".join(self.types)}
}} WENCE_NODE_TYPE_t;

typedef struct wence_node {{ 
    WENCE_NODE_TYPE_t type;
    uintptr_t value;
    const struct wence_node * children[];
}}wence_node_t;
""" + self.output + f"""
const wence_node_t *ast_head = &node_{self.ast['nid']};
const wence_node_t *blocks   = &node_{self.ast['blocks']['nid']};
""";

        print(self.output)
        
        
