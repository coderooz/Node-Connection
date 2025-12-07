import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphModel:
    def __init__(self):
        # directed graph: edges have relation + impact
        self.G = nx.DiGraph()

    def add_node(self, name: str):
        if name not in self.G:
            self.G.add_node(name)

    def remove_node(self, name: str):
        if name in self.G:
            self.G.remove_node(name)

    def connect(self, src: str, dst: str, relation: str = "child", impact: float = 0.5):
        """Create or update a connection between two nodes."""
        try:
            impact = float(impact)
        except ValueError:
            impact = 0.5
        impact = max(0.0, min(1.0, impact))  # clamp 0–1

        self.add_node(src)
        self.add_node(dst)
        self.G.add_edge(src, dst, relation=relation, impact=impact)

    def disconnect(self, src: str, dst: str):
        if self.G.has_edge(src, dst):
            self.G.remove_edge(src, dst)

    def nodes(self):
        return list(self.G.nodes())

    def centrality(self):
        """Impact-aware importance for each node."""
        if len(self.G) == 0:
            return {}
        try:
            # Uses impact as weight, so high-impact links matter more
            return nx.eigenvector_centrality_numpy(self.G, weight="impact")
        except nx.NetworkXException:
            return nx.degree_centrality(self.G)


class Node:
    """
    Convenience wrapper so you can do:

        model = GraphModel()
        a = Node("A-company", model)
        a.connect_node("B-company", node_class="child", impact=0.5)
    """

    def __init__(self, name: str, model: GraphModel):
        self.name = name
        self.model = model
        self.model.add_node(name)

    def connect_node(self, other_name: str, node_class: str = "child", impact: float = 0.5):
        self.model.connect(self.name, other_name, relation=node_class, impact=impact)
        return self.model  # optional chaining


class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Live 3D Node / Company Network")
        self.geometry("1200x750")

        self.model = GraphModel()
        self._build_demo_data()

        self._build_ui()
        self.draw_graph()

    # ---------- demo seed ----------
    def _build_demo_data(self):
        a = Node("A-Tech", self.model)
        a.connect_node("B-Soft", node_class="child", impact=0.7)
        a.connect_node("C-Systems", node_class="child", impact=0.4)

        b = Node("B-Soft", self.model)
        b.connect_node("D-Industries", node_class="child", impact=0.6)

        c = Node("C-Systems", self.model)
        c.connect_node("D-Industries", node_class="child", impact=0.3)

        self.model.connect("D-Industries", "E-Holdings", relation="child", impact=0.9)

    # ---------- UI ----------
    def _build_ui(self):
        # Left = 3D graph canvas
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig = plt.figure(figsize=(7, 7))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.fig, master=left)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right = controls
        right = ttk.Frame(self, padding=10)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # Node list
        ttk.Label(right, text="Nodes").pack(anchor="w")
        self.node_list = tk.Listbox(right, height=10, exportselection=False)
        self.node_list.pack(fill=tk.X)
        self.node_list.bind("<<ListboxSelect>>", self.on_node_select)

        # New node
        ttk.Label(right, text="Add / rename node").pack(anchor="w", pady=(10, 0))
        self.entry_node = ttk.Entry(right)
        self.entry_node.pack(fill=tk.X, pady=2)
        ttk.Button(right, text="Add node", command=self.add_node).pack(fill=tk.X)
        ttk.Button(
            right, text="Delete selected node", command=self.delete_node
        ).pack(fill=tk.X, pady=(5, 10))

        ttk.Separator(right).pack(fill=tk.X, pady=5)

        # Connect nodes
        ttk.Label(right, text="Connect nodes").pack(anchor="w", pady=(5, 0))
        self.src_combo = ttk.Combobox(right, state="readonly")
        self.dst_combo = ttk.Combobox(right, state="readonly")
        self.src_combo.pack(fill=tk.X, pady=2)
        self.dst_combo.pack(fill=tk.X, pady=2)

        ttk.Label(right, text="Relation (class)").pack(anchor="w")
        self.relation_combo = ttk.Combobox(
            right, values=["child", "parent", "peer"], state="readonly"
        )
        self.relation_combo.current(0)
        self.relation_combo.pack(fill=tk.X, pady=2)

        ttk.Label(right, text="Impact (0.0 – 1.0)").pack(anchor="w")
        self.impact_scale = ttk.Scale(right, from_=0.0, to=1.0, orient=tk.HORIZONTAL)
        self.impact_scale.set(0.5)
        self.impact_scale.pack(fill=tk.X, pady=2)

        ttk.Button(right, text="Connect", command=self.connect_nodes).pack(
            fill=tk.X, pady=(5, 0)
        )
        ttk.Button(right, text="Disconnect", command=self.disconnect_nodes).pack(
            fill=tk.X, pady=(5, 10)
        )

        ttk.Separator(right).pack(fill=tk.X, pady=5)

        ttk.Button(right, text="Recalculate & redraw", command=self.draw_graph).pack(
            fill=tk.X
        )

        self.refresh_node_widgets()

    def refresh_node_widgets(self):
        nodes = sorted(self.model.nodes())

        # Listbox
        self.node_list.delete(0, tk.END)
        for n in nodes:
            self.node_list.insert(tk.END, n)

        # Combos
        self.src_combo["values"] = nodes
        self.dst_combo["values"] = nodes
        if nodes:
            self.src_combo.current(0)
            self.dst_combo.current(0)

    # ---------- actions ----------
    def on_node_select(self, event):
        sel = self.node_list.curselection()
        if not sel:
            return
        name = self.node_list.get(sel[0])
        self.entry_node.delete(0, tk.END)
        self.entry_node.insert(0, name)

    def add_node(self):
        name = self.entry_node.get().strip()
        if not name:
            messagebox.showwarning("No name", "Please enter a node / company name.")
            return
        self.model.add_node(name)
        self.refresh_node_widgets()
        self.draw_graph()

    def delete_node(self):
        selection = self.node_list.curselection()
        if not selection:
            messagebox.showwarning("No selection", "Select a node to delete.")
            return
        name = self.node_list.get(selection[0])
        self.model.remove_node(name)
        self.refresh_node_widgets()
        self.draw_graph()

    def connect_nodes(self):
        src = self.src_combo.get()
        dst = self.dst_combo.get()
        if not src or not dst:
            messagebox.showwarning("Missing nodes", "Select both source and target.")
            return
        if src == dst:
            messagebox.showwarning("Same node", "Choose two different nodes.")
            return
        relation = self.relation_combo.get() or "child"
        impact = float(self.impact_scale.get())
        self.model.connect(src, dst, relation=relation, impact=impact)
        self.draw_graph()

    def disconnect_nodes(self):
        src = self.src_combo.get()
        dst = self.dst_combo.get()
        if not src or not dst:
            messagebox.showwarning("Missing nodes", "Select both source and target.")
            return
        self.model.disconnect(src, dst)
        self.draw_graph()

    # ---------- drawing ----------
    def draw_graph(self):
        G = self.model.G
        self.ax.clear()

        if len(G) == 0:
            self.ax.set_title("No nodes yet. Add a company / node.")
            self.canvas.draw()
            return

        # 3D spring layout
        pos = nx.spring_layout(G, dim=3, weight="impact", seed=42)

        centrality = self.model.centrality()
        xs, ys, zs, sizes = [], [], [], []
        for n in G.nodes():
            x, y, z = pos[n]
            xs.append(x)
            ys.append(y)
            zs.append(z)
            c = centrality.get(n, 0.01)
            # base size 50, scaled by centrality
            sizes.append(50 + c * 500)

        # Draw edges as 3D segments
        for u, v, data in G.edges(data=True):
            x_vals = [pos[u][0], pos[v][0]]
            y_vals = [pos[u][1], pos[v][1]]
            z_vals = [pos[u][2], pos[v][2]]
            self.ax.plot(x_vals, y_vals, z_vals, alpha=0.4)

        # Draw nodes
        self.ax.scatter(xs, ys, zs, s=sizes, alpha=0.9)

        # Labels near each node
        for n, (x, y, z) in pos.items():
            self.ax.text(x, y, z, f" {n}", fontsize=8)

        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_title(
            "Live 3D Network (node size = propagated impact / centrality)", pad=20
        )
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
