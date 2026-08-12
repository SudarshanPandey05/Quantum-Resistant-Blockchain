import time
import json
import hashlib
import hmac
import psutil
import math

# Import BB84 module (your file name must be bb84_main.py)
import bb84_main


# ================= BLOCK =================

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

        return hashlib.sha256(content.encode()).hexdigest()


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



# ================= BLOCKCHAIN =================

class QuantumBlockchain:

    def __init__(self, key, bits):

        self.chain = []

        self.key = key
        self.bits = bits

        self.process = psutil.Process()

        self.cpu_start = self.process.cpu_percent()
        self.mem_start = self.process.memory_info().rss

        self.start_time = time.time()

        self.create_genesis()


    def create_genesis(self):

        genesis = Block(
            0,
            "GENESIS",
            "0"*64,
            self.key
        )

        self.chain.append(genesis)


    def add_block(self, data):

        prev = self.chain[-1]

        block = Block(
            len(self.chain),
            data,
            prev.hash,
            self.key
        )

        self.chain.append(block)


    def validate(self):

        for i in range(1, len(self.chain)):

            cur = self.chain[i]
            prev = self.chain[i-1]

            if cur.hash != cur.calc_hash():
                return False

            if cur.prev_hash != prev.hash:
                return False

        return True


    # ================= REPORT =================

    def report(self):

        end_time = time.time()

        cpu_end = self.process.cpu_percent()
        mem_end = self.process.memory_info().rss


        # ----- Time -----
        total_time = end_time - self.start_time
        total_blocks = len(self.chain) - 1

        avg_mining = sum(
            b.mining_time for b in self.chain[1:]
        ) / total_blocks

        throughput = total_blocks / total_time
        latency = avg_mining


        # ----- Resource -----
        cpu_usage = abs(cpu_end - self.cpu_start)
        mem_usage = (mem_end - self.mem_start) / (1024 * 1024)


        # ----- Energy (Estimate) -----
        energy = cpu_usage * total_time * 0.0008


        # ----- Block Size (Fixed) -----
        sample = self.chain[1]

        block_data = {
            "index": sample.index,
            "timestamp": sample.timestamp,
            "data": sample.data,
            "prev_hash": sample.prev_hash,
            "nonce": sample.nonce,
            "hash": sample.hash,
            "sig": sample.sig
        }

        block_size = len(json.dumps(block_data).encode())


        # ----- Print -----

        print("\n📊 PERFORMANCE METRICS (QUANTUM BLOCKCHAIN)")
        print("-----------------------")

        print("Total Blocks       :", total_blocks)
        print("Total Time         :", round(total_time, 2), "sec")
        print("Avg Mining Time    :", round(avg_mining, 2), "sec")
        print("Throughput (TPS)   :", round(throughput, 2))
        print("Latency            :", round(latency, 2), "sec")
        print("Memory Usage       :", round(mem_usage, 2), "MB")
        print("CPU Usage          :", round(cpu_usage, 2), "%")
        print("Energy Estimate    :", round(energy, 4), "Wh")
        print("Block Size         :", block_size, "bytes")
        print("Chain Valid        :", self.validate())


        # ----- Quantum Metrics -----

        print("\n🔐 QUANTUM METRICS")
        print("-----------------------")

        print("QKD Key Length     :", len(self.key) * 8, "bits")
        print("Key Entropy        :", round(self.entropy(), 4))


    # ================= ENTROPY =================

    def entropy(self):

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



# ================= MAIN =================

def main():

    print("\nStarting Quantum Blockchain Test...\n")


    # Get BB84 key
    bits = bb84_main.GLOBAL_SHARED_KEY


    if not bits:

        print("❌ BB84 Key Not Generated")
        return


    # Convert bits → hash key
    bit_string = "".join(map(str, bits))

    key = hashlib.sha256(bit_string.encode()).digest()


    # Create blockchain
    bc = QuantumBlockchain(key, bits)


    # Add blocks
    for i in range(1, 11):

        bc.add_block(f"IoDT Secure Data {i}")

        print(
            f"Block {i} mined in "
            f"{round(bc.chain[-1].mining_time,2)} sec"
        )


    # Print report
    bc.report()



if __name__ == "__main__":
    main()