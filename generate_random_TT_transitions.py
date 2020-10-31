import random

BLANK = 0
ACCEPT_STATE = "accept"
REJECT_STATE = "reject"
START_STATE = "start"
R = "R"
L = "L"
S = "S"

STATES = set((f"state{no}" for no in range(7))) | {ACCEPT_STATE, REJECT_STATE, START_STATE}
ALPHABET = {BLANK, 1, 2}
DIRS = {R, L, S}
transitions = set()
while len(transitions) < 10000:
    transitions |= {(random.sample(STATES, 1)[0], random.sample(ALPHABET, 1)[0], random.sample(ALPHABET, 1)[0], random.sample(STATES, 1)[0], random.sample(ALPHABET, 1)[0], random.sample(ALPHABET, 1)[0], random.sample(DIRS, 1)[0], random.sample(DIRS, 1)[0])}
for (st, l1, l2, tst, tl1, tl2, dir1, dir2) in transitions:
    print(f"{st} {l1} {l2} {tst} {tl1} {tl2} {dir1} {dir2}")