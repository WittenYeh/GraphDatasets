"""
Graph data processing tool.

Features:
1. Read and print the first k lines of a file (for data preview).
2. Count the number of edges in a graph dataset (supports .mtx header parsing or general line counting).
"""

import argparse
import sys

def read_first_k_lines(filename, k):
    """
    Reads and prints the first k lines of the specified file.

    Args:
    filename (str): The path to the file.
    k (int): The number of lines to read.
    """
    # Check if k is valid (if k is None, the user didn't provide it)
    if k is None:
        print("Error: Please provide the number of lines 'k' to read, or use the --count argument.", file=sys.stderr)
        return

    # Check if k is a positive integer
    if k <= 0:
        print(f"Error: Number of lines 'k' must be a positive integer. You provided: {k}", file=sys.stderr)
        return

    try:
        # Use 'with open' to ensure the file is closed properly
        # Specify encoding='utf-8' to handle various text files better
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"--- First {k} lines of file '{filename}' ---")
            # Read the file line by line
            for i, line in enumerate(f):
                # Stop when we reach the k-th line (enumerate starts at 0)
                if i >= k:
                    break
                # Print the line. 'line' already contains a newline, so use end=''
                print(line, end='')

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)


def count_graph_edges(filename):
    """
    Counts the number of edges in the graph dataset.

    Logic:
    1. If Matrix Market (.mtx): Parses the header information (very fast).
    2. If General Text: Counts non-comment lines (starts with # or %).

    Args:
    filename (str): Path to the file.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            first_line = f.readline()

            # Check if it is Matrix Market format
            if first_line.startswith('%%MatrixMarket'):
                # .mtx format: Edges are usually defined in the first non-comment line
                for line in f:
                    # Skip comment lines
                    if line.startswith('%'):
                        continue

                    # Find the first non-comment line. Format: Rows Cols NonZero(Edges)
                    parts = line.split()
                    if len(parts) >= 3:
                        edges = parts[2]
                        print(f"File '{filename}' identified as Matrix Market format.")
                        print(f"Edges defined in header (entries): {edges}")
                        return
                    else:
                        print("Error: Malformed Matrix Market header, could not find size definition.", file=sys.stderr)
                        return
            else:
                # General Edge List format: Count lines (skip header comments)
                count = 0

                # Check if the first line is valid (not empty, not a comment)
                if first_line.strip() and not first_line.startswith(('#', '%')):
                    count += 1

                # Continue reading the rest of the lines
                for line in f:
                    # Skip empty lines and comments
                    if line.strip() and not line.startswith(('#', '%')):
                        count += 1

                print(f"File '{filename}' identified as general edge list format.")
                print(f"Valid edges counted (lines): {count}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
    except Exception as e:
        print(f"Error counting edges: {e}", file=sys.stderr)


if __name__ == "__main__":
    # 1. Create ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Graph dataset tool: Read first k lines or count graph edges.",
        epilog="Examples:\n  Preview 10 lines: python script.py my_graph.mtx 10\n  Count edges:      python script.py my_graph.mtx -c",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 2. Add command line arguments
    # 'filename' is a positional argument, required
    parser.add_argument("filename", help="Path to the file to read")

    # 'k' is an optional positional argument (nargs='?'), ignored if -c is used
    parser.add_argument("k", type=int, nargs='?', help="Number of lines to read from the head (ignored if -c is used)")

    # Add a flag for counting edges
    parser.add_argument("-c", "--count", action="store_true", help="Count the edges of the graph data (auto-detect mtx or edge list)")

    # 3. Parse arguments
    args = parser.parse_args()

    # 4. Decide which function to execute based on arguments
    if args.count:
        # Execute edge counting
        count_graph_edges(args.filename)
    else:
        # Execute reading first k lines
        read_first_k_lines(args.filename, args.k)