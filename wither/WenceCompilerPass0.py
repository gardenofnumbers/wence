import json
from functools import wraps

DEBUG_STRING = True
DEBUG_NAME   = True
DEBUG_INTEGER = True

def _called(f):
    @wraps(f)
    def _impl(self, *method_args, **method_kwargs):
        self.do_more = True
        method_output = f(self, *method_args, **method_kwargs)
        method_args[0]['p0'] = True
        return method_output
    return _impl

class WenceCompilerPass0(object):
    @_called
    def P0_String(self, node, parent, idx):
        if DEBUG_STRING:
            print(f"Visit string: {json.dumps(node)}")
        children = [node[x] for x in node if type(node[x]) == dict]
        s = "";
        for child in children:       
            if child['id'] != 'printable':
                raise RuntimeError(f"TREE ERROR! expect printable, got {child['id']}")
            s += child[0]
        node.clear()
        node['id'] = 'STRING'
        node['value'] = s
        return False 
    @_called  
    def P0_Name(self, node, parent, idx):
        if DEBUG_NAME:
            print(f"Visit name: {json.dumps(node)}")
        children = [node[x] for x in node if type(node[x]) == dict]
        s = "";
        for child in children:       
            if child['id'] != 'letter' and child['id'] != 'digit':
                raise RuntimeError(f"TREE ERROR! expect letter/digit, got {child['id']}")
            s += child[0]
        node.clear()
        node['id'] = 'NAME'
        node['value'] = s
        return False
    @_called
    def P0_Integer(self, node, parent, idx):
        if DEBUG_INTEGER:
            print(f"Visit integer: {json.dumps(node)}")
        
        match node[0]['id']:
            case 'base10':
                mode = 10
            case 'base16':
                mode = 16
            case default:
                raise RuntimeError(f"TREE ERROR!! expect integer type, got {node[0]['id']}")
            
        children = [node[0][x] for x in node[0] if type(node[0][x]) == dict]
        s = "";
        for child in children:       
            if child['id'] != 'hex' and child['id'] != 'digit':
                raise RuntimeError(f"TREE ERROR! expect hex/digit, got {child['id']}")
            s += child[0]
        node.clear()
        node['id'] = f'INT'
        node['value'] = int(s, base=mode)
        return False
    @_called
    def P0_Block(self,node, parent, idx):
        node['eid'] = self.eid
        node['id'] = 'BLOCK'
        self.ast["blocks"][self.eid] = node
        parent[idx] = {
            "id": "BLOCK_REF",
            'value': self.eid
        }
        self.eid += 1;
        return True
    

    @_called
    def P0_Invoke(self, node, parent, idx):
        node[0] = parent[idx+1]
        del parent[idx+1]
        node['id'] = "INVOKE"
        return True
    
    def __init__(self, ast, walker):
        self.handlers = {
            "string" : self.P0_String,
            "name": self.P0_Name,
            "integer" : self.P0_Integer,
            "block": self.P0_Block,  
            "invoke":self.P0_Invoke,
        }
        self.ast = ast
        self.eid = 0
        self.do_more = False
        self.walker = walker
        self.ast["blocks"] = {'id': "BLOCK_STORE"}
        self.ast["flowps"] = {'id': "FLOWP_STORE"}
        self.ast["forkps"] = {'id': "FORKP_STORE"}

    def compile(self):
        while True:
            self.do_more = False
            self.walker.walk(self.ast, self.handlers)
            if not self.do_more:
                break
        