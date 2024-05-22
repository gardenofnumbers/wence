#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

#include "structs.h"

/*
    Initial design notes for runtime
    
    Going with an interpreter for now, although ultimately I want to convert things over to AoT compilation using threaded code
    Interpreter will receive "structs.h" from the wence compiler. This will be essentially a 1:1 translation of the wence AST (json tree) as C structs

    Interpretation occurs in a loop consisting of 3 phases:
        - Dequeue: retrieve an execution step (AST node) from the exec queue
            - pending forkpoints
            - pending flowpoints
            - 
        
        - Process: perform calculations based on the retrieved node
            - when / why does processing stop? one node at a time will be highly inefficient
            - 

        - Enqueue: place output from node onto queue
            - forkpoints
            - flowpoints

    Variable tracking
        - TODO
    Scope Management
        - TODO

    IO: 
        - v1: just read #{in} / write from #{out}
    
    
*/

void walk(const wence_node_t * node, int depth) {
    for(int i = 0; i < depth; i++){
        printf("\t");
    }
    printf("walk: %016llx %d\n", node, node->type);
    for(int i = 0; node->children[i] != NULL; i++   ) {
        walk(node->children[i], depth+1);
    }
}


struct 

void interpret() {
    
}

int main() {
    walk(ast_head, 0);
    walk(blocks, 0);
}