# parser.py

A simple parser implemented in python based on the book: **A Practical Approach to Compiler Construction**.

For run the parser see 'run.sh' script.

The parser can construct a simple AST from files like this:

## Declarations
```c
int noargs(void) {
}

int manyargs() {
}

int pow2(int a) {
}

int add(int a, int b) {
}
```

## Expressions
```c
void main() {
}

//
void main() {
   int b = 0;

   int a = 0;

   a = a + 1;

   a = !a;

   a = a + (12 + b);

   b = b * 12;

   b = b * (a + 12 + 14);

   b = 12 && 0;

   a = 12 || 0;
}
```

## Statements
```c
void main() {
   int a = 0;
   int b = 1;

   if (a > 5) {
       print(15);
   }

   if (b > 7) {
      print(17);
   } else {
      print(-17);
   }

   if (x == 1) {
      return 1;
   } else if (y == 2) {
      return 2;
   } else if (z == 3) {
      return 3;
   } else  {
      return 3;
   }

   int c = 0;
   while (a == 2)
      printf(2);

   int i = 0;
   while (i < 10)  {
       if (mod(i, 2) == 0) {
           print(ispair);
       }
       i = i + 1;
   }
}
```

