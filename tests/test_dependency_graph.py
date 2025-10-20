from pathlib import Path


import pytest
import gotran
import gotranx
from modelgraph import DependencyGraph


here = Path(__file__).absolute().parent
ode_file = here.parent.joinpath("demo").joinpath(
    "hodgkin_huxley_squid_axon_model_1952_original.ode",
)


def handle_request_param(request):
    if request.param == "gotranx":
        return gotranx.load_ode(ode_file)

        return gotranx.load_ode(ode_file)
    elif request.param == "gotran":
        return gotran.load_ode(ode_file)
    else:
        raise ValueError(f"Unknown request param {request.param}")


@pytest.fixture(params=["gotran", "gotranx"])
def graph(request):
    ode = handle_request_param(request)
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


@pytest.mark.parametrize(
    "name, expected_edges",
    [
        (
            "i_K",
            set(
                (
                    ("i_K", "V"),
                    ("i_K", "g_K"),
                    ("i_K", "E_K"),
                    ("i_K", "n"),
                    ("E_K", "E_R"),
                ),
            ),
        ),
        ("i_L", set((("i_L", "V"), ("i_L", "g_L"), ("i_L", "E_L"), ("E_L", "E_R")))),
        (
            "dm_dt",
            set(
                (
                    ("dm_dt", "m"),
                    ("dm_dt", "beta_m"),
                    ("dm_dt", "alpha_m"),
                    ("beta_m", "V"),
                    ("alpha_m", "V"),
                ),
            ),
        ),
        ("g_L", set()),
    ],
)
def test_depedency_graph(graph, name, expected_edges):
    G = graph.dependency_graph(name)
    assert set(G.edges) == expected_edges


@pytest.mark.parametrize(
    "name, expected_edges",
    [
        ("g_Na", set((("g_Na", "i_Na"), ("i_Na", "dV_dt")))),
        (
            "E_R",
            set(
                (
                    ("E_R", "E_Na"),
                    ("E_R", "E_K"),
                    ("E_R", "E_L"),
                    ("E_Na", "i_Na"),
                    ("i_Na", "dV_dt"),
                    ("E_K", "i_K"),
                    ("i_K", "dV_dt"),
                    ("E_L", "i_L"),
                    ("i_L", "dV_dt"),
                ),
            ),
        ),
        ("dV_dt", set()),
        (
            "Cm",
            set((("Cm", "dV_dt"),)),
        ),
    ],
)
def test_inv_depedency_graph(graph, name, expected_edges):
    G = graph.inv_dependency_graph(name)
    assert set(G.edges) == expected_edges


def test_depdedent_names(graph):
    ode = graph.ode
    if isinstance(ode, gotran.ODE):
        assert set(graph.dependent_names) == set(
            [v.name for v in ode.intermediates + ode.state_expressions],
        )
    else:
        assert isinstance(ode, gotranx.ODE)
        names = [i.name for i in ode.intermediates] + [sd.name for sd in ode.state_derivatives]
        assert set(graph.dependent_names) == set(names)


def test_inv_depdedent_names(graph):
    ode = graph.ode
    if isinstance(ode, gotran.ODE):
        assert set(graph.inv_dependent_names) == set(
            [v.name for v in ode.intermediates + ode.parameters + ode.states] + ["t"],
        )
    else:
        assert isinstance(ode, gotranx.ODE)
        names = (
            [i.name for i in ode.intermediates]
            + [s.name for s in ode.states]
            + [p.name for p in ode.parameters]
            + ["time"]
        )
        assert set(graph.inv_dependent_names) == set(names)
