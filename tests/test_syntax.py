"""Tests for the DatalogIR syntax checker."""

import sys

sys.path.insert(0, ".")

from src import check_syntax, LexerError, SyntaxError, Fact, Rule, Query

passed = 0
failed = 0


def ok(label: str):
    global passed
    passed += 1
    print(f"  ✓ {label}")


def fail(label: str, detail: str = ""):
    global failed
    failed += 1
    print(f"  ✗ {label} — {detail}")


# ── Valid programs ──────────────────────────────────

print("Valid programs:")

try:
    p = check_syntax("edge(a,b).")
    assert len(p.clauses) == 1 and isinstance(p.clauses[0], Fact)
    ok("simple fact")
except Exception as e:
    fail("simple fact", str(e))

try:
    p = check_syntax("tc(X,Y) :- edge(X,Y).")
    assert len(p.clauses) == 1 and isinstance(p.clauses[0], Rule)
    ok("simple rule")
except Exception as e:
    fail("simple rule", str(e))

try:
    p = check_syntax("tc(a,X)?")
    assert len(p.clauses) == 1 and isinstance(p.clauses[0], Query)
    ok("query")
except Exception as e:
    fail("query", str(e))

try:
    p = check_syntax("in_cycle(X) :- tc(X,Y), X=Y.")
    assert isinstance(p.clauses[0], Rule)
    ok("equality premise")
except Exception as e:
    fail("equality premise", str(e))

try:
    p = check_syntax("d(X,Y) :- tc(X,Y), X!=Y.")
    ok("inequality premise")
except Exception as e:
    fail("inequality premise", str(e))

try:
    p = check_syntax("p(X) :- q(X), not r(X).")
    ok("negation premise")
except Exception as e:
    fail("negation premise", str(e))

try:
    p = check_syntax("node(X) :- edge(X,_).")
    ok("wildcard term")
except Exception as e:
    fail("wildcard term", str(e))

try:
    p = check_syntax("p.")
    assert isinstance(p.clauses[0], Fact) and p.clauses[0].head.predicate == "p"
    ok("propositional fact (no args)")
except Exception as e:
    fail("propositional fact", str(e))

try:
    source = open("examples/tc.dlir").read()
    p = check_syntax(source)
    assert len(p.clauses) == 14
    ok(f"tc.dlir ({len(p.clauses)} clauses)")
except Exception as e:
    fail("tc.dlir", str(e))

# ── Invalid programs ───────────────────────────────

print("\nInvalid programs (should raise errors):")

try:
    check_syntax("edge(a,b)")
    fail("missing dot", "no error raised")
except SyntaxError:
    ok("missing dot")
except Exception as e:
    fail("missing dot", str(e))

try:
    check_syntax("edge(a,b) @")
    fail("bad token @", "no error raised")
except LexerError:
    ok("bad token @")
except Exception as e:
    fail("bad token @", str(e))

try:
    check_syntax("edge(a,b.")
    fail("missing rparen", "no error raised")
except SyntaxError:
    ok("missing rparen")
except Exception as e:
    fail("missing rparen", str(e))

try:
    check_syntax("Edge(a,b).")
    fail("uppercase head", "no error raised")
except SyntaxError:
    ok("uppercase head rejected")
except Exception as e:
    fail("uppercase head", str(e))

try:
    check_syntax("p(X) :- .")
    fail("empty body", "no error raised")
except SyntaxError:
    ok("empty body rejected")
except Exception as e:
    fail("empty body", str(e))

try:
    check_syntax("p(X) :- q(X),.")
    fail("trailing comma", "no error raised")
except SyntaxError:
    ok("trailing comma rejected")
except Exception as e:
    fail("trailing comma", str(e))

# ── Summary ────────────────────────────────────────

print(f"\n{'=' * 40}")
print(f"Results: {passed} passed, {failed} failed")
if failed:
    sys.exit(1)
