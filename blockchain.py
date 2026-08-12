import hashlib
import time
import json
import psutil
import os


# ---------------- BLOCK CLASS ----------------

class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "nonce": self.nonce
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()


# ---------------- BLOCKCHAIN CLASS ----------------

class Blockchain:

    def __init__(self, difficulty=4):
        self.chain = []
        self.difficulty = difficulty
        self.block_times = []
        self.create_genesis()

    def create_genesis(self):
        genesis = Block(0, time.time(), "Genesis Block", "0")
        self.chain.append(genesis)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):

        start = time.time()

        prev_block = self.get_latest_block()
        new_block = Block(
            len(self.chain),
            time.time(),
            data,
            prev_block.hash
        )

        self.mine_block(new_block)

        self.chain.append(new_block)

        end = time.time()

        mining_time = end - start
        self.block_times.append(mining_time)

        return mining_time

    def mine_block(self, block):

        target = "0" * self.difficulty

        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()

    def is_valid(self):

        for i in range(1, len(self.chain)):

            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.hash != curr.calculate_hash():
                return False

            if curr.prev_hash != prev.hash:
                return False

        return True


# ---------------- PERFORMANCE MONITOR ----------------

class Performance:

    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def cpu(self):
        return psutil.cpu_percent()

    def memory(self):
        return self.process.memory_info().rss / (1024 * 1024)

    def energy_estimate(self, time_sec):
        power = 60   # watts (average CPU)
        return power * time_sec / 3600  # Wh


# ---------------- MAIN TEST ----------------

def run_test():

    blockchain = Blockchain(difficulty=4)
    monitor = Performance()

    NUM_BLOCKS = 10

    print("\n🚀 Starting Normal Blockchain Test...\n")

    start_total = time.time()

    for i in range(NUM_BLOCKS):

        data = f"Transaction Data {i}"

        t = blockchain.add_block(data)

        print(f"Block {i+1} mined in {t:.2f} sec")

    end_total = time.time()

    total_time = end_total - start_total

    # ---------------- METRICS ----------------

    avg_time = sum(blockchain.block_times) / len(blockchain.block_times)

    throughput = NUM_BLOCKS / total_time

    latency = avg_time

    memory = monitor.memory()

    cpu = monitor.cpu()

    energy = monitor.energy_estimate(total_time)

    block_size = len(json.dumps(blockchain.chain[1].__dict__))

    print("\n📊 PERFORMANCE METRICS")
    print("-----------------------")

    print(f"Total Blocks       : {NUM_BLOCKS}")
    print(f"Total Time         : {total_time:.2f} sec")
    print(f"Avg Mining Time    : {avg_time:.2f} sec")
    print(f"Throughput (TPS)   : {throughput:.2f}")
    print(f"Latency            : {latency:.2f} sec")
    print(f"Memory Usage       : {memory:.2f} MB")
    print(f"CPU Usage          : {cpu:.2f}%")
    print(f"Energy Estimate    : {energy:.4f} Wh")
    print(f"Block Size         : {block_size} bytes")
    print(f"Chain Valid        : {blockchain.is_valid()}")


# ---------------- RUN ----------------

if __name__ == "__main__":
    run_test()