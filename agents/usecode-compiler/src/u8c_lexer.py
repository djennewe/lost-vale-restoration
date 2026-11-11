#!/usr/bin/env python3
"""
u8c_lexer.py — Tokenizer for Ultima 8 .UNK source files.

Produces a stream of tokens from raw source text. Handles:
- Keywords (uses, globalflag, npcclass, eggclass, typeclass, etc.)
- Identifiers (variable names, class names, type references)
- Operators (=, !=, <, >, <=, >=, +, -, *, /, ++, --, +=, -=, ^=)
- Delimiters ({ } ( ) [ ] ; , : << >>)
- String literals ("..." including multi-line + concatenation markers)
- Number literals (integer, hex)
- Comments (// single-line, /* multi-line */)
- Preprocessor directives (#if English/French/German { ... })
- Process type annotations ([[PT_DEFAULT, referent]])
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Keywords
    USES = auto()
    GLOBALFLAG = auto()
    GLOBALVAR = auto()
    NPCCLASS = auto()
    EGGCLASS = auto()
    TYPECLASS = auto()
    INHERITS = auto()
    PROCESS = auto()
    ROUTINE = auto()
    STARTUP = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    TO = auto()
    FOREACH = auto()
    RECURSIVE = auto()
    WHERE = auto()
    WITHIN = auto()
    CELLS = auto()
    OF = auto()
    REFERENT = auto()
    CONTAINER = auto()
    SWITCH = auto()
    CASE = auto()
    BREAK = auto()
    RETURN = auto()
    SPAWN = auto()
    WAIT = auto()
    BARK = auto()
    ASK = auto()
    ENTERCONVO = auto()
    EXITCONVO = auto()
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    CREATE = auto()
    DESTROY = auto()

    # Type keywords
    NUMBER = auto()      # Number
    STRING = auto()      # String
    ITEM = auto()        # Item
    NPC = auto()         # Npc
    REFERENT_TYPE = auto()  # Referent
    LIST = auto()        # List
    WORD = auto()        # Word
    LONG = auto()        # Long
    FRAME = auto()       # Frame
    WORLDPOINT = auto()  # WorldPoint
    MAPNUM = auto()      # MapNum

    # Literals
    STRING_LIT = auto()  # "..."
    INTEGER_LIT = auto() # 42, 0x2A
    FLOAT_LIT = auto()   # unused but reserved

    # Identifiers
    IDENT = auto()       # variable/function/class names

    # Operators
    ASSIGN = auto()      # =
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    AMPERSAND = auto()   # & (bitwise and)
    PIPE = auto()        # | (bitwise or; METHOD.UNK `DMG_FIRE|DMG_BLUNT`)
    EQ = auto()          # = (in comparisons, same token as ASSIGN)
    NE = auto()          # !=
    LT = auto()          # <
    GT = auto()          # >
    LE = auto()          # <=
    GE = auto()          # >=
    INC = auto()         # ++
    DEC = auto()         # --
    PLUS_ASSIGN = auto() # +=
    MINUS_ASSIGN = auto()  # -=
    SLASH_ASSIGN = auto()  # /= (FREE.UNK getCellDist: `dist /= 32;`)
    CARET_ASSIGN = auto()  # ^= (prepend to list)
    DOT = auto()         # .
    COLON_COLON = auto() # ::
    ARROW = auto()       # ->

    # Delimiters
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    SEMICOLON = auto()   # ;
    COMMA = auto()       # ,
    COLON = auto()       # :
    LSHIFT = auto()      # <<
    RSHIFT = auto()      # >>

    # Preprocessor
    PREPROC_IF = auto()  # #if
    ENGLISH = auto()     # English
    FRENCH = auto()      # French
    GERMAN = auto()      # German

    # Special
    EOF = auto()
    NEWLINE = auto()     # used internally for line tracking


# Keyword mapping (case-sensitive except for some)
KEYWORDS = {
    'uses': TokenType.USES,
    'globalflag': TokenType.GLOBALFLAG,
    'globalvar': TokenType.GLOBALVAR,
    'npcclass': TokenType.NPCCLASS,
    'eggclass': TokenType.EGGCLASS,
    'typeclass': TokenType.TYPECLASS,
    'inherits': TokenType.INHERITS,
    'process': TokenType.PROCESS,
    'routine': TokenType.ROUTINE,
    'startup': TokenType.STARTUP,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'to': TokenType.TO,
    'foreach': TokenType.FOREACH,
    'recursive': TokenType.RECURSIVE,
    'where': TokenType.WHERE,
    'within': TokenType.WITHIN,
    'cells': TokenType.CELLS,
    'of': TokenType.OF,
    'referent': TokenType.REFERENT,
    'container': TokenType.CONTAINER,
    'switch': TokenType.SWITCH,
    'case': TokenType.CASE,
    'break': TokenType.BREAK,
    'return': TokenType.RETURN,
    'spawn': TokenType.SPAWN,
    'wait': TokenType.WAIT,
    'bark': TokenType.BARK,
    'ask': TokenType.ASK,
    'enterConvo': TokenType.ENTERCONVO,
    'exitConvo': TokenType.EXITCONVO,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'create': TokenType.CREATE,
    'destroy': TokenType.DESTROY,
    # Type keywords
    'Number': TokenType.NUMBER,
    'String': TokenType.STRING,
    'Item': TokenType.ITEM,
    'Npc': TokenType.NPC,
    'Referent': TokenType.REFERENT_TYPE,
    'List': TokenType.LIST,
    'Word': TokenType.WORD,
    'Long': TokenType.LONG,
    'Frame': TokenType.FRAME,
    'WorldPoint': TokenType.WORLDPOINT,
    'MapNum': TokenType.MAPNUM,
    # Preprocessor language names
    'English': TokenType.ENGLISH,
    'French': TokenType.FRENCH,
    'German': TokenType.GERMAN,
}


@dataclass
class Token:
    """A single token from the lexer."""
    type: TokenType
    value: str        # raw text of the token
    line: int         # 1-based line number
    col: int          # 1-based column number

    def __repr__(self):
        if self.type in (TokenType.STRING_LIT, TokenType.INTEGER_LIT, TokenType.IDENT):
            return f"Token({self.type.name}, {self.value!r}, L{self.line}:{self.col})"
        return f"Token({self.type.name}, L{self.line}:{self.col})"


class LexerError(Exception):
    def __init__(self, message, line=0, col=0):
        self.line = line
        self.col = col
        super().__init__(f"Line {line}:{col}: {message}")


class Lexer:
    """Tokenize U8 .UNK source code."""

    def __init__(self, source, filename='<unknown>'):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def _peek(self, offset=0):
        """Look ahead at the character at pos+offset."""
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return '\0'

    def _advance(self, count=1):
        """Advance position by count characters, tracking line/col."""
        for _ in range(count):
            if self.pos < len(self.source):
                if self.source[self.pos] == '\n':
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.pos += 1

    def _at_end(self):
        return self.pos >= len(self.source)

    def _skip_whitespace(self):
        """Skip whitespace (spaces, tabs, newlines, etc.)."""
        while not self._at_end() and self.source[self.pos] in ' \t\r\n':
            self._advance()

    def _skip_line_comment(self):
        """Skip // ... to end of line."""
        while not self._at_end() and self.source[self.pos] != '\n':
            self._advance()

    def _skip_block_comment(self):
        """Skip /* ... */ block comment."""
        self._advance(2)  # skip /*
        while not self._at_end():
            if self._peek() == '*' and self._peek(1) == '/':
                self._advance(2)
                return
            self._advance()
        raise LexerError("Unterminated block comment", self.line, self.col)

    def _read_string(self):
        """Read a string literal "..."

        Handles:
        - Multi-line strings (newlines preserved)
        - Escape sequences: \\f (French), \\g (German)
        - Strings do NOT use backslash escaping for quotes
        """
        start_line = self.line
        start_col = self.col
        self._advance()  # skip opening "
        chars = []

        while not self._at_end():
            c = self.source[self.pos]
            if c == '"':
                self._advance()  # skip closing "
                text = ''.join(chars)
                # Strip multilingual suffixes: \f starts French, \g starts German
                # Find the earliest language marker and truncate there
                for marker in ('\\f', '\\g'):
                    m_idx = text.find(marker)
                    if m_idx >= 0:
                        text = text[:m_idx].rstrip()
                # Strip developer annotations: // @@@ CHANGE F G
                import re
                text = re.sub(r'\s*//\s*@@@\s*CHANGE\s+F\s+G\s*', ' ', text)
                # Normalize source-level whitespace: collapse newlines and
                # runs of spaces into single spaces (the engine word-wraps).
                # The ends are NOT stripped: a literal's own edge space is
                # the word break in a concatenation. Retail ARAMINA 0x40D
                # 1146 stores "Yes, I am " for `"Yes, I am "+getName()`,
                # and 10,150 of retail's 11,312 strings keep a trailing
                # space; stripping made Aramina say "Yes, I amAramina.".
                # Whitespace before a language marker is still dropped
                # (the rstrip above), so ask/case labels are unchanged.
                text = re.sub(r'\s+', ' ', text)
                return Token(TokenType.STRING_LIT, text,
                           start_line, start_col)
            else:
                chars.append(c)
                self._advance()

        raise LexerError("Unterminated string literal", start_line, start_col)

    def _read_number(self):
        """Read a number literal (decimal or hex 0xNN)."""
        start_line = self.line
        start_col = self.col
        start_pos = self.pos

        if self._peek() == '0' and self._peek(1) in ('x', 'X'):
            # Hex literal
            self._advance(2)
            while not self._at_end() and self.source[self.pos] in '0123456789abcdefABCDEF':
                self._advance()
        else:
            # Decimal literal
            while not self._at_end() and self.source[self.pos].isdigit():
                self._advance()

        value = self.source[start_pos:self.pos]
        return Token(TokenType.INTEGER_LIT, value, start_line, start_col)

    def _read_identifier(self):
        """Read an identifier or keyword."""
        start_line = self.line
        start_col = self.col
        start_pos = self.pos

        while not self._at_end() and (self.source[self.pos].isalnum() or
                                       self.source[self.pos] in '_'):
            self._advance()

        value = self.source[start_pos:self.pos]

        # Check for keywords
        tok_type = KEYWORDS.get(value, TokenType.IDENT)
        return Token(tok_type, value, start_line, start_col)

    def _read_preprocessor(self):
        """Read #if directive."""
        start_line = self.line
        start_col = self.col
        self._advance()  # skip #

        # Read directive name
        start_pos = self.pos
        while not self._at_end() and self.source[self.pos].isalpha():
            self._advance()
        directive = self.source[start_pos:self.pos]

        if directive == 'if':
            return Token(TokenType.PREPROC_IF, '#if', start_line, start_col)
        elif directive == '':
            # Bare # character — skip to end of line
            while not self._at_end() and self.source[self.pos] != '\n':
                self._advance()
            return None  # signal to skip this token
        else:
            # Unknown directive — skip line
            while not self._at_end() and self.source[self.pos] != '\n':
                self._advance()
            return None

    def _read_annotation(self):
        """Read [[...]] process type annotation."""
        start_line = self.line
        start_col = self.col
        self._advance(2)  # skip [[

        # Read until ]]
        start_pos = self.pos
        while not self._at_end():
            if self._peek() == ']' and self._peek(1) == ']':
                content = self.source[start_pos:self.pos]
                self._advance(2)  # skip ]]
                # Return as a special identifier
                return Token(TokenType.IDENT, '[[' + content + ']]',
                           start_line, start_col)
            self._advance()

        raise LexerError("Unterminated annotation [[...]]", start_line, start_col)

    def tokenize(self):
        """Tokenize the entire source, return list of Token."""
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.col = 1

        while not self._at_end():
            self._skip_whitespace()
            if self._at_end():
                break

            c = self._peek()
            start_line = self.line
            start_col = self.col

            # Comments
            if c == '/' and self._peek(1) == '/':
                # Handle //@@@ comments (just skip)
                self._skip_line_comment()
                continue
            if c == '/' and self._peek(1) == '*':
                self._skip_block_comment()
                continue

            # String literal
            if c == '"':
                self.tokens.append(self._read_string())
                continue

            # Number literal
            if c.isdigit():
                self.tokens.append(self._read_number())
                continue

            # Identifier or keyword
            if c.isalpha() or c == '_':
                self.tokens.append(self._read_identifier())
                continue

            # Preprocessor
            if c == '#':
                tok = self._read_preprocessor()
                if tok:
                    self.tokens.append(tok)
                continue

            # Annotations [[ ... ]]
            if c == '[' and self._peek(1) == '[':
                self.tokens.append(self._read_annotation())
                continue

            # Multi-char operators and delimiters
            c2 = self._peek(1)

            if c == '<' and c2 == '<':
                self.tokens.append(Token(TokenType.LSHIFT, '<<', start_line, start_col))
                self._advance(2)
                continue
            if c == '>' and c2 == '>':
                self.tokens.append(Token(TokenType.RSHIFT, '>>', start_line, start_col))
                self._advance(2)
                continue
            if c == '+' and c2 == '+':
                self.tokens.append(Token(TokenType.INC, '++', start_line, start_col))
                self._advance(2)
                continue
            if c == '-' and c2 == '-':
                self.tokens.append(Token(TokenType.DEC, '--', start_line, start_col))
                self._advance(2)
                continue
            if c == '+' and c2 == '=':
                self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_col))
                self._advance(2)
                continue
            if c == '-' and c2 == '=':
                self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_col))
                self._advance(2)
                continue
            if c == '/' and c2 == '=':
                self.tokens.append(Token(TokenType.SLASH_ASSIGN, '/=', start_line, start_col))
                self._advance(2)
                continue
            if c == '^' and c2 == '=':
                self.tokens.append(Token(TokenType.CARET_ASSIGN, '^=', start_line, start_col))
                self._advance(2)
                continue
            if c == '!' and c2 == '=':
                self.tokens.append(Token(TokenType.NE, '!=', start_line, start_col))
                self._advance(2)
                continue
            if c == '<' and c2 == '=':
                self.tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
                self._advance(2)
                continue
            if c == '>' and c2 == '=':
                self.tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
                self._advance(2)
                continue
            if c == ':' and c2 == ':':
                self.tokens.append(Token(TokenType.COLON_COLON, '::', start_line, start_col))
                self._advance(2)
                continue
            if c == '-' and c2 == '>':
                self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
                self._advance(2)
                continue

            # Single-char operators and delimiters
            single_chars = {
                '=': TokenType.ASSIGN,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.STAR,
                '/': TokenType.SLASH,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '.': TokenType.DOT,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                ':': TokenType.COLON,
                '&': TokenType.AMPERSAND,
                '|': TokenType.PIPE,
            }

            if c in single_chars:
                self.tokens.append(Token(single_chars[c], c, start_line, start_col))
                self._advance()
                continue

            # Unknown character — skip with warning
            # Some source files have non-ASCII chars (German umlauts, etc.)
            self._advance()

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.col))
        return self.tokens


def tokenize(source, filename='<unknown>'):
    """Convenience function to tokenize source code."""
    lexer = Lexer(source, filename)
    return lexer.tokenize()


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: u8c_lexer.py <source.unk>")
        print("  Tokenizes a .UNK source file and prints tokens.")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r', encoding='ascii', errors='replace') as f:
        source = f.read()

    tokens = tokenize(source, path)
    for tok in tokens:
        print(tok)
    print(f"\nTotal: {len(tokens)} tokens")
