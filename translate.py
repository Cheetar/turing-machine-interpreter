#!/usr/bin/python3

import sys

BLANK = 0
ACCEPT_STATE = "accept"
REJECT_STATE = "reject"
R = "R"
L = "L"
S = "S"


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
            assert dir1 in ("L", "R", "S")
            assert dir2 in ("L", "R", "S")
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
    # Step 1.
    alphabet = get_alphabet(TT_transitions)
    max_val = max(alphabet) + 1  # Used for underlining
    underlined_alphabet = set(max_val + let for let in alphabet)
    double_underlined_alphabet = set(2*max_val + let for let in alphabet)
    SEPARATOR = 4 * max_val  # Separating the first and the second tape
    OT_transitions = []

    ################################################ INITIALIZATION ################################################
    OT_transitions.append(("start", let, "initializeFirstTape", underline(let, max_val), R) for let in alphabet)
    OT_transitions.append(("initializeFirstTape", let, "initializeFirstTape", let, R) for let in alphabet if let != BLANK)
    OT_transitions.append(("initializeFirstTape", BLANK, "initializeSecondTapeBlank", SEPARATOR, R))
    OT_transitions.append(("initializeSecondTapeBlank", BLANK, "initializeSecondTapeSeparator", BLANK, R))
    OT_transitions.append(("initializeSecondTapeSeparator", BLANK, "goBackToFirstHead", SEPARATOR, L))
    OT_transitions.append(("goBackToFirstHeadOnSecondTape", let, "goBackToFirstHeadOnSecondTape", let, L) for let in alphabet | double_underlined_alphabet)
    OT_transitions.append(("goBackToFirstHeadOnSecondTape", SEPARATOR, "goBackToFirstHeadOnFirstTape", SEPARATOR, L))
    OT_transitions.append(("goBackToFirstHeadOnFirstTape", let, "goBackToFirstHeadOnFirstTape", let, L) for let in alphabet)
    OT_transitions.append(("goBackToFirstHeadOnFirstTape", let, f"ReadLet2|let1:{un_underline(let)}", let, R) for let in underlined_alphabet)
    ################################################ EXECUTE FIRST HEAD ACTION ################################################
    OT_transitions.append((f"ReadLet2|let1:{let1}", let, f"ReadLet2|let1:{let1}", let, R) for let in alphabet | {SEPARATOR}
                                                                                          for let1 in alphabet)
    OT_transitions.append((f"ReadLet2|let1:{let1}", let2, f"executeSecondHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", let2, S) for let1 in alphabet
                                                                                                                                                   for let2 in double_underlined_alphabet)
    OT_transitions.append((f"executeSecondHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", let2, f"executeFirstHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", un_double_underline(let2), L) for let1 in alphabet
                                                                                                                                                   for let2 in double_underlined_alphabet)
    OT_transitions.append((f"executeSecondHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", let, f"executeFirstHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", let, L) for let1 in alphabet
                                                                                                                                                                                                        for let2 in double_underlined_alphabet)
    OT_transitions.append((f"executeFirstHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", let1, f"executeFirstHeadAction|tlet1:{tlet1}|tlet2:{tlet2}|dir1:{dir1}|dir2:{dir2}", let, L) for let1 in alphabet
                                                                                                                                                                                                        for let2 in double_underlined_alphabet)


def underline(let, max_val):
    return max_val + let


def double_underline(let, max_val):
    return 2 * max_val + let


def un_underline(let, max_val):
    return let - max_val


def un_double_underline(let, max_val):
    return let - 2 * max_val


def get_alphabet(TT_transitions):
    alphabet = {range(10)}
    for ((_, cur_let1, cur_let2), (_, out_let1, out_let2, _, _)) in TT_transitions.items():
        alphabet |= {cur_let1, cur_let2, out_let1, out_let2}
    return alphabet


def state(name, let1, dir1, t_let1, let2, dir2, t_):
    pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python3 translate <path_to_a_two_tape_turing_machine>")
        sys.exit()

    path_to_turing_machine = sys.argv[1]
    two_tape_transitions = read_two_tape_transitions(path_to_turing_machine)
    one_tape_transitions = translate_transitions_to_one_tape(two_tape_transitions)
    for transition in one_tape_transitions:
        print(transition)
