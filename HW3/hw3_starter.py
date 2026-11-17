"""
AAIN-7001 Foundations of Artificial Intelligence
Homework 3 -- STARTER CODE. Released Thursday Nov 5. Due Monday Nov 30, 11:59 PM.

Write the body of every function marked TODO. Do not change any function's
name or arguments -- the autograder calls them by name.

    python hw3_tests.py        run the public tests (0/17 before you start)
    python hw3_starter.py      print your answers for the PDF once your code works

Parts A, B and C use material from Weeks 8 and 9. Part D (value iteration)
is taught in class on Thursday Nov 12; start it after that class.
Everything in each GIVEN section is yours to read and reuse.
"""

from __future__ import annotations

import itertools
from collections import deque
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

# ===========================================================================
# PART A -- KNOWLEDGE REPRESENTATION (15 points)
# ===========================================================================
# GIVEN: a small university ontology (a semantic network).
#   MEMBER_OF[x] = the category that object x belongs to   (Ali is a GradStudent)
#   SUBSET_OF[c] = the bigger category that category c sits inside (GradStudents are Students)
#   FACTS[c]     = properties stored on category c (or on an object)
# A property is stored once, on the most general place it is true for.
# GradStudents carry an EXCEPTION: they do not pay tuition.

MEMBER_OF: Dict[str, str] = {
    "Ali": "GradStudents", 
    "Bo": "Undergrads", 
    "DrLee": "Professors", 
    "Cy": "TAs",
}
SUBSET_OF: Dict[str, str] = {
    "GradStudents": "Students", 
    "Undergrads": "Students", 
    "Students": "People",
    "Professors": "Employees", 
    "TAs": "Employees", 
    "Employees": "People",
}
FACTS: Dict[str, Dict[str, str]] = {
    "People": {"HasID": "yes", "CanBorrowBooks": "yes"},
    "Students": {"PaysTuition": "yes", "TakesExams": "yes"},
    "GradStudents": {"PaysTuition": "no"},          # exception: overrides Students
    "Employees": {"GetsSalary": "yes", "TakesExams": "no"},
    "Cy": {"CanBorrowBooks": "no"},                 # an exception stored on one object
}


def chain(x: str) -> List[str]:
    """ 
    A1 (4 pts). Return the places to look for x, nearest first.

    Start with x itself. Then follow MEMBER_OF (if x is an object) or SUBSET_OF
    (if x is a category) upward, one link at a time, until there is no parent.
        chain("Ali")      -> ["Ali", "GradStudents", "Students", "People"]
        chain("Students") -> ["Students", "People"]
    """
    returned_chain = [x]
    if x not in MEMBER_OF:
        raise ValueError(f"{x} is not a member")
    subset_name = MEMBER_OF[x]
    returned_chain.append(subset_name)
    while subset_name in SUBSET_OF:
        subset_name = SUBSET_OF[subset_name]
        returned_chain.append(subset_name)
    return returned_chain


def lookup(x: str, prop: str) -> Tuple[str, List[str]]:
    """TODO A2 (7 pts). Inheritance with exceptions.

    Walk chain(x) from nearest to farthest. The FIRST place whose FACTS entry
    contains prop gives the answer. Return (value, trail), where trail lists
    every place you looked at, up to and including the one that answered.
    If no place has the property, return ("unknown", the whole chain).
        lookup("Ali", "PaysTuition") -> ("no", ["Ali", "GradStudents"])
        lookup("Ali", "HasID")       -> ("yes", ["Ali", "GradStudents", "Students", "People"])
    """
    raise NotImplementedError("TODO A2")


def is_a(x: str, category: str) -> bool:
    """TODO A3 (4 pts). True if x is in `category` directly or through any chain of links.
    An object or category is NOT counted as being in itself.
        is_a("Ali", "People") -> True        is_a("Bo", "Employees") -> False
    """
    raise NotImplementedError("TODO A3")


# ===========================================================================
# PART B -- CLASSICAL PLANNING (35 points)   <-- the main implementation part
# ===========================================================================
# GIVEN: a state is a frozenset of facts (strings) that are TRUE. Anything not
# in the set is false (closed world). An action has preconditions, an add list
# and a delete list -- exactly as on the Week 8 slides.

State = FrozenSet[str]


@dataclass(frozen=True)
class Action:
    name: str
    pre: FrozenSet[str]
    add: FrozenSet[str]
    delete: FrozenSet[str]


def make_action(name, pre, add, delete) -> Action:
    return Action(name, frozenset(pre), frozenset(add), frozenset(delete))


def applicable(action: Action, state: State) -> bool:
    """TODO B1 (3 pts). True if EVERY precondition of `action` is in `state`."""
    raise NotImplementedError("TODO B1")


def result(action: Action, state: State) -> State:
    """TODO B2 (4 pts). The new state: remove the delete list, then add the add list.
    Return a frozenset. Do not modify `state` (frozensets cannot be modified anyway)."""
    raise NotImplementedError("TODO B2")


def robot_domain(rooms: List[str], packages: List[str]) -> List[Action]:
    """TODO B3 (8 pts). Build every ground action for a one-handed robot R.

    Facts used:  At(R,<room>)   At(<pkg>,<room>)   Holding(<pkg>)   HandEmpty
    Every room connects directly to every other room.

      Move(a,b)      pre: At(R,a)                          add: At(R,b)                  delete: At(R,a)
      Pick(p,r)      pre: At(R,r), At(p,r), HandEmpty       add: Holding(p)               delete: At(p,r), HandEmpty
      Drop(p,r)      pre: At(R,r), Holding(p)               add: At(p,r), HandEmpty       delete: Holding(p)

    Create one Move for every ordered pair of DIFFERENT rooms, and one Pick and
    one Drop for every (package, room) pair. Names must be written exactly like
    "Move(Office,Lab)", "Pick(P1,Lab)", "Drop(P1,Office)" (no spaces).
    The order of the returned list does not matter.
    """
    raise NotImplementedError("TODO B3")


def forward_bfs(init: State, goal: FrozenSet[str], actions: List[Action]) -> Optional[List[str]]:
    """TODO B4 (12 pts). Forward (progression) planning with breadth-first search.

    Return the SHORTEST plan as a list of action NAMES, e.g.
    ["Move(Office,Mailroom)", "Pick(P1,Mailroom)", ...], or None if no plan exists.
    The goal is reached when every goal fact is in the state (goal <= state).
    Use a reached set so that no state is added to the frontier twice.
    If the start state already satisfies the goal, return [] (an empty plan).
    """
    raise NotImplementedError("TODO B4")


def validate_plan(init: State, goal: FrozenSet[str], actions: List[Action], plan: List[str]) -> bool:
    """TODO B5 (8 pts). Check someone else's plan (for example, one an AI wrote).

    Walk through `plan` one action name at a time, starting from `init`:
      - if a name is not the name of any action in `actions`, the plan is invalid;
      - if the action's preconditions are not all true in the current state, invalid;
      - otherwise apply it.
    At the end, the plan is valid only if every goal fact is in the final state.
    Return True or False.
    """
    raise NotImplementedError("TODO B5")


# GIVEN: the Homework 3 delivery problem (used in the tests and in the PDF questions).
HW_ROOMS = ["Office", "Mailroom", "Lab"]
HW_PACKAGES = ["P1", "P2"]
HW_INIT: State = frozenset({"At(R,Office)", "At(P1,Mailroom)", "At(P2,Lab)", "HandEmpty"})
HW_GOAL: FrozenSet[str] = frozenset({"At(P1,Office)", "At(P2,Mailroom)"})


# ===========================================================================
# PART C -- BAYESIAN NETWORKS (20 points)
# ===========================================================================
# GIVEN: a network is a list of nodes, parents always listed before children.
# Each node is (name, parents, table); table maps a tuple of parent values to
# P(node = True | those parent values). This is the burglar-alarm network
# from the Week 9 slides (R&N Figure 13.2).

Network = List[Tuple[str, Tuple[str, ...], Dict[Tuple[bool, ...], float]]]

ALARM: Network = [
    ("B", (), {(): 0.001}),
    ("E", (), {(): 0.002}),
    ("A", ("B", "E"), {(True, True): 0.95, (True, False): 0.94, (False, True): 0.29, (False, False): 0.001}),
    ("J", ("A",), {(True,): 0.90, (False,): 0.05}),
    ("M", ("A",), {(True,): 0.70, (False,): 0.01}),
]


def p_world(net: Network, world: Dict[str, bool]) -> float:
    """TODO C1 (8 pts). Probability of one COMPLETE world (every node has a value).
    Multiply, for every node, P(node = its value | its parents' values).
    Remember: if the node is False, use 1 - (table number).
        p_world(ALARM, {"B": False, "E": False, "A": True, "J": True, "M": True}) ≈ 0.000628
    """
    raise NotImplementedError("TODO C1")


def enumerate_ask(net: Network, X: str, evidence: Dict[str, bool]) -> float:
    """TODO C2 (12 pts). Inference by enumeration: return P(X = True | evidence).

    1. The hidden variables are all nodes that are neither X nor in `evidence`.
    2. For X = True: add p_world over every combination of hidden values.
       (itertools.product((True, False), repeat=k) gives every combination.)
    3. Do the same for X = False.
    4. Normalise: return the True sum divided by (True sum + False sum).
    (X is never one of the evidence variables in the tests.)
        enumerate_ask(ALARM, "B", {"J": True, "M": True}) ≈ 0.284
    """
    raise NotImplementedError("TODO C2")


# ===========================================================================
# PART D -- MARKOV DECISION PROCESSES (25 points)   -- after the Nov 12 class
# ===========================================================================
# GIVEN: the 4x3 grid world from R&N Figure 17.1.
#   States are (column, row) with (1,1) bottom-left. (2,2) is a wall.
#   (4,3) is a +1 exit, (4,2) is a -1 exit; every other state gives reward r.
#   Actions: "N", "S", "E", "W". The robot moves in the intended direction with
#   probability 0.8, and slips to each side (90 degrees left or right) with 0.1.
#   Bumping into the wall or the edge leaves the robot where it is.

class GridMDP:
    def __init__(self, r: float = -0.04, gamma: float = 1.0):
        self.gamma = gamma
        self.walls = {(2, 2)}
        self.terminals = {(4, 3): 1.0, (4, 2): -1.0}
        self.states = [(c, w) for c in range(1, 5) for w in range(1, 4) if (c, w) not in self.walls]
        self.r = r
        self.moves = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
        self.sides = {"N": ("W", "E"), "S": ("E", "W"), "E": ("N", "S"), "W": ("S", "N")}

    def reward(self, s) -> float:
        return self.terminals.get(s, self.r)

    def actions(self, s) -> List[str]:
        return [] if s in self.terminals else ["N", "S", "E", "W"]

    def _go(self, s, a):
        dx, dy = self.moves[a]
        t = (s[0] + dx, s[1] + dy)
        return t if t in self.states else s

    def transitions(self, s, a) -> List[Tuple[float, Tuple[int, int]]]:
        """List of (probability, next_state) for doing action a in state s."""
        left, right = self.sides[a]
        return [(0.8, self._go(s, a)), (0.1, self._go(s, left)), (0.1, self._go(s, right))]


def value_iteration(mdp: GridMDP, epsilon: float = 1e-6) -> Dict[Tuple[int, int], float]:
    """TODO D1 (17 pts). Return a dict: state -> utility U(s).

    Start with U(s) = 0 for every state. Repeat until no value changes by more
    than epsilon in one round:
        for a terminal state:   U'(s) = reward(s)
        otherwise:              U'(s) = reward(s) + gamma * max over actions a of
                                         sum over (p, s2) in transitions(s, a) of p * U(s2)
    Compute every U'(s) from the OLD U, then replace U by U' (one full round at a time).
    With r = -0.04 and gamma = 1, U[(1,1)] is about 0.705 (R&N Figure 17.3).
    """
    raise NotImplementedError("TODO D1")


def best_policy(mdp: GridMDP, U: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], Optional[str]]:
    """TODO D2 (8 pts). For every non-terminal state, the action with the highest expected
    utility:  sum over (p, s2) in transitions(s, a) of p * U[s2].
    Terminal states map to None. If two actions tie, either is accepted.
    """
    raise NotImplementedError("TODO D2")


# ===========================================================================
# Prints the numbers your PDF answers ask for (run: python hw3_starter.py)
# ===========================================================================
if __name__ == "__main__":
    def safe(label, fn):
        try:
            print(label, fn())
        except NotImplementedError:
            print(label, "-- not implemented yet")
    safe("A: lookup(Cy, CanBorrowBooks) =", lambda: lookup("Cy", "CanBorrowBooks"))
    safe("A: lookup(Cy, TakesExams)     =", lambda: lookup("Cy", "TakesExams"))
    safe("B: plan for the HW problem    =", lambda: forward_bfs(HW_INIT, HW_GOAL, robot_domain(HW_ROOMS, HW_PACKAGES)))
    safe("C: P(E | j, m)                =", lambda: round(enumerate_ask(ALARM, "E", {"J": True, "M": True}), 4))
    safe("C: P(A | b)                   =", lambda: round(enumerate_ask(ALARM, "A", {"B": True}), 4))
    def d():
        out = []
        for r in (-0.04, -0.4, -2.0):
            m = GridMDP(r=r); U = value_iteration(m); pi = best_policy(m, U)
            out.append(f"r={r}: U(1,1)={U[(1, 1)]:.3f}, action at (3,1)={pi[(3, 1)]}, at (3,2)={pi[(3, 2)]}")
        return "\n   " + "\n   ".join(out)
    safe("D: value iteration            =", d)
