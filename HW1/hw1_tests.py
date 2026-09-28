"""
AAIN-7001 Homework 1, Part C -- PUBLIC TESTS.

Run:  python hw1_tests.py

These are the tests you can see. The grading run includes additional hidden
tests of the same kind, so passing everything here is necessary but not
sufficient. If a test fails, read the assertion message before changing code.

Do not modify this file. It is replaced with a fresh copy at grading time.
"""

import sys
import traceback

import hw1_starter as hw

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


# ---------------------------------------------------------------- vacuum ---

def t_vacuum_actions():
    p = hw.VacuumProblem()
    assert list(p.actions(("A", "Dirty", "Dirty"))) == ["Right", "Suck"], \
        "in square A the applicable actions are Right and Suck, sorted"
    assert list(p.actions(("B", "Clean", "Clean"))) == ["Left", "Suck"], \
        "Suck is applicable even when the square is already clean"


def t_vacuum_result():
    p = hw.VacuumProblem()
    s = ("A", "Dirty", "Dirty")
    assert p.result(s, "Suck") == ("A", "Clean", "Dirty")
    assert p.result(s, "Right") == ("B", "Dirty", "Dirty")
    assert s == ("A", "Dirty", "Dirty"), "result() must not mutate its argument"


def t_vacuum_costs_change_the_answer():
    """Moving costs 2 and sucking costs 1, so UCS should prefer to suck first."""
    p = hw.VacuumProblem(("A", "Dirty", "Dirty"))
    node = hw.uniform_cost_search(p)
    assert node is not None, "a solution exists from ('A','Dirty','Dirty')"
    actions = hw.solution_actions(node)
    assert actions == ["Suck", "Right", "Suck"], \
        f"expected ['Suck','Right','Suck'], got {actions}"
    assert node.path_cost == 4, f"expected cost 4, got {node.path_cost}"


def t_vacuum_already_clean():
    p = hw.VacuumProblem(("A", "Clean", "Clean"))
    node = hw.breadth_first_search(p)
    assert node is not None and hw.solution_actions(node) == [], \
        "an initial state that is already a goal returns the empty plan"

# ------------------------------------------------------------ 8-puzzle -----

def t_puzzle_actions_corner():
    p = hw.EightPuzzleProblem((0, 1, 2, 3, 4, 5, 6, 7, 8))
    assert list(p.actions((0, 1, 2, 3, 4, 5, 6, 7, 8))) == ["Down", "Right"], \
        "blank in the top-left corner has exactly two moves"


def t_puzzle_actions_centre():
    p = hw.EightPuzzleProblem((1, 2, 3, 4, 0, 5, 6, 7, 8))
    assert list(p.actions((1, 2, 3, 4, 0, 5, 6, 7, 8))) == \
        ["Down", "Left", "Right", "Up"], "blank in the centre has four moves"


def t_puzzle_result():
    p = hw.EightPuzzleProblem((3, 1, 2, 0, 4, 5, 6, 7, 8))
    s = (3, 1, 2, 0, 4, 5, 6, 7, 8)
    assert p.result(s, "Up") == (0, 1, 2, 3, 4, 5, 6, 7, 8), \
        "'Up' moves the BLANK up, which slides the tile above it down"
    assert p.is_goal(p.result(s, "Up"))


def t_solvable():
    assert hw.is_solvable((1, 0, 2, 3, 4, 5, 6, 7, 8)) is True
    assert hw.is_solvable(hw.EightPuzzleProblem.GOAL) is True
    assert hw.is_solvable((4, 1, 2, 3, 0, 5, 6, 7, 8)) is False, \
        "this arrangement has odd inversion parity and cannot reach the goal"


# ------------------------------------------------------------- search ------

def t_ucs_finds_cheapest_not_shortest():
    """The whole point of Week 3: fewest steps is not cheapest."""
    class Weighted(hw.Problem):
        GRAPH = {"S": {"A": 99, "B": 1}, "A": {"G": 1}, "B": {"G": 2}, "G": {}}

        def actions(self, s):
            return sorted(self.GRAPH[s])

        def result(self, s, a):
            return a

        def action_cost(self, s, a, s2):
            return self.GRAPH[s][a]

    p = Weighted("S", "G")
    ucs = hw.uniform_cost_search(p)
    assert ucs is not None and ucs.path_cost == 3, \
        f"UCS must return the cost-3 path via B, got cost {ucs.path_cost}"
    bfs = hw.breadth_first_search(p)
    assert bfs.path_cost == 100, \
        "BFS returns the two-step path; if yours does not, check the early goal test"


def t_ids_matches_bfs_depth():
    for puzzle in [(1, 0, 2, 3, 4, 5, 6, 7, 8),
                   (3, 1, 2, 4, 5, 0, 6, 7, 8),
                   (1, 2, 5, 3, 4, 8, 6, 0, 7)]:
        bfs = hw.breadth_first_search(hw.EightPuzzleProblem(puzzle))
        ids = hw.iterative_deepening_search(hw.EightPuzzleProblem(puzzle))
        assert ids is not None, f"IDS found no solution for {puzzle}"
        assert len(hw.solution_actions(ids)) == len(hw.solution_actions(bfs)), \
            (f"for {puzzle} IDS returned a {len(hw.solution_actions(ids))}-step plan "
             f"but the shallowest goal is at depth {len(hw.solution_actions(bfs))}")


def t_counters_are_updated():
    c = hw.Counters()
    hw.uniform_cost_search(hw.EightPuzzleProblem((3, 1, 2, 4, 5, 0, 6, 7, 8)), c)
    assert c.expanded > 0 and c.generated > c.expanded, \
        "generated should exceed expanded -- every expansion produces children"


def t_dls_reports_cutoff():
    p = hw.EightPuzzleProblem((1, 2, 5, 6, 3, 8, 0, 4, 7))   # optimal depth 8
    assert hw.depth_limited_search(p, 2) == "cutoff", \
        "a limit shallower than the goal must return the string 'cutoff', not None"


def main():
    print("AAIN-7001 Homework 1 -- public tests\n")
    for name, fn in sorted(globals().items()):
        if name.startswith("t_"):
            check(name[2:].replace("_", " "), fn)
    total = PASSED + FAILED
    print(f"\n{PASSED}/{total} passed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
