# ReBAC-DatalogIR

> Thinking everything is Relation, and then doing Datalog IR on top of it.

## Syntax and Grammar

Support for constants, variables, predicate symbols, terms, atoms, premises, and clauses. The syntax is defined as follows:

a ∈ Const

X ∈ Var

p ∈ PredicateSym

t ∈ Term ::= a | X

A ∈ Atom ::= p | p(t, ..., t)

φ ∈ Premise ::= A | not A | t = t | t != t

C ∈ Clause ::= A. | A :- φ, ..., φ. 

## Case Study: ReBAC Policy

We can represent a ReBAC policy using DatalogIR: 
```json
{
    "datalog_subsets": "<Atoms>",
    "datalog_objects": "<Atoms>",
    "datalog_relationships": "<Atoms/Clauses>",
    "datalog_actions": "<Clauses>"
}
```

Consider a ReBAC policy that defines access control based on relationships between users and resources. For example, we can have a policy that states:
- A github user can access a repo if he/she is the owner of the repo.

```
github_user(x).
repo(y).
owner_of(x, y).
access(X, Y) :- github_user(X), repo(Y), owner_of(X, Y).
```

- A user can access the photo if he/she is a friend of the owner of the photo.

```
user(x).user(y).
photo(z).
friend_of(x, y). owner_of(y, z).
access(X, Z) :- user(X), photo(Z), friend_of(X, Y), owner_of(Y, Z).
```
