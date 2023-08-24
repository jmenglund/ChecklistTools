import argparse
import os


class StoreExpandedPath(argparse.Action):
    """Invoke shell-like path expansion for user- and relative paths."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            filepath = os.path.abspath(os.path.expanduser(str(values)))
            setattr(namespace, self.dest, filepath)


def is_file(filename):
    """Check if a path is a file."""
    if not os.path.isfile(filename):
        msg = "{0} is not a file".format(filename)
        raise argparse.ArgumentTypeError(msg)
    else:
        return filename
