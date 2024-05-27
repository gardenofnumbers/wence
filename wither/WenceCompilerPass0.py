import json
from functools import wraps
class SparseList(list):
  def __setitem__(self, index, value):
    missing = index - len(self) + 1
    if missing > 0:
      self.extend([None] * missing)
    list.__setitem__(self, index, value)
  def __getitem__(self, index):
    try: return list.__getitem__(self, index)
    except IndexError: return None

DEBUG_STRING = False
DEBUG_NAME   = False
DEBUG_INTEGER = False

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
        node['block_id'] = self.block_id
        node['id'] = 'BLOCK'
        self.blocks[self.block_id] = node
        parent[idx] = {
            "id": "BLOCK_REF",
            'value': self.block_id
        }
        self.block_id += 1;
        return True
    

    @_called
    def P0_Invoke(self, node, parent, idx):
        node[0] = parent[idx+1]
        del parent[idx+1]
        node['id'] = "INVOKE"
        return True
    
    @_called
    def P0_Operator(self, node, parent, idx):
        node['value'] = node[0]
        node[0] = None;
        node['id'] = "OPERATOR"
        return True
    
    def __init__(self, ast, walker):
        self.handlers = {
            "string" : self.P0_String,
            "name": self.P0_Name,
            "integer" : self.P0_Integer,
            "block": self.P0_Block,  
            "invoke":self.P0_Invoke,
            "operator":self.P0_Operator,

        }
        self.ast = ast
        self.block_id = 0
        self.do_more = False
        self.walker = walker
        self.blocks = SparseList([]) #{'id': "BLOCK_STORE"}
        
    def compile(self):
        while True:
            self.do_more = False
            self.walker.walk(self.ast, self.handlers)
            if not self.do_more:
                break
        
        return self.blocks
        