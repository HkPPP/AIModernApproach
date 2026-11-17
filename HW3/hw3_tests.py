"""
AAIN-7001 Homework 3 -- PUBLIC TESTS.

Run:  python hw3_tests.py        (0/17 before you start; Part D tests stay TODO until after Nov 12)

The grading run includes more hidden tests of the same kind, on different
networks, rooms, packages and rewards. Passing everything here is necessary
but not sufficient. Do not modify this file; it is replaced at grading time.
"""
import sys
import traceback

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


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol


def plan_is_valid(init, goal, actions, plan):
    """Independent checker (does not use your functions)."""
    by_name = {a.name: a for a in actions}
    state = set(init)
    for name in plan:
        a = by_name.get(name)
        assert a is not None, f"unknown action name {name!r}"
        assert a.pre <= state, f"{name} used when its preconditions are not all true"
        state = (state - set(a.delete)) | set(a.add)
    return set(goal) <= state


import hw3_starter as hw


def _eq(got, want):
    assert got == want, f"got {got!r}, expected {want!r}"


def _close(got, want, tol=1e-3):
    assert close(got, want, tol), f"got {got}, expected about {want}"


def _nospace(acts):
    bad = [a.name for a in acts if " " in a.name]
    assert not bad, f"names with spaces: {bad[:3]}"


print("Part A -- knowledge representation")
check("A1 chain('Ali')", lambda: _eq(hw.chain("Ali"), ["Ali", "GradStudents", "Students", "People"]))
check("A2 lookup: exception wins (Ali does not pay tuition)", lambda: _eq(hw.lookup("Ali", "PaysTuition"), ("no", ["Ali", "GradStudents"])))
check("A2 lookup: inherited from the top (Ali has an ID)", lambda: _eq(hw.lookup("Ali", "HasID"), ("yes", ["Ali", "GradStudents", "Students", "People"])))
check("A3 is_a", lambda: _eq((hw.is_a("Ali", "People"), hw.is_a("Bo", "Employees")), (True, False)))

print("Part B -- classical planning")
def _b1():
    a = hw.make_action("Move(Office,Lab)", ["At(R,Office)"], ["At(R,Lab)"], ["At(R,Office)"])
    assert hw.applicable(a, frozenset({"At(R,Office)", "HandEmpty"})) is True
    assert hw.applicable(a, frozenset({"At(R,Lab)"})) is False
check("B1 applicable", _b1)
def _b2():
    a = hw.make_action("Move(Office,Lab)", ["At(R,Office)"], ["At(R,Lab)"], ["At(R,Office)"])
    s = frozenset({"At(R,Office)", "HandEmpty"})
    _eq(hw.result(a, s), frozenset({"At(R,Lab)", "HandEmpty"}))
check("B2 result removes the delete list and adds the add list", _b2)
def _b3():
    acts = hw.robot_domain(hw.HW_ROOMS, hw.HW_PACKAGES)
    names = {a.name for a in acts}
    assert len(acts) == 18, f"expected 18 actions (6 Move, 6 Pick, 6 Drop), got {len(acts)}"
    for n in ["Move(Office,Lab)", "Pick(P1,Mailroom)", "Drop(P2,Office)"]:
        assert n in names, f"missing action {n}"
check("B3 robot_domain: 3 rooms, 2 packages", _b3)
check("B3 robot_domain names have no spaces", lambda: _nospace(hw.robot_domain(["Office", "Lab"], ["P1"])))
def _b4a():
    acts = hw.robot_domain(["Office", "Mailroom"], ["P"])
    init = frozenset({"At(R,Office)", "At(P,Mailroom)", "HandEmpty"})
    plan = hw.forward_bfs(init, frozenset({"At(P,Office)"}), acts)
    assert plan is not None and len(plan) == 4, f"expected a 4-step plan (the Week 8 example), got {plan}"
    assert plan_is_valid(init, {"At(P,Office)"}, acts, plan), "plan does not reach the goal"
check("B4 forward_bfs: the Week 8 robot (4 steps)", _b4a)
def _b4b():
    acts = hw.robot_domain(hw.HW_ROOMS, hw.HW_PACKAGES)
    plan = hw.forward_bfs(hw.HW_INIT, hw.HW_GOAL, acts)
    assert plan is not None and len(plan) == 7, f"expected a shortest plan of 7 steps, got {plan}"
    assert plan_is_valid(hw.HW_INIT, hw.HW_GOAL, acts, plan), "plan does not reach the goal"
check("B4 forward_bfs: the HW problem (shortest = 7)", _b4b)
def _b4c():
    acts = hw.robot_domain(["Office", "Mailroom"], ["P"])
    init = frozenset({"At(R,Office)", "At(P,Office)", "HandEmpty"})
    _eq(hw.forward_bfs(init, frozenset({"At(P,Office)"}), acts), [])
check("B4 forward_bfs: goal already true -> []", _b4c)
def _b5():
    acts = hw.robot_domain(["Office", "Mailroom"], ["P"])
    init = frozenset({"At(R,Office)", "At(P,Mailroom)", "HandEmpty"}); goal = frozenset({"At(P,Office)"})
    good = ["Move(Office,Mailroom)", "Pick(P,Mailroom)", "Move(Mailroom,Office)", "Drop(P,Office)"]
    bad = ["Pick(P,Mailroom)", "Move(Office,Mailroom)", "Move(Mailroom,Office)", "Drop(P,Office)"]
    assert hw.validate_plan(init, goal, acts, good) is True, "a correct plan was rejected"
    assert hw.validate_plan(init, goal, acts, bad) is False, "a plan that picks up from the wrong room was accepted"
check("B5 validate_plan", _b5)

print("Part C -- Bayesian networks")
check("C1 p_world: one world of the alarm network", lambda: _close(hw.p_world(hw.ALARM, {"B": False, "E": False, "A": True, "J": True, "M": True}), 0.000628, 1e-6))
check("C2 enumerate_ask: P(B | j, m)", lambda: _close(hw.enumerate_ask(hw.ALARM, "B", {"J": True, "M": True}), 0.2842))
check("C2 enumerate_ask: P(A | b) (one parent known)", lambda: _close(hw.enumerate_ask(hw.ALARM, "A", {"B": True}), 0.94))

print("Part D -- MDPs (after the Nov 12 class)")
def _d1():
    U = hw.value_iteration(hw.GridMDP(r=-0.04, gamma=1.0))
    for s, v in {(1, 1): 0.705, (3, 3): 0.918, (4, 1): 0.388, (4, 3): 1.0}.items():
        assert close(U[s], v, 2e-3), f"U{s} = {U[s]:.4f}, expected about {v}"
check("D1 value_iteration: R&N Figure 17.3 values", _d1)
def _d2():
    m = hw.GridMDP(r=-0.04, gamma=1.0); U = hw.value_iteration(m); pi = hw.best_policy(m, U)
    assert pi[(1, 1)] == "N" and pi[(3, 3)] == "E" and pi[(3, 1)] == "W", f"got (1,1)={pi[(1, 1)]}, (3,3)={pi[(3, 3)]}, (3,1)={pi[(3, 1)]}"
    assert pi[(4, 3)] is None and pi[(4, 2)] is None, "terminal states must map to None"
check("D2 best_policy", _d2)


print(f"\n{PASSED}/{PASSED + FAILED} public tests passed.")
