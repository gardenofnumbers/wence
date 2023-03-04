#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

#include "structs.h"

void walk(const wence_node_t * node, int depth) {
    for(int i = 0; i < depth; i++){
        printf("\t");
    }
    printf("walk: %016llx %d\n", node, node->type);
    for(int i = 0; node->children[i] != NULL; i++   ) {
        walk(node->children[i], depth+1);
    }
}

void interpret() {
    
}

int main() {
    walk(ast_head, 0);
    walk(blocks, 0);
}