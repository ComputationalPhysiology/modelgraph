import os
from pathlib import Path

import click

try:
    from importlib.metadata import metadata
except ImportError:
    # python3.7 backport
    from importlib_metadata import metadata  # type: ignore

meta = metadata("modelgraph")
__version__ = meta["Version"]
__author__ = meta["Author"]
__license__ = meta["License"]


here = Path(__file__).absolute().parent


@click.command()
@click.version_option(__version__, prog_name="modelgraph")
@click.argument("filename", required=True, type=click.Path(exists=True))
def main(filename):
    os.environ["MODELGRAPH_FILENAME"] = filename
    # Make sure we can import the required packages
    from pathlib import Path
    import sys
    import subprocess as sp

    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("Please install streamlit - python3 -m pip install streamlit")
        exit(1)

    try:
        import gotranx  # noqa: F401
    except ImportError:
        try:
            import gotran  # noqa: F401
        except ImportError:
            print("Please install gotranx or gotran - python3 -m pip install gotranx")
            exit(1)

    gui_path = Path(__file__).parent.joinpath("gui.py")
    args = [sys.executable, "-m", "streamlit", "run", gui_path.as_posix()]

    sp.run(args)
