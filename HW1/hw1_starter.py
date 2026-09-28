"""
AAIN-7001 Foundations of Artificial Intelligence
Homework 1, Part C -- problem formulation and uninformed search.

Fill in every function marked TODO. Do not rename anything: the autograder
imports these names exactly as written.

Run the public tests with:      python hw1_tests.py
Run your own experiments with:  python hw1_starter.py

You may import only from the Python standard library.
"""

from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional


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
    state: Any = None
    parent: Optional["Node"] = field(default=None, repr=False)
    action: Any = None
    path_cost: float = 0.0
    depth: int = 0


def expand(problem: Problem, node: Node) -> Iterable[Node]:
    s = node.state
    for action in problem.actions(s):
        s2 = problem.result(s, action)
        yield Node(
            state=s2,
            parent=node,
            action=action,
            path_cost=node.path_cost + problem.action_cost(s, action, s2),
            depth=node.depth + 1,
        )


def solution_actions(node: Optional[Node]) -> list:
    """The action sequence from the root to node. Search returns THIS."""
    actions = []
    while node is not None and node.parent is not None:
        actions.append(node.action)
        node = node.parent
    return list(reversed(actions))


class Counters:
    """Node accounting. The autograder checks these are updated."""

    def __init__(self) -> None:
        self.generated = 0
        self.expanded = 0


def breadth_first_search(problem: Problem, counters: Counters = None):
    """WORKED EXAMPLE. Study this before writing the other two.

    Returns the goal Node, or None if no solution exists.
    """
    counters = counters or Counters()
    node = Node(state=problem.initial)
    counters.generated += 1
    if problem.is_goal(node.state):
        return node

    frontier = deque([node])
    reached = {problem.initial}

    while frontier:
        # print(f"Frontier: { list(frontier) }")  # DEBUG
        # print(f"Reached: { reached }")  # DEBUG
        node = frontier.popleft()
        counters.expanded += 1
        for child in expand(problem, node):
            counters.generated += 1
            s = child.state
            if problem.is_goal(s):
                return child
            if s not in reached:
                reached.add(s)
                frontier.append(child)
    return None


# ===========================================================================
# TODO -- your work starts here
# ===========================================================================


class VacuumProblem(Problem):
    """The two-square vacuum world from Week 1.

    A state is a tuple: (agent_location, status_of_A, status_of_B) where
    agent_location is 'A' or 'B' and each status is 'Clean' or 'Dirty'.

    Actions are 'Left', 'Right', 'Suck'.
      - 'Left' in 'A' and 'Right' in 'B' are NOT applicable (do not include
        no-op actions in actions()).
      - 'Suck' is applicable in every state, even a clean one.

    Costs: 'Suck' costs 1. Moving costs 2 (the motor is expensive).
    The goal is any state in which both squares are Clean.
    """

    def __init__(self, initial=("A", "Dirty", "Dirty")):
        super().__init__(initial)
        self.action_map = {
            # TODO: still works?
            # "Suck": "Clean",
            # "Right": "A",       # Going from B -> A
            # "Left": "B",        # Going from A -> B
            "A": "Right",       # At A, allows Right
            "B": "Left"         # At B, allows Left
        }

    @staticmethod
    def _get_area_index(area):
        """
        Return area index of '1' if area is 'A', and '2' if area is 'B'
        """
        return 1 if area =="A" else 2

    def actions(self, state):
        """
        Actions are 'Left', 'Right', 'Suck'.
        - 'Left' in 'A' and 'Right' in 'B' are NOT applicable (do not include
            no-op actions in actions()).
        - 'Suck' is applicable in every state, even a clean one.
        """
        applicable_actions = ["Suck"]
        applicable_actions.append(self.action_map[state[0]])
        return sorted(applicable_actions)
        

    def result(self, state, action):
        """
        The result of the action based on the current agent's state.

        Original 'state' variable is not modified
        """
        res_state = list(state)
        i = VacuumProblem._get_area_index(state[0])
        if action == "Suck":
            res_state[i] = "Clean"
        elif action == "Right":
            res_state[0] = "B"
        elif action == "Left":
            res_state[0] = "A"
        return tuple(res_state)

    def is_goal(self, state):
        """
        Area 'A' and 'B' are clean
        """
        return bool(state[1] == "Clean" and state[2] == "Clean")

    def action_cost(self, state, action, next_state):
        """
        1 for 'Suck', 2 for a move.
        """
        return 1.0 if action == "Suck" else 2.0

class EightPuzzleProblem(Problem):
    """The 8-puzzle from Week 2.

    A state is a 9-tuple of the integers 0-8 read in row-major order, where 0
    is the blank. For example the goal state is (0, 1, 2, 3, 4, 5, 6, 7, 8).

    Actions move the BLANK, not a tile: 'Up', 'Down', 'Left', 'Right'.
    Only actions that keep the blank on the board are applicable.
    Every action costs 1.
    """

    GOAL = (0, 1, 2, 3, 4, 5, 6, 7, 8)

    def __init__(self, initial, goal=GOAL):
        super().__init__(initial, goal)
        self.col_left_right_moves = {
            0: ['Right'],
            1: ['Left', 'Right'],
            2: ['Left']
        }
        self.row_up_down_moves = {
            0: ['Down'],
            1: ['Up', 'Down'],
            2: ['Up']
        }
        self.move_index_value = {
            'Up': -3,
            'Down': 3,
            'Left': -1,
            'Right': 1
        }

    @staticmethod
    def is_illegal_move(state, action):
        row, col = divmod(state.index(0), 3)

        return bool((action == 'Up' and row == 0) 
                    or (action == 'Down' and row == 2) 
                    or (action == 'Left' and col == 0) 
                    or (action == 'Right' and col == 2))

        
    def actions(self, state):
        """
        Return the applicable blank moves, sorted alphabetically.
        """
        row, col = divmod(state.index(0), 3)
        moves = self.col_left_right_moves[col] + self.row_up_down_moves[row]
        # print(f"For {row, col}, moves are: {moves}")
        return sorted(moves)
        

    def result(self, state, action):
        """
        Swap the blank with its neighbour and return a new tuple.

        Actions move the BLANK, not a tile: 'Up', 'Down', 'Left', 'Right'.

        Only actions that keep the blank on the board are applicable.
        """
        if self.is_illegal_move(state, action):
            return state 
        new_state = list(state)

        current_index = new_state.index(0)
        new_index = current_index + self.move_index_value[action]            
        new_state[current_index], new_state[new_index] = new_state[new_index], new_state[current_index]
        return tuple(new_state)

    def action_cost(self, state, action, next_state):
        return 1.0


def is_solvable(state: tuple) -> bool:
    """Return True if `state` can reach EightPuzzleProblem.GOAL.

    Exactly half of the 9! arrangements are reachable from any given state.
    Count inversions among the eight numbered tiles, ignoring the blank: two
    states are mutually reachable if and only if their inversion counts have
    the same parity.

    TODO: implement this. Without it, an unsolvable input still terminates,
    but only after your search has exhausted all 181,440 reachable states.
    """
    tiles = [t for t in state if t != 0]
    inversions = 0

    for i in range(len(tiles)-1):
        for j in range(i+1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions % 2 == 0


def uniform_cost_search(problem: Problem, counters: Counters = None):
    """ 
    Best-first search with f(n) = n.path_cost.

    Requirements the autograder checks:
      - the goal test happens when a node is POPPED, not when it is generated;
      - a state already in `reached` is re-added to the frontier only when the
        new path to it is strictly cheaper;
      - `counters.generated` counts every Node you construct, and
        `counters.expanded` counts every node you pop and expand.

    Hint: heapq cannot compare Node objects. Push tuples of the form
    (priority, tiebreak_int, node) using itertools.count() for the tiebreak.
    """

    counters = counters or Counters()
    node = Node(state=problem.initial)
    counters.generated += 1


    frontier = []
    tiebreak_int = itertools.count()
    heapq.heappush(frontier, (node.path_cost, next(tiebreak_int), node))
    reached = {problem.initial: node.path_cost}

    while frontier:
        # print(f"Frontier: { list(frontier) }")  # DEBUG
        # print(f"Reached: { reached }")  # DEBUG
        cost, tbi, node = heapq.heappop(frontier)

        if cost > reached[node.state]:
            continue

        if problem.is_goal(node.state):
            return node

        counters.expanded += 1
        for child in expand(problem, node):
            counters.generated += 1

            if child.state not in reached or child.path_cost < reached[child.state]:
                reached[child.state] = child.path_cost
                heapq.heappush(frontier, (child.path_cost, next(tiebreak_int), child))
    return None

    
def is_cycle(node: Node) -> bool:
    """Iteratively walk parent pointers back to the root to detect cycles."""
    curr = node.parent
    while curr is not None:
        if node.state == curr.state:
            return True
        curr = curr.parent
    return False
    
def depth_limited_search(problem: Problem, limit: int, counters: Counters = None):
    """
    Depth-first search with a cutoff.

    Return the goal Node if found, the string "cutoff" if the search was
    truncated by the depth limit, or None if the space was exhausted without
    reaching the limit.

    Include a cycle check against the CURRENT PATH only (walk the parent
    pointers). Do not keep a full reached table -- that would throw away the
    memory advantage that is the only reason to use depth-first search.
    """
    counters = counters or Counters()
    root = Node(state=problem.initial)
    counters.generated += 1

    def recursive_dls(node: Node):
        if problem.is_goal(node.state):
            return node
        if node.depth == limit:
            return "cutoff"

        counters.expanded += 1
        cutoff_occurred = False

        for child in expand(problem, node):
            counters.generated += 1
            if is_cycle(child):
                continue

            result = recursive_dls(child)
            if result == "cutoff":
                cutoff_occurred = True
            elif result is not None:
                return result  # Goal found

        return "cutoff" if cutoff_occurred else None

    return recursive_dls(root)



def iterative_deepening_search(problem: Problem, counters: Counters = None,
                               max_limit: int = 40):
    """TODO: call depth_limited_search with limit 0, 1, 2, ... until it returns
    something other than "cutoff". Return that result (a Node or None).

    Accumulate counters across all iterations -- the whole point of the
    analysis in Part D is the total node count, not the count of the last pass.
    """
    counters = counters or Counters()
    for i in range(max_limit+1):
        result = depth_limited_search(problem, i, counters)
        if result != "cutoff":
            return result
    return None


# ===========================================================================
# Part D -- experiment harness (given; you write the analysis, not the code)
# ===========================================================================

TEST_PUZZLES = [
    (1, 0, 2, 3, 4, 5, 6, 7, 8),        # optimal depth 1
    (3, 1, 2, 4, 0, 5, 6, 7, 8),        # optimal depth 2
    (3, 1, 2, 4, 5, 0, 6, 7, 8),        # optimal depth 3
    (1, 2, 5, 3, 4, 8, 6, 0, 7),        # optimal depth 5
    (1, 2, 5, 6, 3, 8, 0, 4, 7),        # optimal depth 8 -- watch the counts
    (4, 1, 2, 3, 0, 5, 6, 7, 8),        # UNSOLVABLE -- is_solvable() saves a 181,440-state sweep
]


def run_experiments() -> None:
    algorithms = [
        ("BFS", breadth_first_search),
        ("UCS", uniform_cost_search),
        ("IDS", iterative_deepening_search),
    ]
    header = f"{'puzzle':<8}{'algorithm':<12}{'len':<6}{'cost':<8}{'expanded':<11}{'generated':<11}"
    print(header)
    print("-" * len(header))
    for i, puzzle in enumerate(TEST_PUZZLES, start=1):
        if not is_solvable(puzzle):
            print(f"{i:<8}unsolvable -- skipped")
            continue
        for name, algo in algorithms:
            counters = Counters()
            node = algo(EightPuzzleProblem(puzzle), counters=counters)
            if node is None:
                print(f"{i:<8}{name:<12}{'-- no solution --'}")
                continue
            actions = solution_actions(node)
            print(f"{i:<8}{name:<12}{len(actions):<6}{node.path_cost:<8g}"
                  f"{counters.expanded:<11}{counters.generated:<11}")
        print()


if __name__ == "__main__":
    run_experiments()
