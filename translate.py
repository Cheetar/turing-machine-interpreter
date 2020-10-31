#!/usr/bin/python3

import sys

BLANK = 0
ACCEPT_STATE = "accept"
REJECT_STATE = "reject"
START_STATE = "start"
R = "R"
L = "L"
S = "S"
DIRS = (R, L, S)


def read_two_tape_transitions(path):
    """ Reads transitions of a two tape Turing Machine from a .tm file.

        Transitions are defined as follows:
        <state> <let1> <let2> <target_state> <out_let1> <out_let2> <dir1> <dir2>

    Args:
        path (str): Path to a .tm file with transitions.

    Returns:
        [transition]: List of two tape Turing Machine transitions.
    """
    transitions = {}
    for transition in open(path, "r").read().split("\n"):
        # Edge case when input file ends with a newline character
        if transition != "":
            [cur_state, cur_let1, cur_let2, target_state, out_let1, out_let2, dir1, dir2] = transition.split(" ")
            try:
                cur_let1 = int(cur_let1)
                cur_let2 = int(cur_let2)
                out_let1 = int(out_let1)
                out_let2 = int(out_let2)
            except ValueError:
                print("Error: Invalid letter in transition! Tape alphabet is natural numbers.")
                sys.exit()
            assert dir1 in DIRS
            assert dir2 in DIRS
            if (cur_state, cur_let1, cur_let2) not in transitions:
                transitions[(cur_state, cur_let1, cur_let2)] = []
            transitions[(cur_state, cur_let1, cur_let2)].append((target_state, out_let1, out_let2, dir1, dir2))
    return transitions


def translate_transitions_to_one_tape(TT_transitions):
    """Translates two tape Turing Machine to a single tape TM.

    Both tapes will be stored on the same tape in format:
    <first tape> # <second tape> #

    General algorithm for transcribtion from two to single tape:
    1. Underline the first letter of the input word. (underline = position
       of the head)
    2. Go to the end of the first tape and write #. Leave one underlined BLANK
       representing the second tape and leave next #. Go back to the beginning
       of the tape. Tape is now in format
       <U_first_letter_of_input> <rest_of_input_word> # <U_BLANK> #.
    3a. Make transition of the first head. Mark new head position.
    3b. If the transition exceeds the first tape size, rewrite the second tape
        one position to the left.
    4. Go to the second head.
    5. Make transition of the second head. If ends up on #, then rewrite it
       one position to the left.
    6. Go back to the position of the first head.
    7. Go to the point 3a. of the algorithm.

    Args:
        TT_transitions ([two_tape_transition]): A two tape transition is
            a tuple: <state> <let1> <let2> <target_state> <out_let1> <out_let2>
            <dir1> <dir2>

    Returns:
        [transition]: List of single tape Turing Machine transitions.
    """
    alphabet = get_alphabet(TT_transitions)
    states = get_states(TT_transitions)
    max_val = max(alphabet) + 1  # Used for underlining
    underlined_alphabet = set(max_val + let for let in alphabet)
    double_underlined_alphabet = set(2*max_val + let for let in alphabet)
    SEPARATOR = 4 * max_val  # Separating the first and the second tape
    OT_transitions = []

    ################################################ 1.INITIALIZATION ################################################
    OT_transitions += [(START_STATE, let, state("initializeFirstTape"), underline(let, max_val), R)
                        for let in alphabet]
    OT_transitions += [(state("initializeFirstTape"), let, state("initializeFirstTape"), let, R)
                          for let in alphabet - {BLANK}]
    OT_transitions += [(state("initializeFirstTape"), BLANK, state("initializeSecondTapeBlank"), SEPARATOR, R)]
    OT_transitions += [(state("initializeSecondTapeBlank"), BLANK, state("initializeSecondTapeSeparator"), double_underline(BLANK, max_val), R)]
    OT_transitions += [(state("initializeSecondTapeSeparator"), BLANK, state("goBackToFirstHeadOnSecondTape", org_state=START_STATE), SEPARATOR, L)]
    OT_transitions += [(state("goBackToFirstHeadOnSecondTape", org_state=org_state), let, state("goBackToFirstHeadOnSecondTape", org_state=org_state), let, L)
                          for let in alphabet | double_underlined_alphabet
                          for org_state in states]
    OT_transitions += [(state("goBackToFirstHeadOnSecondTape", org_state=org_state), SEPARATOR, state("goBackToFirstHeadOnFirstTape", org_state=org_state), SEPARATOR, L)
                          for org_state in states]
    OT_transitions += [(state("goBackToFirstHeadOnFirstTape", org_state=org_state), let, state("goBackToFirstHeadOnFirstTape", org_state=org_state), let, L)
                          for let in alphabet
                          for org_state in states]
    OT_transitions += [(state("goBackToFirstHeadOnFirstTape", org_state=org_state), u_let, state("ReadLet2", org_state=org_state, let1=un_underline(u_let, max_val)), u_let, R)
                          for u_let in underlined_alphabet
                          for org_state in states]
    ################################################ EXECUTE FIRST HEAD ACTION ################################################
    OT_transitions += [(state("ReadLet2", org_state=org_state, let1=let1), let, state("ReadLet2", org_state=org_state, let1=let1), let, R)
                          for let in alphabet | {SEPARATOR}
                          for let1 in alphabet
                          for org_state in states]
    for org_state in states:
        for let1 in alphabet:
            for let2 in alphabet:
                for (target_state, tlet1, tlet2, dir1, dir2) in TT_transitions.get((org_state, let1, let2), []):
                    OT_transitions += [(state("ReadLet2", org_state=org_state, let1=let1), double_underline(let2, max_val), state("executeSecondHeadAction", org_state=target_state, tlet1=tlet1, tlet2=tlet2, dir1=dir1, dir2=dir2), double_underline(let2, max_val), S)]   
    OT_transitions += [(state("executeSecondHeadAction", org_state=org_state, tlet1=tlet1, tlet2=tlet2, dir1=dir1, dir2=R), double_underline(let2, max_val), state("executeSecondHeadActionRightCheckIfExceedsTape", org_state=org_state, tlet1=tlet1, dir1=dir1), tlet2, R)
                          for tlet1 in alphabet
                          for tlet2 in alphabet
                          for let2 in alphabet
                          for dir1 in DIRS
                          for org_state in states]
    OT_transitions += [(state("executeSecondHeadActionRightCheckIfExceedsTape", org_state=org_state, tlet1=tlet1, dir1=dir1), let, state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), double_underline(let2, max_val), R)
                          for tlet1 in alphabet
                          for let in alphabet
                          for dir1 in DIRS
                          for org_state in states]
    OT_transitions += [(state("executeSecondHeadActionRightCheckIfExceedsTape", org_state=org_state, tlet1=tlet1, dir1=dir1), SEPARATOR, state("executeSecondHeadActionRightTapeExceededWriteNewSeparator", org_state=org_state, tlet1=tlet1, dir1=dir1), double_underline(BLANK, max_val), R)
                        for tlet1 in alphabet
                        for dir1 in DIRS
                        for org_state in states]
    OT_transitions += [(state("executeSecondHeadActionRightTapeExceededWriteNewSeparator", org_state=org_state, tlet1=tlet1, dir1=dir1), BLANK, state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), SEPARATOR, L)
                    for tlet1 in alphabet
                    for dir1 in DIRS
                    for org_state in states]
    OT_transitions += [(state("executeSecondHeadAction", org_state=org_state, tlet1=tlet1, tlet2=tlet2, dir1=dir1, dir2=S), let2, state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), double_underline(tlet2, max_val), L)
                          for tlet1 in alphabet
                          for tlet2 in alphabet
                          for let2 in double_underlined_alphabet
                          for dir1 in DIRS
                          for org_state in states]
    OT_transitions += [(state("executeSecondHeadAction", org_state=org_state, tlet1=tlet1, tlet2=tlet2, dir1=dir1, dir2=L), let2, state("executeSecondHeadActionLeftCheckIfExceedsTape", org_state=org_state, tlet1=tlet1, dir1=dir1), tlet2, L)
                        for tlet1 in alphabet
                        for tlet2 in alphabet
                        for let2 in double_underlined_alphabet
                        for dir1 in DIRS
                        for org_state in states]
    OT_transitions += [(state("executeSecondHeadActionLeftCheckIfExceedsTape", org_state=org_state, tlet1=tlet1, dir1=dir1), let, state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), double_underline(let, max_val), L)
                        for tlet1 in alphabet
                        for let in alphabet
                        for dir1 in DIRS
                        for org_state in states]
    OT_transitions += [(state("executeSecondHeadActionLeftCheckIfExceedsTape", org_state=org_state, tlet1=tlet1, dir1=dir1), SEPARATOR, state("executeSecondHeadActionLeftTapeExceededWriteDoubleUnderline", org_state=org_state, tlet1=tlet1, dir1=dir1), SEPARATOR, R)
                        for tlet1 in alphabet
                        for dir1 in DIRS
                        for org_state in states]
    OT_transitions += [(state("executeSecondHeadActionLeftTapeExceededWriteDoubleUnderline", org_state=org_state, tlet1=tlet1, dir1=dir1), let, state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), double_underline(let, max_val), L)
                        for tlet1 in alphabet
                        for dir1 in DIRS
                        for let in alphabet
                        for org_state in states]
    OT_transitions += [(state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), let, state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), let, L)
                    for tlet1 in alphabet
                    for dir1 in DIRS
                    for let in alphabet | double_underlined_alphabet | {SEPARATOR}
                    for org_state in states]
    OT_transitions += [(state("goToFirstHead", org_state=org_state, tlet1=tlet1, dir1=dir1), let1, state("executeFirstHeadAction", org_state=org_state, tlet1=tlet1, dir1=dir1), let1, S)
                    for tlet1 in alphabet
                    for dir1 in DIRS
                    for let1 in underlined_alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadAction", org_state=org_state, tlet1=tlet1, dir1=S), let1, state("checkIfTerminalState", org_state=org_state), underline(tlet1, max_val), S)
                    for tlet1 in alphabet
                    for let1 in underlined_alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadAction", org_state=org_state, tlet1=tlet1, dir1=L), let1, state("executeFirstHeadActionLeftCheckIfExceedsTape", org_state=org_state, tlet1=tlet1), let1, L)
                    for tlet1 in alphabet
                    for let1 in underlined_alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadActionLeftCheckIfExceedsTape", org_state=org_state, tlet1=tlet1), let1, state("checkIfTerminalState", org_state=org_state), underline(tlet1, max_val), S)
                    for tlet1 in alphabet
                    for let1 in underlined_alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadActionLeftCheckIfExceedsTape", org_state=org_state, tlet1=tlet1), let, state("executeFirstHeadActionLeftCheckIfExceedsTapeTapeNotExceeded", org_state=org_state), underline(let, max_val), R)
                    for tlet1 in alphabet
                    for let in alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadActionLeftCheckIfExceedsTapeTapeNotExceeded", org_state=org_state), let1, state("checkIfTerminalState", org_state=org_state), un_underline(let1, max_val), L)
                    for tlet1 in alphabet
                    for let1 in underlined_alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadAction", org_state=org_state, tlet1=tlet1, dir1=R), let1, state("executeFirstHeadActionRightCheckIfExceedsTape", org_state=org_state), tlet1, R)
                    for tlet1 in alphabet
                    for let1 in underlined_alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadActionRightCheckIfExceedsTape", org_state=org_state), let, state("checkIfTerminalState", org_state=org_state), underline(let, max_val), S)
                    for tlet1 in alphabet
                    for let in alphabet
                    for org_state in states]
    OT_transitions += [(state("executeFirstHeadActionRightCheckIfExceedsTape", org_state=org_state), SEPARATOR, state("rewriteSecondTapeWriteSeparator", org_state=org_state), underline(BLANK, max_val), R)
                    for org_state in states]
    OT_transitions += [(state("rewriteSecondTapeWriteSeparator", org_state=org_state), let, state("rewriteSecondTape", org_state=org_state, last_letter=let), SEPARATOR, R)
                       for let in alphabet | double_underlined_alphabet
                       for org_state in states]
    OT_transitions += [(state("rewriteSecondTape", org_state=org_state, last_letter=let), let2, state("rewriteSecondTape", org_state=org_state, last_letter=let2), let, R)
                       for let in alphabet | double_underlined_alphabet
                       for let2 in alphabet | double_underlined_alphabet | {SEPARATOR}
                       for org_state in states]
    OT_transitions += [(state("rewriteSecondTape", org_state=org_state, last_letter=SEPARATOR), BLANK, state("goToFirstHeadCheckTerminal", org_state=org_state), SEPARATOR, L)
                       for org_state in states]
    OT_transitions += [(state("goToFirstHeadCheckTerminal", org_state=org_state), let, state("goToFirstHeadCheckTerminal", org_state=org_state), let, L)
                       for let in alphabet | double_underlined_alphabet | {SEPARATOR}
                       for org_state in states]
    OT_transitions += [(state("goToFirstHeadCheckTerminal", org_state=org_state), let, state("checkIfTerminalState", org_state=org_state), let, S)
                       for let in underlined_alphabet
                       for org_state in states]
    # Check if terminal state
    OT_transitions += [(state("checkIfTerminalState", org_state=org_state), let1, org_state, let1, S)
                    for let1 in underlined_alphabet
                    for org_state in (ACCEPT_STATE, REJECT_STATE)]
    OT_transitions += [(state("checkIfTerminalState", org_state=org_state), let1, state("ReadLet2", org_state=org_state, let1=un_underline(let1, max_val)), let1, R)
                          for let1 in underlined_alphabet
                          for org_state in states - {ACCEPT_STATE, REJECT_STATE}]
    return OT_transitions           


def underline(let, max_val):
    return max_val + let


def double_underline(let, max_val):
    return 2 * max_val + let


def un_underline(let, max_val):
    return let - max_val


def un_double_underline(let, max_val):
    return let - 2 * max_val


def get_alphabet(TT_transitions):
    alphabet = {*range(3)}
    for ((_, cur_let1, cur_let2), TT_transition_results) in TT_transitions.items():
        alphabet |= {cur_let1, cur_let2}
        for (_, out_let1, out_let2, _, _) in TT_transition_results:
            alphabet |= {out_let1, out_let2}
    return alphabet


def get_states(TT_transitions):
    states = {START_STATE, ACCEPT_STATE, REJECT_STATE}
    for ((org_state, _, _), TT_transition_results) in TT_transitions.items():
        states |= {org_state}
        for (t_state, _, _, _, _) in TT_transition_results:
            states |= {t_state}
    return states


def state(name, **kwards):
    out = f"{name}"
    for key, val in kwards.items():
        out += f"|{key}:{val}"
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python3 translate <path_to_a_two_tape_turing_machine>")
        sys.exit()

    path_to_turing_machine = sys.argv[1]
    TT_transitions = read_two_tape_transitions(path_to_turing_machine)
    OT_transitions = translate_transitions_to_one_tape(TT_transitions)
    for (state, let, t_state, t_let, direction) in OT_transitions:
        print(f"{state} {let} {t_state} {t_let} {direction}")
