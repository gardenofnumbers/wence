typedef enum WENCE_NODE_TYPE {
    BLOCK_STORE,BLOCK_REF,BLOCK,file,statement,NAME,flowpoint,INVOKE,STRING
} WENCE_NODE_TYPE_t;

typedef struct wence_node {
    WENCE_NODE_TYPE_t type;
    uintptr_t value;
    const struct wence_node * children[];
}wence_node_t;
const wence_node_t node_2 = {BLOCK_REF, (uintptr_t)0, { NULL}};
const wence_node_t node_3 = {NAME, (uintptr_t)"main"|~(-1ull >> 1), { NULL}};
const wence_node_t node_1 = {statement, (uintptr_t)NULL, {&node_2,&node_3, NULL}};
const wence_node_t node_6 = {NAME, (uintptr_t)"main"|~(-1ull >> 1), { NULL}};
const wence_node_t node_5 = {INVOKE, (uintptr_t)NULL, {&node_6, NULL}};
const wence_node_t node_4 = {statement, (uintptr_t)NULL, {&node_5, NULL}};
const wence_node_t node_0 = {file, (uintptr_t)NULL, {&node_1,&node_4, NULL}};
const wence_node_t node_10 = {STRING, (uintptr_t)"helloworld"|~(-1ull >> 1), { NULL}};
const wence_node_t node_12 = {NAME, (uintptr_t)"out"|~(-1ull >> 1), { NULL}};
const wence_node_t node_11 = {flowpoint, (uintptr_t)NULL, {&node_12, NULL}};
const wence_node_t node_9 = {statement, (uintptr_t)NULL, {&node_10,&node_11, NULL}};
const wence_node_t node_8 = {BLOCK, (uintptr_t)NULL, {&node_9, NULL}};
const wence_node_t node_7 = {BLOCK_STORE, (uintptr_t)NULL, {&node_8, NULL}};

const wence_node_t *ast_head = &node_0;
const wence_node_t *blocks   = &node_7;
