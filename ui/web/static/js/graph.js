/**
 * Graph Interaction Logic
 * Handles 3D graph rendering, interactions, and state management
 */

const GraphManager = {
    graph: null,
    state: {
        data: null,
        highlightNodes: new Set(),
        highlightLinks: new Set(),
        hoverNode: null,
        selectedNode: null,
        pulseEnabled: true,
        useCommunityColors: true,
    },
    
    /**
     * Initialize the 3D graph
     */
    init(container, data, physicsConfig) {
        console.log('Initializing 3D graph...', {
            nodes: data.nodes.length,
            links: data.links.length
        });
        
        this.state.data = data;
        
        // Create graph instance
        this.graph = ForceGraph3D()(container);
        
        // Configure graph
        this.graph
            .backgroundColor(physicsConfig.backgroundColor || '#050816')
            .nodeLabel(node => node.tooltip || node.label)
            .nodeRelSize(4)
            .nodeVal(node => node.size || 4)
            .nodeColor(node => this.getNodeColor(node))
            .linkColor(link => this.getLinkColor(link))
            .linkOpacity(physicsConfig.linkOpacity ?? 0.8)
            .linkWidth(link => 0.2 + (link.impact || 0) * (physicsConfig.linkWidthFactor || 3.5))
            .linkCurvature(link => link.curvature || physicsConfig.linkCurvature || 0.25)
            .linkDirectionalArrowLength(physicsConfig.arrowLength || 4)
            .linkDirectionalArrowRelPos(0.98)
            .linkDirectionalParticles(link => this.computeParticleCount(link))
            .linkDirectionalParticleWidth(2)
            .linkDirectionalParticleSpeed(physicsConfig.particleSpeed || 0.006)
            .d3VelocityDecay(physicsConfig.velocityDecay || 0.25)
            .onNodeHover(node => this.handleNodeHover(node))
            .onLinkHover(link => this.handleLinkHover(link))
            .onNodeClick(node => this.handleNodeClick(node));
        
        // Auto-fit view when stabilized
        this.graph.onEngineStop(() => {
            console.log('Graph simulation stabilized');
            this.graph.zoomToFit(900, 20);
        });
        
        // Set data
        this.graph.graphData(data);
        
        console.log('✓ Graph initialized');
    },
    
    /**
     * Update graph data
     */
    updateData(data) {
        this.state.data = data;
        if (this.graph) {
            this.graph.graphData(data);
        }
    },
    
    /**
     * Get node color based on current settings
     */
    getNodeColor(node) {
        // Highlight mode
        if (this.state.highlightNodes.size > 0) {
            if (this.state.highlightNodes.has(node)) {
                return 'rgba(250, 250, 210, 1)';
            }
            return 'rgba(71, 85, 105, 0.5)';
        }
        
        // Community or category color
        if (this.state.useCommunityColors && node.community_color) {
            return node.community_color;
        }
        return node.category_color || node.community_color || '#38bdf8';
    },
    
    /**
     * Get link color based on current settings
     */
    getLinkColor(link) {
        if (this.state.highlightLinks.size > 0) {
            if (this.state.highlightLinks.has(link)) {
                return 'rgba(251, 191, 36, 0.95)';
            }
            return 'rgba(30, 64, 175, 0.4)';
        }
        return link.color || 'rgba(148, 163, 184, 0.8)';
    },
    
    /**
     * Compute particle count for link animation
     */
    computeParticleCount(link) {
        if (!this.state.pulseEnabled) return 0;
        const impact = link.impact || 0;
        if (impact <= 0) return 0;
        return Math.max(1, Math.round(impact * 4));
    },
    
    /**
     * Handle node hover
     */
    handleNodeHover(node) {
        this.state.hoverNode = node || null;
        this.highlightNeighbors(node);
    },
    
    /**
     * Handle link hover
     */
    handleLinkHover(link) {
        this.state.highlightLinks.clear();
        if (link) {
            this.state.highlightLinks.add(link);
        }
        if (this.graph) {
            this.graph.linkColor(this.graph.linkColor());
        }
    },
    
    /**
     * Handle node click
     */
    handleNodeClick(node) {
        if (!node) return;
        
        this.state.selectedNode = node;
        UI.updateFocusStatus(node.label || node.id);
        UI.updateSelectionLabel(`Selected: ${node.label || node.id}`);
        
        // Smooth camera focus
        const distance = 80;
        const distRatio = 1 + distance / Math.hypot(node.x || 0, node.y || 0, node.z || 0);
        const newPos = {
            x: (node.x || 0) * distRatio,
            y: (node.y || 0) * distRatio,
            z: (node.z || 0) * distRatio,
        };
        this.graph.cameraPosition(newPos, node, 1500);
    },
    
    /**
     * Highlight node neighbors
     */
    highlightNeighbors(node) {
        this.state.highlightNodes.clear();
        this.state.highlightLinks.clear();
        
        if (node && this.state.data) {
            this.state.highlightNodes.add(node);
            
            (this.state.data.links || []).forEach(link => {
                const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                
                if (sourceId === node.id || targetId === node.id) {
                    this.state.highlightNodes.add(link.source);
                    this.state.highlightNodes.add(link.target);
                    this.state.highlightLinks.add(link);
                }
            });
            
            const neighbors = Array.from(this.state.highlightNodes)
                .map(n => n.label || n.id)
                .filter(name => name !== (node.label || node.id));
            
            UI.updateSelectionLabel(
                neighbors.length === 0
                    ? `Node: ${node.label || node.id} (no direct neighbors)`
                    : `Node: ${node.label || node.id} · Neighbors: ${neighbors.join(', ')}`
            );
        } else {
            UI.updateSelectionLabel('Hover or click a node to inspect neighbors.');
        }
        
        if (this.graph) {
            this.graph.nodeColor(this.graph.nodeColor());
            this.graph.linkColor(this.graph.linkColor());
        }
    },
    
    /**
     * Clear highlights
     */
    clearHighlights() {
        this.state.highlightNodes.clear();
        this.state.highlightLinks.clear();
        UI.updateSelectionLabel('Selection cleared.');
        
        if (this.graph) {
            this.graph.nodeColor(this.graph.nodeColor());
            this.graph.linkColor(this.graph.linkColor());
        }
    },
    
    /**
     * Toggle community colors
     */
    toggleCommunityColors(enabled) {
        this.state.useCommunityColors = enabled;
        if (this.graph) {
            this.graph.nodeColor(this.graph.nodeColor());
        }
    },
    
    /**
     * Toggle pulse animation
     */
    togglePulse(enabled) {
        this.state.pulseEnabled = enabled;
        if (this.graph) {
            this.graph.linkDirectionalParticles(link => this.computeParticleCount(link));
        }
    },
    
    /**
     * Reheat simulation
     */
    reheat() {
        if (this.graph) {
            this.graph.d3ReheatSimulation();
        }
    },
    
    /**
     * Search and focus node
     */
    searchNode(query) {
        if (!this.graph || !this.state.data || !query) return;
        
        const value = query.trim().toLowerCase();
        const node = (this.state.data.nodes || []).find(n => {
            return (n.label && n.label.toLowerCase() === value) || 
                   n.id.toLowerCase() === value;
        });
        
        if (!node) {
            UI.updateSelectionLabel(`No node found for "${query}".`);
            return;
        }
        
        this.handleNodeClick(node);
    }
};