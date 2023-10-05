import re
import os
import concurrent.futures
import multiprocessing
from tqdm import tqdm
import tempfile
import time

def process_file(file_number, progress_list):
    input_filename = f"ranges{file_number}.txt"
    output_filename = f"ranges_exclud{file_number}.txt"
    pattern = re.compile(r'([a-zA-Z0-9])\1\1')  # Matches three or more consecutive characters
    pattern2 = re.compile(r'000|fff')

    removed_count = 0

    with open(input_filename, "r") as infile, \
         tempfile.NamedTemporaryFile(mode="w+", delete=False) as valid_tempfile, \
         tempfile.NamedTemporaryFile(mode="w+", delete=False) as excluded_tempfile:

        for line in infile:
            line_start = line[:10]  # Check first 10 characters of each line
            if pattern.search(line_start) or pattern2.search(line_start):
                excluded_tempfile.write(line)
                removed_count += 1
                progress_list.append(1)
            else:
                valid_tempfile.write(line)

    os.replace(valid_tempfile.name, input_filename)
    os.replace(excluded_tempfile.name, output_filename)

    return removed_count

def main():
    total_removed_count = 0
    cpu_count = multiprocessing.cpu_count()
    manager = multiprocessing.Manager()
    progress_list = manager.list()

    with concurrent.futures.ProcessPoolExecutor(max_workers=int(1 * cpu_count)) as executor:
        futures = {executor.submit(process_file, file_number, progress_list): file_number for file_number in range(270)}

        progress_bar = tqdm(total=sum(1 for _ in futures), desc="processing filess", unit="files")
        while not all(future.done() for future in futures):
            while progress_list:
                progress_bar.update(progress_list.pop())
            progress_bar.refresh()
            time.sleep(0.1)

        for future in futures:
            total_removed_count += future.result()

        while progress_list:
            progress_bar.update(progress_list.pop())
        progress_bar.set_postfix({"excluded ranges ": total_removed_count})
        progress_bar.close()

    print(f"Total Excluded Ranges: {total_removed_count}")

if __name__ == "__main__":
    main()
