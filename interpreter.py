#!/usr/bin/python3

import sys
import copy

BLANK = 0
ACCEPT_STATE = "accept"
REJECT_STATE = "reject"


class TuringMachine(object):
    """ Nondeterministic turing machine interpreter.

        The states are represented by strings and the letters from the tape
        and input alphabet as numbers. In particular:
        - 0 denotes the blank symbol;
        - start denotes the initial state;
        - accept and reject denote the accepting and rejecting states.

        The machine’s description is given as a list of its transitions. Each
        transition is written in a separate line in the following format:
        <current_state> <currently_seen_letter> <target_state>
        <letter_to_write> <direction>
        The machine accepts its input by entering the accept state.
        The machine rejects the input word by either:
        - entering the reject state
        - getting stuck -- entering a configuration for which there is no
        applicable transition
        - looping forever

        The Turing machine does not have to have/use the reject state.
        The machine first writes the output letter and then moves its head.
        The machine cannot move left in the first position -- if it tries to,
        it simply stays in place.
        The machine can output blanks.
        The tape alphabet is a subset of natural numbers. The input alphabet
        is a subset of {1..9} .

    """

    def __init__(self, path):
        self._transitions = {}
        self._read_turing_machine(path)

    def _read_turing_machine(self, path):
        """ Reads a set of TM transitions from a *.tm file

            Args:
                path (str): Path to the *.tm file with transitions.

        """
        for transition in open(path, "r").read().split("\n"):
            # Edge case when input file ends with a newline character
            if transition != "":
                [cur_state, cur_letter, target_state, target_letter, direction] = transition.split(" ")
                try:
                    cur_letter = int(cur_letter)
                    target_letter = int(target_letter)
                except ValueError:
                    print("Error: Invalid letter in transition! Tape alphabet is natural numbers.")
                    sys.exit()
                assert direction in ("L", "R", "S")
                if (cur_state, cur_letter) not in self._transitions:
                    self._transitions[(cur_state, cur_letter)] = []
                self._transitions[(cur_state, cur_letter)].append((target_state, target_letter, direction))

    def run(self, tape, max_steps):
        """ Runs the TM over given input word on tape. The run is limited to a
            given number of steps.

            Args:
                tape ([int]): Input word - initial tape values.
                max_steps (int): Maximum steps allowed per run.

            Returns:
                bool: True if TM accepts the input word. False if TM rejects
                        the input word.

        """
        head_pos = 0
        state = "start"
        if len(tape) == 0:
            tape = [BLANK]
        letter = tape[head_pos]

        for transition in self._transitions.get((state, letter), []):
            if self._exists_accepting(state, tape, head_pos, transition, max_steps):
                return True
        return False

    def _exists_accepting(self, state, tape, head_pos, transition, max_steps):
        """ Checks if there exists an accepting run at most max_steps steps
            long from a given configuration after executing given transition.

            Args:
                state (str): Previous state.
                tape ([int]): Previous tape.
                head_pos (int): Previous head position.
                transition((str, int, str)): Transition to execute.
                steps (int): Maximum steps allowed from this configuration.

            Returns:
                bool: True if there exists an accepting run from this
                        configuration. False otherwise.

        """
        if max_steps == 0:
            return False

        tape = copy.copy(tape)

        (target_state, target_letter, direction) = transition
        tape[head_pos] = target_letter
        state = target_state
        if state == ACCEPT_STATE:
            return True
        if state == REJECT_STATE:
            return False

        if direction == "L" and head_pos > 0:
            # Move head to the left if isn't at leftmost position
            head_pos -= 1
        elif direction == "R":
            # Move head to the right. Extend the tape by a blank if neccessary.
            head_pos += 1
            if head_pos == len(tape):
                tape.append(BLANK)

        letter = tape[head_pos]
        for transition in self._transitions.get((state, letter), []):
            if self._exists_accepting(state, tape, head_pos, transition, max_steps - 1):
                return True
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python3 interpreter <path_to_turing_machine> <steps>")
        sys.exit()

    path_to_turing_machine = sys.argv[1]
    steps = int(sys.argv[2])
    tm = TuringMachine(path_to_turing_machine)

    try:
        tape = [int(x) for x in input("")]
        if BLANK in tape:
            raise ValueError
    except ValueError:
        print("Error: Invalid tape value! Input word alphabet: {1..9}")
        sys.exit()

    result = tm.run(tape, steps)
    if result:
        print("YES")
    else:
        print("NO")
