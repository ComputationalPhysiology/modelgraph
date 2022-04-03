from pathlib import Path

import gotran
import pytest
from modelgraph import DependencyGraph

here = Path(__file__).absolute().parent
ode_file = here.parent.joinpath("demo").joinpath(
    "hodgkin_huxley_squid_axon_model_1952_original.ode",
)


@pytest.fixture(scope="session")
def ode():
    return gotran.load_ode(ode_file)


@pytest.fixture
def graph(ode):
    return DependencyGraph(ode)


@pytest.mark.parametrize(
    "name, expected_dependents",
    [
        ("i_K", {"n", "g_K", "V", "E_K"}),
        ("i_L", {"g_L", "E_L", "V"}),
        ("dm_dt", {"beta_m", "alpha_m", "m"}),
        ("g_L", set()),
    ],
)
def test_direct_dependents(graph, name, expected_dependents):
    dependents = graph.dependents(name, direct=True)
    assert dependents == expected_dependents


@pytest.mark.parametrize(
    "name, expected_dependents",
    [
        ("i_K", {"n", "g_K", "V", "E_K", "E_R"}),
        ("i_L", {"g_L", "E_L", "V", "E_R"}),
        ("dm_dt", {"beta_m", "alpha_m", "m", "V"}),
        ("g_L", set()),
    ],
)
def test_indirect_dependents(graph, name, expected_dependents):
    dependents = graph.dependents(name, direct=False)
    assert dependents == expected_dependents


@pytest.mark.parametrize(
    "name, expected_dependents",
    [
        ("g_Na", {"i_Na"}),
        ("E_R", {"E_K", "E_L", "E_Na"}),
        ("dV_dt", set()),
        ("Cm", {"dV_dt"}),
    ],
)
def test_direct_inv_dependents(graph, name, expected_dependents):
    dependents = graph.inv_dependents(name, direct=True)
    assert dependents == expected_dependents


@pytest.mark.parametrize(
    "name, expected_dependents",
    [
        ("g_Na", {"i_Na", "dV_dt"}),
        ("E_R", {"E_K", "E_L", "E_Na", "i_L", "i_Na", "i_K", "dV_dt"}),
        ("dV_dt", set()),
        ("Cm", {"dV_dt"}),
    ],
)
def test_indirect_inv_dependents(graph, name, expected_dependents):
    dependents = graph.inv_dependents(name, direct=False)
    assert dependents == expected_dependents
