#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define MAXIDLEN 30

typedef enum {
  EofSym,
  NoneSym,
  ErrorSym,
  Keyword,
  Constant,
  IntConstant,
  FloatConstant,
  Identifier,
  Strliteral,
  Punctuator,
} TokenKind;

const char* TokenKindNames[] = {
  "EofSym",
  "NoneSym",
  "ErrorSym",
  "Keyword",
  "Constant",
  "IntConstant",
  "FloatConstant",
  "Identifier",
  "Strliteral",
  "Punctuator",
};

char identifier[MAXIDLEN + 1];
char ch;

typedef struct Token Token;

typedef struct Token {
  TokenKind kind;
  int ival;
  float fval;
  char *sval;
  char *token;
  Token *next;
} Token;

Token *tokens;

void panic(const char* msg) {
  perror(msg);
  exit(-1);
}

Token *new_token(TokenKind tkind) {
  Token *tk = calloc(1, sizeof(Token));
  if (tk == NULL) {
    panic("Can't create token.");
  }
  
  tk->kind = tkind;
  tk->next = NULL;
  return tk;
}

int white(int ch) {
  return ch == ' ' || ch == '\n';
}

Token *lex() {
  TokenKind lextoken = NoneSym;
  Token head = {};
  Token *cur = &head;

  ch = getchar();
  while (lextoken != EofSym && lextoken != ErrorSym) {
    int ival = 0;
    float fval = 0;
    char *sval = NULL;
    Token *tk;
   
    while (white(ch)) ch = getchar();
   
    switch (ch) {
        case ';': lextoken = Punctuator; sval = ";"; ch = getchar(); break;
        case ',': lextoken = Punctuator; sval = ","; ch = getchar(); break;
        case '+': lextoken = Punctuator; sval = "+"; ch = getchar(); break;
        case '-': lextoken = Punctuator; sval = "-"; ch = getchar(); break;
        case '/': lextoken = Punctuator; sval = "/"; ch = getchar(); break;
        case '*': lextoken = Punctuator; sval = "*"; ch = getchar(); break;
        case '(': lextoken = Punctuator; sval = "("; ch = getchar(); break;
        case ')': lextoken = Punctuator; sval = ")"; ch = getchar(); break;
        case '{': lextoken = Punctuator; sval = "{"; ch = getchar(); break;
        case '}': lextoken = Punctuator; sval = "}"; ch = getchar(); break;
        case '[': lextoken = Punctuator; sval = "["; ch = getchar(); break;
        case ']': lextoken = Punctuator; sval = "]"; ch = getchar(); break;

        case EOF: lextoken = EofSym; sval = "eof"; break;

        case '<': {
          ch = getchar();
          if (ch == '=') {
            lextoken = Punctuator;
            sval = "<=";
            ch = getchar();
          } else {
            lextoken = Punctuator;
            sval = "<";
          }
          break;
	      }

        case '>': {
          ch = getchar();
          if (ch == '=') {
            lextoken = Punctuator;
            sval = ">=";
            ch = getchar();
          } else {
            lextoken = Punctuator;
            sval = ">";
          }
          break;
	     }

        case '=': {
          ch = getchar();
          if (ch == '=') {
            lextoken = Punctuator;
            sval = "==";
            ch = getchar();
          } else {
            lextoken = Punctuator;
            sval = "=";
          }
          break;
      	}

        case '!': {
      	  ch = getchar();
          if (ch != '=') {
            fprintf(stderr, "***Error - expected = after ! (%c)\n", ch);
            lextoken = Punctuator;
          } else {
            lextoken = Punctuator;
            sval = "!=";
            ch = getchar();
          }
          break;
      	}

      	case '0': case '1': case '2': case '3': case '4': case '5':
      	case '6': case '7': case '8': case '9': 
        {
          int i = 0;
          int isreal = 0;
          while (isdigit(ch)) {
            if (i < MAXIDLEN) identifier[i++] = ch;
            ch = getchar();
          }

          if (ch == '.') {
            isreal = 1;
            if (i < MAXIDLEN) identifier[i++] = ch;
            ch = getchar();
            while (isdigit(ch)) {
              if (i < MAXIDLEN) identifier[i++] = ch;
              ch = getchar();
            }
          }

          identifier[i] = '\0';
          if (isreal) {
            lextoken = FloatConstant;
            fval = strtof(identifier, NULL);
            sval = strdup(identifier);
          } else {
            lextoken = IntConstant;
            ival = strtod(identifier, NULL);
            sval = strdup(identifier);
          }
          break;
        }

        case 'a': case 'b': case 'c': case 'd': case 'e': case 'f':
        case 'g': case 'h': case 'i': case 'j': case 'k': case 'l':
        case 'm': case 'n': case 'o': case 'p': case 'q': case 'r':
        case 's': case 't': case 'u': case 'v': case 'w': case 'x':
        case 'y': case 'z': {
          int i = 0;
          while (islower(ch) || isdigit(ch)) {
            if (i < MAXIDLEN) identifier[i++] = ch;
              ch = getchar();
          }
          identifier[i] = '\0';
          sval = strdup(identifier); // XXX too many alloc
          if (strcmp(identifier, "else") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "if") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "float") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "int") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "print") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "read") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "return") == 0) lextoken = Keyword;
          else if (strcmp(identifier, "while") == 0) lextoken = Keyword;
          else {
            lextoken = Keyword;
          }
          break;
        }
        default:
          fprintf(stderr, "***Unexpected character '%c'\n", ch);
          lextoken = ErrorSym;
          sval = "error";
        break;
    }

    cur = cur->next = new_token(lextoken);
    cur->ival = ival;
    cur->fval = fval;
    cur->sval = sval;
  }

  return head.next;
}

int is_eqsym(Token *tok, TokenKind kind) {
  return tok->kind == kind;
}

void printtk(Token *tk) {
  switch (tk->kind) {
    case Punctuator:
      printf("Punctuator (%d), %s\n", Punctuator, tk->sval);
      break;
    case IntConstant:
      printf("IntConstant (%d), %s\n", IntConstant, tk->sval);
      break;
    case FloatConstant:
      printf("FloatConstant (%d), %s\n", FloatConstant, tk->sval);
      break;
    default:
      printf("Unknown token kind, %d\n", tk->kind);
      break;
  }
}

/// parser section
///
typedef enum {
  NkPrg, // Program
  NkAdd,
  NkSub,
  NkMul,
  NkDiv,
  NkNeg,
  NkExpr,
  NkInt,
} NodeKind;

const char* NodeKindNames[] = {
  "NkPrg", 
  "NkAdd",
  "NkSub",
  "NkMul",
  "NkDiv",
  "NkNeg",
  "NkExpr",
  "NkInt",
};

// Node
typedef struct Node Node;
struct Node {
  NodeKind kind;
  Token *token;
  Node *lhs;
  Node *rhs;

  int nval;
  float fval;
  char *str;
};

void print_spaces(int n) {
  for(int i=0; i < n; i++) {
    printf(" ");
  }
}

void print_nodes(Node *node, int indent) {
  //print_spaces(indent * 3);
  printf("%s (%d)\n", NodeKindNames[node->kind], node->nval);

  if (node->lhs) {
    print_spaces(indent * 5);
    printf("lhs: ");
    print_nodes(node->lhs, indent + 1);
  }
  
  if (node->rhs) {
    print_spaces(indent * 5);
    printf("rhs: ");
    print_nodes(node->rhs, indent + 1);
  }
}

Node *new_node(NodeKind kind, Token *token) {
  Node *node = calloc(1, sizeof(Node));
  node->kind = kind;
  node->token = token;

  return node;
}

Node *new_unary(NodeKind kind, Token *token, Node *lhs) {
  Node *node = calloc(1, sizeof(Node));
  node->kind = kind;
  node->token = token;
  node->lhs = lhs;

  return node;
}

Node *new_binary(NodeKind kind, Token *token, Node *lhs, Node *rhs) {
  Node *node = calloc(1, sizeof(Node));
  node->kind = kind;
  node->token = token;
  node->lhs = lhs;
  node->rhs = rhs;

  return node;
}

// Parser 
typedef struct {
  Token *token;
} Parser;

Parser *new_parser(Token *tokens) {
  Parser *parser = calloc(1, sizeof(Parser));
  parser->token = tokens;

  return parser;
}

Token *next(Parser *st) {
  st->token = st->token->next;
}

Token *skip(Parser *st, char* chk) {
  if (chk[0] != st->token->sval[0]) {
    printf("error: invalid token %s, %s was expected\n", 
        st->token->sval, chk);
    exit(-1);
  }

  next(st);
}

Node *expression(Parser *st);

int equal(Token *tok, char *s) {
  return strcmp(tok->sval, s) == 0;
}

void syntrace(const char *str) {
  printf("%s\n", str);
}

// constant:
//    int
Node *constant(Parser *st) {
  syntrace("<constant>");
  printtk(st->token);

  Node *nconstant = new_node(NkInt, st->token);
  nconstant->nval = st->token->ival;

  next(st);
  return nconstant;
}

// primary:
//     ( expression )
//     constant
Node *primary(Parser *st) {
  syntrace("<primary>");
  
  Node *node;
  if (equal(st->token, "(")) {
    skip(st, "(");
    expression(st); // XXX
    skip(st, ")");
  } else {
    node = constant(st);
  }

  syntrace("</primary>");
  return node;
}

// unary: 
//    + unary
//    - unary (not implemented)
//    primary
Node* unary(Parser *st) {
  syntrace("<unary>");

  Node *node = NULL;

  if (equal(st->token, "+")) {
    //next(st);
    //node = unary(st);
    printf("error not implemented - unary");
    exit(-1);
  } else if (equal(st->token, "-")) {
    // XXX implementar
    printf("error not implemented - unary");
    exit(-1);
  } else {
    node = primary(st);
  }

  syntrace("</unary>");
  return node;
}

// multiply: 
//    unary
//    multiply * unary
//    multiply / unary 
Node *mul(Parser *st) {
  syntrace("<mul>");

  Node *node = unary(st);

  for (;;) {
    if (equal(st->token, "*")) {
      syntrace("<*>");
      next(st);
      Node *rhs = unary(st);
      node = new_binary(NkMul, st->token, node, rhs);
      syntrace("</*>");
    } else if (equal(st->token, "/")) {
      next(st);
      Node *rhs = unary(st);
      node = new_binary(NkDiv, st->token, node, rhs);
    } else {
      break;
    }
  }

  syntrace("</mul>");
  return node;
}

// additive: 
//    multiply
//    additive + multiply
//    additive - multiply
Node *add(Parser *st) {
  syntrace("<add>");

  Node* node = mul(st);
  for (;;) {
    if (equal(st->token, "+")) {
      syntrace("<+>");
      next(st);
      Node *rhs = mul(st);
      node = new_binary(NkAdd, st->token, node, rhs);
      syntrace("</+>");
    } else if (equal(st->token, "-")) {
      syntrace("<->");
      next(st);
      Node *rhs = mul(st);
      node = new_binary(NkSub, st->token, node, rhs);
      syntrace("</->");
    } else {
      break;
    }
  }

  syntrace("</add>");
  return node;
}

// expression: 
//    adding unary
Node *expression(Parser *st) {
  syntrace("<expression>");

  Node *nadd = add(st);
  Node *nexpr = new_unary(NkExpr, st->token, nadd);

  syntrace("</expression>");
  return nexpr;
}

/// main

int main(int argc, char *argv[]) {
  // tokenize
  Token *tokens = lex();

  for(Token *tk = tokens; tk->next; tk = tk->next) {
    //printf("token: %d '%s', %d, %f\n", tk->kind, tk->sval, tk->ival, tk->fval);
    printtk(tk);
  }

  // parse
  Parser *parser = new_parser(tokens);

  Node *prg = expression(parser);
  print_nodes(prg, 0);
}

// vi: tabstop=2 shiftwidth=2 expandtab
