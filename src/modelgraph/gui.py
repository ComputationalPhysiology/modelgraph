import os
import tempfile
from pathlib import Path

import networkx as nx


try:
    import streamlit as st
except ImportError:
    print("Please install streamlit - python3 -m pip install streamlit")
    exit(1)

try:
    import gotranx as gotran
except ImportError:
    import gotran

from modelgraph import DependencyGraph


here = Path(__file__).absolute().parent


@st.cache_data
def get_graph():
    ode = gotran.load_ode(os.getenv("MODELGRAPH_FILENAME"))
    return DependencyGraph(ode)


def dependency_graph():
    st.title("Dendencency graph")

    graph = get_graph()

    name = st.radio("Select parameter / expression", graph.dependent_names)
    G = graph.dependency_graph(name)
    P = nx.nx_pydot.to_pydot(G)
    with tempfile.NamedTemporaryFile(suffix=".png") as temp:
        P.write_png(temp.name)
        st.image(temp.name)


def inv_dependency_graph():
    st.title("Inverse dendencency graph")

    graph = get_graph()

    name = st.radio("Select parameter / expression", graph.inv_dependent_names)
    G = graph.inv_dependency_graph(name)
    P = nx.nx_pydot.to_pydot(G)
    with tempfile.NamedTemporaryFile(suffix=".png") as temp:
        P.write_png(temp.name)
        st.image(temp.name)


if __name__ == "__main__":
    # Page settings
    st.set_page_config(page_title="modelgraph")

    # Sidebar settings
    pages = {
        "Dendencency graph": dependency_graph,
        "Inverse dendencency graph": inv_dependency_graph,
    }

    st.sidebar.title("modelgraph")

    # Radio buttons to select desired option
    keys = list(pages.keys())
    page = st.sidebar.radio("Select a page", keys)

    pages[page]()

    # About
    st.sidebar.markdown(
        """
    - [Source code](https://github.com/ComputationalPhysiology/modelgraph)
    - [Documentation](https://computationalphysiology.github.io/modelgraph/)
    """,
    )
