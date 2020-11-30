import arithmeticcoding
import ppmmodel
import os
import time
from datetime import timedelta

# Must be at least -1 and match ppm-compress.py. Warning: Exponential memory usage at O(257^n).
MODEL_ORDER = 3


# Command line main application function.
def main(inputFile, outputFile):
    # Perform file decompression
    with open(inputFile, "rb") as inp, open(outputFile, "wb") as out:
        bitin = arithmeticcoding.BitInputStream(inp)
        decompress(bitin, out)


def decompress(bitin, out):
    # Set up decoder and model. In this PPM model, symbol 256 represents EOF;
    # its frequency is 1 in the order -1 context but its frequency
    # is 0 in all other contexts (which have non-negative order).
    dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
    model = ppmmodel.PpmModel(MODEL_ORDER, 257, 256)
    history = []

    while True:
        # Decode and write one byte
        symbol = decode_symbol(dec, model, history)
        if symbol == 256:  # EOF symbol
            break
        out.write(bytes((symbol,)))
        model.increment_contexts(history, symbol)

        if model.model_order >= 1:
            # Prepend current symbol, dropping oldest symbol if necessary
            if len(history) == model.model_order:
                history.pop()
            history.insert(0, symbol)


def decode_symbol(dec, model, history):
    # Try to use highest order context that exists based on the history suffix. When symbol 256
    # is consumed at a context at any non-negative order, it means "escape to the next lower order
    # with non-empty context". When symbol 256 is consumed at the order -1 context, it means "EOF".
    for order in reversed(range(len(history) + 1)):
        ctx = model.root_context
        for sym in history[: order]:
            assert ctx.subcontexts is not None
            ctx = ctx.subcontexts[sym]
            if ctx is None:
                break
        else:  # ctx is not None
            symbol = dec.read(ctx.frequencies)
            if symbol < 256:
                return symbol
        # Else we read the context escape symbol, so continue decrementing the order
    # Logic for order = -1
    return dec.read(model.order_minus1_freqs)


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

    output_file = compressed_file_folder + input_file_name + "_ppm_decompressed"
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
