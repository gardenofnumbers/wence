import json

DEBUG_INTERP = True
DEBUG_PARSER = False
DEBUG_STACK  = False
class TerminationFound(Exception):
    pass
class witherParser(object):
    def __init__(self, src):
        self.states = {}
        self.ingest(src);
    def ingest(self, source):
        source = list(filter(None, source.split ("\n")))
        hdr = source[:2]
        source = source[2:]
        self.hdr = hdr
        print(f"Processing {len(source)} lines of wither")
        for line in source:
            self.ingestLine(line);
        
        
    def ingestLine(self, line):
        words = list(filter(None, line.split(" ")))
        print(f"Processing {len(words)} words of wither {words}")
        s = words[0]
        if s in self.states:
            raise RuntimeError(f"Redeclaration of state {s}!")
        if words[1] != ":=":
            raise RuntimeError("Syntax error (expected := after state name)")
        stateSeries = {0: [], "id":"Any"}#SparseList()
        self.recurse(words[2:], stateSeries)
        if 1 not in stateSeries:
            stateSeries = stateSeries[0]
        else:
            stateSeries = [stateSeries]
        self.states[s] = stateSeries
        
    def recurse(self, tape, series, terminate = "", idx=0):
        if DEBUG_PARSER:
            print(f"{chr(9)*idx}Recurse ({terminate}): {series} {tape}")
        if len(tape) == 0:
            if terminate != "":
                raise RuntimeError(f"Expected to reach {terminate} before EOL")
            return
        word = tape.pop(0)

        if word == terminate:
            raise TerminationFound

        if word.startswith('"'):
            series[idx].append({"id":"Match", 0: word.strip('"')})

        elif word == "?(":
            subseries = {0: [], "id":"Any"}#SparseList()         
            try:
                self.recurse(tape, subseries, terminate=")", idx=0)
            except TerminationFound:
                if not 1 in subseries:
                    subseries = subseries[0]
                else:
                    subseries = [subseries]
                series[idx].append({"id":"Optional", 0:  subseries})
            else:
                raise RuntimeError("This should be unreachable?? parsing ?( fail")

        elif word == "*{":
            subseries = {0: [], "id":"Any"}#SparseList()#{0: []}
            try:
                self.recurse(tape, subseries, terminate="}", idx=0)
            except TerminationFound:
                if not 1 in subseries:
                    subseries = subseries[0]
                else:
                    subseries = [subseries]
                series[idx].append({"id":"Repeat", 0: subseries})
            else:
                raise RuntimeError("This should be unreachable?? parsing *{ fail")
       
        elif word.isalnum():
            series[idx].append({"id":"Goto", 0:  word})
       
        elif word == "|":
            idx += 1;
            series[idx] = []
       
        else:
            raise RuntimeError(f"Unimplemented word {word}")
        self.recurse(tape, series, terminate=terminate, idx=idx)


class WitherStack(object):
    def __init__(self):
        self.s  = []
        self.b = []
    def new_frame(self):
        self.s.insert(0, self.b)
        self.b = []
        if DEBUG_STACK:
            print(f"@@@@ -> @@@ {json.dumps(self.s)}")
    def end_frame(self):
        if DEBUG_STACK:
            print(f"@@@@ <- @@@ {json.dumps(self.s)}")
            print(f"            {json.dumps(self.b)}")
        _ = self.b
        self.b = self.s.pop(0)
        return _
    def buffer(self, v):
        self.b.append(v)
        if DEBUG_STACK:
            print(f"@@@@    @@@ {json.dumps(self.b)}")
    def extend(self, v):
        self.b += v
        if DEBUG_STACK:
            print(f"@@@@ ## @@@ {json.dumps(self.b)}")


class WitherInterpreter(object):
    def __init__(self, machine, hdr):
        self.machine = machine
        self.stack   = WitherStack();
        self.tags    = json.loads(hdr[0])
        self.drop    = json.loads(hdr[1])
        
    def run(self, source):
        self.tape = source.replace(" ", "").replace("\n", "").replace("\t", "") 
        self.stack.new_frame();
        (v, l) = self.recurse("file", self.machine["file"], self.tape)
        if not v:
            print(f"Error while processing at {l}")
        out = {
            'id':"file"
        }
        for i,s in enumerate(self.stack.end_frame()):
            out[i] = s
        return out
         

    def recurse(self, i, sl, tape):
        for s in sl:
            match s["id"]:
                case "Match":
                    if tape.startswith(s[0]):
                        if DEBUG_INTERP:
                            print(f"____ Matched {s[0]} {i} {tape}")
                        tape = tape[len(s[0]):]
                        if not s[0] in self.drop:
                            self.stack.buffer({
                                'id':i, 0:s[0]
                            })

                    else:
                        return (False, tape)
                case "Optional":
                    
                    f = s[0]
                    (v, l) = self.recurse(i, f, tape)
                    if v:
                        tape = l
                case "Repeat":
                    self.stack.new_frame();
                    f = s[0]
                    (v, l) = (True, tape)
                    while v:
                        (v, l) = self.recurse(i, f, tape)
                        if(v):
                            tape = l
                        else:
                            tape = l
                            f = self.stack.end_frame()
                            self.stack.extend(f)
                        
                case "Goto":
                    if DEBUG_INTERP:
                        print(f")(}}{{)( call {i} -> {s[0]} {tape}")
                    self.stack.new_frame()
                    (v, l) = self.recurse(s[0], self.machine[s[0]], tape)
                    if not v:
                        self.stack.end_frame();
                        if DEBUG_INTERP:
                                print(f")(}}{{)( retn {s[0]} -> {i} {None}")     
                        return (False, tape)
                    else:
                        f = self.stack.end_frame()
                        if DEBUG_INTERP:
                                print(f")(}}{{)( retn {s[0]} -> {i} {json.dumps(f)}")

                        if s[0] in self.tags and tape != l:
                            box = lambda x: dict(zip(range(len(x)), x))                 
                            self.stack.buffer( { **{"id": s[0]}, **box(f)} )     #{"id": s[0], 0: f})
                        else:
                            self.stack.extend(f)
                    tape = l

                case "Any":
                    for v in [s[v] for v in s if type(v) is int]:
                        (v, l) = self.recurse(i, v, tape)
                        if v:
                            tape = l
                            break;
                    else:
                        return (False, tape)
        return (True, tape)
                    
                    

