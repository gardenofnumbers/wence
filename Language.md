```
'hello world' -> #{stdout};
```
### Hello World

Wence is an experimental dataflow oriented programming language currently in the early prototyping stage, developed as a toy and learning project by numbers. Wence is syntactically flexible by design, often allowing multiple equivilent expressions of the same semantics, and also allowing for certain semantically useless constructions. This design decision is intended to enable a motivated programmer to elegantly express complex programs, while simplifying the parser and compiler.

This document is intended to provide both a first-look onboarding to the syntax and semantics of Wence, as well as to provide a snapshot of design principles for the language. For additional details about language implementation, and for information on wence's grammar DSL ("Wither"), see other docs (pending).  

Programs in wence are defined by the flow of data between nodes, primarily by using the continuation operator "->". A special node type, a "flowpoint", is provided to allow for IO and nonlocal dataflow. Statements are composed by a series of nodes joined by the continuation operator, and organized into blocks. Wence does not have a strictly familiar analogue to "functions" in a traditional language. Blocks provide much of the functionality expected from traditional functions, such as encapsulation of scope ("local variables", "closures") and input/output abstraction ("arguments", "return values").  

### Starter Example (Euclid GCD)

For a simple example of a program in Wence, let us examine an implementation of Euclid's GCD algorithm, which can be expressed in recursive, controlflow driven code as:  

```
function gcd(a, b)
    if b = 0
        return a
    else
        return gcd(b, a mod b)
```
(source: wikipedia)

In wence, Euclid's algorithm can be implemented as:
```
#{a, b} -> ?{
        (b==0) : { a -> #{stdout} },
        (1)    : { @{b, (a%b)} -> #{a, b} }
};
@{2740, 5984} -> #{a, b};
```

Let's break this down node by node:

```
#{a, b}
```
This is a flowpoint. Flowpoints take the form: `#{label, ...}` 
Downstream nodes from a flowpoint will be executed once all labels within the flowpoint have received data.
Labels within a flowpoint are "in scope" for all dependant nodes, allowing their values to be accessed directly.

In this example, all subsequent code depends on this flowpoint, so it will not execute until data becomes available on both `a` and `b`.

```
?{
```
This is a filter. Filters take the form:
```
?{
    (condition) : { block },
    (condition) : { block }
}
```
Conditions can utilize any in-scope values. Conditions are evaluated sequentially, halting at the first true condition, and executing it's associated block. These blocks inherit scope from the filter's parent, and also receive any continuation input from the filter itself. Output from the selected block is then provided to any continuation children of the filter. (note: continuation inputs and outputs for blocks described later. this example does not utilize this feature)

```
(b==0) : { a -> #{stdout} },
```
The first condition is simple. If the `b` received from the flowpoint is 0, write `a` to stdout.

```
(1)    : { @{b, (a%b)} -> #{a, b} }
```
The second condition is always evaluated if the first condition is false. 

```
{ @{b, (a%b)} -> #{a, b} }
```
`@{}` is a glom node. A glom node takes the form `@{expression, ...}`, and provides a mechanism for bundling values for the continuation operator. 
E.g. `@{foo, bar} -> #{bizz, buzz}` could also be written as:
```
foo -> #{bizz};
bar -> #{buzz};
```
However, code written in this way quickly becomes unwieldy due to dependancy duplication. 

In this example, `b` is written to `a` and a new value for `b` is computed and written to `b`. Note that this forms a "loop" with the statement utilizing the same flowpoint for both input and output.


```
@{2740, 5984} -> #{a, b};
```
This statement provides static input to `a` and `b` in order to provide starting conditions for execution. A more 'useful' program might retrieve these values from stdin.

### A more detailed study of blocks
Blocks are near equal in importance to the continuation operator in providing expressivity to wence.

### A more detailed study of the continuation operator and value
The continuation operator `->` can be thought of as saying "take the continuation value output from the node on the left, and provide it as input to the node on the right." The continuation value is an abstract object which contains both a runtime snapshot of the current scope (analoguous to a closure) and an ordered array of values (explicit output from the source node). Often, the explicit array can be ignored, in which case the continuation operator primarily defines execution order and dependencies for nodes.

The continuation value can be directly accessed using the special node `%`. This is primarily meaningful in the way it interacts with blocks.



