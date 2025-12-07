let Graph = null;
let graphState = {
    data: null,
    highlightNodes: new Set(),
    highlightLinks: new Set(),
    hoverNode: null,
    selectedNode: null,
    pulseEnabled: true,
    useCommunityColors: true,
};

const selectionLabelEl = document.getElementById('selection-label');
const statusNodesEl = document.getElementById('status-nodes');
const statusEdgesEl = document.getElementById('status-edges');
const statusFocusEl = document.getElementById('status-focus');
const contextMenuEl = document.getElementById('context-menu');
const toggleClustersEl = document.getElementById('toggle-clusters');
const togglePulseEl = document.getElementById('toggle-pulse');

function setSelectionLabel(text) {
    if (selectionLabelEl) {
        selectionLabelEl.textContent = text;
    }
}

function updateStatusCounts() {
    if (!graphState.data) return;
    const nodes = graphState.data.nodes || [];
    const links = graphState.data.links || [];
    if (statusNodesEl) statusNodesEl.textContent = nodes.length;
    if (statusEdgesEl) statusEdgesEl.textContent = links.length;
}

function updateNodeSelects() {
    if (!graphState.data) return;
    const nodes = graphState.data.nodes || [];
    const selects = [
        document.getElementById('edge-source'),
        document.getElementById('edge-target'),
        document.getElementById('delete-node-select'),
    ];
    
    selects.forEach(sel => {
        if (!sel) return;
        sel.innerHTML = '';
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = sel.id === 'delete-node-select' ? 'Select node…' : 'Select…';
        sel.appendChild(placeholder);
        
        nodes.forEach(node => {
            const opt = document.createElement('option');
            opt.value = node.id;
            opt.textContent = node.label || node.id;
            sel.appendChild(opt);
        });
    });
}

async function fetchGraph() {
    try {
        console.log('Fetching graph data...');
        const res = await fetch('/graph-data');
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const payload = await res.json();
        
        // Validate data structure
        if (!payload.graph || !payload.graph.nodes || !payload.graph.links) {
            throw new Error('Invalid graph data structure');
        }
        
        graphState.data = payload.graph;
        
        console.log('Graph data loaded:', {
            nodes: graphState.data.nodes.length,
            links: graphState.data.links.length,
            payload: payload
        });
        
        updateStatusCounts();
        updateNodeSelects();
        
        if (!Graph) {
            // Wait a bit to ensure container has dimensions
            setTimeout(() => initGraph(payload), 100);
        } else {
            Graph.graphData(graphState.data);
        }
    } catch (error) {
        console.error('Failed to fetch graph:', error);
        setSelectionLabel('❌ Error loading graph data. Check console.');
    }
}

function initGraph(payload) {
    const data = payload.graph;
    const physicsConfig = payload.physicsConfig || {};
    const container = document.getElementById('3d-graph');

    if (!container) {
        console.error('Container #3d-graph not found!');
        return;
    }

    // Check container has dimensions
    const rect = container.getBoundingClientRect();
    console.log('Container dimensions:', rect.width, 'x', rect.height);
    
    if (rect.width === 0 || rect.height === 0) {
        console.error('Container has zero dimensions!');
        setSelectionLabel('❌ Container not ready. Refresh page.');
        return;
    }

    // Validate data
    if (!data.nodes || data.nodes.length === 0) {
        console.error('No nodes in graph data!');
        setSelectionLabel('❌ No nodes to display.');
        return;
    }

    console.log('Initializing ForceGraph3D with', data.nodes.length, 'nodes and', data.links.length, 'links');

    try {
        // Initialize graph
        Graph = ForceGraph3D()(container);
        
        // Configure graph properties
        Graph
            .backgroundColor(physicsConfig.backgroundColor || '#050816')
            .nodeLabel(node => node.tooltip || node.label)
            .nodeRelSize(4)
            .nodeVal(node => node.size || 4)
            .nodeColor(node => getNodeColor(node))
            .linkColor(link => getLinkColor(link))
            .linkOpacity(physicsConfig.linkOpacity ?? 0.8)
            .linkWidth(link => 0.2 + (link.impact || 0) * (physicsConfig.linkWidthFactor || 3.5))
            .linkCurvature(link => link.curvature || physicsConfig.linkCurvature || 0.25)
            .linkDirectionalArrowLength(physicsConfig.arrowLength || 4)
            .linkDirectionalArrowRelPos(0.98)
            .linkDirectionalParticles(link => computeParticleCount(link))
            .linkDirectionalParticleWidth(2)
            .linkDirectionalParticleSpeed(physicsConfig.particleSpeed || 0.006)
            .d3VelocityDecay(physicsConfig.velocityDecay || 0.25)
            .onNodeHover(handleNodeHover)
            .onLinkHover(handleLinkHover)
            .onNodeClick(handleNodeClick);

        // Auto-fit view when simulation stabilizes
        Graph.onEngineStop(() => {
            console.log('Graph simulation stabilized, fitting view');
            Graph.zoomToFit(900, 20);
        });

        // Set graph data
        Graph.graphData(data);
        
        // Attach context menu
        attachContextMenu(container);
        
        console.log('✓ Graph initialized successfully');
        setSelectionLabel('✓ Graph loaded. Hover or click nodes to explore.');
        
    } catch (error) {
        console.error('Failed to initialize graph:', error);
        setSelectionLabel('❌ Failed to initialize graph. See console.');
    }
}

function computeParticleCount(link) {
    if (!graphState.pulseEnabled) return 0;
    const impact = link.impact || 0;
    if (impact <= 0) return 0;
    return Math.max(1, Math.round(impact * 4));
}

function getNodeColor(node) {
    if (graphState.highlightNodes.size > 0) {
        if (graphState.highlightNodes.has(node)) {
            return 'rgba(250, 250, 210, 1)';
        }
        return 'rgba(71, 85, 105, 0.5)';
    }

    if (graphState.useCommunityColors && node.community_color) {
        return node.community_color;
    }
    return node.category_color || node.community_color || '#38bdf8';
}

function getLinkColor(link) {
    if (graphState.highlightLinks.size > 0) {
        if (graphState.highlightLinks.has(link)) {
            return 'rgba(251, 191, 36, 0.95)';
        }
        return 'rgba(30, 64, 175, 0.4)';
    }
    return link.color || 'rgba(148, 163, 184, 0.8)';
}

function handleNodeHover(node) {
    graphState.hoverNode = node || null;
    highlightNeighbors(node);
}

function handleLinkHover(link) {
    graphState.highlightLinks.clear();
    if (link) {
        graphState.highlightLinks.add(link);
    }
    if (Graph) {
        Graph.linkColor(Graph => getLinkColor);
    }
}

function handleNodeClick(node) {
    if (!node) return;
    graphState.selectedNode = node;
    if (statusFocusEl) statusFocusEl.textContent = node.label || node.id || 'Node';
    setSelectionLabel(`Selected: ${node.label || node.id}`);
    
    // Smooth camera focus
    const distance = 80;
    const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);
    const newPos = {
        x: (node.x || 0) * distRatio,
        y: (node.y || 0) * distRatio,
        z: (node.z || 0) * distRatio,
    };
    Graph.cameraPosition(newPos, node, 1500);
}

function highlightNeighbors(node) {
    graphState.highlightNodes.clear();
    graphState.highlightLinks.clear();
    
    if (node && graphState.data) {
        graphState.highlightNodes.add(node);
        (graphState.data.links || []).forEach(link => {
            // Handle both object and string references
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
            
            if (sourceId === node.id || targetId === node.id) {
                graphState.highlightNodes.add(link.source);
                graphState.highlightNodes.add(link.target);
                graphState.highlightLinks.add(link);
            }
        });
        
        const neighbors = Array.from(graphState.highlightNodes)
            .map(n => n.label || n.id)
            .filter(name => name !== (node.label || node.id));
        
        setSelectionLabel(
            neighbors.length === 0
                ? `Node: ${node.label || node.id} (no direct neighbors)`
                : `Node: ${node.label || node.id} · Neighbors: ${neighbors.join(', ')}`
        );
    } else {
        setSelectionLabel('Hover or click a node to inspect neighbors.');
    }

    if (Graph) {
        Graph.nodeColor(Graph => getNodeColor);
        Graph.linkColor(Graph => getLinkColor);
    }
}

function attachContextMenu(container) {
    container.addEventListener('contextmenu', (event) => {
        event.preventDefault();
        const node = graphState.hoverNode || graphState.selectedNode;
        if (!node || !contextMenuEl) return;
        graphState.selectedNode = node;
        if (statusFocusEl) statusFocusEl.textContent = node.label || node.id;
        contextMenuEl.style.display = 'block';
        contextMenuEl.style.left = `${event.clientX + 4}px`;
        contextMenuEl.style.top = `${event.clientY + 4}px`;
    });

    document.addEventListener('click', () => {
        if (contextMenuEl) contextMenuEl.style.display = 'none';
    });

    if (contextMenuEl) {
        contextMenuEl.addEventListener('click', (event) => {
            const action = event.target.getAttribute('data-action');
            const node = graphState.selectedNode;
            if (!action || !node) return;
            event.stopPropagation();
            
            if (action === 'focus') {
                handleNodeClick(node);
            } else if (action === 'neighbors') {
                highlightNeighbors(node);
            } else if (action === 'clear') {
                graphState.highlightNodes.clear();
                graphState.highlightLinks.clear();
                setSelectionLabel('Selection cleared.');
                if (Graph) {
                    Graph.nodeColor(Graph => getNodeColor);
                    Graph.linkColor(Graph => getLinkColor);
                }
            }
            contextMenuEl.style.display = 'none';
        });
    }
}

// ---------- Form handlers ----------

const nodeForm = document.getElementById('node-form');
if (nodeForm) {
    nodeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const payload = {
            id: form.id.value,
            label: form.label.value,
            category: form.category.value,
            valuation: form.valuation.value,
            role: form.role.value,
            company_type: form.company_type.value,
            logo_url: form.logo_url.value,
        };
        
        try {
            const res = await fetch('/api/nodes/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                await fetchGraph();
            }
        } catch (error) {
            console.error('Failed to add node:', error);
        }
    });
}

const nodeReset = document.getElementById('node-reset');
if (nodeReset) {
    nodeReset.addEventListener('click', () => {
        const form = document.getElementById('node-form');
        if (form) form.reset();
    });
}

const edgeForm = document.getElementById('edge-form');
if (edgeForm) {
    edgeForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.target;
        const payload = {
            source: form.source.value,
            target: form.target.value,
            relationship_type: form.relationship_type.value,
            impact: form.impact.value,
        };
        
        try {
            const res = await fetch('/api/edges/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                await fetchGraph();
            }
        } catch (error) {
            console.error('Failed to add edge:', error);
        }
    });
}

const edgeDelete = document.getElementById('edge-delete');
if (edgeDelete) {
    edgeDelete.addEventListener('click', async () => {
        const source = document.getElementById('edge-source')?.value;
        const target = document.getElementById('edge-target')?.value;
        const relationship_type = document.getElementById('edge-type')?.value;
        if (!source || !target) return;
        
        try {
            const res = await fetch('/api/edges/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source, target, relationship_type }),
            });
            if (res.ok) {
                await fetchGraph();
            }
        } catch (error) {
            console.error('Failed to delete edge:', error);
        }
    });
}

const btnDeleteNode = document.getElementById('btn-delete-node');
if (btnDeleteNode) {
    btnDeleteNode.addEventListener('click', async () => {
        const nodeId = document.getElementById('delete-node-select')?.value;
        if (!nodeId) return;
        
        try {
            const res = await fetch('/api/nodes/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: nodeId }),
            });
            if (res.ok) {
                await fetchGraph();
            }
        } catch (error) {
            console.error('Failed to delete node:', error);
        }
    });
}

const btnCommunity = document.getElementById('btn-community');
if (btnCommunity) {
    btnCommunity.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/graph/community', { method: 'POST' });
            if (res.ok) {
                await fetchGraph();
            }
        } catch (error) {
            console.error('Failed to run community detection:', error);
        }
    });
}

const btnReload = document.getElementById('btn-reload');
if (btnReload) {
    btnReload.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/graph/reload', { method: 'POST' });
            if (res.ok) {
                await fetchGraph();
            }
        } catch (error) {
            console.error('Failed to reload graph:', error);
        }
    });
}

const btnSave = document.getElementById('btn-save');
if (btnSave) {
    btnSave.addEventListener('click', async () => {
        try {
            await fetch('/api/graph/save', { method: 'POST' });
            alert('Graph saved successfully!');
        } catch (error) {
            console.error('Failed to save graph:', error);
            alert('Failed to save graph');
        }
    });
}

const btnReheat = document.getElementById('btn-reheat');
if (btnReheat) {
    btnReheat.addEventListener('click', () => {
        if (Graph) {
            Graph.d3ReheatSimulation();
        }
    });
}

if (toggleClustersEl) {
    toggleClustersEl.addEventListener('change', () => {
        graphState.useCommunityColors = toggleClustersEl.checked;
        if (Graph) Graph.nodeColor(Graph => getNodeColor);
    });
}

if (togglePulseEl) {
    togglePulseEl.addEventListener('change', () => {
        graphState.pulseEnabled = togglePulseEl.checked;
        if (Graph) {
            Graph.linkDirectionalParticles(link => computeParticleCount(link));
        }
    });
}

const searchBtn = document.getElementById('search-btn');
if (searchBtn) {
    searchBtn.addEventListener('click', () => {
        const value = document.getElementById('search-input')?.value.trim().toLowerCase();
        if (!Graph || !graphState.data || !value) return;
        
        const node = (graphState.data.nodes || []).find(n => {
            return (n.label && n.label.toLowerCase() === value) || n.id.toLowerCase() === value;
        });
        
        if (!node) {
            setSelectionLabel(`No node found for "${value}".`);
            return;
        }
        
        graphState.selectedNode = node;
        if (statusFocusEl) statusFocusEl.textContent = node.label || node.id;
        setSelectionLabel(`Focused: ${node.label || node.id}`);
        handleNodeClick(node);
    });
}

const searchInput = document.getElementById('search-input');
if (searchInput) {
    searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchBtn?.click();
        }
    });
}

// Initialize when DOM is ready
function initialize() {
    console.log('=== Network Intelligence Initializing ===');
    console.log('DOM ready, checking dependencies...');
    
    // Check if ForceGraph3D is loaded
    if (typeof ForceGraph3D === 'undefined') {
        console.error('❌ ForceGraph3D library not loaded!');
        setSelectionLabel('❌ 3D graph library failed to load. Check internet connection.');
        return;
    }
    
    console.log('✓ ForceGraph3D library loaded');
    
    // Check container exists
    const container = document.getElementById('3d-graph');
    if (!container) {
        console.error('❌ Container #3d-graph not found!');
        return;
    }
    
    console.log('✓ Container found');
    console.log('Fetching graph data...');
    
    // Fetch and initialize graph
    fetchGraph();
}

// Wait for both DOM and 3d-force-graph library
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    // DOM already loaded, but wait a bit for scripts
    setTimeout(initialize, 100);
}