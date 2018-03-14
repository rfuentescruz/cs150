#include <ctype.h>
#include <stdio.h>
#include <string.h>

/* Global declarations */
/* Variables */
int charClass;
int prevClass;
char lexeme[100];
char nextChar;
int lexLen;
int token;
int nextToken;
FILE *in_fp, *fopen();

void addChar();
void getChar();
void ungetChar();
void getNonBlank();
int lex();

/* Character classes */
#define LETTER 0
#define DIGIT 1
#define UNKNOWN 99

/* Token codes */
#define INT_LIT 10
#define IDENT 11
#define _TRUE 12
#define _FALSE 13
#define _NONE 14

#define ASSIGN_OP 20
#define ADD_OP 21
#define SUB_OP 22
#define MULT_OP 23
#define DIV_OP 24
#define LEFT_PAREN 25
#define RIGHT_PAREN 26
#define MATMUL_OP 27
#define MOD_OP 28
#define FDIV_OP 29
#define EXP_OP 30

#define LT_OP 40
#define LTEQ_OP 41
#define GT_OP 42
#define GTEQ_OP 43
#define EQ_OP 44
#define NEQ_OP 45

#define OR_OP 50
#define AND_OP 51
#define NOT_OP 52

#define BOR_OP 60
#define BAND_OP 61
#define BXOR_OP 62
#define BNOT_OP 63
#define BLSHIFT_OP 64
#define BRSHIFT_OP 65

#define UNRECOGNIZED -2

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s inputfile\n", argv[0]);
    }

    if ((in_fp = fopen(argv[1], "r")) == NULL) {
        printf("ERROR - cannot open front.in \n");
    } else {
        getChar();
        do {
            lex();
            if (nextToken == UNRECOGNIZED) {
                printf("LEXICAL ERROR: Unrecognized symbol: %s\n", lexeme);
            }
        } while (nextToken != EOF);
    }
}


/*****************************************************/
/* lookup - a function to lookup operators and parentheses
and return the token */
int lookup(char ch) {
    switch (ch) {
        case '(':
            addChar();
            nextToken = LEFT_PAREN;
            break;
        case ')':
            addChar();
            nextToken = RIGHT_PAREN;
            break;
        case '+':
            addChar();
            nextToken = ADD_OP;
            break;
        case '-':
            addChar();
            nextToken = SUB_OP;
            break;
        case '*':
            addChar();
            nextToken = MULT_OP;

            getChar();
            if (nextChar == '*') {
                addChar();
                nextToken = EXP_OP;
            } else {
                ungetChar();
            }
            break;
        case '/':
            addChar();
            nextToken = DIV_OP;

            getChar();
            if (nextChar == '/') {
                addChar();
                nextToken = FDIV_OP;
            } else {
                ungetChar();
            }
            break;
        case '@':
            addChar();
            nextToken = MATMUL_OP;
            break;
        case '%':
            addChar();
            nextToken = MOD_OP;
            break;
        case '<':
            addChar();
            nextToken = LT_OP;

            getChar();
            if (nextChar == '=') {
                addChar();
                nextToken = LTEQ_OP;
            } else if (nextChar == '<') {
                addChar();
                nextToken = BLSHIFT_OP;
            } else {
                ungetChar();
            }
            break;
        case '>':
            addChar();
            nextToken = GT_OP;

            getChar();
            if (nextChar == '=') {
                addChar();
                nextToken = GTEQ_OP;
            } else if (nextChar == '>') {
                addChar();
                nextToken = BRSHIFT_OP;
            } else {
                ungetChar();
            }
            break;
        case '=':
            addChar();
            getChar();
            if (nextChar == '=') {
                addChar();
                nextToken = EQ_OP;
            } else {
                ungetChar();
                nextToken = UNRECOGNIZED;
            }
            break;
        case '!':
            addChar();
            getChar();
            if (nextChar == '=') {
                addChar();
                nextToken = NEQ_OP;
            } else {
                ungetChar();
                nextToken = UNRECOGNIZED;
            }
            break;
        case '|':
            addChar();
            nextToken = BOR_OP;
            break;
        case '&':
            addChar();
            nextToken = BAND_OP;
            break;
        case '^':
            addChar();
            nextToken = BXOR_OP;
            break;
        case '~':
            addChar();
            nextToken = BNOT_OP;
            break;
        default:
            addChar();
            nextToken = UNRECOGNIZED;
            break;
    }
    return nextToken;
}

/*****************************************************/
/* addChar - a function to add nextChar to lexeme */
void addChar() {
    if (lexLen <= 98) {
        lexeme[lexLen++] = nextChar;
        lexeme[lexLen] = 0;
    } else {
        printf("Error - lexeme is too long \n");
    }
}

/*****************************************************/
/* getChar - a function to get the next character of
input and determine its character class */
void getChar() {
    if ((nextChar = getc(in_fp)) != EOF) {
        if (isalpha(nextChar)) {
            charClass = LETTER;
        } else if (isdigit(nextChar)) {
            charClass = DIGIT;
        } else {
            charClass = UNKNOWN;
        }
    } else {
        charClass = EOF;
    }
    prevClass = charClass;
}

/*****************************************************/
/* ungetChar - a function to push the most recent character fetched by getChar
back to the input stream */
void ungetChar() {
    ungetc(nextChar, in_fp);
    charClass = prevClass;
}

/*****************************************************/
/* getNonBlank - a function to call getChar until it
returns a non-whitespace character */
void getNonBlank() {
    while (isspace(nextChar)) {
        getChar();
    }
}

/*****************************************************/
/* lex - a simple lexical analyzer for arithmetic expressions */
int lex() {
    lexLen = 0;
    getNonBlank();
    switch (charClass) {
        /* Parse identifiers */
        case LETTER:
            addChar();
            getChar();
            while (charClass == LETTER || charClass == DIGIT) {
                addChar();
                getChar();
            }

            if (strcmp(lexeme, "True") == 0) {
                nextToken = _TRUE;
            } else if (strcmp(lexeme, "False") == 0) {
                nextToken = _FALSE;
            } else if (strcmp(lexeme, "None") == 0) {
                nextToken = _NONE;
            } else if (strcmp(lexeme, "or") == 0) {
                nextToken = OR_OP;
            } else if (strcmp(lexeme, "and") == 0) {
                nextToken = AND_OP;
            } else if (strcmp(lexeme, "not") == 0) {
                nextToken = NOT_OP;
            } else {
                nextToken = IDENT;
            }
            break;
        /* Parse integer literals */
        case DIGIT:
            addChar();
            getChar();
            while (charClass == DIGIT) {
                addChar();
                getChar();
            }
            nextToken = INT_LIT;
            break;
        /* Parentheses and operators */
        case UNKNOWN:
            lookup(nextChar);
            getChar();
            break;
        /* EOF */
        case EOF:
            nextToken = EOF;
            lexeme[0] = 'E';
            lexeme[1] = 'O';
            lexeme[2] = 'F';
            lexeme[3] = 0;
            break;
    } /* End of switch */
    printf(
        "Next token is: %d, Next lexeme is %s\n",
        nextToken,
        lexeme
    );
    return nextToken;
} /* End of function lex */
