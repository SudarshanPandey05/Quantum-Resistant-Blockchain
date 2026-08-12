import time
import json
import hashlib
import hmac
import psutil
import math

# ============================================================
# IMPORT BB84 MODULE
# File name: bb84_main_noice.py
# ============================================================

import bb84_main_noice


# ============================================================
# BLOCK
# ============================================================

class Block:

    def __init__(self, index, data, prev_hash, key):

        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash

        self.nonce = 0
        self.key = key

        self.hash = ""
        self.sig = ""

        self.mine()
        self.sign()


    def calc_hash(self):

        content = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce
        }, sort_keys=True)

        return hashlib.sha256(
            content.encode()
        ).hexdigest()


    def mine(self, diff=3):

        start = time.time()

        target = "0" * diff

        while True:

            self.hash = self.calc_hash()

            if self.hash[:diff] == target:
                break

            self.nonce += 1


        self.mining_time = time.time() - start


    def sign(self):

        self.sig = hmac.new(
            self.key,
            self.hash.encode(),
            hashlib.sha256
        ).hexdigest()


# ============================================================
# QUANTUM BLOCKCHAIN
# ============================================================

class QuantumBlockchain:

    def __init__(self, key, bits):

        self.chain = []

        self.key = key
        self.bits = bits

        self.process = psutil.Process()

        self.cpu_start = self.process.cpu_percent()

        self.mem_start = (
            self.process.memory_info().rss
        )

        self.start_time = time.time()

        self.create_genesis()


    # ========================================================
    # GENESIS BLOCK
    # ========================================================

    def create_genesis(self):

        genesis = Block(
            0,
            "GENESIS",
            "0" * 64,
            self.key
        )

        self.chain.append(genesis)


    # ========================================================
    # ADD BLOCK
    # ========================================================

    def add_block(self, data):

        prev = self.chain[-1]

        block = Block(
            len(self.chain),
            data,
            prev.hash,
            self.key
        )

        self.chain.append(block)


    # ========================================================
    # VALIDATE BLOCKCHAIN
    # ========================================================

    def validate(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check block hash
            if current.hash != current.calc_hash():
                return False

            # Check previous block connection
            if current.prev_hash != previous.hash:
                return False

            # Check HMAC signature
            expected_signature = hmac.new(
                self.key,
                current.hash.encode(),
                hashlib.sha256
            ).hexdigest()

            if current.sig != expected_signature:
                return False

        return True


    # ========================================================
    # ENTROPY
    # ========================================================

    def entropy(self):

        if len(self.bits) == 0:
            return 0

        ones = self.bits.count(1)
        zeros = self.bits.count(0)

        p1 = ones / len(self.bits)
        p0 = zeros / len(self.bits)

        ent = 0

        if p1 > 0:
            ent -= p1 * math.log2(p1)

        if p0 > 0:
            ent -= p0 * math.log2(p0)

        return ent


    # ========================================================
    # PERFORMANCE REPORT
    # ========================================================

    def report(self):

        end_time = time.time()

        cpu_end = self.process.cpu_percent()

        mem_end = (
            self.process.memory_info().rss
        )


        # ----------------------------------------------------
        # Time Metrics
        # ----------------------------------------------------

        total_time = (
            end_time - self.start_time
        )

        total_blocks = len(self.chain) - 1


        if total_blocks > 0:

            avg_mining = sum(
                block.mining_time
                for block in self.chain[1:]
            ) / total_blocks

        else:

            avg_mining = 0


        throughput = (
            total_blocks / total_time
            if total_time > 0
            else 0
        )

        latency = avg_mining


        # ----------------------------------------------------
        # Resource Metrics
        # ----------------------------------------------------

        cpu_usage = abs(
            cpu_end - self.cpu_start
        )

        mem_usage = (
            mem_end - self.mem_start
        ) / (1024 * 1024)


        # ----------------------------------------------------
        # Energy Estimate
        # ----------------------------------------------------

        energy = (
            cpu_usage *
            total_time *
            0.0008
        )


        # ----------------------------------------------------
        # Block Size
        # ----------------------------------------------------

        if len(self.chain) > 1:

            sample = self.chain[1]

        else:

            sample = self.chain[0]


        block_data = {

            "index": sample.index,

            "timestamp": sample.timestamp,

            "data": sample.data,

            "prev_hash": sample.prev_hash,

            "nonce": sample.nonce,

            "hash": sample.hash,

            "sig": sample.sig

        }


        block_size = len(
            json.dumps(
                block_data
            ).encode()
        )


        # ====================================================
        # PERFORMANCE OUTPUT
        # ====================================================

        print("\n")
        print("=" * 55)
        print("📊 PERFORMANCE METRICS")
        print("    QUANTUM BLOCKCHAIN")
        print("=" * 55)

        print(
            "Total Blocks       :",
            total_blocks
        )

        print(
            "Total Time         :",
            round(total_time, 4),
            "sec"
        )

        print(
            "Avg Mining Time    :",
            round(avg_mining, 4),
            "sec"
        )

        print(
            "Throughput (TPS)   :",
            round(throughput, 4)
        )

        print(
            "Latency            :",
            round(latency, 4),
            "sec"
        )

        print(
            "Memory Usage       :",
            round(mem_usage, 4),
            "MB"
        )

        print(
            "CPU Usage          :",
            round(cpu_usage, 4),
            "%"
        )

        print(
            "Energy Estimate    :",
            round(energy, 6),
            "Wh"
        )

        print(
            "Block Size         :",
            block_size,
            "bytes"
        )

        print(
            "Chain Valid        :",
            self.validate()
        )


        # ====================================================
        # QUANTUM METRICS
        # ====================================================

        print("\n")
        print("=" * 55)
        print("🔐 QUANTUM SECURITY METRICS")
        print("=" * 55)

        print(
            "QKD Key Length     :",
            len(self.key) * 8,
            "bits"
        )

        print(
            "Raw BB84 Key Length:",
            len(self.bits),
            "bits"
        )

        print(
            "Key Entropy        :",
            round(
                self.entropy(),
                4
            ),
            "bits"
        )


        # ====================================================
        # BB84 ERROR METRICS
        # ====================================================

        print("\n")
        print("=" * 55)
        print("⚛ BB84 QUANTUM CHANNEL PARAMETERS")
        print("=" * 55)


        # Read parameters from bb84_main_noice.py

        bit_flip = getattr(
            bb84_main_noice,
            "BIT_FLIP_PROBABILITY",
            0.0
        )

        phase_flip = getattr(
            bb84_main_noice,
            "PHASE_FLIP_PROBABILITY",
            0.0
        )

        depolarizing = getattr(
            bb84_main_noice,
            "DEPOLARIZING_PROBABILITY",
            0.0
        )

        readout = getattr(
            bb84_main_noice,
            "READOUT_ERROR_PROBABILITY",
            0.0
        )


        print(
            "Bit-Flip Error     :",
            round(bit_flip * 100, 2),
            "%"
        )

        print(
            "Phase-Flip Error   :",
            round(phase_flip * 100, 2),
            "%"
        )

        print(
            "Depolarizing Error:",
            round(depolarizing * 100, 2),
            "%"
        )

        print(
            "Readout Error      :",
            round(readout * 100, 2),
            "%"
        )


        # ----------------------------------------------------
        # QBER
        # ----------------------------------------------------

        qber = None

        if hasattr(
            bb84_main_noice,
            "calculate_qber"
        ):

            ron_key = getattr(
                bb84_main_noice,
                "shared_key_Ron",
                []
            )

            sam_key = getattr(
                bb84_main_noice,
                "shared_key_Sam",
                []
            )

            if sam_key and ron_key:

                qber = (
                    sum(
                        a != b
                        for a, b
                        in zip(
                            sam_key,
                            ron_key
                        )
                    )
                    / len(sam_key)
                )


        if qber is not None:

            print(
                "Measured QBER      :",
                round(qber * 100, 2),
                "%"
            )

        else:

            print(
                "Measured QBER      :",
                "Available in BB84 output"
            )


        print("=" * 55)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 55)
    print("🚀 STARTING QUANTUM BLOCKCHAIN TEST")
    print("=" * 55)


    # ========================================================
    # GET BB84 SHARED KEY
    # ========================================================

    bits = (
        bb84_main_noice.GLOBAL_SHARED_KEY
    )


    if not bits:

        print(
            "\n❌ BB84 Key Not Generated"
        )

        print(
            "Please generate a valid shared "
            "key using bb84_main_noice.py"
        )

        return


    # ========================================================
    # DISPLAY BB84 KEY
    # ========================================================

    print(
        "\n✅ BB84 Shared Key Generated"
    )

    print(
        "Raw Key:",
        bits
    )

    print(
        "Key Length:",
        len(bits),
        "bits"
    )


    # ========================================================
    # CONVERT BB84 BITS → SHA-256 KEY
    # ========================================================

    bit_string = "".join(
        map(str, bits)
    )

    key = hashlib.sha256(
        bit_string.encode()
    ).digest()


    print(
        "\n🔑 SHA-256 Derived Blockchain Key:"
    )

    print(
        key.hex()
    )


    # ========================================================
    # CREATE QUANTUM BLOCKCHAIN
    # ========================================================

    bc = QuantumBlockchain(
        key,
        bits
    )


    # ========================================================
    # ADD BLOCKS
    # ========================================================

    print("\n")
    print("=" * 55)
    print("⛓ BLOCK MINING")
    print("=" * 55)


    for i in range(1, 11):

        bc.add_block(
            f"IoDT Secure Data {i}"
        )

        print(
            f"Block {i} mined in "
            f"{round(
                bc.chain[-1].mining_time,
                4
            )} sec"
        )


    # ========================================================
    # FINAL REPORT
    # ========================================================

    bc.report()


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()