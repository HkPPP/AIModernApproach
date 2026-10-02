"""
AAIN-7001 Foundations of Artificial Intelligence
Homework 2 -- STARTER CODE. Due Thursday Oct 15, 6:00 PM.

Fill in every function marked TODO. Do not change any function's name or
arguments -- the autograder calls them by name.

    python hw2_tests.py        run the public tests (0/13 before you start)
    python hw2_starter.py      print the Part D table once Part C works

Everything in the GIVEN section is yours to read and reuse. Read
uniform_cost_search first: astar_search is that function with one change.
"""

from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional


# ===========================================================================
# GIVEN -- do not modify this section
# ===========================================================================


class Problem:
    """The five components of a search problem (R&N Section 3.1.1)."""

    def __init__(self, initial: Any, goal: Any = None) -> None:
        self.initial = initial
        self.goal = goal

    def actions(self, state: Any) -> Iterable[Any]:
        raise NotImplementedError

    def result(self, state: Any, action: Any) -> Any:
        raise NotImplementedError

    def is_goal(self, state: Any) -> bool:
        return state == self.goal

    def action_cost(self, state: Any, action: Any, next_state: Any) -> float:
        return 1.0


@dataclass
class Node:
    state: Any
    parent: Optional["Node"] = None
    action: Any = None
    path_cost: float = 0.0
    depth: int = field(default=0)


def expand(problem: Problem, node: Node) -> Iterable[Node]:
    s = node.state
    for action in problem.actions(s):
        s2 = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s2)
        yield Node(s2, node, action, cost, node.depth + 1)


def solution_states(node: Optional[Node]) -> list:
    """States from the start to this node, in order."""
    out = []
    while node is not None:
        out.append(node.state)
        node = node.parent
    return list(reversed(out))


class Counters:
    """Instrumentation. 'expanded' counts nodes whose children were generated."""

    def __init__(self) -> None:
        self.expanded = 0
        self.generated = 0


class RouteProblem(Problem):
    """Find a cheapest route on a directed weighted graph.

    graph: {state: [(neighbour, cost), ...]}
    """

    def __init__(self, graph: Dict[str, list], initial: str, goal: str) -> None:
        super().__init__(initial, goal)
        self.graph = graph

    def actions(self, state):
        return [n for n, _ in self.graph.get(state, [])]

    def result(self, state, action):
        return action

    def action_cost(self, state, action, next_state):
        for n, c in self.graph[state]:
            if n == next_state:
                return c
        raise ValueError(f"no edge {state}->{next_state}")


class EightPuzzleProblem(Problem):
    """The 8-puzzle -- IDENTICAL to Homework 1, so your numbers match lecture.

    A state is a 9-tuple of 0-8 in row-major order; 0 is the blank.
    Goal: (0, 1, 2, 3, 4, 5, 6, 7, 8). Actions move the BLANK. Each costs 1.
    """

    GOAL = (0, 1, 2, 3, 4, 5, 6, 7, 8)

    def __init__(self, initial, goal=GOAL):
        super().__init__(tuple(initial), tuple(goal))

    DELTA = {"Down": 3, "Left": -1, "Right": 1, "Up": -3}

    def actions(self, state):
        blank = state.index(0)
        row, col = divmod(blank, 3)
        acts = []
        if row > 0:
            acts.append("Up")
        if row < 2:
            acts.append("Down")
        if col > 0:
            acts.append("Left")
        if col < 2:
            acts.append("Right")
        return sorted(acts)

    def result(self, state, action):
        blank = state.index(0)
        target = blank + self.DELTA[action]
        tiles = list(state)
        tiles[blank], tiles[target] = tiles[target], tiles[blank]
        return tuple(tiles)

    def action_cost(self, state, action, next_state):
        return 1.0


def uniform_cost_search(problem: Problem, counters: Counters = None) -> Optional[Node]:
    """GIVEN as a worked example. A* is this function with one change."""
    counters = counters or Counters()
    tie = itertools.count()
    start = Node(problem.initial)
    frontier = [(0.0, next(tie), start)]
    best_g = {problem.initial: 0.0}
    while frontier:
        g, _, node = heapq.heappop(frontier)
        if g > best_g.get(node.state, float("inf")):
            continue                                  # stale copy
        if problem.is_goal(node.state):
            return node                               # goal test ON POP
        counters.expanded += 1
        for child in expand(problem, node):
            counters.generated += 1
            if child.path_cost < best_g.get(child.state, float("inf")):
                best_g[child.state] = child.path_cost
                heapq.heappush(frontier, (child.path_cost, next(tie), child))
    return None


# ------------------- the practice graph from lecture slide 30 -------------------

PRACTICE_GRAPH = {
    "S": [("X", 1), ("Y", 4)],
    "X": [("Y", 2), ("G", 12)],
    "Y": [("G", 3)],
    "G": [],
}
PRACTICE_H = {"S": 5, "X": 4, "Y": 3, "G": 0}


# --------------------------- CSP scaffolding --------------------------------


class CSP:
    """A map-colouring style CSP: every constraint is 'neighbours differ'."""

    def __init__(self, variables: List[str], domains: Dict[str, List[str]],
                 neighbors: Dict[str, List[str]]) -> None:
        self.variables = list(variables)
        self.domains = {v: list(d) for v, d in domains.items()}
        self.neighbors = {v: list(n) for v, n in neighbors.items()}
        self.assignments_tried = 0                     # instrumentation


NEW_ENGLAND_NEIGHBORS = {
    "ME": ["NH"],
    "NH": ["ME", "VT", "MA"],
    "VT": ["NH", "MA", "NY"],
    "MA": ["NH", "VT", "NY", "CT", "RI"],
    "CT": ["MA", "RI", "NY"],
    "RI": ["MA", "CT"],
    "NY": ["VT", "MA", "CT"],
}


def new_england_csp(colors: List[str]) -> CSP:
    vs = list(NEW_ENGLAND_NEIGHBORS)
    return CSP(vs, {v: list(colors) for v in vs}, NEW_ENGLAND_NEIGHBORS)


# ===========================================================================
# PART C -- heuristics and search
# ===========================================================================


def misplaced_tiles(state: tuple, goal: tuple = EightPuzzleProblem.GOAL) -> int:
    """
    h1: number of non-blank tiles not in their goal square.
    (Part C1). Count non-blank tiles that are not in their goal square.
    Do NOT count the blank -- that would let h overestimate by one.
    """
    count = sum([1 for c, g in zip(state, goal) if c != g])
    return count - 1 if count else 0


def manhattan_distance(state: tuple, goal: tuple = EightPuzzleProblem.GOAL) -> int:
    """
    h2: sum over non-blank tiles of |row - goal row| + |col - goal col|.
    Hint: square i is at row i // 3, column i % 3.
    """
    
    # S: [4,0,1,2,3,8,5,6,7]
    # G: [3,2,4,5,7,1,9,3,0]
    distance = 0
    goal_to_index = { i: n for i, n in enumerate(goal)}
    for i, n in enumerate(state):
        if n == 0:
            continue
        s_row, s_col = divmod(i, 3)
        g_row, g_col = divmod(goal_to_index[n], 3)

        distance += abs(s_row - g_row) + abs(s_col - g_col)

    return distance




def astar_search(problem: Problem, h: Callable[[Any], float],
                 counters: Counters = None) -> Optional[Node]:
    """
    A* graph search. Priority f = g + h. Goal test on POP.

    Re-adds a state whenever a strictly cheaper path to it is found, so it is
    optimal with any admissible h.
    (Part C3). Copy uniform_cost_search and change ONE thing:
    the number you push onto the heap is g + h(state), not g.
    Keep: the tiebreak counter, the best_g table, the stale-copy skip,
    and the goal test ON POP. Count counters.expanded exactly as UCS does.
    """
    counters = counters or Counters()
    frontier = []
    tiebreak = itertools.count()

    node = Node(state=problem.initial)
    counters.generated += 1
    # f = g + h(state) where g is path_cost and h is the hueristic, but g is 0 initially
    f = h(node.state)
    heapq.heappush(frontier, (f, next(tiebreak), node))
    reached = {node.state: f}

    while frontier:
        cost, _, node = heapq.heappop(frontier)

        if cost > reached[node.state]:
            continue

        if problem.is_goal(node.state):
            return node

        counters.expanded += 1
        for child in expand(problem, node):
            counters.generated += 1
            f = child.path_cost + h(child.state)
            if child.state not in reached or f < reached[child.state]:
                reached[child.state] = f
                heapq.heappush(frontier, (f, next(tiebreak), child))
    return None



def greedy_best_first_search(problem: Problem, h: Callable[[Any], float],
                             counters: Counters = None) -> Optional[Node]:
    """
    Greedy best-first graph search. Priority f = h only. Goal test on POP.
    TODO (Part C4). Like astar_search, but the priority is h(state) ONLY.
    Use a `reached` set so a state is only ever pushed once.
    Test the goal when a node is popped.
    """
    counters = counters or Counters()
    tiebreak = itertools.count()
    frontier = []

    node = Node(problem.initial)
    counters.generated += 1
    f = h(node.state)
    heapq.heappush(frontier, (f, tiebreak, node))
    reached = {node.state: f}

    while frontier:
        cost, _, node = heapq.heappop(frontier)
        if cost > reached[node.state]:
            continue

        if problem.is_goal(node.state):
            return node

        counters.expanded += 1
        for child in expand(problem, node):
            counters.generated += 1
            f = h(child.state)
            if child.state not in reached or f < reached[child.state]:
                reached[child.state] = f
                heapq.heappush(frontier, (f, tiebreak, child))
    return None
    


# ===========================================================================
# PART E -- constraint satisfaction
# ===========================================================================


def is_consistent(csp: CSP, var: str, value: str, assignment: Dict[str, str]) -> bool:
    """True if giving `var` this `value` breaks no constraint with assigned neighbours."""
    # TODO (Part E2). Return False if any ALREADY-ASSIGNED neighbour of `var`
    # has the same value; otherwise True. Unassigned neighbours never conflict.
    raise NotImplementedError("is_consistent")


def backtracking_search(csp: CSP) -> Optional[Dict[str, str]]:
    """Plain backtracking: variables in csp.variables order, values in domain order."""
    # TODO (Part E3). Recursive backtracking:
    #   - if every variable is assigned, return a copy of the assignment
    #   - pick the FIRST unassigned variable in csp.variables order
    #   - try each value in csp.domains[var], in order:
    #       add 1 to csp.assignments_tried
    #       if is_consistent(...): assign it, recurse, return the result if
    #       it is not None, otherwise un-assign and try the next value
    #   - if no value works, return None
    raise NotImplementedError("backtracking_search")


# ===========================================================================


def run_experiments() -> None:
    """Part D. Prints the table students report."""
    instances = [
        (1, 5, 4, 3, 2, 8, 6, 7, 0),
        (0, 4, 1, 3, 2, 5, 6, 7, 8),
        (7, 6, 2, 4, 1, 3, 0, 5, 8),
    ]
    print(f"{'start':28s} {'depth':>5} {'UCS':>8} {'A* h1':>8} {'A* h2':>8}")
    for s in instances:
        row = []
        depth = None
        for algo in ("ucs", "h1", "h2"):
            c = Counters()
            p = EightPuzzleProblem(s)
            if algo == "ucs":
                n = uniform_cost_search(p, c)
            else:
                n = astar_search(p, misplaced_tiles if algo == "h1" else manhattan_distance, c)
            depth = n.depth
            row.append(c.expanded)
        print(f"{str(s):28s} {depth:5d} {row[0]:8d} {row[1]:8d} {row[2]:8d}")


if __name__ == "__main__":
    run_experiments()
