import os
import concurrent.futures
import math
import multiprocessing
from tqdm import tqdm

INITIAL_RANGE = 0x20000000000000000
FINAL_RANGE = 0x3ffffffffffffffff
NUM_CHUNKS = 350_223_996
CHUNK_SIZE = (FINAL_RANGE - INITIAL_RANGE) // NUM_CHUNKS
BLOCK_SIZE = 1_500_000
NUM_PROCESSES = int(multiprocessing.cpu_count() * 1)  # Number of processes to use (80% of total)
NUM_FILES = math.ceil(NUM_CHUNKS / BLOCK_SIZE)  # Number of files to generate

def generate_chunk_range(block_id):
    start = block_id * BLOCK_SIZE
    # Adjust the size of the last block if necessary
    if block_id == NUM_FILES - 1 and NUM_CHUNKS % BLOCK_SIZE != 0:
        end = start + NUM_CHUNKS % BLOCK_SIZE
    else:
        end = min(start + BLOCK_SIZE, NUM_CHUNKS)
    ranges = []

    for i in tqdm(range(start, end), desc=f"Generating blocks ({block_id+1}/{NUM_FILES})"):
        initial_range = INITIAL_RANGE + (i * CHUNK_SIZE)
        final_range = initial_range + CHUNK_SIZE - 1
        ranges.append((initial_range, final_range))

        if len(ranges) == 10000:  # Write the ranges to the file after every 10,000 generated ranges
            with open(os.path.join(os.getcwd(), f"ranges{block_id}.txt"), "a") as f:
                for range in ranges:
                    f.write(f"{hex(range[0])}:{hex(range[1])}\n")
            ranges.clear()

    # Write the remaining ranges to the file
    with open(os.path.join(os.getcwd(), f"ranges{block_id}.txt"), "a") as f:
        for range in ranges:
            f.write(f"{hex(range[0])}:{hex(range[1])}\n")

def generate_ranges():
    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_PROCESSES) as executor:
        executor.map(generate_chunk_range, range(NUM_FILES))

if __name__ == "__main__":
    # Check if the range files have already been generated
    if not all([os.path.exists(os.path.join(os.getcwd(), f"ranges{i}.txt")) for i in range(NUM_FILES)]):
        generate_ranges()
