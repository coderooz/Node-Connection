# 3D Network Intelligence – Interactive Graph Visualizer

A product-grade, interactive **3D WebGL network visualization system** for exploring company & dependency graphs.

- 3D physics-based WebGL visualization
- Live editing of nodes and edges
- Influence-based node sizing (centrality)
- Community detection & clustering toggle
- Relationship-type colored edges with impact strength
- Impact “flow” animations and neighbor highlighting
- JSON persistence for loading/saving graph models

---

## 1. Features

### Core

- **3D WebGL graph** using `3d-force-graph` (Three.js)
- **Interactive editing** from a GUI:
  - Add / rename / delete nodes
  - Create / classify / remove edges
  - Adjust edge impact strength (0.0–1.0)
- **Node appearance**
  - Size scales with influence (eigenvector / degree centrality via NetworkX)
  - Color by community (cluster) or by category
  - Hover tooltips show:
    - Company label
    - Category, role, type
    - Valuation
    - Influence score
    - Community index
- **Edge appearance**
  - Color by relationship: hardware, software, cloud, services, VC, investment, etc.
  - Thickness scales with impact strength
  - Arrows show direction
  - Curved edges with physics
  - Animated particles to show impact “flow”
- **Real-time updates**
  - Any change via the UI triggers an immediate re-render of the 3D graph
- **Clean, modern UI**
  - Dark, glassy sidebar for controls
  - 3D canvas fills the rest of the screen
  - Zoom, pan, rotate in 3D; drag nodes with physics
- **Clustering**
  - Button to run community detection (modularity-based)
  - Toggle to color nodes by community vs. category
- **Persistence**
  - Graph auto-loads from `storage/default_network.json`
  - Save / reload actions from the UI

### Bonus

- Highlight neighbors of the selected/hovered node
- Edge animation showing “influence pulses”
- Right-click context menu on nodes:
  - Focus node
  - Highlight neighbors
  - Clear highlight
- Search & focus node by name (ID or label)
- Node metadata supports future time-series / evolution tracking

---

## 2. Tech Stack

- **Python 3.10+**
- **Flask** – local web server & API
- **NetworkX** – graph analytics & centrality
- **3d-force-graph** (Three.js) – 3D WebGL visualization in browser
- **Vanilla JS + HTML + CSS** – UI and controller in the browser

---

## 3. Project Structure

```text
project_root/
├─ app.py                    # Main entry – launches Flask & opens browser
├─ model/
│  ├─ graph_model.py         # GraphModel: nodes, edges, analytics, JSON
│  └─ node.py                # Node wrapper with business metadata
├─ ui/
│  ├─ controller.py          # AppController: UI ↔ model ↔ visualizer
│  └─ widgets.py             # Flask routes + HTML/JS single-page app
├─ visualization/
│  ├─ network_visualizer.py  # Builds WebGL-ready JSON + styling
│  └─ physics_settings.json  # Physics + theme config
├─ storage/
│  ├─ default_network.json   # Demo network (OpenAI, Nvidia, etc.)
│  └─ io_manager.py          # Save/load / seeding helper
├─ .gitignore                # 
└─ README.md                 # This file
```

---

## 4. Installation

### 4.1. Clone / copy the project

Create a folder (e.g. `network_intel`) and place all files in the shown structure.

### 4.2. Create a virtual environment (recommended)

```bash
cd project_root

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### 4.3. Install dependencies

```bash
pip install flask networkx
```

*(All other dependencies are browser-side via CDNs.)*

---

## 5. Running the app

From `project_root`:

```bash
python app.py
```

* This starts a Flask server on **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**
* Your default browser will open automatically.
* You’ll see:

  * A **left control panel** to manage the graph.
  * A **right 3D canvas** with the live network.

---
## 6. Using the application

### 6.1. Initial demo graph

On first run, the app will load the JSON at:

```text
storage/default_network.json
```

This contains a pre-built network of:

* OpenAI, Nvidia, Microsoft, Oracle, AMD, Intel, xAI, CoreWeave, Mistral, Figure AI, Anthropic, Google, Amazon
* Investment, hardware, cloud, and services edges between them

You can immediately:

* Hover nodes to inspect metadata
* Drag nodes to see the physics
* Rotate / zoom the graph

### 6.2. Adding / editing nodes

In the **Node** panel:

1. Fill in:

   * **ID / Name** (required; unique key)
   * Optional: Label, Category, Role, Valuation, Company Type, Logo URL
2. Click **Save Node**

   * The node is created or updated.
   * The 3D graph re-renders with the new influence and clustering.
3. Click **Clear** to reset the form.

### 6.3. Adding / editing edges

In the **Edge** panel:

1. Choose **Source** and **Target** from the dropdowns.
2. Select a **Type**: hardware, software, investment, cloud, services, VC, etc.
3. Set **Impact (0.0–1.0)**.
4. Click **Save Edge**.
5. The 3D graph re-renders:

   * Edge color reflects type.
   * Thickness and particle count reflect impact strength.

To delete an edge:

* Select the same **Source**, **Target**, and **Type**.
* Click **Delete Edge**.

### 6.4. Deleting nodes

In the **Maintenance** panel:

1. Choose a node from **Delete node** dropdown.
2. Click **Delete selected node**.
3. Node and all incident edges are removed.

### 6.5. Analytics & layout

In the **Model** panel:

* **Re-layout graph**: re-heats the force simulation for a fresh layout.
* **Run community detection**:

  * Runs modularity-based clustering using NetworkX.
  * Updates each node’s community.
* **Use community colors** (toggle):

  * On: node color determined by community cluster.
  * Off: node color determined by category.

### 6.6. Influence waves & impact flow

* **Influence waves** (toggle):

  * On: edges show directional particles (speed based on physics config).
  * Particle count scales with impact strength.
  * Visually represents “impact flow” through the network.

### 6.7. Search & focus

At the top-right overlay:

1. Type node **ID or label**.
2. Click **Go**.
3. The camera smoothly animates to focus on that node.
4. Status bar updates the current focus.

### 6.8. Neighbor highlighting

* Hover a node:

  * Node + neighbors get highlighted.
  * Related edges are brightened.
  * Text overlay shows the neighbor list.
* Click a node:

  * Locks focus on that node and centers camera.

### 6.9. Right-click context menu

On the 3D canvas:

1. Hover or select a node.
2. Right-click near it:

   * Context menu shows:

     * **Focus node** – camera centers on node.
     * **Highlight neighbors** – emphasize immediate neighbors.
     * **Clear highlight** – reset focus.

### 6.10. Saving and reloading

* **Save model**:

  * Persists current graph to `storage/default_network.json`.
* **Reload model**:

  * Re-reads from `storage/default_network.json` and discards unsaved changes.

---

## 7. Extensibility / Future Evolution

The architecture is intentionally modular:

* **GraphModel / Node**

  * Easy to extend with time-series data, versioning, scenario comparisons.
* **NetworkVisualizer**

  * Can be extended to:

    * Encode time slices as edge or node attributes.
    * Map temporal dynamics to animation schedules.
* **UI / controller**

  * Add additional endpoints for time-travel, snapshots, or scenario tags.
  * Integrate authentication or multi-user editing.

You can also swap or augment:

* Visualization with a dedicated front-end (React, Next.js) consuming `/graph-data`.
* Backend with FastAPI instead of Flask, without changing `GraphModel`.

