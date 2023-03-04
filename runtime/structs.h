typedef enum WENCE_NODE_TYPE {
    BLOCK_STORE,equation,operator,BLOCK,INT,BLOCK_REF,file,flowpoint,NAME,statement,INVOKE,STRING
} WENCE_NODE_TYPE_t;

typedef struct wence_node {
    WENCE_NODE_TYPE_t type;
    uintptr_t value;
    const struct wence_node * children[];
}wence_node_t;
const wence_node_t node_2 = {BLOCK_REF, (uintptr_t)0, { NULL}};
const wence_node_t node_3 = {NAME, (uintptr_t)"c" , { NULL}};
const wence_node_t node_1 = {statement, (uintptr_t)NULL, {&node_2,&node_3, NULL}};
const wence_node_t node_5 = {BLOCK_REF, (uintptr_t)1, { NULL}};
const wence_node_t node_6 = {NAME, (uintptr_t)"main" , { NULL}};
const wence_node_t node_4 = {statement, (uintptr_t)NULL, {&node_5,&node_6, NULL}};
const wence_node_t node_9 = {NAME, (uintptr_t)"main" , { NULL}};
const wence_node_t node_8 = {INVOKE, (uintptr_t)NULL, {&node_9, NULL}};
const wence_node_t node_7 = {statement, (uintptr_t)NULL, {&node_8, NULL}};
const wence_node_t node_0 = {file, (uintptr_t)NULL, {&node_1,&node_4,&node_7, NULL}};
const wence_node_t node_13 = {NAME, (uintptr_t)"p" , { NULL}};
const wence_node_t node_14 = {NAME, (uintptr_t)"e" , { NULL}};
const wence_node_t node_12 = {statement, (uintptr_t)NULL, {&node_13,&node_14, NULL}};
const wence_node_t node_11 = {BLOCK, (uintptr_t)NULL, {&node_12, NULL}};
const wence_node_t node_17 = {STRING, (uintptr_t)"helloworld" , { NULL}};
const wence_node_t node_19 = {NAME, (uintptr_t)"out" , { NULL}};
const wence_node_t node_18 = {flowpoint, (uintptr_t)NULL, {&node_19, NULL}};
const wence_node_t node_16 = {statement, (uintptr_t)NULL, {&node_17,&node_18, NULL}};
const wence_node_t node_22 = {INT, (uintptr_t)2, { NULL}};
const wence_node_t node_23 = {operator, (uintptr_t)"*" , { NULL}};
const wence_node_t node_24 = {INT, (uintptr_t)3, { NULL}};
const wence_node_t node_21 = {equation, (uintptr_t)NULL, {&node_22,&node_23,&node_24, NULL}};
const wence_node_t node_26 = {NAME, (uintptr_t)"c" , { NULL}};
const wence_node_t node_25 = {INVOKE, (uintptr_t)NULL, {&node_26, NULL}};
const wence_node_t node_20 = {statement, (uintptr_t)NULL, {&node_21,&node_25, NULL}};
const wence_node_t node_15 = {BLOCK, (uintptr_t)NULL, {&node_16,&node_20, NULL}};
const wence_node_t node_10 = {BLOCK_STORE, (uintptr_t)NULL, {&node_11,&node_15, NULL}};

const wence_node_t *ast_head = &node_0;
const wence_node_t *blocks   = &node_10;