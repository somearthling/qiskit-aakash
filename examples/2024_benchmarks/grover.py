import numpy as np
from time import time

from qiskit import QuantumCircuit, BasicAer, execute
from qiskit.circuit.library import Diagonal

def initialize_s(circ, qubits):
    """Apply a H-gate to 'qubits' in circ."""
    for q in qubits:
        circ.h(q)
    return circ

def grover_problem_oracle(n, variant=0, print_solutions=False):
    np.random.seed(variant)
    if n < 3:
        nsolutions = 1
    else:
        nsolutions = np.random.randint(1, np.ceil((2**n)/4))
    diagonal_elements = [-1]*nsolutions + [1]*((2**n) - nsolutions)
    np.random.shuffle(diagonal_elements)
    oracle_gate = Diagonal(diagonal_elements)
    oracle_gate.name = "Oracle\nn=%i, var=%i" % (n, variant)
    solutions = [format(idx, "0%ib" % n) for idx, e in enumerate(diagonal_elements) if e < 1]
    if print_solutions:
        print("Solutions:")
        for idx, e in enumerate(diagonal_elements):
            if e < 1:
                print("|%s>" % format(idx, "0%ib" % n))
    return oracle_gate, solutions

def grover_problem_diffuser(n):
    qc = QuantumCircuit(n)

    # |s> -> |00..0> -> |11..1>
    for qubit in range(n):
        qc.h(qubit)
        qc.x(qubit)

    qc.h(n-1)
    qc.mct(list(range(n-1)), n-1)  # multi-controlled-toffoli
    qc.h(n-1)

    # |11..1> -> |00..0> -> |s>
    for qubit in range(n):
        qc.x(qubit)
        qc.h(qubit)

    U_s = qc.to_gate()
    U_s.name = "U$_s$"

    return U_s

def grover_circuit(n, variant=0, print_solutions=False):
    circ = QuantumCircuit(n, n)
    circ = initialize_s(circ, range(n))
    oracle, solutions = grover_problem_oracle(n, variant, print_solutions)

    for _ in range(np.ceil((np.pi/4)*np.sqrt(n/len(solutions))).astype(int)):
        circ.append(oracle, range(n))
        circ.append(grover_problem_diffuser(n), range(n))

    circ.measure(range(n), range(n))

    return circ, solutions


if __name__ == "__main__":
    gpu = True
    qubits = 6
    seed = 0

    grover_circuits = []
    solutions_list = []

    for i in range(3, qubits+1):
        grover_circ, solutions = grover_circuit(i, seed)
        grover_circuits.append(grover_circ)
        solutions_list.append(solutions)

    if gpu:
        print("dm simulator gpu")
        sim_backend = BasicAer.get_backend("dm_simulator_gpu")
    else:
        print("dm simulator")
        sim_backend = BasicAer.get_backend("dm_simulator")
    job = execute(grover_circuits, sim_backend)
    results = job.result().results

    partial_probabilities = [result.data.partial_probability for result in results]

    outcomes = np.empty((len(partial_probabilities), 0)).tolist()
    # print(outcomes)

    for i, partial_probability in enumerate(partial_probabilities):
        # print(partial_probability)
        max_probability = max(partial_probability.values())
        outcome = []
        for measurement in partial_probability:
            if np.isclose(partial_probability[measurement], max_probability, atol=max_probability/2):
                outcome.append(measurement)
        outcomes[i] = {measurement[::-1]: partial_probability[measurement] for measurement in outcome}

    for i, solutions in enumerate(solutions_list):
        print("n=%i" % (i+3))

        if set(solutions) == set(outcomes[i].keys()):
            print("Success!")