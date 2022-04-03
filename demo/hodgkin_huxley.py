import gotran
import matplotlib.pyplot as plt
import networkx as nx
from modelgraph import DependencyGraph

ode = gotran.load_ode("hodgkin_huxley_squid_axon_model_1952_original.ode")

# Build graph
graph = DependencyGraph(ode)

# Visualize what depends on g_Na
G_g_Na = graph.inv_dependency_graph("g_Na")

nx.draw(G_g_Na, with_labels=True, font_size=10, node_size=2000)
plt.savefig("g_Na_mpl.png")

P_g_Na = nx.nx_pydot.to_pydot(G_g_Na)
P_g_Na.write_png("g_Na_pydot.png")

# Visualize what dV_dt depdens on
G_dV_dt = graph.dependency_graph("dV_dt")

nx.draw(G_dV_dt, with_labels=True, font_size=10, node_size=2000)
plt.savefig("dV_dt_mpl.png")

P_dV_dt = nx.nx_pydot.to_pydot(G_dV_dt)
P_dV_dt.write_png("dV_dt_pydot.png")
