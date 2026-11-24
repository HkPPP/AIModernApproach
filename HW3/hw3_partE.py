from hw3_starter import *
 
broken = []
actions = robot_domain(HW_ROOMS, HW_PACKAGES)
for a in actions:
    dele = [] if a.name.startswith("Move") else a.delete
    if a.name.startswith("Move"):
        print(f"{a.name} add: {a.add} delete {a.delete}")
    broken.append(make_action(a.name, a.pre, a.add, dele))
plan = forward_bfs(HW_INIT, HW_GOAL, broken)
print(plan)
print(validate_plan(HW_INIT, HW_GOAL, actions, plan))

for b in (True, False):
    s = sum(p_world(ALARM, {"B": b, "E": e, "A": a, "J": True, "M": True})
            for e in (True, False) for a in (True, False))
    print("B =", b, "  sum =", round(s, 6))
