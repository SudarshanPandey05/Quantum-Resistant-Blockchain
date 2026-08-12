import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# ============================================================
# REPRODUCIBILITY
# ============================================================

RANDOM_SEED = 42
random.seed(RANDOM_SEED)


# ============================================================
# USER INPUT FUNCTIONS
# ============================================================

def get_user_bits_multi(num_bits, entity_name):
    while True:
        bits_str = input(
            f"Enter {num_bits} binary bits for {entity_name} "
            f"(e.g., 01010101): "
        )

        if len(bits_str) == num_bits and all(bit in '01' for bit in bits_str):
            return [int(bit) for bit in bits_str]

        print(f"Invalid input. Please enter exactly {num_bits} binary bits.")


def get_user_bases_multi(num_bits, entity_name):
    while True:
        bases_str = input(
            f"Enter {num_bits} bases for {entity_name} "
            f"(0 for +, 1 for x, e.g., 01100110): "
        )

        if len(bases_str) == num_bits and all(base in '01' for base in bases_str):
            return [int(base) for base in bases_str]

        print(
            f"Invalid input. Please enter exactly {num_bits} "
            f"bases (0 or 1)."
        )


# ============================================================
# 1. SAM TRANSMISSION
# ============================================================

def Sam_transmission_multi_qubit(Sam_bits, Sam_bases):

    num_bits = len(Sam_bits)

    qc = QuantumCircuit(num_bits, num_bits)

    for i in range(num_bits):

        bit = Sam_bits[i]
        basis = Sam_bases[i]

        if basis == 0:
            # Rectilinear basis (+)
            # |0> = 0
            # |1> = X|0>
            if bit == 1:
                qc.x(i)

        else:
            # Diagonal basis (x)
            # |+> = H|0>
            # |-> = H|1>
            if bit == 0:
                qc.h(i)
            else:
                qc.x(i)
                qc.h(i)

    return [qc]


# ============================================================
# 2. QUANTUM CHANNEL ERRORS
# ============================================================

def apply_quantum_errors(
    qc,
    bit_flip_probability=0.0,
    phase_flip_probability=0.0,
    depolarizing_probability=0.0
):
    """
    Apply quantum-channel errors to each qubit.

    bit_flip_probability:
        Probability of applying X gate.

    phase_flip_probability:
        Probability of applying Z gate.

    depolarizing_probability:
        Probability of applying one of X, Y, Z.
    """

    num_qubits = qc.num_qubits

    for i in range(num_qubits):

        # ----------------------------------------------------
        # Bit-flip error (X)
        # ----------------------------------------------------
        if random.random() < bit_flip_probability:
            qc.x(i)

        # ----------------------------------------------------
        # Phase-flip error (Z)
        # ----------------------------------------------------
        if random.random() < phase_flip_probability:
            qc.z(i)

        # ----------------------------------------------------
        # Depolarizing error
        # ----------------------------------------------------
        if random.random() < depolarizing_probability:

            error = random.choice(["X", "Y", "Z"])

            if error == "X":
                qc.x(i)

            elif error == "Y":
                qc.y(i)

            elif error == "Z":
                qc.z(i)

    return qc


# ============================================================
# 3. RON MEASUREMENT + READOUT ERROR
# ============================================================

def Ron_measurement_multi_qubit_with_noise(
    transmitted_circuits,
    Ron_bases,
    bit_flip_probability=0.0,
    phase_flip_probability=0.0,
    depolarizing_probability=0.0,
    readout_error_probability=0.0
):

    simulator = AerSimulator()

    # Copy Sam's transmitted circuit
    qc = transmitted_circuits[0].copy()

    num_qubits = qc.num_qubits

    # --------------------------------------------------------
    # Apply quantum-channel errors BEFORE measurement
    # --------------------------------------------------------

    qc = apply_quantum_errors(
        qc,
        bit_flip_probability,
        phase_flip_probability,
        depolarizing_probability
    )

    # --------------------------------------------------------
    # Ron chooses measurement basis
    # --------------------------------------------------------

    for i in range(num_qubits):

        basis = Ron_bases[i]

        if basis == 1:
            # Diagonal basis
            qc.h(i)

        # Measurement
        qc.measure(i, i)

    # --------------------------------------------------------
    # Execute circuit
    # --------------------------------------------------------

    compiled_circuit = transpile(
        qc,
        simulator,
        seed_transpiler=RANDOM_SEED
    )

    job = simulator.run(
        compiled_circuit,
        shots=1,
        seed_simulator=RANDOM_SEED
    )

    result = job.result()

    counts = result.get_counts(compiled_circuit)

    measured_str = list(counts.keys())[0]

    # Qiskit classical bit ordering is reversed
    measured_bits = [
        int(bit)
        for bit in reversed(measured_str)
    ]

    # --------------------------------------------------------
    # Readout error
    # --------------------------------------------------------

    noisy_results = []

    for bit in measured_bits:

        if random.random() < readout_error_probability:
            bit = 1 - bit

        noisy_results.append(bit)

    return noisy_results


# ============================================================
# 4. BASIS RECONCILIATION
# ============================================================

def basis_reconciliation(
    Sam_bases,
    Ron_bases,
    Sam_bits,
    Ron_results
):

    shared_key_Sam = []
    shared_key_Ron = []

    for i in range(len(Sam_bases)):

        if Sam_bases[i] == Ron_bases[i]:

            shared_key_Sam.append(Sam_bits[i])
            shared_key_Ron.append(Ron_results[i])

    return shared_key_Sam, shared_key_Ron


# ============================================================
# 5. ERROR RATE CALCULATION
# ============================================================

def calculate_qber(shared_key_Sam, shared_key_Ron):

    if len(shared_key_Sam) == 0:
        return 0.0

    errors = sum(
        a != b
        for a, b in zip(shared_key_Sam, shared_key_Ron)
    )

    qber = errors / len(shared_key_Sam)

    return qber


# ============================================================
# MAIN PROGRAM
# ============================================================

num_bits = 8


# ============================================================
# ERROR PARAMETERS
# ============================================================

BIT_FLIP_PROBABILITY = 0.05
PHASE_FLIP_PROBABILITY = 0.05
DEPOLARIZING_PROBABILITY = 0.05
READOUT_ERROR_PROBABILITY = 0.02


print("=" * 60)
print("BB84 QUANTUM KEY DISTRIBUTION SIMULATION")
print("=" * 60)

print("\nQuantum Error Parameters")
print("-" * 60)

print(
    f"Bit-flip error       : "
    f"{BIT_FLIP_PROBABILITY * 100:.2f}%"
)

print(
    f"Phase-flip error     : "
    f"{PHASE_FLIP_PROBABILITY * 100:.2f}%"
)

print(
    f"Depolarizing error   : "
    f"{DEPOLARIZING_PROBABILITY * 100:.2f}%"
)

print(
    f"Readout error        : "
    f"{READOUT_ERROR_PROBABILITY * 100:.2f}%"
)

print(f"Random seed          : {RANDOM_SEED}")


# ============================================================
# SAM
# ============================================================

print("\n--- Sam's Input ---")

Sam_bits = get_user_bits_multi(
    num_bits,
    "Sam"
)

Sam_bases = get_user_bases_multi(
    num_bits,
    "Sam"
)

Sam_transmitted_circuits = Sam_transmission_multi_qubit(
    Sam_bits,
    Sam_bases
)

print("\nSam's generated bits:")
print(Sam_bits)

print("\nSam's chosen bases:")
print(Sam_bases)


# ============================================================
# RON
# ============================================================

print("\n--- Ron's Input ---")

Ron_bases = get_user_bases_multi(
    num_bits,
    "Ron"
)

Ron_measured_results = Ron_measurement_multi_qubit_with_noise(
    Sam_transmitted_circuits,
    Ron_bases,

    bit_flip_probability=BIT_FLIP_PROBABILITY,

    phase_flip_probability=PHASE_FLIP_PROBABILITY,

    depolarizing_probability=DEPOLARIZING_PROBABILITY,

    readout_error_probability=READOUT_ERROR_PROBABILITY
)

print("\nRon's chosen bases:")
print(Ron_bases)

print("\nRon's measurement results:")
print(Ron_measured_results)


# ============================================================
# BASIS RECONCILIATION
# ============================================================

shared_key_Sam, shared_key_Ron = basis_reconciliation(
    Sam_bases,
    Ron_bases,
    Sam_bits,
    Ron_measured_results
)


print("\n" + "=" * 60)
print("KEY RECONCILIATION")
print("=" * 60)

print("\nShared key (Sam):")
print(shared_key_Sam)

print("\nShared key (Ron):")
print(shared_key_Ron)


# ============================================================
# KEY LENGTHS
# ============================================================

print("\nLength of Sam's raw key:")
print(len(Sam_bits))

print("\nLength of Ron's raw measurements:")
print(len(Ron_measured_results))

print("\nLength of shared raw key:")
print(len(shared_key_Sam))


# ============================================================
# QBER
# ============================================================

qber = calculate_qber(
    shared_key_Sam,
    shared_key_Ron
)

print(
    f"\nQuantum Bit Error Rate (QBER): "
    f"{qber * 100:.2f}%"
)


# ============================================================
# KEY VERIFICATION
# ============================================================

if shared_key_Sam == shared_key_Ron:

    print("\nShared keys match!")

else:

    print(
        "\nShared keys do NOT match "
        "(quantum-channel/readout errors detected)."
    )


# ============================================================
# EXPORT KEY
# ============================================================

GLOBAL_SHARED_KEY = shared_key_Sam

print("\nGlobal shared key:")
print(GLOBAL_SHARED_KEY)