"""
AAIN-7001 Homework 2 -- PUBLIC TESTS.

Run:  python hw2_tests.py

These are the tests you can see. The grading run includes additional hidden
tests of the same kind -- including graphs with unequal costs where stopping
on generation gives the wrong answer. Passing everything here is necessary
but not sufficient.

Do not modify this file. It is replaced with a fresh copy at grading time.
"""

import sys
import traceback

import hw2_starter as hw

PASSED = 0
FAILED = 0


def check(name, fn):
    global PASSED, FAILED
    try:
        fn()
    except NotImplementedError:
        FAILED += 1
        print(f"  [ TODO ] {name}: not implemented yet")
    except AssertionError as exc:
        FAILED += 1
        print(f"  [ FAIL ] {name}: {exc}")
    except Exception:
        FAILED += 1
        print(f"  [ERROR ] {name}:")
        traceback.print_exc(limit=2)
    else:
        PASSED += 1
        print(f"  [  ok  ] {name}")


EXAMPLE = (1, 5, 4, 3, 2, 8, 6, 7, 0)      # the state from lecture slide 25
DEPTH14 = (0, 4, 1, 3, 2, 5, 6, 7, 8)


def route():
    return hw.RouteProblem(hw.PRACTICE_GRAPH, "S", "G")


def h_b(s):
    return hw.PRACTICE_H[s]


# ---------------------------------------------------------------- Part C1-C2


def t_misplaced_goal():
    assert hw.misplaced_tiles(hw.EightPuzzleProblem.GOAL) == 0, "goal state must score 0"


def t_misplaced_example():
    got = hw.misplaced_tiles(EXAMPLE)
    assert got == 5, f"expected 5 (tiles 1,2,4,5,8 misplaced), got {got}. Are you counting the blank?"


def t_manhattan_example():
    got = hw.manhattan_distance(EXAMPLE)
    assert got == 8, f"expected 8 (1+2+2+2+1), got {got}"


def t_dominance():
    states = [EXAMPLE, DEPTH14, (7, 6, 2, 4, 1, 3, 0, 5, 8), (8, 7, 6, 5, 4, 3, 2, 1, 0)]
    for s in states:
        h1, h2 = hw.misplaced_tiles(s), hw.manhattan_distance(s)
        assert h2 >= h1, f"Manhattan must dominate misplaced tiles; failed on {s}: h1={h1}, h2={h2}"


# ---------------------------------------------------------------- Part C3-C4


def t_astar_route_cost():
    n = hw.astar_search(route(), h_b)
    assert n is not None, "A* returned None on a solvable graph"
    assert n.path_cost == 6, f"expected cost 6, got {n.path_cost}"


def t_astar_stops_on_pop():
    n = hw.astar_search(route(), h_b)
    path = hw.solution_states(n)
    assert path == ["S", "X", "Y", "G"], (
        f"expected S-X-Y-G, got {'-'.join(path)}. If you got S-X-G at cost 13, "
        "you stopped when G was GENERATED. Test the goal when a node is POPPED.")


def t_astar_h0_is_ucs():
    n = hw.astar_search(route(), lambda s: 0)
    assert n is not None and n.path_cost == 6, "A* with h = 0 must behave exactly like UCS"


def t_greedy_route():
    n = hw.greedy_best_first_search(route(), h_b)
    path = hw.solution_states(n)
    assert path == ["S", "Y", "G"] and n.path_cost == 7, (
        f"greedy should follow the smallest h and return S-Y-G at cost 7; got "
        f"{'-'.join(path)} at {n.path_cost}")


def t_astar_8puzzle_optimal():
    for s in (EXAMPLE, DEPTH14):
        a = hw.astar_search(hw.EightPuzzleProblem(s), hw.manhattan_distance)
        u = hw.uniform_cost_search(hw.EightPuzzleProblem(s))
        assert a.depth == u.depth, f"A* found depth {a.depth}, optimal is {u.depth} for {s}"


def t_astar_saves_work():
    cu, ca = hw.Counters(), hw.Counters()
    hw.uniform_cost_search(hw.EightPuzzleProblem(DEPTH14), cu)
    hw.astar_search(hw.EightPuzzleProblem(DEPTH14), hw.manhattan_distance, ca)
    assert ca.expanded > 0, "counters.expanded was never incremented in astar_search"
    assert ca.expanded < cu.expanded / 5, (
        f"A* with Manhattan should expand far fewer nodes than UCS; got {ca.expanded} vs {cu.expanded}")


# ---------------------------------------------------------------- Part E


def t_is_consistent():
    c = hw.new_england_csp(["red", "green", "blue"])
    assert hw.is_consistent(c, "MA", "red", {"NH": "green"}), "red next to green should be allowed"
    assert not hw.is_consistent(c, "MA", "red", {"NH": "red"}), "MA and NH are neighbours; both red must fail"
    assert hw.is_consistent(c, "ME", "red", {"MA": "red"}), "ME and MA are NOT neighbours"


def t_csp_three_colours():
    c = hw.new_england_csp(["red", "green", "blue"])
    a = hw.backtracking_search(c)
    assert a is not None, "New England is 3-colourable; backtracking returned None"
    assert set(a) == set(c.variables), f"not every state was assigned: {sorted(a)}"
    for v in c.variables:
        for n in c.neighbors[v]:
            assert a[v] != a[n], f"{v} and {n} are neighbours but both are {a[v]}"


def t_csp_two_colours():
    c = hw.new_england_csp(["red", "green"])
    assert hw.backtracking_search(c) is None, (
        "two colours are NOT enough (MA, CT and RI all touch each other); expected None")


TESTS = [
    ("C1 misplaced tiles: goal scores 0", t_misplaced_goal),
    ("C1 misplaced tiles: lecture example = 5", t_misplaced_example),
    ("C2 Manhattan: lecture example = 8", t_manhattan_example),
    ("C2 Manhattan dominates misplaced tiles", t_dominance),
    ("C3 A*: lecture practice graph costs 6", t_astar_route_cost),
    ("C3 A*: does not stop when the goal is generated", t_astar_stops_on_pop),
    ("C3 A*: with h = 0 it is UCS", t_astar_h0_is_ucs),
    ("C4 greedy: follows h to cost 7", t_greedy_route),
    ("C3 A*: optimal on the 8-puzzle", t_astar_8puzzle_optimal),
    ("C3 A*: expands far fewer nodes than UCS", t_astar_saves_work),
    ("E2 is_consistent", t_is_consistent),
    ("E3 backtracking: 3 colours, valid map", t_csp_three_colours),
    ("E3 backtracking: 2 colours, no solution", t_csp_two_colours),
]


def main():
    print("AAIN-7001 Homework 2 -- public tests\n")
    for name, fn in TESTS:
        check(name, fn)
    total = PASSED + FAILED
    print(f"\n{PASSED}/{total} passed")
    sys.exit(0 if FAILED == 0 else 1)


if __name__ == "__main__":
    main()
