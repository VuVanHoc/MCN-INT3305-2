
import contextlib
import sys
import arithmeticcoding
import os
import time
from datetime import timedelta

# Command line main application function.
def main(inputfile, outputfile):


    # Perform file compression
    with open(inputfile, "rb") as inp, \
            contextlib.closing(arithmeticcoding.BitOutputStream(open(outputfile, "wb"))) as bitOut:
        compress(inp, bitOut)
    print("Adaptive Compress Success !!!")


def compress(inp, bitout):
    initfreqs = arithmeticcoding.FlatFrequencyTable(257)
    freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
    enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
    while True:
        # Read and encode one byte
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, symbol[0])
        freqs.increment(symbol[0])
    enc.write(freqs, 256)  # EOF
    enc.finish()  # Flush remaining code bits


# Main launcher
if __name__ == "__main__":

    absolute_path = os.path.dirname(os.path.abspath("main.py"))

    original_file_folder = absolute_path + "/OriginalFiles/"
    compressed_file_folder = absolute_path + "/CompressedFiles/"

    input_file_name = input("Enter your filename: ")
    input_file = original_file_folder + input_file_name
    print("Input filename: " + input_file)

    # Get size of file input
    file_stats_input = os.stat(input_file)
    print(f'Input filename Size in Bytes is {file_stats_input.st_size}')

    output_file = compressed_file_folder + input_file_name + "_adaptive_compressed"
    if not os.path.exists(output_file):
        open(output_file, 'w')

    start_time = time.time()

    main(input_file, output_file)

    elapsed_time_secs = time.time() - start_time

    # Get size of file output
    file_stats_output = os.stat(output_file)
    print(f'Output filename Size in Bytes is {file_stats_output.st_size}')

    print("Ti Le: " , file_stats_output.st_size/file_stats_input.st_size)

    # Get time execution
    msg = "Execution took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))
    print(msg)