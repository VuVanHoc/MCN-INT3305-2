import contextlib
import arithmeticcoding
import hashlib
import os
import time
from datetime import timedelta


# Command line main application function.
def main(inputfile, outputfile):
    # Handle command line arguments
    # if len(args) != 2:
    # 	sys.exit("Usage: python arithmetic-compress.py InputFile OutputFile")

    # Read input file once to compute symbol frequencies
    freqs = get_frequencies(inputfile)
    freqs.increment(256)  # EOF symbol gets a frequency of 1

    # Read input file again, compress with arithmetic coding, and write compress_file file
    with open(inputfile, "rb") as inp, \
            contextlib.closing(arithmeticcoding.BitOutputStream(open(outputfile, "wb"))) as bitout:
        write_frequencies(bitout, freqs)
        compress(freqs, inp, bitout)
    print("Compress Success !!!")


# Returns a frequency table based on the bytes in the given file.
# Also contains an extra entry for symbol 256, whose frequency is set to 0.
def get_frequencies(filepath):
    freqs = arithmeticcoding.SimpleFrequencyTable([0] * 257)
    with open(filepath, "rb") as input:
        while True:
            b = input.read(1)
            if len(b) == 0:
                break
            freqs.increment(b[0])
    return freqs


def write_frequencies(bitout, freqs):
    for i in range(256):
        write_int(bitout, 32, freqs.get(i))


def compress(freqs, inp, bitout):
    enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
    while True:
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, symbol[0])
    enc.write(freqs, 256)  # EOF
    enc.finish()  # Flush remaining code bits


# Writes an unsigned integer of the given bit width to the given stream.
def write_int(bitout, numbits, value):
    for i in reversed(range(numbits)):
        bitout.write((value >> i) & 1)  # Big endian


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

    output_file = compressed_file_folder + input_file_name + "_compressed"
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
