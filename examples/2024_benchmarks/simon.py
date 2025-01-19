from random import choice
import numpy as np

from qiskit import QuantumCircuit, execute
from qiskit import BasicAer

def simon_oracle(b):
    """returns a Simon oracle for bitstring b"""
    b = b[::-1] # reverse b for easy iteration
    n = len(b)
    qc = QuantumCircuit(n*2)
    # Do copy; |x>|0> -> |x>|x>
    for q in range(n):
        qc.cx(q, q+n)
    if '1' not in b: 
        return qc  # 1:1 mapping, so just exit
    i = b.find('1') # index of first non-zero bit in b
    # Do |x> -> |s.x> on condition that q_i is 1
    for q in range(n):
        if b[q] == '1':
            qc.cx(i, (q)+n)
    return qc

def simon_circuit(b):
    """returns a Simon circuit for bitstring b"""
    n = len(b)
    circ = QuantumCircuit(n*2, n)
    circ.h(range(n))
    circ += simon_oracle(b)
    circ.h(range(n))

    # Measure the first n qubits
    circ.measure(range(n), range(n))

    return circ


if __name__ == "__main__":
    gpu = True
    qubits = 5

    simon_list = []
    solutions = []

    for i in range(3, qubits+1):
        solutions.append(''.join(choice(['0', '1']) for _ in range(i)))
        simon_list.append(simon_circuit(solutions[-1]))

    solutions = [int(sol, 2) for sol in solutions]

    if gpu:
        print("dm simulator gpu")
        sim_backend = BasicAer.get_backend("dm_simulator_gpu")
    else:
        print("dm simulator")
        sim_backend = BasicAer.get_backend("dm_simulator")

    job = execute(simon_list, sim_backend)
    results = job.result().results

    partial_probabilities = [result.data.partial_probability for result in results]

    outcomes = np.empty((len(partial_probabilities), 0)).tolist()

    for i, partial_probability in enumerate(partial_probabilities):
        max_probability = max(partial_probability.values())
        outcome = []
        for measurement in partial_probability:
            if np.isclose(partial_probability[measurement], max_probability, atol=max_probability/2):
                outcome.append(measurement)
        outcomes[i] = {int(measurement[::-1], 2): partial_probability[measurement] for measurement in outcome}

    # verify that the solutions are correct
    for i, solution in enumerate(solutions):
        print("n=%i, solution=%i" % (i+3, solution))
        print("outcomes:", outcomes[i])
        print(np.all([outcome^solution %2 == 0 for outcome in outcomes[i]]))
        assert np.all([outcome^solution %2 == 0 for outcome in outcomes[i]])
        print("Solutions are correct")