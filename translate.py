#!/usr/bin/python3

import sys

BLANK = 0
ACCEPT_STATE = "accept"
REJECT_STATE = "reject"


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


def translate_transitions_to_one_tape(two_tape_transitions):
    raise NotImplementedError


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python3 translate <path_to_a_two_tape_turing_machine>")
        sys.exit()

    path_to_turing_machine = sys.argv[1]
    two_tape_transitions = read_two_tape_transitions(path_to_turing_machine)
    one_tape_transitions = translate_transitions_to_one_tape(two_tape_transitions)
    for transition in one_tape_transitions:
        print(transition)
