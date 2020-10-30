#!/usr/bin/python3

import sys

BLANK = 0
ACCEPT_STATE = "accept"
REJECT_STATE = "reject"
START_STATE = "start"


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
            given number of steps. The configurations are traversed using BFS.
            If a given configuration have already appeared then there is a
            cycle in transition graph. Configuration is a tuple:
            (state, tape, head_pos).

            Args:
                tape ((int)): Input word - initial tape values.
                max_steps (int): Maximum steps allowed per run.

            Returns:
                bool: True if TM accepts the input word. False if TM rejects
                        the input word.

        """
        head_pos = 0
        state = START_STATE
        tape += (BLANK,)
        steps = 1

        current_configurations = [(state, tape, head_pos)]
        next_configurations = set()
        history = set()

        while len(current_configurations) and steps <= max_steps:
            while len(current_configurations):
                conf = current_configurations.pop()
                if conf not in history:
                    history |= {conf}
                    if self.is_conf_terminal(conf):
                        return self.is_conf_accepting(conf)
                    next_configurations |= self.get_next_configurations(conf)

            current_configurations = next_configurations.copy()
            next_configurations.clear()
            steps += 1
        return False

    @staticmethod
    def is_conf_terminal(conf):
        """Check if configuration is a terminal one.

        Args:
            conf (configuration): Tuple (state, tape, head_pos)

        Returns:
            Bool: True if configuration is in a terminal state
        """
        (state, _, _) = conf
        return state in (ACCEPT_STATE, REJECT_STATE)

    @staticmethod
    def is_conf_accepting(conf):
        """Check if configuration is an accepting one.

        Args:
            conf (configuration): Tuple (state, tape, head_pos)

        Returns:
            Bool: True if configuration is in an accepting state
        """
        (state, _, _) = conf
        return state == ACCEPT_STATE

    def get_next_configurations(self, conf):
        """Generates all reachable configurations from a given configuration
           in one transition i.e. all neighbours in configuration graph.

        Args:
            conf (configuration): Tuple (state, tape, head_pos)

        Returns:
            set(configuration): Set of all reachable configurations in one
                                transition
        """
        (state, tape, head_pos) = conf
        letter = tape[head_pos]
        next_configurations = set()
        for transition in self._transitions.get((state, letter), []):
            (target_state, target_letter, direction) = transition
            new_head_pos = head_pos
            new_state = target_state
            new_tape = tape[:head_pos] + (target_letter,) + tape[(head_pos + 1):]

            if direction == "L" and new_head_pos > 0:
                # Move head to the left if isn't at leftmost position
                new_head_pos -= 1
            elif direction == "R":
                # Move head to the right. Extend the tape by a blank if neccessary.
                new_head_pos += 1
                if new_head_pos == len(tape):
                    new_tape = tape[:head_pos] + (target_letter,) + tape[(head_pos + 1):] + (BLANK,)
            next_configurations |= {(new_state, new_tape, new_head_pos)}
        return next_configurations


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python3 interpreter <path_to_turing_machine> <steps>")
        sys.exit()

    path_to_turing_machine = sys.argv[1]
    steps = int(sys.argv[2])
    tm = TuringMachine(path_to_turing_machine)

    try:
        tape = tuple(int(x) for x in input(""))
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
