"""
Interactive 3D-style company / node network

- Build your graph in Python using GraphModel + Node
- Visualize + edit it interactively in the browser (PyVis / vis.js)
- Node size = propagated impact (eigenvector centrality)
- Edge color = relationship type (investment, service, etc.)

Run:
    python company_network_3d.py

Then open the generated HTML file in your browser.
"""

from pyvis.network import Network
import networkx as nx


# -------------------------------------------------------------------
# Core data model
# -------------------------------------------------------------------

class GraphModel:
    """
    Directed graph with edge metadata:

        relation: string (child, parent, investment, hardware, ...)
        impact: float in [0,1] (0 = no contact, 1 = total dependency)
    """

    def __init__(self):
        self.G = nx.DiGraph()

    def add_node(self, name: str, **attrs):
        if name not in self.G:
            self.G.add_node(name, **attrs)
        else:
            # update attributes if node exists
            self.G.nodes[name].update(attrs)

    def remove_node(self, name: str):
        if name in self.G:
            self.G.remove_node(name)

    def connect(self, src: str, dst: str,
                relation: str = "relation",
                impact: float = 0.5,
                **attrs):
        """
        Create or update a connection between two nodes.

        impact: 0.0 – 1.0
        """
        try:
            impact = float(impact)
        except ValueError:
            impact = 0.5
        impact = max(0.0, min(1.0, impact))  # clamp

        self.add_node(src)
        self.add_node(dst)

        data = {"relation": relation, "impact": impact}
        data.update(attrs)
        self.G.add_edge(src, dst, **data)

    def disconnect(self, src: str, dst: str):
        if self.G.has_edge(src, dst):
            self.G.remove_edge(src, dst)

    def nodes(self):
        return list(self.G.nodes())

    def edges(self):
        return list(self.G.edges(data=True))

    def centrality(self):
        """Impact-aware importance for each node."""
        if len(self.G) == 0:
            return {}
        try:
            return nx.eigenvector_centrality_numpy(self.G, weight="impact")
        except nx.NetworkXException:
            # fallback
            return nx.degree_centrality(self.G)


class Node:
    """
    Convenience wrapper to create & connect nodes.

    Example:
        model = GraphModel()
        r = Node("A-company", model)
        r.connect_node("B-company", node_class="child", impact=0.5)
    """

    def __init__(self, name: str, model: GraphModel, **attrs):
        self.name = name
        self.model = model
        self.model.add_node(name, **attrs)

    def connect_node(self,
                     other_name: str,
                     node_class: str = "relation",
                     impact: float = 0.5,
                     **attrs):
        """
        node_class maps to edge['relation'].

        e.g. "investment", "services", "hardware", "VC", "child", "parent"
        """
        self.model.connect(
            self.name,
            other_name,
            relation=node_class,
            impact=impact,
            **attrs
        )
        return self.model  # allow chaining if you like


# -------------------------------------------------------------------
# Visualization layer: PyVis / vis.js
# -------------------------------------------------------------------

class LiveNetworkVisualizer:
    """
    Takes a GraphModel and renders an interactive HTML network.

    - drag nodes
    - zoom / pan
    - add/edit/delete nodes & edges in the browser (manipulation)
    """

    # mapping from relation (edge type) to color
    RELATION_COLORS = {
        # you can customize these labels and colors
        "hardware": "#ff1493",       # pink
        "software": "#ff8c00",       # orange
        "investment": "#00e676",     # green
        "services": "#00b0ff",       # light blue
        "vc": "#9c27b0",             # purple
        "child": "#00e676",
        "parent": "#ffeb3b",
        "peer": "#ff6f00",
    }

    def __init__(self, model: GraphModel, title: str = "Company Network"):
        self.model = model
        self.title = title

    def _edge_color(self, relation: str) -> str:
        return self.RELATION_COLORS.get(relation.lower(), "#cccccc")

    def render(self, output_html: str = "company_network.html"):
        G = self.model.G
        if len(G) == 0:
            raise ValueError("Graph is empty. Add some nodes / edges first.")

        # height/width "100%" so browser window can control the viewport
        net = Network(
            height="100%",
            width="100%",
            bgcolor="#111111",
            font_color="#eeeeee",
            directed=True,
            notebook=False,
        )

        # Physics: barnes_hut = force-directed (nice organic layout)
        net.barnes_hut(
            gravity=-8000,
            central_gravity=0.1,
            spring_length=200,
            spring_strength=0.01,
            damping=0.8
        )


        centrality = self.model.centrality()
        max_central = max(centrality.values()) if centrality else 1.0

        # ------------- add nodes -------------
        for n, attrs in G.nodes(data=True):
            influence = centrality.get(n, 0.0)
            # scale size between 10 and 70
            size = 10 + (influence / max_central) * 60 if max_central else 20

            title_lines = [f"<b>{n}</b>"]
            if influence:
                title_lines.append(f"Influence score: {influence:.3f}")
            if attrs:
                for k, v in attrs.items():
                    title_lines.append(f"{k}: {v}")

            net.add_node(
                n,
                label=n,
                size=size,
                title="<br>".join(title_lines),
                color="#3aa8ff",  # default node color; can be overridden per node
            )

        # ------------- add edges -------------
        for u, v, data in G.edges(data=True):
            relation = data.get("relation", "relation")
            impact = data.get("impact", 0.5)
            impact = max(0.0, min(1.0, float(impact)))

            width = 1 + impact * 7  # line thickness
            color = self._edge_color(relation)

            title_lines = [f"{u} → {v}", f"Type: {relation}", f"Impact: {impact:.2f}"]
            # include any other metadata
            for k, v_attr in data.items():
                if k not in ("relation", "impact"):
                    title_lines.append(f"{k}: {v_attr}")

            net.add_edge(
                u,
                v,
                value=impact,    # used by some physics / clustering options
                width=width,
                color=color,
                title="<br>".join(title_lines),
                arrows="to"
            )

        # ------------- UI / interaction options -------------
        # show some built-in control panels
        net.show_buttons(filter_=["physics", "interaction", "nodes", "edges"])

        # enable node/edge manipulation (add / edit / delete) in browser
        options = """
        var options = {
          "interaction": {
            "hover": true,
            "dragNodes": true,
            "multiselect": true,
            "navigationButtons": true
          },
          "manipulation": {
            "enabled": true,
            "initiallyActive": true
          },
          "nodes": {
            "shape": "dot",
            "borderWidth": 1,
            "shadow": true,
            "scaling": {
              "min": 10,
              "max": 70
            },
            "font": {
              "size": 18,
              "strokeWidth": 3
            }
          },
          "edges": {
            "smooth": {
              "type": "dynamic"
            },
            "shadow": true,
            "arrows": {
              "to": {"enabled": true, "scaleFactor": 0.8}
            }
          },
          "physics": {
            "enabled": true,
            "stabilization": {
              "iterations": 500
            }
          }
        }
        """
        net.set_options(options)

        # write HTML and open it (default browser)
        net.show(output_html)
        print(f"[OK] Network written to: {output_html}")


# -------------------------------------------------------------------
# Demo data: rough analogue of the Nvidia / OpenAI style graph
# -------------------------------------------------------------------

def build_demo_graph() -> GraphModel:
    model = GraphModel()

    # Big players
    openai = Node("OpenAI", model, market_value="$500B")
    nvidia = Node("Nvidia", model, market_value="$4.5T")
    oracle = Node("Oracle", model, market_value="$1.0T")
    microsoft = Node("Microsoft", model, market_value="$3.9T")
    amd = Node("AMD", model)
    intel = Node("Intel", model)
    xai = Node("xAI", model)
    coreweave = Node("CoreWeave", model)
    mistral = Node("Mistral", model)
    figure_ai = Node("Figure AI", model)

    # Example relations (totally illustrative, not accurate numbers)
    # investment relations
    nvidia.connect_node("OpenAI", node_class="investment", impact=0.9,
                        note="Invest up to $100B")
    microsoft.connect_node("OpenAI", node_class="investment", impact=0.8)
    nvidia.connect_node("xAI", node_class="investment", impact=0.6)
    nvidia.connect_node("CoreWeave", node_class="investment", impact=0.5)

    # hardware / supply
    amd.connect_node("OpenAI", node_class="hardware", impact=0.7,
                     note="GPU supply, share options")
    nvidia.connect_node("OpenAI", node_class="hardware", impact=0.9)
    intel.connect_node("Cloud Partners", node_class="hardware", impact=0.4)

    # cloud / services
    oracle.connect_node("OpenAI", node_class="services", impact=0.9,
                        note="Cloud infrastructure")
    microsoft.connect_node("OpenAI", node_class="services", impact=0.9,
                           note="Azure cloud & integration")

    # ecosystem startups
    openai.connect_node("Harvey AI", node_class="software", impact=0.4)
    openai.connect_node("Anysphere", node_class="software", impact=0.4)
    openai.connect_node("Ambience Healthcare", node_class="software", impact=0.4)

    nvidia.connect_node("Mistral", node_class="vc", impact=0.3)
    nvidia.connect_node("Figure AI", node_class="vc", impact=0.3)

    return model


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    # 1) build a demo graph (you can replace with your own)
    model = build_demo_graph()

    # 2) or build your own using the Node API:
    #
    #   model = GraphModel()
    #   r = Node("A-company", model)
    #   r.connect_node("B-company", node_class="investment", impact=0.5)
    #   r.connect_node("C-company", node_class="services", impact=0.8)
    #
    #   # more edges...
    #

    # 3) render to HTML
    visualizer = LiveNetworkVisualizer(model, title="Company Relationship Universe")
    visualizer.render("company_network.html")
