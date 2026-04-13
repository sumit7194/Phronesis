// Phronesis Dashboard — Client-side logic

let extractionData = {};
let steeringData = {};
let statusData = {};
let currentSteeringRun = null;
let currentPromptIdx = 0;

// ─── Tab switching ──────────────────────────────────────────────────────────

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
    });
});

// ─── Data loading ───────────────────────────────────────────────────────────

// ─── Progress tab ──────────────────────────────────────────────────────────

async function loadProgress() {
    try {
        const prog = await fetch('/api/progress').then(r => r.json());
        renderProgress(prog);
    } catch (e) {
        console.error('Failed to load progress:', e);
    }
}

function renderProgress(prog) {
    const container = document.getElementById('progress-content');
    const refreshEl = document.getElementById('last-refresh');
    refreshEl.textContent = `Last refresh: ${new Date().toLocaleTimeString()}`;
    let html = '';

    // Running processes
    html += '<div class="status-section"><h3>Running Processes</h3>';
    if (prog.processes?.length) {
        html += '<div class="process-list">';
        prog.processes.forEach(p => {
            html += `<div class="process-item">
                <span class="process-indicator pulse"></span>
                <code>${p.command}</code>
                <span class="process-stats">CPU: ${p.cpu}% | MEM: ${p.mem}%</span>
            </div>`;
        });
        html += '</div>';
    } else {
        html += '<p class="idle-msg">No Phronesis processes running</p>';
    }
    html += '</div>';

    // Corpora progress
    html += '<div class="status-section"><h3>Corpora</h3>';
    html += '<div class="progress-grid">';
    for (const [name, info] of Object.entries(prog.corpora || {})) {
        const target = info.target || info.total_dirs;
        const pct = target > 0 ? Math.round(info.complete_triplets / target * 100) : 0;
        const done = info.complete_triplets >= target && target > 0;
        const isActive = !done && info.complete_triplets > 0 && info.complete_triplets < target;
        html += `<div class="progress-card ${done ? 'done' : ''} ${isActive ? 'active' : ''}">
            <div class="progress-card-title">${isActive ? '<span class="process-indicator pulse"></span> ' : ''}${name}</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${pct}%"></div></div>
            <div class="progress-card-detail">${info.complete_triplets} / ${target} triplets (${pct}%)</div>
        </div>`;
    }
    html += '</div></div>';

    // Vectors progress
    html += '<div class="status-section"><h3>Saved Vectors</h3>';
    if (Object.keys(prog.vectors || {}).length) {
        html += '<table class="status-table"><thead><tr><th>Model / Corpus / Method</th><th>Layers</th><th>.npy files</th></tr></thead><tbody>';
        for (const [key, info] of Object.entries(prog.vectors)) {
            html += `<tr><td>${key}</td><td>${info.layers}</td><td>${info.npy_files}</td></tr>`;
        }
        html += '</tbody></table>';
    } else {
        html += '<p class="idle-msg">No vectors saved yet</p>';
    }
    html += '</div>';

    // Live extraction (triplet-level progress)
    if (prog.live_extraction) {
        const le = prog.live_extraction;
        const pct = le.total_triplets > 0 ? Math.round(le.triplet / le.total_triplets * 100) : 0;
        const methodIdx = (le.methods_order || []).indexOf(le.method);
        const totalMethods = (le.methods_order || []).length;
        html += `<div class="status-section"><h3>Active Extraction</h3>
            <div class="task-output">
                <div class="task-header">${le.model} / ${le.corpus}</div>
                <div class="task-progress">Method: ${le.method} (${methodIdx + 1}/${totalMethods}) — Triplet ${le.triplet} / ${le.total_triplets}</div>
                <div class="progress-bar-bg" style="height:10px;margin:8px 0"><div class="progress-bar-fill" style="width:${pct}%"></div></div>
                <div class="progress-card-detail">Overall: method ${methodIdx + 1} of ${totalMethods} — ${pct}% through current method</div>
            </div>
        </div>`;
    }

    // Extraction method progress (completed methods)
    html += '<div class="status-section"><h3>Completed Extractions (by method)</h3>';
    if (Object.keys(prog.extraction_progress || {}).length) {
        for (const [corpusKey, methods] of Object.entries(prog.extraction_progress)) {
            html += `<div class="task-output"><div class="task-header">${corpusKey}</div><div class="progress-grid" style="margin-top:8px">`;
            for (const [method, info] of Object.entries(methods)) {
                const pct = info.total > 0 ? Math.round(info.layers_done / info.total * 100) : 0;
                const done = info.layers_done === info.total;
                const statusIcon = done ? '&#10003;' : (info.layers_done > 0 ? '&#9679;' : '&#8211;');
                const statusColor = done ? '#56d364' : (info.layers_done > 0 ? '#58a6ff' : '#484f58');
                html += `<div class="progress-card ${done ? 'done' : ''}">
                    <div class="progress-card-title"><span style="color:${statusColor}">${statusIcon}</span> ${method}</div>
                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${pct}%"></div></div>
                    <div class="progress-card-detail">${info.layers_done} / ${info.total} layers (${pct}%)</div>
                </div>`;
            }
            html += '</div></div>';
        }
    } else {
        html += '<p class="idle-msg">No extraction runs yet</p>';
    }
    html += '</div>';

    // Steering progress
    html += '<div class="status-section"><h3>Steering Progress</h3>';
    const steeringKeys = Object.keys(prog.extraction_progress || {}).filter(k => k.startsWith('steering_'));
    if (steeringKeys.length) {
        for (const key of steeringKeys) {
            const info = prog.extraction_progress[key];
            html += `<div class="task-output">
                <div class="task-header">${key.replace('steering_', '')}</div>
                <div class="task-progress">${info.latest_progress}</div>
            </div>`;
        }
    } else {
        html += '<p class="idle-msg">No steering runs yet — waiting for extraction to complete</p>';
    }
    html += '</div>';

    container.innerHTML = html;
}

document.getElementById('refresh-btn')?.addEventListener('click', loadProgress);

async function loadAll() {
    try {
        const [ext, steer, stat] = await Promise.all([
            fetch('/api/extraction').then(r => r.json()),
            fetch('/api/steering').then(r => r.json()),
            fetch('/api/status').then(r => r.json()),
        ]);
        extractionData = ext;
        steeringData = steer;
        statusData = stat;

        renderExtractionSelect();
        renderSteeringSelect();
        renderStatus();
    } catch (e) {
        console.error('Failed to load data:', e);
    }
}

// ─── Extraction Heatmap ─────────────────────────────────────────────────────

function renderExtractionSelect() {
    const sel = document.getElementById('extraction-select');
    sel.innerHTML = '';
    for (const key of Object.keys(extractionData)) {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = key.replace('mvp_v2_', '').replace(/_/g, ' ');
        sel.appendChild(opt);
    }
    sel.addEventListener('change', () => renderHeatmap(sel.value));
    if (sel.options.length > 0) renderHeatmap(sel.value);
}

function probeColor(val) {
    if (val === null || val === undefined) return '#161b22';
    const v = Math.max(0, Math.min(1, val));
    if (v < 0.5) return `rgb(${Math.round(180 + 75 * (v / 0.5))}, ${Math.round(60 * (v / 0.5))}, 60)`;
    if (v < 0.75) {
        const t = (v - 0.5) / 0.25;
        return `rgb(${Math.round(255 - 30 * t)}, ${Math.round(60 + 140 * t)}, 60)`;
    }
    const t = (v - 0.75) / 0.25;
    return `rgb(${Math.round(60 + 165 * (1 - t))}, ${Math.round(200 + 55 * t)}, ${Math.round(60 + 100 * t)})`;
}

function renderHeatmap(key) {
    const data = extractionData[key];
    if (!data) return;
    const container = document.getElementById('heatmap-container');

    const methods = Object.keys(data);
    // Collect all layers across methods
    const allLayers = new Set();
    methods.forEach(m => {
        Object.keys(data[m].per_layer || {}).forEach(l => allLayers.add(parseInt(l)));
    });
    const layers = [...allLayers].sort((a, b) => a - b);

    let html = '<table class="heatmap"><thead><tr><th>Layer</th>';
    methods.forEach(m => {
        html += `<th>${m}</th>`;
    });
    html += '</tr></thead><tbody>';

    layers.forEach(l => {
        html += `<tr><th>${l}</th>`;
        methods.forEach(m => {
            const layerData = (data[m].per_layer || {})[String(l)];
            if (layerData) {
                const wp = layerData.whitened?.probe_accuracy;
                const rp = layerData.raw?.probe_accuracy;
                const val = wp !== null && wp !== undefined ? wp : rp;
                const pct = val !== null && val !== undefined ? `${Math.round(val * 100)}%` : 'N/A';
                const bg = probeColor(val);
                const textColor = val > 0.65 ? '#000' : '#c9d1d9';
                html += `<td style="background:${bg};color:${textColor}" data-method="${m}" data-layer="${l}">${pct}</td>`;
            } else {
                html += '<td class="na">-</td>';
            }
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;

    // Click handler for detail
    container.querySelectorAll('td[data-method]').forEach(td => {
        td.addEventListener('click', () => {
            const m = td.dataset.method;
            const l = td.dataset.layer;
            showCellDetail(key, m, l);
        });
    });
}

function showCellDetail(key, method, layer) {
    const panel = document.getElementById('cell-detail');
    const layerData = extractionData[key]?.[method]?.per_layer?.[layer];
    if (!layerData) { panel.classList.remove('visible'); return; }

    const r = layerData.raw || {};
    const w = layerData.whitened || {};

    panel.innerHTML = `
        <h4>Layer ${layer} — ${method}</h4>
        <div>
            <span class="metric"><span class="label">Raw Probe: </span><span class="value">${r.probe_accuracy !== null ? Math.round(r.probe_accuracy * 100) + '%' : 'N/A'}</span></span>
            <span class="metric"><span class="label">Whitened Probe: </span><span class="value">${w.probe_accuracy !== null ? Math.round(w.probe_accuracy * 100) + '%' : 'N/A'}</span></span>
            <span class="metric"><span class="label">Separation: </span><span class="value">${(w.separation || 0).toFixed(3)}</span></span>
            <span class="metric"><span class="label">Cosine Diff: </span><span class="value">${(w.cosine_diff || 0).toFixed(4)}</span></span>
            <span class="metric"><span class="label">PCs removed: </span><span class="value">${layerData.n_pcs || '?'}</span></span>
        </div>
    `;
    panel.classList.add('visible');
}

// ─── Steering Comparison ────────────────────────────────────────────────────

function renderSteeringSelect() {
    const sel = document.getElementById('steering-select');
    sel.innerHTML = '<option value="">-- select a run --</option>';
    for (const key of Object.keys(steeringData)) {
        const opt = document.createElement('option');
        opt.value = key;
        const cfg = steeringData[key].config || {};
        opt.textContent = `${cfg.method || key} L${cfg.layer || '?'}`;
        sel.appendChild(opt);
    }
    sel.addEventListener('change', () => {
        currentSteeringRun = sel.value;
        currentPromptIdx = 0;
        renderPromptList();
        updateAlphaSlider();
    });
}

function renderPromptList() {
    const list = document.getElementById('prompt-list');
    const run = steeringData[currentSteeringRun];
    if (!run) { list.innerHTML = '<p style="padding:12px;color:#8b949e">No steering results yet</p>'; return; }

    const results = run.results || [];
    list.innerHTML = results.map((r, i) => `
        <div class="prompt-item ${i === currentPromptIdx ? 'selected' : ''}" data-idx="${i}">
            <strong>${r.prompt_id}</strong> — ${r.prompt_text.substring(0, 80)}...
        </div>
    `).join('');

    list.querySelectorAll('.prompt-item').forEach(item => {
        item.addEventListener('click', () => {
            currentPromptIdx = parseInt(item.dataset.idx);
            renderPromptList();
            renderComparison();
        });
    });

    renderComparison();
}

function updateAlphaSlider() {
    const run = steeringData[currentSteeringRun];
    if (!run) return;
    const alphas = run.config?.alphas || [];
    const slider = document.getElementById('alpha-slider');
    slider.max = alphas.length - 1;
    slider.value = Math.min(5, alphas.length - 1);
    slider.addEventListener('input', () => {
        document.getElementById('alpha-value').textContent = alphas[slider.value]?.toFixed(4) || '?';
        renderComparison();
    });
    document.getElementById('alpha-value').textContent = alphas[slider.value]?.toFixed(4) || '?';
}

function renderComparison() {
    const run = steeringData[currentSteeringRun];
    if (!run) return;
    const result = (run.results || [])[currentPromptIdx];
    if (!result) return;

    const alphas = run.config?.alphas || [];
    const slider = document.getElementById('alpha-slider');
    const alphaKey = alphas[slider.value]?.toFixed(4);

    const baseline = result.baseline?.response || '(no baseline)';
    const steered = result.steered?.[alphaKey]?.response || '(no steered output for this alpha)';

    document.getElementById('baseline-text').textContent = baseline;

    // Simple word-level diff
    const bWords = baseline.split(/\s+/);
    const sWords = steered.split(/\s+/);
    const bSet = new Set(bWords);
    const sSet = new Set(sWords);

    const highlighted = sWords.map(w => {
        if (!bSet.has(w)) return `<span class="diff-add">${w}</span>`;
        return w;
    }).join(' ');

    document.getElementById('steered-text').innerHTML = highlighted;
}

// ─── Status ─────────────────────────────────────────────────────────────────

function renderStatus() {
    const container = document.getElementById('status-content');
    let html = '';

    // Extraction files
    html += '<div class="status-section"><h3>Extraction Results</h3>';
    if (statusData.extraction_files?.length) {
        html += '<table class="status-table"><thead><tr><th>Name</th><th>Size</th><th>Modified</th></tr></thead><tbody>';
        statusData.extraction_files.forEach(f => {
            const date = new Date(f.modified * 1000).toLocaleString();
            html += `<tr><td>${f.name}</td><td>${f.size_kb} KB</td><td>${date}</td></tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p style="color:#8b949e">No extraction results yet</p>';
    }
    html += '</div>';

    // Vectors
    html += '<div class="status-section"><h3>Saved Vectors</h3>';
    if (statusData.vector_dirs?.length) {
        html += '<table class="status-table"><thead><tr><th>Path</th><th>Vectors</th><th>Modified</th></tr></thead><tbody>';
        statusData.vector_dirs.forEach(d => {
            const date = new Date(d.modified * 1000).toLocaleString();
            html += `<tr><td>${d.path}</td><td>${d.vectors} .npy files</td><td>${date}</td></tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p style="color:#8b949e">No vectors saved yet (run extraction with --save-vectors)</p>';
    }
    html += '</div>';

    // Steering
    html += '<div class="status-section"><h3>Steering Runs</h3>';
    if (statusData.steering_files?.length) {
        html += '<table class="status-table"><thead><tr><th>Name</th><th>Method</th><th>Layer</th><th>Prompts</th><th>Modified</th></tr></thead><tbody>';
        statusData.steering_files.forEach(f => {
            const date = new Date(f.modified * 1000).toLocaleString();
            html += `<tr><td>${f.name}</td><td>${f.method}</td><td>${f.layer}</td><td>${f.prompts}</td><td>${date}</td></tr>`;
        });
        html += '</tbody></table>';
    } else {
        html += '<p style="color:#8b949e">No steering runs yet</p>';
    }
    html += '</div>';

    container.innerHTML = html;
}

// ─── Init ───────────────────────────────────────────────────────────────────

loadAll();
loadProgress();
setInterval(loadAll, 30000);
setInterval(loadProgress, 10000); // Progress refreshes every 10s
