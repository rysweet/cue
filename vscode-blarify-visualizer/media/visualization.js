// Import Three.js as ES module
import * as THREE from window.threeModuleUrl;

class BlarifyVisualization {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.nodes = new Map();
        this.edges = new Map();
        this.selectedNode = null;
        this.hoveredNode = null;
        
        this.nodeGeometry = new THREE.SphereGeometry(1, 16, 16);
        this.nodeMaterials = new Map();
        this.edgeMaterial = new THREE.LineBasicMaterial({ 
            color: 0x666666,
            opacity: 0.5,
            transparent: true 
        });
        
        this.layout = 'force-directed';
        this.forceSimulation = null;
        
        this.init();
        this.setupEventListeners();
        this.animate();
        
        // Notify extension that webview is ready
        this.postMessage({ command: 'ready' });
    }
    
    init() {
        const container = document.getElementById('visualization');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1e1e1e);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 10000);
        this.camera.position.set(0, 0, 200);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(this.renderer.domElement);
        
        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight.position.set(100, 100, 100);
        this.scene.add(directionalLight);
        
        // Grid helper
        const gridHelper = new THREE.GridHelper(1000, 50, 0x444444, 0x222222);
        gridHelper.rotation.x = Math.PI / 2;
        this.scene.add(gridHelper);
    }
    
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Mouse events
        this.renderer.domElement.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.renderer.domElement.addEventListener('click', (e) => this.onClick(e));
        this.renderer.domElement.addEventListener('contextmenu', (e) => this.onRightClick(e));
        
        // Toolbar events
        document.getElementById('searchBtn').addEventListener('click', () => this.handleSearch());
        document.getElementById('clearSearchBtn').addEventListener('click', () => this.clearSearch());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
        document.getElementById('layoutSelect').addEventListener('change', (e) => {
            this.layout = e.target.value;
            this.applyLayout();
        });
        
        document.getElementById('resetViewBtn').addEventListener('click', () => this.resetView());
        document.getElementById('fitToScreenBtn').addEventListener('click', () => this.fitToScreen());
        
        // Message handling from extension
        window.addEventListener('message', (e) => this.handleMessage(e.data));
    }
    
    onWindowResize() {
        const container = document.getElementById('visualization');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    onMouseMove(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Check for hover
        this.checkIntersection();
    }
    
    onClick(event) {
        const intersected = this.getIntersectedNode();
        if (intersected) {
            this.selectNode(intersected.userData.id);
        } else {
            this.deselectNode();
        }
    }
    
    onRightClick(event) {
        event.preventDefault();
        const intersected = this.getIntersectedNode();
        if (intersected) {
            this.showContextMenu(event, intersected.userData);
        }
    }
    
    checkIntersection() {
        const intersected = this.getIntersectedNode();
        
        if (intersected !== this.hoveredNode) {
            if (this.hoveredNode) {
                this.hoveredNode.scale.setScalar(1);
            }
            
            this.hoveredNode = intersected;
            
            if (this.hoveredNode) {
                this.hoveredNode.scale.setScalar(1.2);
                this.showTooltip(this.hoveredNode.userData);
            } else {
                this.hideTooltip();
            }
        }
    }
    
    getIntersectedNode() {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(
            Array.from(this.nodes.values())
        );
        return intersects.length > 0 ? intersects[0].object : null;
    }
    
    selectNode(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return;
        
        // Deselect previous
        if (this.selectedNode) {
            this.selectedNode.material.emissive = new THREE.Color(0x000000);
        }
        
        this.selectedNode = node;
        node.material.emissive = new THREE.Color(0xffff00);
        
        // Show details
        this.showNodeDetails(node.userData);
        
        // Notify extension
        this.postMessage({
            command: 'selectNode',
            nodeId: nodeId
        });
    }
    
    deselectNode() {
        if (this.selectedNode) {
            this.selectedNode.material.emissive = new THREE.Color(0x000000);
            this.selectedNode = null;
        }
        
        document.getElementById('details-content').innerHTML = 
            '<p>Select a node to view details</p>';
    }
    
    handleMessage(message) {
        switch (message.command) {
            case 'loadGraph':
                this.loadGraph(message.data);
                break;
            case 'search':
                this.performSearch(message.query);
                break;
            case 'showNodeDetails':
                this.showNodeDetails(message.node);
                break;
            case 'expandNode':
                this.expandNode(message.nodeId, message.data);
                break;
        }
    }
    
    loadGraph(data) {
        // Clear existing graph
        this.clearGraph();
        
        // Create node materials by type
        const typeColors = {
            'FILE': 0x4a90e2,
            'CLASS': 0xe74c3c,
            'FUNCTION': 0x2ecc71,
            'METHOD': 0x27ae60,
            'MODULE': 0x9b59b6,
            'FOLDER': 0xf39c12,
            'DOCUMENTATION_FILE': 0x1abc9c,
            'CONCEPT': 0xe67e22,
            'DOCUMENTED_ENTITY': 0x34495e
        };
        
        // Create nodes
        data.nodes.forEach(nodeData => {
            const color = typeColors[nodeData.type] || 0x7f8c8d;
            let material = this.nodeMaterials.get(nodeData.type);
            
            if (!material) {
                material = new THREE.MeshPhongMaterial({
                    color: color,
                    emissive: 0x000000,
                    emissiveIntensity: 0.3
                });
                this.nodeMaterials.set(nodeData.type, material);
            }
            
            const node = new THREE.Mesh(this.nodeGeometry, material);
            node.userData = nodeData;
            
            // Random initial position
            node.position.set(
                (Math.random() - 0.5) * 200,
                (Math.random() - 0.5) * 200,
                (Math.random() - 0.5) * 200
            );
            
            this.scene.add(node);
            this.nodes.set(nodeData.id, node);
        });
        
        // Create edges
        data.edges.forEach(edgeData => {
            const sourceNode = this.nodes.get(edgeData.source);
            const targetNode = this.nodes.get(edgeData.target);
            
            if (sourceNode && targetNode) {
                const points = [
                    sourceNode.position,
                    targetNode.position
                ];
                
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const edge = new THREE.Line(geometry, this.edgeMaterial);
                edge.userData = edgeData;
                
                this.scene.add(edge);
                this.edges.set(`${edgeData.source}-${edgeData.target}`, {
                    line: edge,
                    source: sourceNode,
                    target: targetNode
                });
            }
        });
        
        // Update UI
        this.updateStatusBar(data);
        this.updateLegend(data);
        this.updateFilters(data);
        
        // Apply layout
        this.applyLayout();
    }
    
    clearGraph() {
        // Remove all nodes
        this.nodes.forEach(node => {
            this.scene.remove(node);
        });
        this.nodes.clear();
        
        // Remove all edges
        this.edges.forEach(edge => {
            this.scene.remove(edge.line);
        });
        this.edges.clear();
        
        this.selectedNode = null;
        this.hoveredNode = null;
    }
    
    applyLayout() {
        switch (this.layout) {
            case 'force-directed':
                this.applyForceDirectedLayout();
                break;
            case 'hierarchical':
                this.applyHierarchicalLayout();
                break;
            case 'circular':
                this.applyCircularLayout();
                break;
        }
    }
    
    applyForceDirectedLayout() {
        // Simple force-directed layout
        const nodes = Array.from(this.nodes.values());
        const edges = Array.from(this.edges.values());
        
        const iterations = 100;
        const k = 50; // Ideal edge length
        const c = 0.01; // Repulsion constant
        
        for (let iter = 0; iter < iterations; iter++) {
            // Repulsive forces between all nodes
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const nodeA = nodes[i];
                    const nodeB = nodes[j];
                    
                    const diff = nodeA.position.clone().sub(nodeB.position);
                    const distance = diff.length() || 0.1;
                    const force = diff.normalize().multiplyScalar(k * k / distance * c);
                    
                    nodeA.position.add(force);
                    nodeB.position.sub(force);
                }
            }
            
            // Attractive forces along edges
            edges.forEach(edge => {
                const diff = edge.target.position.clone().sub(edge.source.position);
                const distance = diff.length();
                const force = diff.normalize().multiplyScalar((distance - k) * 0.01);
                
                edge.source.position.add(force);
                edge.target.position.sub(force);
            });
        }
        
        this.updateEdgePositions();
        this.fitToScreen();
    }
    
    applyHierarchicalLayout() {
        // Simple hierarchical layout based on node types
        const layers = {
            'FOLDER': 0,
            'MODULE': 1,
            'FILE': 2,
            'CLASS': 3,
            'METHOD': 4,
            'FUNCTION': 4
        };
        
        const layerNodes = {};
        this.nodes.forEach(node => {
            const layer = layers[node.userData.type] || 5;
            if (!layerNodes[layer]) layerNodes[layer] = [];
            layerNodes[layer].push(node);
        });
        
        const layerHeight = 50;
        Object.keys(layerNodes).forEach(layer => {
            const nodes = layerNodes[layer];
            const angleStep = (Math.PI * 2) / nodes.length;
            const radius = Math.min(nodes.length * 10, 200);
            
            nodes.forEach((node, i) => {
                const angle = i * angleStep;
                node.position.set(
                    Math.cos(angle) * radius,
                    parseInt(layer) * layerHeight - 100,
                    Math.sin(angle) * radius
                );
            });
        });
        
        this.updateEdgePositions();
        this.fitToScreen();
    }
    
    applyCircularLayout() {
        const nodes = Array.from(this.nodes.values());
        const angleStep = (Math.PI * 2) / nodes.length;
        const radius = nodes.length * 5;
        
        nodes.forEach((node, i) => {
            const angle = i * angleStep;
            node.position.set(
                Math.cos(angle) * radius,
                0,
                Math.sin(angle) * radius
            );
        });
        
        this.updateEdgePositions();
        this.fitToScreen();
    }
    
    updateEdgePositions() {
        this.edges.forEach(edge => {
            const positions = [
                edge.source.position,
                edge.target.position
            ];
            edge.line.geometry.setFromPoints(positions);
        });
    }
    
    fitToScreen() {
        const box = new THREE.Box3();
        this.nodes.forEach(node => {
            box.expandByObject(node);
        });
        
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        const distance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;
        
        this.camera.position.set(center.x, center.y, center.z + distance);
        this.camera.lookAt(center);
        this.controls.target.copy(center);
        this.controls.update();
    }
    
    resetView() {
        this.camera.position.set(0, 0, 200);
        this.camera.lookAt(0, 0, 0);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }
    
    handleSearch() {
        const query = document.getElementById('searchInput').value;
        if (query) {
            this.performSearch(query);
        }
    }
    
    clearSearch() {
        document.getElementById('searchInput').value = '';
        this.nodes.forEach(node => {
            node.visible = true;
        });
        this.edges.forEach(edge => {
            edge.line.visible = true;
        });
    }
    
    performSearch(query) {
        const lowerQuery = query.toLowerCase();
        const matchingNodes = new Set();
        
        this.nodes.forEach((node, id) => {
            const matches = 
                node.userData.label.toLowerCase().includes(lowerQuery) ||
                node.userData.type.toLowerCase().includes(lowerQuery) ||
                Object.values(node.userData.properties).some(val => 
                    String(val).toLowerCase().includes(lowerQuery)
                );
            
            node.visible = matches;
            if (matches) {
                matchingNodes.add(id);
            }
        });
        
        // Show edges connected to visible nodes
        this.edges.forEach(edge => {
            edge.line.visible = 
                matchingNodes.has(edge.line.userData.source) ||
                matchingNodes.has(edge.line.userData.target);
        });
    }
    
    showNodeDetails(nodeData) {
        const detailsHtml = `
            <div class="property">
                <div class="property-name">Name</div>
                <div class="property-value">${nodeData.label}</div>
            </div>
            <div class="property">
                <div class="property-name">Type</div>
                <div class="property-value">${nodeData.type}</div>
            </div>
            ${Object.entries(nodeData.properties)
                .filter(([key]) => key !== 'node_id')
                .map(([key, value]) => `
                    <div class="property">
                        <div class="property-name">${key}</div>
                        <div class="property-value">${value}</div>
                    </div>
                `).join('')}
        `;
        
        document.getElementById('details-content').innerHTML = detailsHtml;
    }
    
    showTooltip(nodeData) {
        // Implementation for tooltip display
        // Would show a floating tooltip near the mouse position
    }
    
    hideTooltip() {
        // Hide tooltip
    }
    
    showContextMenu(event, nodeData) {
        // Implementation for context menu
        // Would show options like "Expand", "Open File", "Show Details"
    }
    
    updateStatusBar(data) {
        document.getElementById('node-count').textContent = `${data.nodes.length} nodes`;
        document.getElementById('edge-count').textContent = `${data.edges.length} edges`;
    }
    
    updateLegend(data) {
        const typeColors = {
            'FILE': '#4a90e2',
            'CLASS': '#e74c3c',
            'FUNCTION': '#2ecc71',
            'METHOD': '#27ae60',
            'MODULE': '#9b59b6',
            'FOLDER': '#f39c12',
            'DOCUMENTATION_FILE': '#1abc9c',
            'CONCEPT': '#e67e22',
            'DOCUMENTED_ENTITY': '#34495e'
        };
        
        const typeCounts = {};
        data.nodes.forEach(node => {
            typeCounts[node.type] = (typeCounts[node.type] || 0) + 1;
        });
        
        const legendHtml = Object.entries(typeCounts)
            .sort(([,a], [,b]) => b - a)
            .map(([type, count]) => `
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${typeColors[type] || '#7f8c8d'}"></div>
                    <div class="legend-label">${type} (${count})</div>
                </div>
            `).join('');
        
        document.getElementById('legend-content').innerHTML = legendHtml;
    }
    
    updateFilters(data) {
        const types = [...new Set(data.nodes.map(n => n.type))];
        
        const filterHtml = types.map(type => `
            <label class="filter-checkbox">
                <input type="checkbox" value="${type}" checked>
                ${type}
            </label>
        `).join('');
        
        document.getElementById('filter-content').innerHTML = filterHtml;
        
        // Add event listeners
        document.querySelectorAll('#filter-content input').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateFilters());
        });
    }
    
    updateNodeVisibility() {
        const checkedTypes = Array.from(
            document.querySelectorAll('#filter-content input:checked')
        ).map(cb => cb.value);
        
        this.nodes.forEach(node => {
            node.visible = checkedTypes.includes(node.userData.type);
        });
        
        // Update edge visibility
        this.edges.forEach(edge => {
            edge.line.visible = edge.source.visible || edge.target.visible;
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        
        // Update edge positions if nodes are moving
        if (this.forceSimulation) {
            this.updateEdgePositions();
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    postMessage(message) {
        vscode.postMessage(message);
    }
}

// OrbitControls implementation (simplified)
class OrbitControls {
    constructor(camera, domElement) {
        this.camera = camera;
        this.domElement = domElement;
        this.target = new THREE.Vector3();
        
        this.enableDamping = false;
        this.dampingFactor = 0.05;
        
        this.spherical = new THREE.Spherical();
        this.sphericalDelta = new THREE.Spherical();
        
        this.scale = 1;
        this.panOffset = new THREE.Vector3();
        
        this.rotateSpeed = 1.0;
        this.panSpeed = 1.0;
        this.zoomSpeed = 1.0;
        
        this.mouseButtons = {
            LEFT: THREE.MOUSE.ROTATE,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.PAN
        };
        
        this.init();
    }
    
    init() {
        this.domElement.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.domElement.addEventListener('wheel', (e) => this.onMouseWheel(e));
        this.domElement.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    onMouseDown(event) {
        event.preventDefault();
        
        const onMouseMove = (e) => this.handleMouseMove(e, event);
        const onMouseUp = () => {
            this.domElement.removeEventListener('mousemove', onMouseMove);
            this.domElement.removeEventListener('mouseup', onMouseUp);
        };
        
        this.domElement.addEventListener('mousemove', onMouseMove);
        this.domElement.addEventListener('mouseup', onMouseUp);
    }
    
    handleMouseMove(event, startEvent) {
        const deltaX = event.clientX - startEvent.clientX;
        const deltaY = event.clientY - startEvent.clientY;
        
        if (startEvent.button === 0) { // Left click - rotate
            this.rotateLeft(2 * Math.PI * deltaX / this.domElement.clientHeight);
            this.rotateUp(2 * Math.PI * deltaY / this.domElement.clientHeight);
        } else if (startEvent.button === 2) { // Right click - pan
            this.pan(deltaX, -deltaY);
        }
    }
    
    onMouseWheel(event) {
        event.preventDefault();
        
        if (event.deltaY < 0) {
            this.dollyOut(0.95);
        } else {
            this.dollyIn(0.95);
        }
        
        this.update();
    }
    
    rotateLeft(angle) {
        this.sphericalDelta.theta -= angle;
    }
    
    rotateUp(angle) {
        this.sphericalDelta.phi -= angle;
    }
    
    pan(deltaX, deltaY) {
        const offset = new THREE.Vector3();
        const position = this.camera.position;
        
        offset.copy(position).sub(this.target);
        let targetDistance = offset.length();
        targetDistance *= Math.tan((this.camera.fov / 2) * Math.PI / 180.0);
        
        const panLeft = new THREE.Vector3();
        const panUp = new THREE.Vector3();
        
        panLeft.setFromMatrixColumn(this.camera.matrix, 0);
        panLeft.multiplyScalar(-2 * deltaX * targetDistance / this.domElement.clientHeight);
        
        panUp.setFromMatrixColumn(this.camera.matrix, 1);
        panUp.multiplyScalar(2 * deltaY * targetDistance / this.domElement.clientHeight);
        
        this.panOffset.add(panLeft);
        this.panOffset.add(panUp);
    }
    
    dollyIn(scale) {
        this.scale /= scale;
    }
    
    dollyOut(scale) {
        this.scale *= scale;
    }
    
    update() {
        const offset = new THREE.Vector3();
        const quat = new THREE.Quaternion().setFromUnitVectors(
            this.camera.up,
            new THREE.Vector3(0, 1, 0)
        );
        const quatInverse = quat.clone().invert();
        
        const position = this.camera.position;
        
        offset.copy(position).sub(this.target);
        offset.applyQuaternion(quat);
        
        this.spherical.setFromVector3(offset);
        
        this.spherical.theta += this.sphericalDelta.theta;
        this.spherical.phi += this.sphericalDelta.phi;
        this.spherical.phi = Math.max(0.01, Math.min(Math.PI - 0.01, this.spherical.phi));
        
        this.spherical.radius *= this.scale;
        this.spherical.radius = Math.max(10, Math.min(5000, this.spherical.radius));
        
        this.target.add(this.panOffset);
        
        offset.setFromSpherical(this.spherical);
        offset.applyQuaternion(quatInverse);
        
        position.copy(this.target).add(offset);
        
        this.camera.lookAt(this.target);
        
        if (this.enableDamping) {
            this.sphericalDelta.theta *= (1 - this.dampingFactor);
            this.sphericalDelta.phi *= (1 - this.dampingFactor);
            this.panOffset.multiplyScalar(1 - this.dampingFactor);
        } else {
            this.sphericalDelta.set(0, 0, 0);
            this.panOffset.set(0, 0, 0);
        }
        
        this.scale = 1;
    }
}

// VS Code API
const vscode = acquireVsCodeApi();

// Initialize visualization when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new BlarifyVisualization();
    });
} else {
    new BlarifyVisualization();
}