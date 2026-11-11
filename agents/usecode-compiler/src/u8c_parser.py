#!/usr/bin/env python3
"""
u8c_parser.py — Parser for Ultima 8 .UNK source files.

Produces an AST from the token stream. Handles the full UNK language
including classes, processes, routines, control flow, expressions,
and the various U8-specific constructs (foreach, spawn, bark, etc.).

Grammar overview (simplified):
    program     = (uses | globalflag | class_decl | function_def)*
    uses        = 'uses' STRING ';'
    globalflag  = 'globalflag' IDENT [':' NUMBER] ';'
    class_decl  = ('npcclass'|'eggclass'|'typeclass') IDENT 'inherits' IDENT '{' members '}'
    function_def = ('process'|'routine') IDENT '::' IDENT '(' params ')' [':' type] block
    block       = '{' statement* '}'
    statement   = var_decl | if | while | for | foreach | switch | return | break
                | spawn | wait | bark | enterConvo | exitConvo | preproc_if
                | assignment | expr_stmt
"""

import sys
from typing import List, Optional

from u8c_lexer import Token, TokenType, Lexer, tokenize
from u8c_ast import *


class ParseError(Exception):
    def __init__(self, message, token=None):
        self.token = token
        if token:
            message = f"L{token.line}:{token.col}: {message}"
        super().__init__(message)


class Parser:
    """Recursive descent parser for UNK source code."""

    def __init__(self, tokens, filename='<unknown>'):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0
        # Every recovered ParseError, in order. "Parse succeeded" with a
        # non-empty list means statements were DROPPED from the AST —
        # the build gate decides which files may tolerate that.
        self.recovered_errors = []

    def _note_error(self, e):
        self.recovered_errors.append(str(e))
        sys.stderr.write(f"Parse error in {self.filename}: {e}\n")

    def _expect_func_name(self):
        """Function NAME position: an IDENT, or a statement keyword used
        as a name. FREE.UNK defines `process wait(...)` — `wait` lexes
        as the wait-statement keyword and was rejected here, which is
        how the provider's own wait() (and everything the recovery scan
        ate after it) vanished from the build (found 2026-07-04)."""
        tok = self._peek()
        if tok.type == TokenType.IDENT or (
                tok.value and tok.value[0].isalpha()):
            self._advance()
            return tok.value
        raise ParseError(f"Expected function name, got {tok.type.name} "
                         f"('{tok.value}')", tok)

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _at(self, *types):
        """Check if current token is one of the given types."""
        return self._peek().type in types

    def _at_value(self, value):
        """Check if current token value matches."""
        return self._peek().value == value

    def _advance(self):
        tok = self._peek()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _expect(self, tok_type, message=None):
        tok = self._peek()
        if tok.type != tok_type:
            msg = message or f"Expected {tok_type.name}, got {tok.type.name} ({tok.value!r})"
            raise ParseError(msg, tok)
        return self._advance()

    def _expect_value(self, value, message=None):
        tok = self._peek()
        if tok.value != value:
            msg = message or f"Expected '{value}', got '{tok.value}'"
            raise ParseError(msg, tok)
        return self._advance()

    def _match(self, *types):
        """If current token matches, consume and return it. Otherwise None."""
        if self._at(*types):
            return self._advance()
        return None

    def _loc(self):
        """Get line/col of current token for AST nodes."""
        tok = self._peek()
        return tok.line, tok.col

    # ─── Top-level ─────────────────────────────────────────────────────────

    def parse(self):
        """Parse the complete source file into a Program AST."""
        prog = Program()
        line, col = self._loc()
        prog.line, prog.col = line, col

        while not self._at(TokenType.EOF):
            try:
                if self._at(TokenType.USES):
                    prog.uses.append(self._parse_uses())
                elif self._at(TokenType.GLOBALFLAG):
                    prog.globalflags.append(self._parse_globalflag())
                elif self._at(TokenType.NPCCLASS, TokenType.EGGCLASS, TokenType.TYPECLASS):
                    prog.class_decl = self._parse_class_decl()
                elif self._at(TokenType.PROCESS, TokenType.ROUTINE):
                    # Could be a member declaration inside class or a function definition
                    # Look ahead to distinguish: process ClassName::func vs process func()
                    # A body-less `process crumble();` is a forward
                    # declaration (EAPUZL.UNK:11-12): no function, no bytes.
                    fdef = self._parse_function_def()
                    if fdef is not None:
                        prog.functions.append(fdef)
                else:
                    # Skip unknown tokens
                    self._advance()
            except ParseError as e:
                # Recovery: skip to next statement boundary
                self._note_error(e)
                self._recover()

        prog.parse_errors = list(self.recovered_errors)
        return prog

    def _recover(self):
        """Error recovery: skip to next likely statement start."""
        while not self._at(TokenType.EOF):
            if self._at(TokenType.SEMICOLON):
                self._advance()
                return
            if self._at(TokenType.RBRACE):
                return
            if self._at(TokenType.PROCESS, TokenType.ROUTINE, TokenType.USES,
                        TokenType.GLOBALFLAG, TokenType.NPCCLASS,
                        TokenType.EGGCLASS, TokenType.TYPECLASS):
                return
            self._advance()

    def _is_function_def(self):
        """Look ahead to check if this is a function definition.

        Patterns:
        - process ClassName::func(...)
        - routine ClassName::func(...)
        - routine func(...)  (bare routine without class)
        - process func(...)  (bare process — only at top level)
        """
        i = self.pos
        if i + 2 >= len(self.tokens):
            return False
        if self.tokens[i].type not in (TokenType.PROCESS, TokenType.ROUTINE):
            return False

        # Skip annotations
        j = i + 1
        if j < len(self.tokens) and self.tokens[j].value.startswith('[['):
            j += 1

        if j + 2 >= len(self.tokens):
            return False

        # Check for ClassName::func pattern
        if (self.tokens[j].type in (TokenType.IDENT, TokenType.NPC, TokenType.ITEM) and
            self.tokens[j + 1].type == TokenType.COLON_COLON):
            return True

        # Check for bare routine/process: IDENT LPAREN
        if (self.tokens[j].type == TokenType.IDENT and
            self.tokens[j + 1].type == TokenType.LPAREN):
            return True

        return False

    # ─── Declarations ──────────────────────────────────────────────────────

    def _parse_uses(self):
        """Parse: uses "filename";"""
        line, col = self._loc()
        self._expect(TokenType.USES)
        name_tok = self._expect(TokenType.STRING_LIT)
        self._expect(TokenType.SEMICOLON)
        return UsesDecl(line=line, col=col, filename=name_tok.value)

    def _parse_globalflag(self):
        """Parse: globalflag name; or globalflag name:bits;"""
        line, col = self._loc()
        self._expect(TokenType.GLOBALFLAG)
        name_tok = self._expect(TokenType.IDENT)
        bits = 1
        if self._match(TokenType.COLON):
            bits_tok = self._expect(TokenType.INTEGER_LIT)
            bits = int(bits_tok.value)
        self._expect(TokenType.SEMICOLON)
        return GlobalFlagDecl(line=line, col=col, name=name_tok.value, bits=bits)

    def _parse_class_decl(self):
        """Parse class declaration."""
        line, col = self._loc()
        kind_tok = self._advance()  # npcclass/eggclass/typeclass
        name_tok = self._expect(TokenType.IDENT)
        self._expect(TokenType.INHERITS)
        # Base class can be Item, Npc, Egg, or an identifier
        if self._at(TokenType.ITEM):
            base = self._advance().value
        elif self._at(TokenType.NPC):
            base = self._advance().value
        elif self._at(TokenType.IDENT):
            base = self._advance().value
        else:
            base = self._expect(TokenType.IDENT).value

        self._expect(TokenType.LBRACE)
        members = []
        while not self._at(TokenType.RBRACE, TokenType.EOF):
            members.append(self._parse_member_decl())
        self._expect(TokenType.RBRACE)

        return ClassDecl(line=line, col=col, kind=kind_tok.value,
                        name=name_tok.value, inherits=base, members=members)

    def _parse_member_decl(self):
        """Parse a member declaration inside a class body."""
        line, col = self._loc()
        kind_tok = self._expect(TokenType.PROCESS) if self._at(TokenType.PROCESS) \
                   else self._expect(TokenType.ROUTINE)

        annotations = []
        # Check for annotations like [[PT_DEFAULT, referent]]
        while self._at(TokenType.IDENT) and self._peek().value.startswith('[['):
            annotations.append(self._advance().value)

        name_tok = self._expect(TokenType.IDENT)
        self._expect(TokenType.LPAREN)
        params = self._parse_params()
        self._expect(TokenType.RPAREN)
        # Optional return type, as on a definition: ORLOK1.UNK:11
        # declares `routine getDrink():String;`.
        if self._match(TokenType.COLON):
            self._parse_type_name()
        self._expect(TokenType.SEMICOLON)

        return MemberDecl(line=line, col=col, kind=kind_tok.value,
                         name=name_tok.value, params=params,
                         annotations=annotations)

    def _parse_params(self):
        """Parse parameter list: name:Type, name:Type, ..."""
        params = []
        while not self._at(TokenType.RPAREN, TokenType.EOF):
            if params:
                self._expect(TokenType.COMMA)
            name_tok = self._expect(TokenType.IDENT)
            # Optional type annotation
            type_name = ''
            if self._match(TokenType.COLON):
                type_name = self._parse_type_name()
            params.append(ParamDecl(line=name_tok.line, col=name_tok.col,
                                   name=name_tok.value, type_name=type_name))
        return params

    # Second words of a compound type name. `Item List`, `Number List`
    # and `String List` are list locals (FREE.UNK give/take/combine,
    # countNumList/countStrList); `String Reference` is a by-reference
    # parameter (METHOD.UNK timedBark/lookBark).
    _TYPE_SUFFIXES = {TokenType.LIST: 'List'}
    _TYPE_SUFFIX_IDENTS = ('Reference',)

    def _parse_type_name(self):
        """Parse a type name (may be a keyword like Item, Npc, etc.),
        including a compound `<Type> List` / `<Type> Reference`."""
        tok = self._peek()
        if tok.type in (TokenType.NUMBER, TokenType.STRING, TokenType.ITEM,
                        TokenType.NPC, TokenType.REFERENT_TYPE, TokenType.LIST,
                        TokenType.WORD, TokenType.LONG, TokenType.FRAME,
                        TokenType.WORLDPOINT, TokenType.MAPNUM,
                        TokenType.IDENT):
            self._advance()
            nxt = self._peek()
            if tok.type != TokenType.LIST and (
                    nxt.type in self._TYPE_SUFFIXES or
                    (nxt.type == TokenType.IDENT
                     and nxt.value in self._TYPE_SUFFIX_IDENTS)):
                self._advance()
                return f'{tok.value} {nxt.value}'
            return tok.value
        raise ParseError(f"Expected type name, got {tok.type.name}", tok)

    # ─── Function definitions ──────────────────────────────────────────────

    def _parse_function_def(self):
        """Parse: process/routine ClassName::funcName(params) { body }
        Also handles bare routines: routine funcName(params) { body }
        """
        line, col = self._loc()
        kind_tok = self._advance()  # process or routine

        annotations = []
        while self._at(TokenType.IDENT) and self._peek().value.startswith('[['):
            annotations.append(self._advance().value)

        # Check for bare function (no class::) vs qualified (Class::func)
        if self._peek(1).type == TokenType.COLON_COLON:
            # Class name (could be a type keyword like Npc)
            if self._at(TokenType.NPC):
                class_name = self._advance().value
            elif self._at(TokenType.ITEM):
                class_name = self._advance().value
            else:
                class_name = self._expect(TokenType.IDENT).value
            self._expect(TokenType.COLON_COLON)
            func_name = self._expect_func_name()
        else:
            # Bare function: routine funcName(...)
            class_name = ''
            func_name = self._expect_func_name()

        # The parameter list may be omitted entirely: retail-compiled
        # U8/TEMP.UNK:27 defines `process Avatar::use { ... }`.
        params = []
        if not self._at(TokenType.LBRACE):
            self._expect(TokenType.LPAREN)
            params = self._parse_params()
            self._expect(TokenType.RPAREN)

        # Optional return type: `routine getPeriod():Number { ... }`.
        # CORRECTED 2026-07-03 (uses-import work): this was previously
        # unhandled, so any routine/process declaring a return type failed
        # to parse at all (`Expected LBRACE, got COLON`) and was dropped
        # by top-level error recovery — silently losing the function AND
        # desyncing the recovery scan through the rest of the file. This
        # affected most of FREE.UNK's library routines (getPeriod, getHour,
        # give, getDistance, createNear, unkCloseAllGumps, ...), which is
        # exactly the source-level reason `uses`-imported calls to them
        # never had anything to resolve to.
        return_type = ''
        if self._match(TokenType.COLON):
            return_type = self._parse_type_name()

        # Forward declaration (EAPUZL.UNK:11 `process crumble();`): a
        # prototype, not a definition. Returns None; the caller skips it.
        if self._match(TokenType.SEMICOLON):
            return None

        self._expect(TokenType.LBRACE)

        fdef = FunctionDef(line=line, col=col, kind=kind_tok.value,
                          class_name=class_name, func_name=func_name,
                          params=params, annotations=annotations,
                          return_type=return_type)

        # Function body.
        #
        # FIXED 2026-07-19: there used to be a second, special-cased path here
        # that fired when the body opened DIRECTLY with `startup {`. It parsed
        # the startup/process blocks into fdef.startup_block / fdef.process_block
        # — attributes u8c_codegen.py has never read. The generator emits only
        # fdef.body, so every such function compiled to an empty stub
        # (`init 00h; ret`). The identical source with any leading statement
        # before `startup` (typically a `[[PT_DEFAULT, referent]];` annotation)
        # missed the special case, fell through to this loop, and compiled
        # correctly — _parse_statement() already handles STARTUP and PROCESS
        # blocks as ordinary block statements. That asymmetry was the whole bug
        # (symptom: LORDBRIT's puppet ghost never animated).
        #
        # There is now ONE path. startup_block/process_block are never
        # populated; the blocks land in fdef.body as nested Block statements,
        # which is byte-for-byte what the already-known-good annotated form
        # produced.
        stmts = []
        while not self._at(TokenType.RBRACE, TokenType.EOF):
            try:
                stmt = self._parse_statement()
                if stmt:
                    stmts.append(stmt)
            except ParseError as e:
                # Recover within the function body instead of losing
                # the entire method — skip to next statement boundary
                self._note_error(e)
                self._recover()
        fdef.body = Block(stmts=stmts, line=line, col=col)

        self._expect(TokenType.RBRACE)
        return fdef

    # ─── Statements ────────────────────────────────────────────────────────

    def _parse_block(self):
        """Parse a { ... } block.

        Recovery is SCOPED to the statement: before 2026-07-04 a
        ParseError deep inside a nested block unwound through every
        enclosing while/switch/case to the function-body loop, silently
        abandoning the whole structure (EZEKREL shipped with its entire
        conversation missing). Now an error inside a block loses at most
        one statement, is counted in self.recovered_errors, and parsing
        resumes at the next boundary inside the SAME block.
        """
        line, col = self._loc()
        self._expect(TokenType.LBRACE)
        stmts = []
        while not self._at(TokenType.RBRACE, TokenType.EOF):
            try:
                stmt = self._parse_statement()
                if stmt:
                    stmts.append(stmt)
            except ParseError as e:
                self._note_error(e)
                self._recover()
        self._expect(TokenType.RBRACE)
        return Block(stmts=stmts, line=line, col=col)

    def _parse_statement(self):
        """Parse a single statement."""
        tok = self._peek()

        # Preprocessor
        if tok.type == TokenType.PREPROC_IF:
            return self._parse_preproc_if()

        # Startup block (used inside process functions in base game files)
        if tok.type == TokenType.STARTUP:
            self._advance()
            return self._parse_block()

        # Process block (companion to startup). Tagged kind='process' so
        # u8c_codegen.py can wrap it in the backward-jump loop retail's
        # 1994 compiler gives this construct (see Block's docstring in
        # u8c_ast.py) -- startup's block is NOT tagged, and runs once.
        if tok.type == TokenType.PROCESS:
            # Only treat as a statement if followed by { (not a function def)
            if self._peek(1).type == TokenType.LBRACE:
                self._advance()
                blk = self._parse_block()
                blk.kind = 'process'
                return blk

        # Control flow
        if tok.type == TokenType.IF:
            return self._parse_if()
        if tok.type == TokenType.WHILE:
            return self._parse_while()
        if tok.type == TokenType.FOR:
            return self._parse_for()
        if tok.type == TokenType.FOREACH:
            return self._parse_foreach()
        if tok.type == TokenType.SWITCH:
            return self._parse_switch()
        if tok.type == TokenType.RETURN:
            return self._parse_return()
        if tok.type == TokenType.BREAK:
            self._advance()
            self._match(TokenType.SEMICOLON)
            return BreakStmt(line=tok.line, col=tok.col)

        # Spawn statement
        if tok.type == TokenType.SPAWN:
            return self._parse_spawn()

        # Wait statement
        if tok.type == TokenType.WAIT:
            return self._parse_wait()

        # Enter/exit convo
        if tok.type == TokenType.ENTERCONVO:
            self._advance()
            self._expect(TokenType.LPAREN)
            self._expect(TokenType.RPAREN)
            self._match(TokenType.SEMICOLON)
            return EnterConvoStmt(line=tok.line, col=tok.col)
        if tok.type == TokenType.EXITCONVO:
            self._advance()
            self._expect(TokenType.LPAREN)
            self._expect(TokenType.RPAREN)
            self._match(TokenType.SEMICOLON)
            return ExitConvoStmt(line=tok.line, col=tok.col)

        # Variable declaration: name:Type [= expr];
        # Detecting: IDENT (COMMA IDENT)* COLON TypeName
        if self._is_var_decl():
            return self._parse_var_decl()

        # Expression statement (assignment, function call, etc.)
        expr = self._parse_expression()
        if expr:
            # Check for assignment operators
            if self._at(TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
                       TokenType.MINUS_ASSIGN, TokenType.SLASH_ASSIGN,
                       TokenType.CARET_ASSIGN):
                op_tok = self._advance()
                value = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                return Assignment(line=tok.line, col=tok.col,
                                target=expr, op=op_tok.value, value=value)

            # Check for postfix ++ / --
            if self._at(TokenType.INC, TokenType.DEC):
                op_tok = self._advance()
                self._match(TokenType.SEMICOLON)
                return PostfixOp(line=tok.line, col=tok.col,
                               op=op_tok.value, operand=expr)

            # `npc.enterConvo();` / `npc.exitConvo();` (FREE.UNK's five
            # `agent.enterConvo()` pairs): the same statement as the bare
            # form, aimed at the named NPC instead of `referent`.
            if (isinstance(expr, MethodCall) and not expr.args
                    and expr.method in ('enterConvo', 'exitConvo')):
                self._match(TokenType.SEMICOLON)
                node = (EnterConvoStmt if expr.method == 'enterConvo'
                        else ExitConvoStmt)
                return node(line=tok.line, col=tok.col, target=expr.obj)

            self._match(TokenType.SEMICOLON)
            return ExprStmt(line=tok.line, col=tok.col, expr=expr)

        # Skip unknown
        self._advance()
        return None

    def _is_var_decl(self):
        """Check if current position starts a variable declaration.

        Pattern: IDENT [, IDENT]* : TypeName
        """
        i = self.pos
        # Must start with identifier
        if self.tokens[i].type != TokenType.IDENT:
            return False

        j = i + 1
        # Skip comma-separated identifiers
        while j + 1 < len(self.tokens):
            if self.tokens[j].type == TokenType.COMMA:
                j += 1
                if self.tokens[j].type == TokenType.IDENT:
                    j += 1
                else:
                    return False
            elif self.tokens[j].type == TokenType.COLON:
                # Check that what follows the colon is a type name
                if j + 1 < len(self.tokens):
                    next_tok = self.tokens[j + 1]
                    if next_tok.type in (TokenType.NUMBER, TokenType.STRING,
                                        TokenType.ITEM, TokenType.NPC,
                                        TokenType.REFERENT_TYPE, TokenType.LIST,
                                        TokenType.WORD, TokenType.LONG,
                                        TokenType.FRAME, TokenType.WORLDPOINT,
                                        TokenType.MAPNUM, TokenType.IDENT):
                        return True
                return False
            else:
                return False
        return False

    def _parse_var_decl(self):
        """Parse variable declaration."""
        line, col = self._loc()
        names = []
        names.append(self._expect(TokenType.IDENT).value)
        while self._match(TokenType.COMMA):
            names.append(self._expect(TokenType.IDENT).value)
        self._expect(TokenType.COLON)
        type_name = self._parse_type_name()

        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()

        self._match(TokenType.SEMICOLON)
        return VarDecl(line=line, col=col, names=names,
                      type_name=type_name, initializer=initializer)

    def _parse_if(self):
        """Parse if/else statement."""
        line, col = self._loc()
        self._expect(TokenType.IF)

        # Parse the condition. It may be:
        # 1. (expr) { ... }
        # 2. (expr1) or (expr2) { ... }
        # 3. expr { ... }
        condition = self._parse_expression()

        then_block = self._parse_block()
        else_block = None
        if self._match(TokenType.ELSE):
            if self._at(TokenType.IF):
                else_block = self._parse_if()
            else:
                else_block = self._parse_block()

        return IfStmt(line=line, col=col, condition=condition,
                     then_block=then_block, else_block=else_block)

    def _parse_while(self):
        """Parse while loop."""
        line, col = self._loc()
        self._expect(TokenType.WHILE)
        condition = self._parse_expression()
        body = self._parse_block()
        return WhileStmt(line=line, col=col, condition=condition, body=body)

    def _parse_for(self):
        """Parse for loop: for var=start to end { body }"""
        line, col = self._loc()
        self._expect(TokenType.FOR)
        var_tok = self._expect(TokenType.IDENT)
        self._expect(TokenType.ASSIGN)
        start = self._parse_expression()
        self._expect(TokenType.TO)
        end = self._parse_expression()
        body = self._parse_block()
        return ForStmt(line=line, col=col, var_name=var_tok.value,
                      start=start, end=end, body=body)

    def _parse_foreach(self):
        """Parse foreach loop."""
        line, col = self._loc()
        self._expect(TokenType.FOREACH)

        recursive = bool(self._match(TokenType.RECURSIVE))
        var_tok = self._expect(TokenType.IDENT)

        # `foreach x in L { }`: iterate a list local (FREE.UNK give/take/
        # createNear/countNumList/countStrList, METHOD.UNK boom).
        if self._at(TokenType.IDENT) and self._peek().value == 'in':
            self._advance()
            list_expr = self._parse_postfix()
            body = self._parse_block()
            return ForEachStmt(line=line, col=col, recursive=recursive,
                               var_name=var_tok.value, search_type='list',
                               container_expr=list_expr, body=body)

        conditions = []
        if self._match(TokenType.WHERE):
            conditions = self._parse_foreach_conditions()

        self._expect(TokenType.WITHIN)

        if self._at(TokenType.CONTAINER):
            self._advance()
            # Full postfix expression: SHADES.UNK searches `within
            # container backpack.referent` — a bare _parse_primary left
            # the `.referent` in the stream and the recovery unwind ate
            # the foreach (found 2026-07-04).
            container_expr = self._parse_postfix()
            body = self._parse_block()
            return ForEachStmt(line=line, col=col, recursive=recursive,
                             var_name=var_tok.value, conditions=conditions,
                             search_type='container',
                             container_expr=container_expr, body=body)
        else:
            range_expr = self._parse_expression()
            # `cells`, or the singular `cell` (METHOD.UNK:499 `within 1
            # cell of item.referent`), which lexes as a plain IDENT.
            has_cells = bool(self._match(TokenType.CELLS))
            if not has_cells and self._at(TokenType.IDENT) \
                    and self._peek().value == 'cell':
                self._advance()
                has_cells = True
            self._expect(TokenType.OF)
            # 'referent' keyword or an expression. Full postfix, as for
            # containers: retail-compiled AVATAR.UNK searches `within 30
            # cells of caster.referent` and `within 30 cells of
            # Avatar:Referent`, and a bare primary left `.referent` /
            # `:Referent` in the stream, so the recovery unwind dropped
            # everything from the foreach on.
            if self._at(TokenType.REFERENT):
                self._advance()
                container_expr = Identifier(name='referent')
            else:
                container_expr = self._parse_postfix()
            body = self._parse_block()
            return ForEachStmt(line=line, col=col, recursive=recursive,
                             var_name=var_tok.value, conditions=conditions,
                             search_type='cells', range_expr=range_expr,
                             container_expr=container_expr, body=body,
                             cells=has_cells)

    def _parse_foreach_conditions(self):
        """Parse foreach where conditions: (type = X) and (frame = Y) etc."""
        conditions = []
        has_paren = self._match(TokenType.LPAREN)
        cond = self._parse_expression()
        if has_paren:
            self._expect(TokenType.RPAREN)
        conditions.append(cond)

        while self._at(TokenType.AND):
            self._advance()
            has_paren = self._match(TokenType.LPAREN)
            cond = self._parse_expression()
            if has_paren:
                self._expect(TokenType.RPAREN)
            conditions.append(cond)

        return conditions

    def _parse_switch(self):
        """Parse switch statement."""
        line, col = self._loc()
        self._expect(TokenType.SWITCH)
        expr = self._parse_primary()
        self._expect(TokenType.LBRACE)

        cases = []
        default = None
        while not self._at(TokenType.RBRACE, TokenType.EOF):
            if self._at(TokenType.CASE):
                cases.append(self._parse_case())
            elif (self._at(TokenType.IDENT) and self._peek().value == 'default'
                  and default is None):
                # `default { ... }` (retail-compiled U8/MORDEA.UNK:798,
                # AIRSPEL.UNK x4): runs when no case matched.
                self._advance()
                default = self._parse_block()
            else:
                # Anything else used to be skipped token by token without
                # a trace, dropping whole `default` blocks; skip it still,
                # but count it like every other recovered error.
                self._note_error(ParseError(
                    f"Unexpected token in switch: {self._peek().type.name} "
                    f"({self._peek().value!r})", self._peek()))
                self._advance()

        self._expect(TokenType.RBRACE)
        return SwitchStmt(line=line, col=col, expr=expr, cases=cases,
                          default=default)

    def _parse_case(self):
        """Parse a case clause. May have multiple comma-separated values."""
        line, col = self._loc()
        self._expect(TokenType.CASE)
        # Additive expression: retail-compiled U8/SALKIND.UNK:639 and
        # XAVIER.UNK:1044 switch on `case "I am "+getName()+"."`.
        value = self._parse_addition()
        # Handle multi-value cases: case "A", "B" { ... }
        while self._match(TokenType.COMMA):
            next_val = self._parse_addition()
            # Store as a StringList for multi-value cases
            if isinstance(value, StringList):
                value.elements.append(next_val)
            else:
                value = StringList(line=line, col=col, elements=[value, next_val])
        body = self._parse_block()
        return CaseClause(line=line, col=col, value=value, body=body)

    def _parse_return(self):
        """Parse return statement."""
        line, col = self._loc()
        self._expect(TokenType.RETURN)
        expr = None
        if not self._at(TokenType.SEMICOLON, TokenType.RBRACE):
            expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return ReturnStmt(line=line, col=col, expr=expr)

    def _parse_spawn(self):
        """Parse spawn statement: spawn funcCall(args) -> return;

        Also the inline-process form (lv-patched/AVATAR.UNK:1047-1050):
            spawn call -> [[PT_DEFAULT,NULL_REF]] { body } -> return;
        and a chain (UNK/ARAMINA.UNK:501-503):
            spawn a(..) -> spawn b(..) -> spawn c(..) -> return;
        """
        line, col = self._loc()
        self._expect(TokenType.SPAWN)
        call = self._parse_expression()
        has_arrow = bool(self._match(TokenType.ARROW))
        inline_body = None
        inline_pragma = ''
        chain = []
        if has_arrow and (self._at(TokenType.LBRACE) or (
                self._at(TokenType.IDENT)
                and self._peek().value.startswith('[['))):
            if self._at(TokenType.IDENT):
                inline_pragma = self._advance().value
            inline_body = self._parse_block()
            has_arrow = bool(self._match(TokenType.ARROW))
        while has_arrow and inline_body is None and self._at(TokenType.SPAWN):
            self._advance()
            chain.append(self._parse_expression())
            has_arrow = bool(self._match(TokenType.ARROW))
        if has_arrow:
            self._match(TokenType.RETURN)
        self._match(TokenType.SEMICOLON)
        return SpawnStmt(line=line, col=col, call=call, has_arrow_return=has_arrow,
                         inline_body=inline_body, inline_pragma=inline_pragma,
                         chain=chain)

    def _parse_wait(self):
        """Parse wait statement."""
        line, col = self._loc()
        self._expect(TokenType.WAIT)
        self._expect(TokenType.LPAREN)
        ticks = self._parse_expression()
        self._expect(TokenType.RPAREN)
        self._match(TokenType.SEMICOLON)
        return WaitStmt(line=line, col=col, ticks=ticks)

    def _parse_preproc_if(self):
        """Parse #if English/French/German { ... }"""
        line, col = self._loc()
        self._expect(TokenType.PREPROC_IF)
        lang_tok = self._advance()  # English/French/German
        body = self._parse_block()
        return PreprocIf(line=line, col=col, language=lang_tok.value, body=body)

    # ─── Expressions ───────────────────────────────────────────────────────

    def _parse_expression(self):
        """Parse an expression (top-level, handles 'or')."""
        return self._parse_or()

    def _parse_or(self):
        left = self._parse_and()
        while self._at(TokenType.OR):
            op_tok = self._advance()
            right = self._parse_and()
            left = BinaryOp(line=op_tok.line, col=op_tok.col,
                          op='or', left=left, right=right)
        return left

    def _parse_and(self):
        left = self._parse_not()
        while self._at(TokenType.AND):
            op_tok = self._advance()
            right = self._parse_not()
            left = BinaryOp(line=op_tok.line, col=op_tok.col,
                          op='and', left=left, right=right)
        return left

    def _parse_not(self):
        if self._at(TokenType.NOT):
            op_tok = self._advance()
            operand = self._parse_not()
            return UnaryOp(line=op_tok.line, col=op_tok.col,
                         op='not', operand=operand)
        return self._parse_comparison()

    def _parse_comparison(self):
        left = self._parse_addition()
        if self._at(TokenType.ASSIGN, TokenType.NE, TokenType.LT,
                    TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self._advance()
            right = self._parse_addition()
            return BinaryOp(line=op_tok.line, col=op_tok.col,
                          op=op_tok.value, left=left, right=right)
        return left

    def _parse_addition(self):
        left = self._parse_multiplication()
        while self._at(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_multiplication()
            left = BinaryOp(line=op_tok.line, col=op_tok.col,
                          op=op_tok.value, left=left, right=right)
        return left

    def _parse_multiplication(self):
        # `&` (bitwise and) binds here, tighter than comparison: retail
        # source always reads `(getStatus() & INVISIBLE) = false`
        # (U8/ARAMINA.UNK:281, U8/CYRRUS.UNK:315) or tests the masked
        # value bare (`if Avatar.getStatus() & OWNED`, POTION.UNK). `|`
        # (METHOD.UNK:510 `DMG_FIRE|DMG_BLUNT`) and the word operator
        # `modulo` (FREE.UNK getHour/setHour, METHOD.UNK) bind alongside.
        left = self._parse_unary()
        while (self._at(TokenType.STAR, TokenType.SLASH, TokenType.AMPERSAND,
                        TokenType.PIPE)
               or (self._at(TokenType.IDENT)
                   and self._peek().value == 'modulo')):
            op_tok = self._advance()
            right = self._parse_unary()
            left = BinaryOp(line=op_tok.line, col=op_tok.col,
                          op=op_tok.value, left=left, right=right)
        return left

    def _parse_unary(self):
        if self._at(TokenType.MINUS):
            op_tok = self._advance()
            operand = self._parse_unary()
            return UnaryOp(line=op_tok.line, col=op_tok.col,
                         op='-', operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self):
        """Parse postfix operations: member access, method calls, indexing."""
        expr = self._parse_primary()

        while True:
            if self._at(TokenType.DOT):
                self._advance()
                member_tok = self._peek()
                # Member can be a keyword like bark, destroy, create, referent, etc.
                if member_tok.type in (TokenType.IDENT, TokenType.BARK,
                                       TokenType.CREATE, TokenType.DESTROY,
                                       TokenType.REFERENT, TokenType.ASK,
                                       TokenType.ENTERCONVO,
                                       TokenType.EXITCONVO):
                    member_name = self._advance().value
                else:
                    member_name = self._expect(TokenType.IDENT).value

                # Check for method call: obj.method(args)
                if self._at(TokenType.LPAREN):
                    self._advance()
                    args = self._parse_arg_list()
                    self._expect(TokenType.RPAREN)
                    expr = MethodCall(line=member_tok.line, col=member_tok.col,
                                    obj=expr, method=member_name, args=args)
                else:
                    expr = MemberAccess(line=member_tok.line, col=member_tok.col,
                                       obj=expr, member=member_name)
            elif self._at(TokenType.COLON):
                # Type cast: var:Type (like Avatar:Referent, 13:Frame).
                # Accept EVERY type keyword: `Frame`, `Number`, etc. lex
                # as keywords, not IDENTs, and rejecting them here (after
                # the colon is already consumed) used to leave the type
                # token in the stream — `give(..., 13:Frame, ...)` then
                # died with "Expected COMMA, got FRAME", and the recovery
                # unwind gutted EZEKREL's whole conversation (the entire
                # while/ask/switch dropped from the build, 2026-07-04).
                self._advance()
                type_tok = self._peek()
                if type_tok.type in (TokenType.REFERENT_TYPE, TokenType.IDENT,
                                    TokenType.ITEM, TokenType.NPC,
                                    TokenType.NUMBER, TokenType.STRING,
                                    TokenType.LIST, TokenType.WORD,
                                    TokenType.LONG, TokenType.FRAME,
                                    TokenType.WORLDPOINT, TokenType.MAPNUM):
                    type_name = self._advance().value
                    # This is a type annotation on an expression
                    expr = MemberAccess(line=type_tok.line, col=type_tok.col,
                                       obj=expr, member=type_name)
                else:
                    break
            elif self._at(TokenType.LBRACKET):
                # `L[i]`: one element of a list local (FREE.UNK take()
                # `item = itemList[element]`, `if deadList[1]`).
                lb = self._advance()
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET)
                expr = IndexExpr(line=lb.line, col=lb.col, obj=expr,
                                 index=index)
            else:
                break

        return expr

    def _parse_primary(self):
        """Parse a primary expression."""
        tok = self._peek()

        # Parenthesized expression
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        # String list: <<"str1", "str2">>
        if tok.type == TokenType.LSHIFT:
            return self._parse_string_list()

        # String literal
        if tok.type == TokenType.STRING_LIT:
            self._advance()
            return StringLit(line=tok.line, col=tok.col, value=tok.value)

        # Number literal
        if tok.type == TokenType.INTEGER_LIT:
            self._advance()
            if tok.value.startswith('0x') or tok.value.startswith('0X'):
                val = int(tok.value, 16)
            else:
                val = int(tok.value)
            return NumberLit(line=tok.line, col=tok.col, value=val)

        # Boolean literals
        if tok.type == TokenType.TRUE:
            self._advance()
            return BoolLit(line=tok.line, col=tok.col, value=True)
        if tok.type == TokenType.FALSE:
            self._advance()
            return BoolLit(line=tok.line, col=tok.col, value=False)

        # bark("text") as expression
        if tok.type == TokenType.BARK:
            self._advance()
            if self._at(TokenType.LPAREN):
                self._advance()
                text_expr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return BarkStmt(line=tok.line, col=tok.col, text=text_expr)
            return Identifier(line=tok.line, col=tok.col, name='bark')

        # ask(list) as expression
        if tok.type == TokenType.ASK:
            self._advance()
            if self._at(TokenType.LPAREN):
                self._advance()
                list_expr = self._parse_expression()
                self._expect(TokenType.RPAREN)
                return AskExpr(line=tok.line, col=tok.col, list_expr=list_expr)
            return Identifier(line=tok.line, col=tok.col, name='ask')

        # Type keywords used as identifiers (Avatar, referent, etc.)
        if tok.type in (TokenType.ITEM, TokenType.NPC, TokenType.REFERENT,
                        TokenType.REFERENT_TYPE):
            self._advance()
            name = tok.value
            # Check for function call
            if self._at(TokenType.LPAREN):
                self._advance()
                args = self._parse_arg_list()
                self._expect(TokenType.RPAREN)
                return FunctionCall(line=tok.line, col=tok.col,
                                  name=name, args=args)
            return Identifier(line=tok.line, col=tok.col, name=name)

        # Regular identifier or function call
        if tok.type == TokenType.IDENT:
            self._advance()
            # `Camera::scrollTo(...)`, `Kernel::getNumProcesses(...)`: a
            # call qualified with an intrinsic class (FREE.UNK, CHANGTAR,
            # EAPUZL, METHOD). The name is the intrinsic's method name.
            if self._at(TokenType.COLON_COLON):
                self._advance()
                fn_tok = self._peek()
                fn_name = self._expect_func_name()
                self._expect(TokenType.LPAREN)
                args = self._parse_arg_list()
                self._expect(TokenType.RPAREN)
                return FunctionCall(line=fn_tok.line, col=fn_tok.col,
                                    name=fn_name, args=args, scope=tok.value)
            # Check for function call
            if self._at(TokenType.LPAREN):
                self._advance()
                args = self._parse_arg_list()
                self._expect(TokenType.RPAREN)
                return FunctionCall(line=tok.line, col=tok.col,
                                  name=tok.value, args=args)
            return Identifier(line=tok.line, col=tok.col, name=tok.value)

        # Handle remaining keyword-as-identifiers (wait, create, destroy, etc.)
        # These are sometimes used as function names
        for kw_type in (TokenType.WAIT, TokenType.CREATE, TokenType.DESTROY,
                        TokenType.ENTERCONVO, TokenType.EXITCONVO,
                        TokenType.NUMBER, TokenType.STRING, TokenType.WORD,
                        TokenType.LONG, TokenType.FRAME, TokenType.WORLDPOINT,
                        TokenType.MAPNUM):
            if tok.type == kw_type:
                self._advance()
                if self._at(TokenType.LPAREN):
                    self._advance()
                    args = self._parse_arg_list()
                    self._expect(TokenType.RPAREN)
                    return FunctionCall(line=tok.line, col=tok.col,
                                      name=tok.value, args=args)
                return Identifier(line=tok.line, col=tok.col, name=tok.value)

        raise ParseError(f"Unexpected token: {tok.type.name} ({tok.value!r})", tok)

    def _parse_string_list(self):
        """Parse <<"str1", "str2", ...>>"""
        line, col = self._loc()
        self._expect(TokenType.LSHIFT)
        elements = []
        while not self._at(TokenType.RSHIFT, TokenType.EOF):
            if elements:
                self._match(TokenType.COMMA)
            elem = self._parse_expression()
            elements.append(elem)
        self._expect(TokenType.RSHIFT)
        return StringList(line=line, col=col, elements=elements)

    def _parse_arg_list(self):
        """Parse comma-separated argument list."""
        args = []
        while not self._at(TokenType.RPAREN, TokenType.EOF):
            if args:
                self._expect(TokenType.COMMA)
            args.append(self._parse_expression())
        return args


def parse_source(source, filename='<unknown>'):
    """Parse source code string into an AST."""
    tokens = tokenize(source, filename)
    parser = Parser(tokens, filename)
    return parser.parse()


def parse_file(path):
    """Parse a .UNK file into an AST."""
    with open(path, 'r', encoding='ascii', errors='replace') as f:
        source = f.read()
    return parse_source(source, path)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _print_ast(node, indent=0):
    """Pretty-print an AST node."""
    prefix = '  ' * indent
    if node is None:
        print(f"{prefix}None")
        return
    name = type(node).__name__
    if isinstance(node, NumberLit):
        print(f"{prefix}{name}({node.value})")
    elif isinstance(node, StringLit):
        v = node.value[:40]
        if len(node.value) > 40:
            v += '...'
        print(f"{prefix}{name}({v!r})")
    elif isinstance(node, BoolLit):
        print(f"{prefix}{name}({node.value})")
    elif isinstance(node, Identifier):
        print(f"{prefix}{name}({node.name})")
    elif isinstance(node, BinaryOp):
        print(f"{prefix}{name}(op={node.op!r})")
        _print_ast(node.left, indent + 1)
        _print_ast(node.right, indent + 1)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}{name}(op={node.op!r})")
        _print_ast(node.operand, indent + 1)
    elif isinstance(node, Assignment):
        print(f"{prefix}{name}(op={node.op!r})")
        _print_ast(node.target, indent + 1)
        _print_ast(node.value, indent + 1)
    elif isinstance(node, FunctionCall):
        print(f"{prefix}{name}({node.name})")
        for a in node.args:
            _print_ast(a, indent + 1)
    elif isinstance(node, MethodCall):
        print(f"{prefix}{name}(.{node.method})")
        _print_ast(node.obj, indent + 1)
        for a in node.args:
            _print_ast(a, indent + 1)
    elif isinstance(node, MemberAccess):
        print(f"{prefix}{name}(.{node.member})")
        _print_ast(node.obj, indent + 1)
    elif isinstance(node, Program):
        print(f"{prefix}Program")
        for u in node.uses:
            _print_ast(u, indent + 1)
        for g in node.globalflags:
            _print_ast(g, indent + 1)
        if node.class_decl:
            _print_ast(node.class_decl, indent + 1)
        for f in node.functions:
            _print_ast(f, indent + 1)
    elif isinstance(node, UsesDecl):
        print(f"{prefix}{name}({node.filename!r})")
    elif isinstance(node, GlobalFlagDecl):
        print(f"{prefix}{name}({node.name}, bits={node.bits})")
    elif isinstance(node, ClassDecl):
        print(f"{prefix}{name}({node.kind} {node.name} inherits {node.inherits})")
        for m in node.members:
            _print_ast(m, indent + 1)
    elif isinstance(node, MemberDecl):
        print(f"{prefix}{name}({node.kind} {node.name})")
    elif isinstance(node, FunctionDef):
        params = ', '.join(f'{p.name}:{p.type_name}' for p in node.params)
        print(f"{prefix}{name}({node.kind} {node.class_name}::{node.func_name}({params}))")
        if node.body:
            _print_ast(node.body, indent + 1)
        if node.startup_block:
            print(f"{prefix}  startup:")
            _print_ast(node.startup_block, indent + 2)
        if node.process_block:
            print(f"{prefix}  process:")
            _print_ast(node.process_block, indent + 2)
    elif isinstance(node, Block):
        print(f"{prefix}Block")
        for s in node.stmts:
            _print_ast(s, indent + 1)
    elif isinstance(node, VarDecl):
        print(f"{prefix}{name}({', '.join(node.names)}:{node.type_name})")
        if node.initializer:
            _print_ast(node.initializer, indent + 1)
    elif isinstance(node, IfStmt):
        print(f"{prefix}If")
        _print_ast(node.condition, indent + 1)
        print(f"{prefix}  then:")
        _print_ast(node.then_block, indent + 2)
        if node.else_block:
            print(f"{prefix}  else:")
            _print_ast(node.else_block, indent + 2)
    elif isinstance(node, WhileStmt):
        print(f"{prefix}While")
        _print_ast(node.condition, indent + 1)
        _print_ast(node.body, indent + 1)
    elif isinstance(node, ForStmt):
        print(f"{prefix}For({node.var_name})")
        _print_ast(node.start, indent + 1)
        _print_ast(node.end, indent + 1)
        _print_ast(node.body, indent + 1)
    elif isinstance(node, ForEachStmt):
        rec = 'recursive ' if node.recursive else ''
        print(f"{prefix}ForEach({rec}{node.var_name} {node.search_type})")
        for c in node.conditions:
            _print_ast(c, indent + 1)
        _print_ast(node.body, indent + 1)
    elif isinstance(node, SwitchStmt):
        print(f"{prefix}Switch")
        _print_ast(node.expr, indent + 1)
        for c in node.cases:
            _print_ast(c, indent + 1)
    elif isinstance(node, CaseClause):
        print(f"{prefix}Case")
        _print_ast(node.value, indent + 1)
        _print_ast(node.body, indent + 1)
    elif isinstance(node, ReturnStmt):
        print(f"{prefix}Return")
        if node.expr:
            _print_ast(node.expr, indent + 1)
    elif isinstance(node, SpawnStmt):
        arrow = '-> return' if node.has_arrow_return else ''
        print(f"{prefix}Spawn {arrow}")
        _print_ast(node.call, indent + 1)
    elif isinstance(node, WaitStmt):
        print(f"{prefix}Wait")
        _print_ast(node.ticks, indent + 1)
    elif isinstance(node, BarkStmt):
        print(f"{prefix}Bark")
        if node.target:
            _print_ast(node.target, indent + 1)
        _print_ast(node.text, indent + 1)
    elif isinstance(node, AskExpr):
        print(f"{prefix}Ask")
        _print_ast(node.list_expr, indent + 1)
    elif isinstance(node, StringList):
        print(f"{prefix}StringList({len(node.elements)} items)")
        for e in node.elements:
            _print_ast(e, indent + 1)
    elif isinstance(node, PreprocIf):
        print(f"{prefix}PreprocIf({node.language})")
        _print_ast(node.body, indent + 1)
    elif isinstance(node, ExprStmt):
        print(f"{prefix}ExprStmt")
        _print_ast(node.expr, indent + 1)
    elif isinstance(node, PostfixOp):
        print(f"{prefix}PostfixOp({node.op})")
        _print_ast(node.operand, indent + 1)
    else:
        print(f"{prefix}{name}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: u8c_parser.py <source.unk>")
        sys.exit(1)

    ast = parse_file(sys.argv[1])
    _print_ast(ast)
