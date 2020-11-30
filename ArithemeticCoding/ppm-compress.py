import contextlib
import sys

import arithmeticcoding
import ppmmodel
import hashlib
import os
import time
from datetime import timedelta

# Must be at least -1 and match ppm-decompress.py. Warning: Exponential memory usage at O(257^n).
MODEL_ORDER = 3


# Command line main application function.
def main(inputFile, outputFile):
    # Perform file compression
    with open(inputFile, "rb") as inp, \
            contextlib.closing(arithmeticcoding.BitOutputStream(open(outputFile, "wb"))) as bitOut:
        compress(inp, bitOut)
    print("PPM Compress Success !!!")


def compress(inp, bitOut):
    # Set up encoder and model. In this PPM model, symbol 256 represents EOF;
    # its frequency is 1 in the order -1 context but its frequency
    # is 0 in all other contexts (which have non-negative order).
    enc = arithmeticcoding.ArithmeticEncoder(32, bitOut)
    model = ppmmodel.PpmModel(MODEL_ORDER, 257, 256)
    history = []

    while True:
        # Read and encode one byte
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        symbol = symbol[0]
        encode_symbol(model, history, symbol, enc)
        model.increment_contexts(history, symbol)

        if model.model_order >= 1:
            # Prepend current symbol, dropping oldest symbol if necessary
            if len(history) == model.model_order:
                history.pop()
            history.insert(0, symbol)

    encode_symbol(model, history, 256, enc)  # EOF
    enc.finish()  # Flush remaining code bits


def encode_symbol(model, history, symbol, enc):
    # Try to use highest order context that exists based on the history suffix, such
    # that the next symbol has non-zero frequency. When symbol 256 is produced at a context
    # at any non-negative order, it means "escape to the next lower order with non-empty
    # context". When symbol 256 is produced at the order -1 context, it means "EOF".
    for order in reversed(range(len(history) + 1)):
        ctx = model.root_context
        for sym in history[: order]:
            assert ctx.subcontexts is not None
            ctx = ctx.subcontexts[sym]
            if ctx is None:
                break
        else:  # ctx is not None
            if symbol != 256 and ctx.frequencies.get(symbol) > 0:
                enc.write(ctx.frequencies, symbol)
                return
            # Else write context escape symbol and continue decrementing the order
            enc.write(ctx.frequencies, 256)
    # Logic for order = -1
    enc.write(model.order_minus1_freqs, symbol)


# Main launcher
if __name__ == "__main__":
    # main(sys.argv[1:])
    absolute_path = os.path.dirname(os.path.abspath("main.py"))

    original_file_folder = absolute_path + "/OriginalFiles/"
    compressed_file_folder = absolute_path + "/CompressedFiles/"

    input_file_name = input("Enter your filename: ")
    input_file = original_file_folder + input_file_name
    print("Input filename: " + input_file)

    # Get size of file input
    file_stats_input = os.stat(input_file)
    print(f'Input filename Size in Bytes is {file_stats_input.st_size}')

    output_file = compressed_file_folder + input_file_name + "_ppm_compressed"
    if not os.path.exists(output_file):
        open(output_file, 'w')

    start_time = time.time()

    main(input_file, output_file)

    elapsed_time_secs = time.time() - start_time

    # Get size of file output
    file_stats_output = os.stat(output_file)
    print(f'Output filename Size in Bytes is {file_stats_output.st_size}')

    print("Ti le: ", file_stats_output.st_size / file_stats_input.st_size)

    # Get time execution
    msg = "Execution took: %s secs (Wall clock time)" % timedelta(milliseconds=round(elapsed_time_secs))
    print(msg)
