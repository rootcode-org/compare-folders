# Copyright is waived. No warranty is provided. Unrestricted use and modification is permitted.

import os
import sys
import hashlib

PURPOSE = """\
Fast comparison of large folders

compare-folders.py [-t] [-c] <path> <path>

where,
   -t       compare file timestamps
   -c       compare file contents (overrides -t)
   <path>   path to file system folder
   
If neither option is specified then files are compared by file name and size only.
"""


def compare_folders(src_path, dst_path, checkstamp, checksum):

    # List files in each folder
    src_path = os.path.realpath(src_path)
    if not os.path.exists(src_path):
        sys.exit ('Path ' + src_path + ' does not exist')

    dst_path = os.path.realpath(dst_path)
    if not os.path.exists(dst_path):
        sys.exit ('Path ' + dst_path + ' does not exist')

    src_files = []
    for root, folders, files in os.walk(src_path):
        base_path = root[len(src_path)+1:]
        for f in files:
            src_files.append(os.path.join(base_path, f))

    dst_files = []
    for root, folders, files in os.walk(dst_path):
        base_path = root[len(dst_path)+1:]
        for f in files:
            dst_files.append(os.path.join(base_path, f))

    # Compare lists of files
    src_files.sort()
    dst_files.sort()
    i = j = 0
    src_only = []
    dst_only = []
    both = []
    while (i < len(src_files)) and (j < len(dst_files)):
        x = src_files[i]
        y = dst_files[j]
        result = (x > y) - (x < y)
        if result < 0:
            src_only.append(src_files[i])
            i += 1
        elif result > 0:
            dst_only.append(dst_files[j])
            j += 1
        else:
            both.append(src_files[i])
            i += 1
            j += 1

    src_only.extend(src_files[i:])
    dst_only.extend(dst_files[j:])

    # Output files that are present in the src folder only
    if src_only:
        print("ONLY IN {0}".format(src_path))
        for f in src_only:
            print("  " + f)
        print("\n\n")

    # Output files that are present in the dst folder only
    if dst_only:
        print("ONLY IN {0}".format(dst_path))
        for f in dst_only:
            print("  " + f)
        print("\n\n")

    # Compare files that are in both folders
    different_size = []
    different_timestamp = []
    different_checksum = []
    for f in both:
        src_file = os.path.join(src_path, f)
        dst_file = os.path.join(dst_path, f)
        if os.path.getsize(src_file) != os.path.getsize(dst_file):
            different_size.append(f)
        else:
            if checksum:
                with open(src_file, "rb") as g:
                    src_checksum = hashlib.sha256(g.read()).digest()
                with open(dst_file, "rb") as g:
                    dst_checksum = hashlib.sha256(g.read()).digest()
                if src_checksum != dst_checksum:
                    different_checksum.append(f)
            elif checkstamp:
                if os.path.getmtime(src_file) != os.path.getmtime(dst_file):
                    different_timestamp.append(f)

    # Output files that differ by file size
    if different_size:
        print("DIFFER BY SIZE:")
        for f in different_size:
            print("  " + f)
        print("\n\n")

    # Output files that differ by timestamp
    if different_timestamp:
        print("DIFFER BY TIMESTAMP:")
        for f in different_timestamp:
            print("  " + f)
        print("\n\n")

    # Output files that differ by checksum
    if different_checksum:
        print("DIFFER BY CONTENT:")
        for f in different_checksum:
            print("  " + f)
        print("\n\n")


if __name__ == '__main__':

    if len(sys.argv) < 3:
        sys.exit(PURPOSE)
    checkstamp = "-t" in sys.argv
    if checkstamp: sys.argv.pop(sys.argv.index("-t"))
    checksum = "-c" in sys.argv
    if checksum: sys.argv.pop(sys.argv.index("-c"))
    compare_folders(sys.argv[1], sys.argv[2], checkstamp, checksum)
