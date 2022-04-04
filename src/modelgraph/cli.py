import os
from pathlib import Path

import click


here = Path(__file__).absolute().parent
graph = None


@click.command()
@click.argument("filename", required=True, type=click.Path(exists=True))
def main(filename):
    os.environ["MODELGRAPH_FILENAME"] = filename
    # Make sure we can import the required packages
    from . import gui  # noqa: F401
    from pathlib import Path

    gui_path = Path(__file__).parent.joinpath("gui.py")
    import subprocess as sp

    sp.run(["streamlit", "run", gui_path.as_posix()])
