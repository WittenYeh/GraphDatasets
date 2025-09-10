import numpy as np
from scipy.io import mmread
from scipy.sparse import csr_matrix
import struct
import os
import argparse
from tqdm import tqdm

def write_binary_with_progress(file_path, data_array):
    """
    Writes a NumPy array to a file in binary format with a progress bar.

    Args:
        file_path (str): The path to the output file.
        data_array (np.ndarray): The NumPy array to be written.
    """
    # Define the write buffer size in bytes, 64KB
    buffer_size = 65536
    item_size = data_array.itemsize
    # Calculate how many items fit in one chunk
    chunk_size_items = buffer_size // item_size if item_size > 0 else buffer_size

    with open(file_path, 'wb') as f:
        # Write the file header
        # The first 8 bytes: total number of valid elements in the file.
        f.write(struct.pack('Q', len(data_array)))
        # The second 8 bytes: a placeholder.
        f.write(struct.pack('Q', 0))

        # Use tqdm to display writing progress
        with tqdm(total=len(data_array), unit='elements', desc=f"Writing {os.path.basename(file_path)}") as pbar:
            # Write in chunks to show a smooth progress bar
            for i in range(0, len(data_array), chunk_size_items):
                chunk = data_array[i:i + chunk_size_items]
                f.write(chunk.tobytes())
                pbar.update(len(chunk))


def convert_matrix_market_to_custom_binary(matrix_market_path, output_dataset_name):
    """
    Converts a graph dataset from Matrix Market format to a custom binary CSR format.
    Automatically creates the output directory if it does not exist.

    Args:
        matrix_market_path (str): The path to the input Matrix Market (.mtx) file.
        output_dataset_name (str): The base name for the output files, which can include a path.
    """
    # --- New Feature: Automatically create output directory ---
    output_dir = os.path.dirname(output_dataset_name)
    # If output_dir is not an empty string and the directory does not exist, create it.
    if output_dir and not os.path.exists(output_dir):
        print(f"Output directory '{output_dir}' does not exist. Creating it...")
        os.makedirs(output_dir, exist_ok=True)
    # --- End of New Feature ---

    print(f"Reading Matrix Market file from {matrix_market_path}...")
    try:
        coo_matrix = mmread(matrix_market_path)
        print("Read complete.")
        # Check if the matrix is of "pattern" type (unweighted)
        if coo_matrix.data is None or len(coo_matrix.data) != coo_matrix.getnnz():
            print("Detected an unweighted (pattern) graph. Edge weights will be set to 1.0.")
            coo_matrix.data = np.ones(coo_matrix.getnnz(), dtype=np.float32)

    except FileNotFoundError:
        print(f"Error: File '{matrix_market_path}' not found. Please check the path.")
        return
    except Exception as e:
        print(f"An error occurred while reading or processing the file: {e}")
        return

    print("Converting matrix to CSR format...")
    csr_mat = coo_matrix.tocsr()

    # Extract the three key arrays of the CSR format
    row_offsets = csr_mat.indptr.astype(np.uint64)
    col_indices = csr_mat.indices.astype(np.uint64)
    edge_weights = csr_mat.data.astype(np.float32)

    # Define output filenames
    dst_file = f"{output_dataset_name}.bel.dst"  # Expected to contain Column Indices
    col_file = f"{output_dataset_name}.bel.col"  # Expected to contain Row Offsets
    val_file = f"{output_dataset_name}.bel.val"

    # --- Write the three binary files ---
    # FIX: Ensure the correct data is written to the correct file
    # The CUDA code reads row offsets from the .col file
    write_binary_with_progress(col_file, row_offsets)
    # The CUDA code reads column indices from the .dst file
    write_binary_with_progress(dst_file, col_indices)
    
    write_binary_with_progress(val_file, edge_weights)

    print("\nConversion successful! The following files have been generated:")
    print(f"- {col_file} (CSR.indptr)")
    print(f"- {dst_file} (CSR.indices)")
    print(f"- {val_file} (CSR.data)")


if __name__ == '__main__':
    # Create a command-line argument parser
    parser = argparse.ArgumentParser(
        description="Converts a graph file from Matrix Market format to a custom binary CSR format.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Add the required arguments
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input Matrix Market file (e.g., my_graph.mtx)"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Base name for the output files, without extension.\n"
             "Can include a path (e.g., data/output/my_dataset).\n"
             "The directory will be created if it does not exist."
    )

    # Parse the arguments passed from the command line
    args = parser.parse_args()

    # Call the main function
    convert_matrix_market_to_custom_binary(args.input_file, args.output_dir)