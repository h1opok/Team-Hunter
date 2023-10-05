import multiprocessing
from tqdm import tqdm

def is_range_too_large(range_tuple):
    range_start, range_end = range_tuple
    start = int(range_start, 16)
    end = int(range_end, 16)
    range_size = end - start
    limit = 105342548110
    if range_size > limit:
        return (True, f"{range_start}:{range_end}:{range_size}")
    else:
        return (False, f"{range_start}:{range_end}")

def process_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    data = [tuple(line.strip().split(':')) for line in lines]

    num_processes = int(multiprocessing.cpu_count() * 0.8)
    with multiprocessing.Pool(num_processes) as pool:
        results = list(tqdm(pool.imap(is_range_too_large, data), total=len(data)))

    with open(filename, 'w') as queue, open('large_ranges.txt', 'a') as large:
        for is_too_large, range_str in results:
            if is_too_large:
                large.write(range_str + '\n')
            else:
                queue.write(range_str.split(':')[0] + ':' + range_str.split(':')[1] + '\n')

if __name__ == "__main__":
    multiprocessing.freeze_support()
    for i in range(234):
        process_file(f'ranges{i}.txt')
