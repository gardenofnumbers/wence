class TerminationFound(Exception):
    pass
class witherParser(object):
    def __init__(self):
        self.states = {}
        
    def ingest(self, source):
        source = list(filter(None, source.split ("\n")))
        print(f"Processing {len(source)} lines of wither")
        for line in source:
            self.ingestLine(line);
        return self.states
        
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
