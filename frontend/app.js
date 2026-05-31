const API_BASE = "http://localhost:8000";
let queryCount = 0;

console.log("App.js loaded");

// Clear query results (NOT the input)
function clearQuery() {
    console.log("Clearing query results");
    document.getElementById("queryResults").classList.remove("visible");
    document.getElementById("queryResults").innerHTML = "";
    // Input field stays filled
}

// Clear database function
async function clearDatabase() {
    if (!confirm("Are you sure you want to clear ALL data? This cannot be undone.")) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/clear`, {
            method: "POST"
        });

        const data = await response.json();

        if (response.ok) {
            alert("✓ Database cleared successfully!");
            console.log("Database cleared");
            updateStats();
            loadGraph();
            document.getElementById("uploadStatus").textContent = "";
            // IMPORTANT: Do NOT clear the query input or results
            // User can still search after clearing DB
        } else {
            alert(`✗ Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`✗ Error: ${error.message}`);
        console.error("Clear database error:", error);
    }
}

// Upload functionality
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");

uploadArea.addEventListener("click", () => fileInput.click());

uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
    handleFileUpload(e.dataTransfer.files[0]);
});

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    if (!file) return;

    console.log("Uploading file:", file.name);

    const formData = new FormData();
    formData.append("file", file);

    const statusDiv = document.getElementById("uploadStatus");
    statusDiv.innerHTML = '<div class="status-loading"><div class="spinner-small"></div> Processing...</div>';

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        console.log("Upload response:", data);

        if (response.ok) {
            statusDiv.innerHTML = `
                <div class="status-success">
                    ✓ Success!<br>
                    Entities: ${data.entities_count}<br>
                    Relations: ${data.relationships_count}
                </div>
            `;
            
            console.log("Upload successful. Updating stats and graph...");
            
            // Update stats
            await updateStats();
            
            // Load and render graph
            await loadGraph();
            
            console.log("Graph updated");
        } else {
            statusDiv.innerHTML = `<div class="status-error">✗ Error: ${data.detail}</div>`;
            console.error("Upload error:", data.detail);
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="status-error">✗ Error: ${error.message}</div>`;
        console.error("Upload error:", error);
    }
}

// Query functionality
async function queryGraph() {
    const query = document.getElementById("queryInput").value;
    if (!query) return;

    const loading = document.getElementById("loading");
    const results = document.getElementById("queryResults");

    loading.classList.add("visible");
    results.classList.remove("visible");

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: query })
        });

        const data = await response.json();

        if (response.ok) {
            queryCount++;
            document.getElementById("queryCount").textContent = queryCount;

            results.innerHTML = `
                <div class="result-item">
                    <div class="result-question">Q: ${data.question}</div>
                    <div class="result-answer">${data.answer}</div>
                    <div class="result-metadata">
                        <div><strong>Results:</strong> ${data.results.length} record(s)</div>
                    </div>
                </div>
            `;
            results.classList.add("visible");
        } else {
            results.innerHTML = `<div style="color: #c33; padding: 8px; font-size: 0.8em;">✗ Error: ${data.detail}</div>`;
            results.classList.add("visible");
        }
    } catch (error) {
        results.innerHTML = `<div style="color: #c33; padding: 8px; font-size: 0.8em;">✗ Error: ${error.message}</div>`;
        results.classList.add("visible");
    } finally {
        loading.classList.remove("visible");
    }
}

// Allow Enter key to submit query
document.getElementById("queryInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") queryGraph();
});

// Load graph data from API
async function loadGraph() {
    console.log("Loading graph...");
    
    try {
        const response = await fetch(`${API_BASE}/graph`);
        const data = await response.json();

        console.log("Graph data received:", data);

        if (response.ok) {
            console.log(`Nodes: ${data.nodes.length}, Edges: ${data.edges.length}`);
            visualizeGraph(data.nodes, data.edges);
        } else {
            console.error("Graph error:", data);
        }
    } catch (error) {
        console.error("Error loading graph:", error);
    }
}

// Visualize graph with D3
function visualizeGraph(nodes, edges) {
    console.log("Starting visualization. Nodes:", nodes.length, "Edges:", edges.length);
    
    // Clear previous graph
    d3.select("#graph").selectAll("*").remove();

    if (nodes.length === 0) {
        console.log("No nodes to visualize");
        d3.select("#graph").append("text")
            .attr("x", "50%")
            .attr("y", "50%")
            .attr("text-anchor", "middle")
            .attr("dy", "0.3em")
            .style("fill", "#999")
            .style("font-size", "16px")
            .text("No data to visualize. Upload a filing first!");
        return;
    }

    const graphElement = document.getElementById("graph");
    const width = graphElement.clientWidth;
    const height = graphElement.clientHeight;

    console.log("SVG dimensions:", width, "x", height);

    const svg = d3.select("#graph")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`);

    // Define color mapping by type
    const colorMap = {
        "COMPANY": "#2563eb",
        "PRODUCT": "#7c3aed",
        "PRODUCT_LINE": "#7c3aed",
        "OPERATING_SYSTEM": "#db2777",
        "PERSON": "#059669",
        "EXECUTIVE": "#059669",
        "DIVISION": "#059669",
        "UNKNOWN": "#6b7280"
    };

    // Initialize force simulation
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges)
            .id(d => d.id)
            .distance(100))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // Add arrow markers
    svg.append("defs").selectAll("marker")
        .data(["end"])
        .enter().append("marker")
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#999");

    // Draw links
    console.log("Drawing links...");
    const link = svg.selectAll("line")
        .data(edges)
        .enter()
        .append("line")
        .attr("stroke", "#d1d5db")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 2)
        .attr("marker-end", "url(#end)");

    // Draw link labels
    const linkLabels = svg.selectAll(".link-label")
        .data(edges)
        .enter()
        .append("text")
        .attr("class", "link-label")
        .attr("font-size", "11px")
        .attr("fill", "#666")
        .attr("text-anchor", "middle")
        .attr("dy", "-4px")
        .text(d => d.type)
        .style("pointer-events", "none");

    // Draw nodes
    console.log("Drawing nodes...");
    const node = svg.selectAll("circle")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("r", d => {
            const base = Math.max(8, Math.min(25, d.confidence * 30));
            return base;
        })
        .attr("fill", d => colorMap[d.type] || colorMap["UNKNOWN"])
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .call(d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded));

    // Draw node labels
    console.log("Drawing labels...");
    const labels = svg.selectAll(".node-label")
        .data(nodes)
        .enter()
        .append("text")
        .attr("class", "node-label")
        .attr("font-size", "12px")
        .attr("font-weight", "600")
        .attr("text-anchor", "middle")
        .attr("dy", "0.3em")
        .attr("fill", "#fff")
        .text(d => {
            const name = d.label;
            return name.length > 15 ? name.substring(0, 15) + "..." : name;
        })
        .style("pointer-events", "none")
        .style("text-shadow", "0 0 3px rgba(0,0,0,0.8)");

    // Add tooltip
    const tooltip = document.createElement("div");
    tooltip.className = "tooltip";
    document.body.appendChild(tooltip);

    node.on("mouseover", function(event, d) {
        tooltip.style.display = "block";
        tooltip.innerHTML = `
            <strong>${d.label}</strong><br/>
            Type: ${d.type}<br/>
            Confidence: ${(d.confidence * 100).toFixed(0)}%
        `;
        tooltip.style.left = (event.pageX + 10) + "px";
        tooltip.style.top = (event.pageY - 10) + "px";
    })
    .on("mousemove", function(event) {
        tooltip.style.left = (event.pageX + 10) + "px";
        tooltip.style.top = (event.pageY - 10) + "px";
    })
    .on("mouseout", function() {
        tooltip.style.display = "none";
    });

    // Update on simulation tick
    console.log("Starting simulation...");
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        linkLabels
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        labels
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });

    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    console.log("Visualization complete");
}

// Update statistics
async function updateStats() {
    console.log("Updating stats...");
    
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        console.log("Stats:", data);
        
        document.getElementById("entityCount").textContent = data.entities;
        document.getElementById("relationshipCount").textContent = data.relationships;
    } catch (error) {
        console.error("Error updating stats:", error);
    }
}

// Initialize on page load
console.log("Initializing application...");
updateStats();
loadGraph();