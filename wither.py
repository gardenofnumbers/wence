src = """letter      := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
hex         := "a" | "b" | "c" | "d" | "e" | "f"
digit       := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
operator    := "/" | "*" | "+" | "-" | "%" | "&" | "|" | "^" | "~" | "!" | "=" | ">" | "<" | "<<" | ">>" | "<=" | ">=" | "!=" | "=="
this        := "%"
sysc        := "^"
string      := "'" ?( *{ ! "'" } ) "'"
integer     := "0x" *{ digit | hex } | digit ?( *{ digit } )
array       := "[" *{ expression ?( "," ) } "]"
constant    := integer | string | array
label       := letter ?( *{ letter | digit } ) 
subscript   := "[" expression "]
equation    := "(" expression ?( operator expression ) ")"
statement   := expression ?( *{ "->" expression } )
block       := "{" ?( unglom ) *{ statement ?( ";" ) } "}"
dict        := "${" *{ expression ":" expression ?(",") } "}"
filter      := "?{" *{ expression ":" expression ?(",") } "}"
glom        := "@{" *{ statement ?(",") } "}"
unglom      := "#{" *{ label ?( "," ) } "}"
expression2 := block | filter | dict | glom | equation | label | constant | this | sysc
expression  := ?( "~" ) expression2 ?( *{ subscript } ) """
class TerminationFound(Exception):
    pass

class ParseTree(object):
    pass

class ParseTreeNode(object):
    pass

class WhitherEngine(object):
    def __init__(self):
        self.tree = ParseTree()
        self.currentState = "block"
    def Characters(self, chars):
        def _matchCharacters(tape):
            if tape.startswith(chars):
                return tape[len(chars):]
            else:
                #what do?
                print(chars)
                print(tape)
                raise RuntimeError("Crap")
            
        return _matchCharacters
    def Optional(self, subseries):
        def _matchOptional(tape):
            return tape
        return _matchOptional
    def Repeat(self, subseries):
        def _matchRepeat(tape):
            return self.runState(subseries, tape)
        return _matchRepeat
    def Goto(self, state):
        def _matchGoto(tape):
            print(f"{self.currentState} TO {state}")
            self.currentState = state
            return self.runState(self.states[state], tape)
        return _matchGoto

        
    def recurse(self, tape, series, terminate = ""):
        if len(tape) == 0:
            if terminate != "":
                raise RuntimeError(f"Expected to reach {terminate} before EOL")
            return
        word = tape.pop(0)
        if word == terminate:
            raise TerminationFound
        
        if word.startswith('"'):
            series.append(self.Characters(word.strip('"')))
        elif word == "?(":
            subseries = []
            try:
                self.recurse(tape, subseries, terminate=")")
            except TerminationFound:
                series.append(self.Optional(subseries))
            else:
                raise RuntimeError("This should be unreachable?? parsing ?( fail")
        elif word == "*{":
            subseries = []
            try:
                self.recurse(tape, subseries, terminate="}")
            except TerminationFound:
                series.append(self.Repeat(subseries))
            else:
                raise RuntimeError("This should be unreachable?? parsing *{ fail")
        elif word.isalnum:
            series.append(self.Goto(word))
        else:
            raise RuntimeError(f"Unimplemented word {word}")
        self.recurse(tape, series, terminate)

    def runState(self, state, tape):
        print(state)
        for s in state:
            tape = s(tape);
            print(s)
            print(tape)
        return tape


class WhitherParser(object):
    def __init__(self):
        self.engine = WhitherEngine()
        self.states = {}
    def ingest(self, source):
        source = list(filter(None, source.split ("\n")))
        print(f"Processing {len(source)} lines of whither")
        for line in source:
            self.ingestLine(line);
        self.engine.states = self.states

    def ingestLine(self, line):
        words = list(filter(None, line.split(" ")))
        print(f"Processing {len(words)} words of whither")
        s = words[0]
        if s in self.states:
            raise RuntimeError(f"Redeclaration of state {s}!")
        if words[1] != ":=":
            raise RuntimeError("Syntax error (expected := after state name)")

        stateSeries = []
        self.engine.recurse(words[2:], stateSeries)
        self.states[s] = stateSeries
        
        
    def execute(self, src):
        self.engine.runState(self.states["block"], "{" + src +  "}")

    


        



p = WhitherParser();
p.ingest(src);

p.execute('{ "hello world" -> (a * 2) -> ~b -> {c,d} -> |; } -> main; ~main;')