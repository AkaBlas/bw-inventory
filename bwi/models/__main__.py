import sys

from . import merge_comment_inputs_into_inventory

if __name__ == "__main__":
    # get single argument from command line
    arg = sys.argv[1]
    merge_comment_inputs_into_inventory(arg)
