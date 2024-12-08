import csv
import sys
from collections import defaultdict

# Represents a single configuration (state of the machine) during the simulation
class Configuration:
    def __init__(self, tape, state, head, parent=None):
        self.tape = tape # Current tape contents
        self.state = state # Current state of the machine
        self.head = head # Position of the tape head
        self.parent = parent # Reference to the parent configuration (for backtracking)

# Implements the Non-Deterministic Turing Machine (NTM)
class NonDeterministicTuringMachine:
    def __init__(self, filename):
        self.transitions = defaultdict(list) # Stores the state transition rules
        self.parse_file(filename) # Reads machine configuration from a CSV file
        self.max_depth = 0 # Maximum depth for the simulation
        self.accept_path = None # Path to an accepting configuration, if found
        self.total_configurations = 0 # Total number of unique configurations explored
        self.level_branching = [] # Tracks branching factor at each simulation level

    # Parses the NTM configuration from a CSV file
    def parse_file(self, filename):
        with open(filename, "r") as file:
            reader = csv.reader(file)
            self.name = next(reader)[0] # Name of the machine
            self.states = next(reader) # List of machine states
            self.input_alphabet = next(reader) # Input alphabet
            self.tape_alphabet = next(reader) # Tape alphabet
            self.start_state = next(reader)[0] # Starting state
            self.accept_state = next(reader)[0] # Accepting state
            self.reject_state = next(reader)[0] # Rejecting state
            # Add transitions to the machine
            for line in reader:
                if line:
                    current_state, read_char, next_state, write_char, move = line
                    self.transitions[(current_state, read_char)].append(
                        (next_state, write_char, move)
                    )

    # Simulates the NTM for a given input string and maximum depth
    def simulate(self, input_string, max_depth):
        self.max_depth = max_depth
        initial_config = Configuration(input_string, self.start_state, 0) # Initialize with starting configuration
        self.tree = [[initial_config]] # Tracks configurations at each depth level
        visited = set() # Tracks visited configurations to avoid duplication
        level = 0 # Tracks the current depth of the simulation

        while level <= max_depth:
            current_level = self.tree[level] # Configurations at the current depth
            next_level = [] # Configurations to explore at the next depth
            branching_factor = 0 # Tracks the number of new branches at this level

            for current_config in current_level:
                self.total_configurations += 1 # Increment unique configurations explored
                tape = current_config.tape
                state = current_config.state
                head = current_config.head

                # Skip already-visited configurations
                if (tape, state, head) in visited:
                    continue
                visited.add((tape, state, head))

                # Check for accepting or rejecting states
                if state == self.accept_state:
                    self.accept_path = current_config
                    self.print_accept_path() # Print the accepting path
                    return "accept"
                elif state == self.reject_state:
                    continue

                # Handle out-of-bounds tape head
                if head < 0:
                    continue
                if head >= len(tape):
                    tape += "_" * (head - len(tape) + 1)

                # Apply transitions for the current state and tape character
                char_at_head = tape[head]
                for next_state, write_char, move in self.transitions.get(
                    (state, char_at_head), []
                ):
                    branching_factor += 1
                    new_tape = list(tape)
                    new_tape[head] = write_char
                    new_head = head + (1 if move == "R" else -1)
                    next_config = Configuration("".join(new_tape), next_state, new_head, parent=current_config)
                    next_level.append(next_config)

            # Update branching factor and prepare for the next level
            if next_level:
                self.level_branching.append(branching_factor / len(current_level))

            # If no further configurations can be explored
            if not next_level:
                print("String rejected in", level, "steps.")
                return "reject"

            self.tree.append(next_level)
            level += 1

        # If the depth limit is reached without a result
        print("Execution stopped after", max_depth, "steps.")
        return "stopped"

    # Prints the path from the start state to the accepting configuration
    def print_accept_path(self):
        path = []
        config = self.accept_path
        while config:
            path.append(config)
            config = config.parent
        path.reverse()  # Start from the initial configuration

        # Print details of the accepting path
        depth = len(path) - 1
        print(f"String accepted in {depth} steps.")
        print("-" * 40)
        print(f"{'Left of Head':<10} | {'State':<4} | {'Head Char':<5} | {'Right of Head'}")
        print("-" * 40)

        # Print each configuration in the path
        for config in path:
            tape = config.tape
            state = config.state
            head = config.head

            if head < 0:
                left = ""
                head_char = "_"
                right = tape
            elif head >= len(tape):
                left = tape
                head_char = "_"
                right = ""
            else:
                left = tape[:head]
                head_char = tape[head]
                right = tape[head + 1:]

            print(f"{left:<10} | {state:<4} | {head_char:<5} | {right}")

    # Calculates the average branching factor across all levels
    def average_nondeterminism(self):
        return sum(self.level_branching) / len(self.level_branching) if self.level_branching else 0

# Entry point for running the NTM simulation
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python traceNTM.py <machine_file> <input_string> <max_depth>")
        sys.exit(1)

    machine_file = sys.argv[1]
    input_string = sys.argv[2]
    max_depth = int(sys.argv[3])

    ntm = NonDeterministicTuringMachine(machine_file)
    print(f"Machine Name: {ntm.name}")
    print(f"Initial String: {input_string}")
    print("-" * 40)

    result = ntm.simulate(input_string, max_depth)
    print("-" * 40)
    print(f"Result: {result}")
    print(f"Depth of Tree: {len(ntm.tree) - 1}")
    print(f"Total Configurations Explored: {ntm.total_configurations}")
    print(f"Average Nondeterminism: {ntm.average_nondeterminism():.2f}")
