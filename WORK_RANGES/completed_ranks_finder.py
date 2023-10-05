import multiprocessing
import os
from tqdm import tqdm

def create_total_ranges_file():
    total_lines = set()

    for completed_file in os.listdir('.'):
        if completed_file.startswith('completed_ranges_'):
            with open(completed_file, 'r') as f:
                for line in f:
                    total_lines.add(line.strip())

    with open('total_completed_ranges.txt', 'w') as f:
        for line in total_lines:
            f.write(line + '\n')

create_total_ranges_file()

def search_and_remove_ranges(file):
    removed_ranges = []

    # Read ranges from the main file
    with open('total_completed_ranges.txt', 'r') as f:
        ranges_to_remove = set(line.strip() for line in f)

    # Read lines from the current file and remove duplicates
    with open(file, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        count = 0

        with tqdm(total=len(lines), desc=os.path.basename(file), unit='line') as pbar:
            for line in lines:
                if line.strip() in ranges_to_remove:
                    count += 1
                    removed_ranges.append(line.strip())
                else:
                    f.write(line)

                pbar.update(1)

    with open('removed_ranges.txt', 'a') as f:
        for r in removed_ranges:
            f.write(r + '\n')

    return count


if __name__ == '__main__':
    # Get the number of available processors
    num_processors = multiprocessing.cpu_count()

    # Get the list of files to process
    files = ['rangos{}.txt'.format(i) for i in range(234)]

    # Create a process pool using all available processors
    pool = multiprocessing.Pool(processes=num_processors)

    # Apply the function to each file using multiprocessing
    results = list(tqdm(pool.imap(search_and_remove_ranges, files), total=len(files), desc='Progress', unit='file'))

    # Close the process pool
    pool.close()
    pool.join()

    # Calculate the total count
    total_count = sum(results)

    print('A total of {} ranges were found and removed.'.format(total_count))
