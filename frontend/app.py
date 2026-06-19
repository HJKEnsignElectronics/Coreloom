// CoreLoom Frontend Client
const API_URL = window.location.protocol === 'https:' ? 'https://localhost:8443' : 'http://localhost:8000';

let authToken = localStorage.getItem('token');
let userName = localStorage.getItem('userName');
let activeContainerId = null;
let startTime = null;
let telemetryInterval = null;
let allocationHistory = JSON.parse(localStorage.getItem('allocationHistory') || '[]');
let isRegisterMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    detectNetwork();
    updateSliderValues();
    setupEventListeners();
    
    if (authToken && userName) {
        verifyAndEnterDashboard();
    } else {
        showLoginSection();
    }
});

// Network Detection
function detectNetwork() {
    const indicator = document.getElementById('statusIndicator');
    const text = document.getElementById('statusText');
    
    if (navigator.onLine) {
        indicator.className = 'status-dot online';
        text.textContent = '✓ Connected to CoreLoom Network';
    } else {
        indicator.className = 'status-dot offline';
        text.textContent = '✗ Network Unavailable';
    }
}
window.addEventListener('online', detectNetwork);
window.addEventListener('offline', detectNetwork);

// UI Setup & Event Listeners
function updateSliderValues() {
    ['compute', 'rom'].forEach(type => {
        const input = document.getElementById(type);
        const display = document.getElementById(`${type}Value`);
        const bar = document.getElementById(`${type}Bar`);
        if (input) {
            input.addEventListener('input', () => {
                display.textContent = `${input.value}%`;
                bar.style.width = `${input.value}%`;            });
        }
    });
}

function setupEventListeners() {
    document.getElementById('authForm').addEventListener('submit', handleAuth);
    document.getElementById('toggleAuthMode').addEventListener('click', toggleAuthMode);
    document.getElementById('resourceForm').addEventListener('submit', handleAllocation);
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
}

// Authentication Flow
function toggleAuthMode() {
    isRegisterMode = !isRegisterMode;
    const btn = document.getElementById('authBtn');
    const toggle = document.getElementById('toggleAuthMode');
    const title = document.querySelector('#loginSection h1');
    
    if (isRegisterMode) {
        btn.textContent = 'Register Node';
        toggle.textContent = 'Back to Login';
        title.textContent = '📝 Register New Node';
    } else {
        btn.textContent = 'Join Network';
        toggle.textContent = 'Register New Node';
        title.textContent = '🔐 Node Authentication';
    }
}

async function handleAuth(e) {
    e.preventDefault();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const statusEl = document.getElementById('authStatus');
    const btn = document.getElementById('authBtn');
    
    if (username.length < 3 || password.length < 6) {
        showStatus(statusEl, 'Username must be 3+ chars, Password 6+ chars', 'error');
        return;
    }

    btn.disabled = true;
    btn.textContent = isRegisterMode ? 'Registering...' : 'Joining Network...';
    
    try {
        const endpoint = isRegisterMode ? '/register' : '/login';
        const headers = { 'Content-Type': isRegisterMode ? 'application/json' : 'application/x-www-form-urlencoded' };
        
        let body;        if (isRegisterMode) {
            body = JSON.stringify({ username, password });
        } else {
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);
            body = params;
        }

        const res = await fetch(`${API_URL}${endpoint}`, { method: 'POST', headers, body });
        const data = await res.json();

        if (res.ok) {
            authToken = data.access_token;
            userName = username;
            localStorage.setItem('token', authToken);
            localStorage.setItem('userName', userName);
            showStatus(statusEl, '✓ Authentication successful!', 'success');
            setTimeout(enterDashboard, 800);
        } else {
            showStatus(statusEl, `✗ ${data.detail || 'Authentication failed'}`, 'error');
        }
    } catch (err) {
        showStatus(statusEl, '✗ Network error: Is the backend running?', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = isRegisterMode ? 'Register Node' : 'Join Network';
    }
}

function showStatus(el, msg, type) {
    el.textContent = msg;
    el.className = `status-message status-${type}`;
    setTimeout(() => el.textContent = '', 4000);
}

async function verifyAndEnterDashboard() {
    try {
        const res = await fetch(`${API_URL}/system-health`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) enterDashboard();
        else handleLogout();
    } catch {
        handleLogout();
    }
}

function showLoginSection() {
    document.getElementById('loginSection').style.display = 'block';    document.getElementById('provisioningSection').style.display = 'none';
}

function enterDashboard() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('provisioningSection').style.display = 'block';
    document.getElementById('userName').textContent = `👤 ${userName}`;
    startTime = Date.now();
    updateConnectionTime();
    renderHistory();
}

function updateConnectionTime() {
    if (!startTime) return;
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const h = Math.floor(elapsed / 3600);
    const m = Math.floor((elapsed % 3600) / 60);
    const s = elapsed % 60;
    document.getElementById('connectionTime').textContent = `Connected: ${h ? h+'h ' : ''}${m}m ${s}s`;
    setTimeout(updateConnectionTime, 1000);
}

// Resource Allocation
async function handleAllocation(e) {
    e.preventDefault();
    if (!authToken) return handleLogout();
    
    const compute = document.getElementById('compute').value;
    const rom = document.getElementById('rom').value;
    const btn = document.getElementById('allocateBtn');
    const statusEl = document.getElementById('allocationStatus');

    btn.disabled = true;
    btn.textContent = 'Synthesizing Virtual Cores...';
    
    try {
        const res = await fetch(`${API_URL}/allocate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                rom_percent: parseFloat(rom),
                compute_percent: parseFloat(compute),
                task_description: 'Frontend pipeline allocation'
            })
        });
        
        const data = await res.json();        if (res.ok) {
            activeContainerId = data.container_id;
            document.getElementById('containerIdDisplay').textContent = activeContainerId;
            showStatus(statusEl, `✓ Allocated ${data.virtual_cores_allocated} Virtual Cores. Container: ${activeContainerId}`, 'success');
            
            addToHistory(activeContainerId, { compute, rom, cores: data.virtual_cores_allocated });
            
            // Start telemetry polling
            if (telemetryInterval) clearInterval(telemetryInterval);
            telemetryInterval = setInterval(fetchTelemetry, 2000);
            fetchTelemetry();
        } else {
            showStatus(statusEl, `✗ ${data.detail || 'Allocation failed'}`, 'error');
        }
    } catch (err) {
        showStatus(statusEl, '✗ Network error during allocation', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Allocate Resources';
    }
}

// Telemetry Polling
async function fetchTelemetry() {
    if (!authToken || !activeContainerId) return;
    
    try {
        const res = await fetch(`${API_URL}/telemetry/${activeContainerId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!res.ok) {
            clearInterval(telemetryInterval);
            return;
        }
        
        const data = await res.json();
        document.getElementById('telemetryCpu').textContent = `${data.cpu_usage}%`;
        document.getElementById('telemetryMem').textContent = `${data.memory_usage}%`;
        document.getElementById('telemetrySpeed').textContent = `${data.thread_speed_mhz} MHz`;
    } catch {
        // Silently handle polling errors
    }
}

// History Management
function addToHistory(id, resources) {
    const item = { id, timestamp: new Date().toLocaleTimeString(), resources };
    allocationHistory.unshift(item);
    if (allocationHistory.length > 10) allocationHistory.pop();
    localStorage.setItem('allocationHistory', JSON.stringify(allocationHistory));    renderHistory();
}

function renderHistory() {
    const list = document.getElementById('historyList');
    if (allocationHistory.length === 0) {
        list.innerHTML = '<p style="color:#9ca3af; text-align:center; padding:15px;">No allocations yet</p>';
        return;
    }
    list.innerHTML = allocationHistory.map(item => `
        <div class="history-item">
            <span class="history-item-time">${item.timestamp}</span>
            Compute: ${item.resources.compute}% | ROM: ${item.resources.rom}% | Cores: ${item.resources.cores || 'N/A'}
            <br><small style="color:#6b7280;">ID: ${item.id}</small>
        </div>
    `).join('');
}

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    authToken = null;
    userName = null;
    activeContainerId = null;
    startTime = null;
    clearInterval(telemetryInterval);
    document.getElementById('telemetryCpu').textContent = '0%';
    document.getElementById('telemetryMem').textContent = '0%';
    document.getElementById('telemetrySpeed').textContent = '0 MHz';
    document.getElementById('containerIdDisplay').textContent = 'None';
    showLoginSection();
}
