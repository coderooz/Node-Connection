/**
 * Network Intelligence - Main Application
 * Handles UI interactions, API calls, and graph updates
 */

// UI Manager
const UI = {
    elements: {},
    
    init() {
        // Cache DOM elements
        this.elements = {
            selectionLabel: document.getElementById('selection-label'),
            statusNodes: document.getElementById('status-nodes'),
            statusEdges: document.getElementById('status-edges'),
            statusFocus: document.getElementById('status-focus'),
            contextMenu: document.getElementById('context-menu'),
            toggleClusters: document.getElementById('toggle-clusters'),
            togglePulse: document.getElementById('toggle-pulse'),
            searchInput: document.getElementById('search-input'),
            searchBtn: document.getElementById('search-btn'),
            nodeForm: document.getElementById('node-form'),
            edgeForm: document.getElementById('edge-form'),
        };
        
        // Setup event listeners
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        // Node form
        if (this.elements.nodeForm) {
            this.elements.nodeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                API.addNode(new FormData(e.target));
            });
        }
        
        // Edge form
        if (this.elements.edgeForm) {
            this.elements.edgeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                API.addEdge(new FormData(e.target));
            });
        }
        
        // Node reset button
        const nodeReset = document.getElementById('node-reset');
        if (nodeReset) {
            nodeReset.addEventListener('click', () => {
                this.elements.nodeForm?.reset();
            });
        }
        
        // Edge delete button
        const edgeDelete = document.getElementById('edge-delete');
        if (edgeDelete) {
            edgeDelete.addEventListener('click', () => {
                const source = document.getElementById('edge-source')?.value;
                const target = document.getElementById('edge-target')?.value;
                const type = document.getElementById('edge-type')?.value;
                if (source && target) {
                    API.deleteEdge(source, target, type);
                }
            });
        }
        
        // Node delete button
        const btnDeleteNode = document.getElementById('btn-delete-node');
        if (btnDeleteNode) {
            btnDeleteNode.addEventListener('click', () => {
                const nodeId = document.getElementById('delete-node-select')?.value;
                if (nodeId) {
                    API.deleteNode(nodeId);
                }
            });
        }
        
        // Community detection
        const btnCommunity = document.getElementById('btn-community');
        if (btnCommunity) {
            btnCommunity.addEventListener('click', () => API.runCommunityDetection());
        }
        
        // Reload button
        const btnReload = document.getElementById('btn-reload');
        if (btnReload) {
            btnReload.addEventListener('click', () => API.reloadGraph());
        }
        
        // Save button
        const btnSave = document.getElementById('btn-save');
        if (btnSave) {
            btnSave.addEventListener('click', () => API.saveGraph());
        }
        
        // Reheat button
        const btnReheat = document.getElementById('btn-reheat');
        if (btnReheat) {
            btnReheat.addEventListener('click', () => GraphManager.reheat());
        }
        
        // Toggle switches
        if (this.elements.toggleClusters) {
            this.elements.toggleClusters.addEventListener('change', (e) => {
                GraphManager.toggleCommunityColors(e.target.checked);
            });
        }
        
        if (this.elements.togglePulse) {
            this.elements.togglePulse.addEventListener('change', (e) => {
                GraphManager.togglePulse(e.target.checked);
            });
        }
        
        // Search
        if (this.elements.searchBtn) {
            this.elements.searchBtn.addEventListener('click', () => {
                const query = this.elements.searchInput?.value;
                if (query) {
                    GraphManager.searchNode(query);
                }
            });
        }
        
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.elements.searchBtn?.click();
                }
            });
        }
        
        // Context menu
        this.setupContextMenu();
    },
    
    setupContextMenu() {
        const container = document.getElementById('3d-graph');
        const menu = this.elements.contextMenu;
        
        if (!container || !menu) return;
        
        // Show on right-click
        container.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const node = GraphManager.state.hoverNode || GraphManager.state.selectedNode;
            if (!node) return;
            
            GraphManager.state.selectedNode = node;
            this.updateFocusStatus(node.label || node.id);
            
            menu.style.display = 'block';
            menu.style.left = `${e.clientX + 4}px`;
            menu.style.top = `${e.clientY + 4}px`;
        });
        
        // Hide on click outside
        document.addEventListener('click', () => {
            menu.style.display = 'none';
        });
        
        // Handle menu actions
        menu.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            const node = GraphManager.state.selectedNode;
            
            if (!action || !node) return;
            e.stopPropagation();
            
            switch(action) {
                case 'focus':
                    GraphManager.handleNodeClick(node);
                    break;
                case 'neighbors':
                    GraphManager.highlightNeighbors(node);
                    break;
                case 'clear':
                    GraphManager.clearHighlights();
                    break;
            }
            
            menu.style.display = 'none';
        });
    },
    
    updateSelectionLabel(text) {
        if (this.elements.selectionLabel) {
            this.elements.selectionLabel.textContent = text;
        }
    },
    
    updateStatusCounts(nodes, edges) {
        if (this.elements.statusNodes) {
            this.elements.statusNodes.textContent = nodes;
        }
        if (this.elements.statusEdges) {
            this.elements.statusEdges.textContent = edges;
        }
    },
    
    updateFocusStatus(text) {
        if (this.elements.statusFocus) {
            this.elements.statusFocus.textContent = text || 'None';
        }
    },
    
    updateNodeSelects(nodes) {
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
            placeholder.textContent = sel.id === 'delete-node-select' 
                ? 'Select node…' 
                : 'Select…';
            sel.appendChild(placeholder);
            
            nodes.forEach(node => {
                const opt = document.createElement('option');
                opt.value = node.id;
                opt.textContent = node.label || node.id;
                sel.appendChild(opt);
            });
        });
    },
    
    showNotification(message, type = 'info') {
        // Simple alert for now - can be enhanced with toast notifications
        console.log(`[${type.toUpperCase()}]`, message);
        if (type === 'error') {
            alert(`Error: ${message}`);
        }
    }
};

// API Manager
const API = {
    async fetchGraph() {
        try {
            console.log('Fetching graph data...');
            const res = await fetch('/graph-data');
            
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            }
            
            const payload = await res.json();
            
            if (!payload.graph || !payload.graph.nodes || !payload.graph.links) {
                throw new Error('Invalid graph data structure');
            }
            
            console.log('Graph data loaded:', {
                nodes: payload.graph.nodes.length,
                links: payload.graph.links.length
            });
            
            // Update UI
            UI.updateStatusCounts(
                payload.graph.nodes.length,
                payload.graph.links.length
            );
            UI.updateNodeSelects(payload.graph.nodes);
            
            return payload;
            
        } catch (error) {
            console.error('Failed to fetch graph:', error);
            UI.updateSelectionLabel('❌ Error loading graph data');
            UI.showNotification(error.message, 'error');
            throw error;
        }
    },
    
    async addNode(formData) {
        try {
            const payload = {
                id: formData.get('id'),
                label: formData.get('label'),
                category: formData.get('category'),
                valuation: formData.get('valuation'),
                role: formData.get('role'),
                company_type: formData.get('company_type'),
                logo_url: formData.get('logo_url'),
            };
            
            const res = await fetch('/api/nodes/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to add node');
            }
            
            await this.refreshGraph();
            UI.showNotification('Node saved successfully');
            
        } catch (error) {
            console.error('Error adding node:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async deleteNode(nodeId) {
        try {
            const confirmed = confirm(`Delete node "${nodeId}" and all its edges?`);
            if (!confirmed) return;
            
            const res = await fetch('/api/nodes/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: nodeId }),
            });
            
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to delete node');
            }
            
            await this.refreshGraph();
            UI.showNotification('Node deleted successfully');
            
        } catch (error) {
            console.error('Error deleting node:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async addEdge(formData) {
        try {
            const payload = {
                source: formData.get('source'),
                target: formData.get('target'),
                relationship_type: formData.get('relationship_type'),
                impact: formData.get('impact'),
            };
            
            const res = await fetch('/api/edges/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to add edge');
            }
            
            await this.refreshGraph();
            UI.showNotification('Edge saved successfully');
            
        } catch (error) {
            console.error('Error adding edge:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async deleteEdge(source, target, relationshipType) {
        try {
            const res = await fetch('/api/edges/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source, target, relationship_type: relationshipType }),
            });
            
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to delete edge');
            }
            
            await this.refreshGraph();
            UI.showNotification('Edge deleted successfully');
            
        } catch (error) {
            console.error('Error deleting edge:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async runCommunityDetection() {
        try {
            const res = await fetch('/api/graph/community', { method: 'POST' });
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to run community detection');
            }
            
            await this.refreshGraph();
            UI.showNotification('Communities detected');
            
        } catch (error) {
            console.error('Error in community detection:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async reloadGraph() {
        try {
            const confirmed = confirm('Reload graph from disk? Unsaved changes will be lost.');
            if (!confirmed) return;
            
            const res = await fetch('/api/graph/reload', { method: 'POST' });
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to reload graph');
            }
            
            await this.refreshGraph();
            UI.showNotification('Graph reloaded from disk');
            
        } catch (error) {
            console.error('Error reloading graph:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async saveGraph() {
        try {
            const res = await fetch('/api/graph/save', { method: 'POST' });
            const result = await res.json();
            
            if (!res.ok) {
                throw new Error(result.message || 'Failed to save graph');
            }
            
            UI.showNotification('Graph saved successfully');
            
        } catch (error) {
            console.error('Error saving graph:', error);
            UI.showNotification(error.message, 'error');
        }
    },
    
    async refreshGraph() {
        const payload = await this.fetchGraph();
        GraphManager.updateData(payload.graph);
    }
};

// Application Initialization
async function initializeApp() {
    console.log('=== Network Intelligence Initializing ===');
    
    // Check dependencies
    if (typeof ForceGraph3D === 'undefined') {
        console.error('❌ ForceGraph3D library not loaded!');
        UI.updateSelectionLabel('❌ 3D graph library failed to load');
        return;
    }
    
    const container = document.getElementById('3d-graph');
    if (!container) {
        console.error('❌ Container #3d-graph not found!');
        return;
    }
    
    console.log('✓ Dependencies loaded');
    
    // Initialize UI
    UI.init();
    console.log('✓ UI initialized');
    
    // Fetch and render graph
    try {
        UI.updateSelectionLabel('Loading graph data...');
        const payload = await API.fetchGraph();
        
        // Initialize graph
        GraphManager.init(container, payload.graph, payload.physicsConfig);
        
        UI.updateSelectionLabel('✓ Graph loaded. Hover or click nodes to explore.');
        
    } catch (error) {
        console.error('Failed to initialize:', error);
    }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    setTimeout(initializeApp, 100);
}