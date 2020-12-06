
import sys
import arithmeticcoding
import os
import time
from datetime import timedelta


def main(inputfile, outputfile):


	# Perform file decompression
	with open(outputfile, "wb") as out, open(inputfile, "rb") as inp:
		bitin = arithmeticcoding.BitInputStream(inp)
		decompress(bitin, out)
	print('Decompress Success !!!')


def decompress(bitin, out):
    initfreqs = arithmeticcoding.FlatFrequencyTable(257)
    freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
    dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
    while True:
        # Decode and write one byte
        symbol = dec.read(freqs)
        if symbol == 256:  # EOF symbol
            break
        out.write(bytes((symbol,)))
        freqs.increment(symbol)


# Main launcher
if __name__ == "__main__":
    absolute_path = os.path.dirname(os.path.abspath("main.py"))

    original_file_folder = absolute_path + "/CompressedFiles/"
    compressed_file_folder = absolute_path + "/DecompressedFiles/"

    input_file_name = input("Enter your filename: ")
    input_file = original_file_folder + input_file_name
    print("Input filename: " + input_file)

    # Get size of file input
    file_stats_input = os.stat(input_file)
    print(f'Input filename Size in Bytes is {file_stats_input.st_size}')

    output_file = compressed_file_folder + input_file_name + "_adaptive_decompressed"
    if not os.path.exists(output_file):
        open(output_file, 'w')

    start_time = time.time()

    main(input_file, output_file)

    elapsed_time_secs = time.time() - start_time

    # Get size of file output
    file_stats_output = os.stat(output_file)
    print(f'Output filename Size in Bytes is {file_stats_output.st_size}')

    print("Ti Le: ", file_stats_output.st_size / file_stats_input.st_size)

    # Get time execution
    msg = "Execution took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))
    print(msg)