from __future__ import annotations

from collections import defaultdict
from typing import Callable

import gotran
import networkx as nx


def _add_dependents_recursively(func: Callable[[str], set[str]], arg: str) -> set[str]:

    deps = set()

    def add_deps(root):
        dependents = func(root)
        for dependent in dependents:
            deps.add(dependent)
            add_deps(dependent)

    add_deps(arg)
    return deps


def _build_graph(func: Callable[[str], set[str]], arg: str) -> nx.DiGraph:
    G = nx.DiGraph()

    def build_graph(root):

        deps = func(root)
        for dep in deps:
            G.add_edge(root, dep)
            build_graph(dep)

    build_graph(arg)
    return G


class DependencyGraph:
    def __init__(self, ode: gotran.ODE) -> None:

        self._dependents: dict[str, set[str]] = {}
        self._inv_dependents: dict[str, set[str]] = defaultdict(set)
        self._ode = ode
        self._load_dependents()

    def _load_dependents(self):

        for intermediate in self._ode.intermediates + self._ode.state_expressions:

            self._dependents[intermediate.name] = set()
            for dependent in intermediate.dependent:

                if dependent.is_Symbol:
                    depname = str(dependent)

                else:
                    depname = str(type(dependent))

                self._dependents[intermediate.name].add(depname)
                self._inv_dependents[depname].add(intermediate.name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.ode})"

    @property
    def dependent_names(self) -> list[str]:
        return list(self._dependents.keys())

    @property
    def inv_dependent_names(self) -> list[str]:
        return list(self._inv_dependents.keys())

    @property
    def ode(self) -> gotran.ODE:
        return self._ode

    def dependents(self, name: str, direct: bool = True) -> set[str]:
        if direct:
            return self._dependents.get(name) or set()

        # Grab all decendents recursively
        return _add_dependents_recursively(self.dependents, name)

    def inv_dependents(self, name: str, direct: bool = True) -> set[str]:
        if direct:
            return self._inv_dependents.get(name) or set()

        # Grab all decendents recursively
        return _add_dependents_recursively(self.inv_dependents, name)

    def dependency_graph(self, name: str) -> nx.DiGraph:
        return _build_graph(self.dependents, name)

    def inv_dependency_graph(self, name: str):
        return _build_graph(self.inv_dependents, name)
