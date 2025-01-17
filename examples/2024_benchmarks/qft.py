# This code is part of Qiskit.
#
# (C) Copyright IBM 2017.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Quantum Fourier Transform examples.
"""

import math
import numpy as np
from qiskit import QuantumCircuit
from qiskit import execute, BasicAer


###############################################################
# make the qft
###############################################################
def input_state(circ, n):
    """n-qubit input state for QFT that produces output 1."""
    for j in range(n):
        circ.h(j)
        circ.p(-math.pi / float(2 ** (j)), j)


def qft(circ, n):
    """n-qubit QFT on q in circ."""
    for j in range(n):
        for k in range(j):
            circ.cp(math.pi / float(2 ** (j - k)), j, k)
        circ.h(j)

qubits = 6

qft_list = []

for i in range(3, qubits+1):
    qft_list.append(QuantumCircuit(qubits, qubits, name="qft" + str(i)))

    input_state(qft_list[i - 3], i)
    qft_list[i - 3].barrier()
    qft(qft_list[i - 3], i)
    qft_list[i - 3].barrier()
    for j in range(i):
        qft_list[i - 3].measure(j, j)

print("dm simulator")
sim_backend = BasicAer.get_backend("dm_simulator")
job = execute(qft_list, sim_backend)
results = job.result().results

partial_probabilities = [result.data.partial_probability for result in results]

outcomes = np.empty((len(partial_probabilities), 0)).tolist()
# print(outcomes)

for i, partial_probability in enumerate(partial_probabilities):
    # print(partial_probability)
    for measurement in partial_probability:
        # print(measurement)
        if np.isclose(partial_probability[measurement], 1, atol=1e-2):
            # outcomes[i].append((measurement, partial_probability[measurement]))
            outcomes[i]=np.append(outcomes[i], (measurement, partial_probability[measurement]))

print(outcomes)