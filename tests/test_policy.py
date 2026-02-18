import sys

sys.path.insert(0, ".")
from src.IR import check_syntax

"""
This test checks that the syntax of a more complex program is accepted by the parser.

The program models a simple social network with users, photos, and friendships. It defines rules for who can read which photos based on ownership and friendship.

The test will pass if the program is parsed without any syntax errors, and fail if any syntax errors are raised.
"""
p = check_syntax("""github_user(x).
repo(y).
owner_of(x, y).
access(X, Y) :- github_user(X), repo(Y), owner_of(X, Y).""")
