#!/usr/bin/env python3
"""
u8c_ast.py — AST node definitions for the U8 usecode compiler.

All source-level constructs are represented as AST nodes. The parser
creates these; the code generator walks them to emit bytecode.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


# ─── Base ──────────────────────────────────────────────────────────────────────

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0
    col: int = 0


# ─── Top-level declarations ───────────────────────────────────────────────────

@dataclass
class Program(ASTNode):
    """Root node: a complete .UNK source file."""
    uses: List['UsesDecl'] = field(default_factory=list)
    globalflags: List['GlobalFlagDecl'] = field(default_factory=list)
    class_decl: Optional['ClassDecl'] = None
    functions: List['FunctionDef'] = field(default_factory=list)


@dataclass
class UsesDecl(ASTNode):
    """uses "filename";"""
    filename: str = ''


@dataclass
class GlobalFlagDecl(ASTNode):
    """globalflag flagName;  or  globalflag flagName:bits;"""
    name: str = ''
    bits: int = 1  # default 1 bit


@dataclass
class ClassDecl(ASTNode):
    """npcclass/eggclass/typeclass Name inherits Base { members }"""
    kind: str = ''  # 'npcclass', 'eggclass', 'typeclass'
    name: str = ''
    inherits: str = ''
    members: List['MemberDecl'] = field(default_factory=list)


@dataclass
class MemberDecl(ASTNode):
    """A member declaration in a class body (process/routine declaration)."""
    kind: str = ''  # 'process', 'routine'
    name: str = ''
    params: List['ParamDecl'] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)


@dataclass
class ParamDecl(ASTNode):
    """Parameter declaration: name : Type"""
    name: str = ''
    type_name: str = ''


@dataclass
class FunctionDef(ASTNode):
    """process/routine ClassName::funcName(params)[:ReturnType] { body }

    Also handles the startup/process block pattern used for puppet-style
    processes.
    """
    kind: str = ''  # 'process', 'routine'
    class_name: str = ''
    func_name: str = ''
    params: List[ParamDecl] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    body: Optional['Block'] = None
    # DEPRECATED 2026-07-19 — always None. The parser used to stash a body
    # that opened directly with `startup {` into these two fields instead of
    # into `body`, and u8c_codegen.py only ever emits `body`, so those
    # functions silently compiled to empty stubs. Both forms now parse into
    # `body` as nested Block statements. Retained only so any external reader
    # of the AST keeps working; do not start populating them again.
    startup_block: Optional['Block'] = None
    process_block: Optional['Block'] = None
    # Optional ':ReturnType' after the parameter list — e.g.
    # `routine getPeriod():Number { ... }`. '' when the source declares no
    # return type (most process/routine defs). See u8c_parser.py's
    # _parse_function_def for the grammar; used by u8c_codegen.py's
    # `uses`-import cross-class-call resolution to choose between
    # `push retval` (word) and `push byte retval` (Boolean) at call sites.
    return_type: str = ''


# ─── Statements ────────────────────────────────────────────────────────────────

@dataclass
class Block(ASTNode):
    """A { ... } block of statements.

    `kind` tags a block parsed from the bare `process { ... }` keyword
    form (set by _parse_statement's PROCESS branch). Retail's 1994
    compiler loops that block unconditionally until an internal `return`
    fires (confirmed against retail class 0x2FE, TypePotion::protection()/
    invisible() at offsets 0x059B/0x0687: each ends in a backward `jmp` to
    right after its own `startup` section) -- found 2026-10-01 while
    reviewing the LORDBRIT.UNK fix. u8c_codegen.py's _generate_statement
    reads this tag to wrap the block in that same loop. An ordinary
    brace block, or one parsed from `startup { ... }`, carries kind=''
    and generates exactly as before.
    """
    stmts: List[ASTNode] = field(default_factory=list)
    kind: str = ''


@dataclass
class VarDecl(ASTNode):
    """name:Type = initializer;  or  name,name2:Type;"""
    names: List[str] = field(default_factory=list)
    type_name: str = ''
    initializer: Optional[ASTNode] = None


@dataclass
class ExprStmt(ASTNode):
    """An expression used as a statement (e.g., function call)."""
    expr: Optional[ASTNode] = None


@dataclass
class IfStmt(ASTNode):
    """if (condition) { then_block } else { else_block }"""
    condition: Optional[ASTNode] = None
    then_block: Optional[Block] = None
    else_block: Optional[ASTNode] = None  # Block or IfStmt (else if)


@dataclass
class WhileStmt(ASTNode):
    """while (condition) { body }"""
    condition: Optional[ASTNode] = None
    body: Optional[Block] = None


@dataclass
class ForStmt(ASTNode):
    """for var=start to end { body }"""
    var_name: str = ''
    start: Optional[ASTNode] = None
    end: Optional[ASTNode] = None
    body: Optional[Block] = None


@dataclass
class ForEachStmt(ASTNode):
    """foreach [recursive] item where (conditions) within N cells of referent { body }
    foreach [recursive] item where (conditions) within container X { body }
    """
    recursive: bool = False
    var_name: str = ''
    conditions: List[ASTNode] = field(default_factory=list)
    search_type: str = ''  # 'cells', 'container', 'list'
    range_expr: Optional[ASTNode] = None  # N cells of referent
    container_expr: Optional[ASTNode] = None  # container X / the list of `in L`
    body: Optional[Block] = None
    cells: bool = False  # range was written `N cells` (units of 32)


@dataclass
class SwitchStmt(ASTNode):
    """switch expr { case "val" { ... } ... [default { ... }] }"""
    expr: Optional[ASTNode] = None
    cases: List['CaseClause'] = field(default_factory=list)
    default: Optional['Block'] = None


@dataclass
class CaseClause(ASTNode):
    """case value { body }"""
    value: Optional[ASTNode] = None  # string or number literal
    body: Optional[Block] = None


@dataclass
class ReturnStmt(ASTNode):
    """return [expr];"""
    expr: Optional[ASTNode] = None


@dataclass
class BreakStmt(ASTNode):
    """break;"""
    pass


@dataclass
class SpawnStmt(ASTNode):
    """spawn funcCall(args) -> return;"""
    call: Optional[ASTNode] = None
    has_arrow_return: bool = False
    # `spawn call -> [[PT_*, ref]] { body } -> return;` (AVATAR.UNK's
    # "Call Guards"): an inline process that waits on the spawned call,
    # then runs `body`. `inline_pragma` is the `[[...]]` text or ''.
    inline_body: Optional['Block'] = None
    inline_pragma: str = ''
    # `spawn a -> spawn b -> spawn c -> return;` (ARAMINA.UNK:501-503):
    # the calls after `call`, in source order.
    chain: List[ASTNode] = field(default_factory=list)


@dataclass
class WaitStmt(ASTNode):
    """wait(ticks);"""
    ticks: Optional[ASTNode] = None


@dataclass
class BarkStmt(ASTNode):
    """bark("text");  or  obj.bark("text");"""
    target: Optional[ASTNode] = None  # None = implicit this
    text: Optional[ASTNode] = None


@dataclass
class AskExpr(ASTNode):
    """ask(listExpr)"""
    list_expr: Optional[ASTNode] = None


@dataclass
class EnterConvoStmt(ASTNode):
    """enterConvo(); or npc.enterConvo();

    target is None for the bare form (the NPC is `referent`, this
    process's own item) or the expression naming the NPC (FREE's
    `agent.enterConvo()`, a local Npc)."""
    target: Optional[Any] = None


@dataclass
class ExitConvoStmt(ASTNode):
    """exitConvo(); or npc.exitConvo(); — target as EnterConvoStmt."""
    target: Optional[Any] = None


@dataclass
class PreprocIf(ASTNode):
    """#if English { ... }"""
    language: str = ''  # 'English', 'French', 'German'
    body: Optional[Block] = None


# ─── Expressions ───────────────────────────────────────────────────────────────

@dataclass
class NumberLit(ASTNode):
    """Integer literal."""
    value: int = 0


@dataclass
class StringLit(ASTNode):
    """String literal."""
    value: str = ''


@dataclass
class BoolLit(ASTNode):
    """true or false."""
    value: bool = False


@dataclass
class Identifier(ASTNode):
    """Variable or function name."""
    name: str = ''


@dataclass
class BinaryOp(ASTNode):
    """left op right"""
    op: str = ''  # '+', '-', '*', '/', '=', '!=', '<', '>', '<=', '>=', 'and', 'or'
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None


@dataclass
class UnaryOp(ASTNode):
    """op expr  (e.g., not expr, -expr)"""
    op: str = ''  # 'not', '-'
    operand: Optional[ASTNode] = None


@dataclass
class PostfixOp(ASTNode):
    """expr++  or  expr--"""
    op: str = ''  # '++', '--'
    operand: Optional[ASTNode] = None


@dataclass
class Assignment(ASTNode):
    """target = value  or  target += value  or  target -= value"""
    target: Optional[ASTNode] = None
    op: str = '='  # '=', '+=', '-=', '/=', '^='
    value: Optional[ASTNode] = None


@dataclass
class MemberAccess(ASTNode):
    """object.member"""
    obj: Optional[ASTNode] = None
    member: str = ''


@dataclass
class MethodCall(ASTNode):
    """object.method(args)"""
    obj: Optional[ASTNode] = None
    method: str = ''
    args: List[ASTNode] = field(default_factory=list)


@dataclass
class FunctionCall(ASTNode):
    """func(args), or Scope::func(args) (`Camera::getX()`): `scope` names
    the intrinsic class the call is qualified with, '' when bare."""
    name: str = ''
    args: List[ASTNode] = field(default_factory=list)
    scope: str = ''


@dataclass
class IndexExpr(ASTNode):
    """list[index] — one element of an Item/Number List (1-based)."""
    obj: Optional[ASTNode] = None
    index: Optional[ASTNode] = None


@dataclass
class CreateExpr(ASTNode):
    """var.create(Type, frame)"""
    target: Optional[ASTNode] = None
    type_expr: Optional[ASTNode] = None
    frame_expr: Optional[ASTNode] = None


@dataclass
class DestroyExpr(ASTNode):
    """var.destroy()"""
    target: Optional[ASTNode] = None


@dataclass
class StringList(ASTNode):
    """<<"str1", "str2", ...>>"""
    elements: List[ASTNode] = field(default_factory=list)


@dataclass
class TypeRef(ASTNode):
    """A type reference like TypeMonskul, TypeAbacus, etc."""
    name: str = ''


@dataclass
class ReferentAccess(ASTNode):
    """var.referent  or  referent"""
    obj: Optional[ASTNode] = None
