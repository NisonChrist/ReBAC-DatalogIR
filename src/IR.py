from enum import Enum

"""
a ∈ Const
X ∈ Va
p ∈ PredicateSym
t ∈ Term ::= a | X
A ∈ Atom ::= p | p(t, ..., t)
φ ∈ Premise ::= A | not A | t = t | t != t
C ∈ Clause ::= A. | A :- φ, ..., φ.

a 属于常量集
X 属于变量集
p 属于谓词符号集
t 属于项集，定义为：t 等于 a 或 X
A 属于原子公式集，定义为：A 等于 p，或 A 等于 p(t, ..., t)
φ 属于前提集，定义为：φ 等于 A、非 A、t = t 或 t ≠ t
C 属于子句集，定义为：C 等于 A.（事实），或 C 等于 A :- φ, ..., φ.（规则）

a ∈ 常量
X ∈ 变量
p ∈ 谓词符号
t ∈ 项 ::= a | X
A ∈ 原子 ::= p | p(t, ..., t)
φ ∈ 前提 ::= A | 非A | t = t | t != t
C ∈ 子句 ::= A. | A :- φ, ..., φ.
"""


class DatalogIRToken(Enum):
    Const = "Const"
    Var = "Var"
    PredicateSym = "PredicateSym"
    Term = "Term"
    Atom = "Atom"
    Premise = "Premise"
    Clause = "Clause"
