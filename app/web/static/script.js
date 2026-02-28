document.addEventListener('DOMContentLoaded', () => {
    const sensitivitySlider = document.getElementById('sensitivity-slider');
    const sensitivityVal = document.getElementById('sensitivity-val');
    const testBtn = document.getElementById('test-trigger-btn');
    const connectionStatus = document.getElementById('connection-status');
    const canvas = document.getElementById('zone-canvas');
    const ctx = canvas.getContext('2d');
    const clearBtn = document.getElementById('clear-zones-btn');
    const alertContainer = document.getElementById('alert-container');
    const silenceBtn = document.getElementById('silence-alarm-btn');

    // Tools
    const toolBtns = {
        point: document.getElementById('tool-point'),
        rect: document.getElementById('tool-rect'),
        poly: document.getElementById('tool-poly')
    };

    // Config
    const API_BASE = '/api';
    let currentTool = 'point';
    let zones = [];
    let isAlarming = false;
    let alarmOscillator = null;
    let alarmAudioCtx = null;
    let alarmFreqOsc = null;

    // Drawing State
    let isDrawing = false;
    let startPoint = null; // {x, y}
    let currentPolyPoints = [];

    // Initial fetch
    fetchStatus();
    loadZones();
    setInterval(fetchStatus, 500); // Increased polling frequency for better response

    // Tool Selection
    Object.keys(toolBtns).forEach(key => {
        toolBtns[key].addEventListener('click', () => {
            currentTool = key;
            // Update UI
            Object.values(toolBtns).forEach(btn => btn.classList.remove('active'));
            toolBtns[key].classList.add('active');

            // Reset drawing state if switching tools mid-draw
            isDrawing = false;
            currentPolyPoints = [];
            drawZones();
        });
    });

    // Clear Zones
    clearBtn.addEventListener('click', () => {
        zones = [];
        drawZones();
        // Since backend API for clearing isn't explicit in the simple list, 
        // we might need to implement a clear endpoint or just not persist deletions for now.
        // For this demo, let's just clear client side or send a special clear command if needed.
        // Assuming the user wants to clear:
        // Ideally we'd have DELETE /api/zones but simple demo app uses append only.
        // Let's re-init backend list if possible or just clear locally.
        // Note: The provided backend code doesn't support clearing.
        console.warn("Backend clear not implemented, clearing locally.");
    });

    // Sensitivity
    sensitivitySlider.addEventListener('input', (e) => {
        const val = e.target.value;
        sensitivityVal.textContent = val;
    });

    sensitivitySlider.addEventListener('change', (e) => {
        updateSensitivity(e.target.value);
    });

    testBtn.addEventListener('click', () => {
        fetch(`${API_BASE}/trigger_test`, { method: 'POST' })
            .then(res => res.json())
            .then(data => console.log('Test trigger:', data));
    });

    silenceBtn.addEventListener('click', () => {
        fetch(`${API_BASE}/silence`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                stopAlarmSound();
                hideAlert();
            });
    });

    // Canvas Interactions
    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(canvas, e);

        if (currentTool === 'point') {
            const zone = { type: 'point', x: pos.x, y: pos.y };
            addZone(zone);
        } else if (currentTool === 'rect') {
            isDrawing = true;
            startPoint = pos;
        } else if (currentTool === 'poly') {
            if (currentPolyPoints.length === 0) {
                currentPolyPoints.push(pos);
            } else {
                // If close to start point, maybe close it? 
                // Let's rely on double click to close for now
                currentPolyPoints.push(pos);
            }
            drawZones(); // Update to show lines
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        const pos = getMousePos(canvas, e);

        if (currentTool === 'rect' && isDrawing) {
            drawZones(); // Clear and redraw established
            // Draw current rect preview
            const w = pos.x - startPoint.x;
            const h = pos.y - startPoint.y;
            ctx.strokeStyle = '#3b82f6';
            ctx.strokeRect(startPoint.x, startPoint.y, w, h);
            ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
            ctx.fillRect(startPoint.x, startPoint.y, w, h);
        } else if (currentTool === 'poly' && currentPolyPoints.length > 0) {
            drawZones();
            // Draw lines for current poly
            ctx.beginPath();
            ctx.moveTo(currentPolyPoints[0].x, currentPolyPoints[0].y);
            currentPolyPoints.forEach(p => ctx.lineTo(p.x, p.y));
            ctx.lineTo(pos.x, pos.y); // Rubberband to cursor
            ctx.strokeStyle = '#3b82f6';
            ctx.stroke();

            // Draw dots at vertices
            ctx.fillStyle = '#3b82f6';
            [...currentPolyPoints, pos].forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
                ctx.fill();
            });
        }
    });

    canvas.addEventListener('mouseup', (e) => {
        const pos = getMousePos(canvas, e);

        if (currentTool === 'rect' && isDrawing) {
            const w = pos.x - startPoint.x;
            const h = pos.y - startPoint.y;
            // Ignore tiny clicks
            if (Math.abs(w) > 5 && Math.abs(h) > 5) {
                const zone = { type: 'rect', x: startPoint.x, y: startPoint.y, w, h };
                addZone(zone);
            }
            isDrawing = false;
            startPoint = null;
            drawZones();
        }
    });

    canvas.addEventListener('dblclick', (e) => {
        if (currentTool === 'poly' && currentPolyPoints.length >= 3) {
            const zone = { type: 'poly', points: [...currentPolyPoints] };
            addZone(zone);
            currentPolyPoints = [];
            drawZones();
        }
    });

    function getMousePos(canvas, evt) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: evt.clientX - rect.left,
            y: evt.clientY - rect.top
        };
    }

    function addZone(zone) {
        zones.push(zone);
        drawZones();

        // Normalize for backend if needed. Sending raw object.
        fetch(`${API_BASE}/zones`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(zone)
        });
    }

    function loadZones() {
        fetch(`${API_BASE}/zones`)
            .then(res => res.json())
            .then(data => {
                // Backend returns list of objects.
                // Convert old format {x, y} to {type: 'point', ...} if needed
                zones = data.map(z => z.type ? z : { ...z, type: 'point' });
                drawZones();
            });
    }

    function drawZones() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        zones.forEach(zone => {
            ctx.fillStyle = 'rgba(59, 130, 246, 0.5)';
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;

            ctx.beginPath();
            if (zone.type === 'point') {
                ctx.arc(zone.x, zone.y, 10, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            } else if (zone.type === 'rect') {
                ctx.rect(zone.x, zone.y, zone.w, zone.h);
                ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
                ctx.fill();
                ctx.stroke();
            } else if (zone.type === 'poly') {
                if (zone.points && zone.points.length > 0) {
                    ctx.moveTo(zone.points[0].x, zone.points[0].y);
                    zone.points.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
                    ctx.closePath();
                    ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
                    ctx.fill();
                    ctx.stroke();
                }
            }
        });
    }

    function updateSensitivity(value) {
        fetch(`${API_BASE}/sensitivity`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value })
        })
            .then(res => res.json())
            .then(data => console.log('Sensitivity updated:', data));
    }

    function fetchStatus() {
        fetch(`${API_BASE}/status`)
            .then(res => res.json())
            .then(data => {
                const statusBadge = document.getElementById('connection-status');
                const systemState = document.getElementById('system-state');

                if (data.connected) {
                    statusBadge.textContent = '🛡️ SYSTEM SHIELD ACTIVE';
                    statusBadge.className = 'status-badge connected';
                    systemState.textContent = 'OPTIMAL';
                    systemState.style.color = 'var(--success)';
                } else {
                    statusBadge.textContent = '⚠️ SYSTEM OFFLINE';
                    statusBadge.className = 'status-badge disconnected';
                    systemState.textContent = 'INTERRUPTED';
                    systemState.style.color = 'var(--danger)';
                }

                document.getElementById('intrusion-count').textContent = data.intrusion_count;

                const lastEventEl = document.getElementById('last-event');
                if (data.last_event) {
                    lastEventEl.textContent = data.last_event;
                    lastEventEl.style.color = data.alarm_active ? 'var(--danger)' : 'var(--warning)';
                } else {
                    lastEventEl.textContent = 'SCANNING...';
                    lastEventEl.style.color = 'var(--text-secondary)';
                }

                if (data.alarm_active) {
                    showAlert(data.last_event || "INTRUSION DETECTED");
                    silenceBtn.style.display = 'block';
                } else {
                    hideAlert();
                    silenceBtn.style.display = 'none';
                }
            })
            .catch(err => {
                // Ignore silent fetch errors
            });
    }

    function showAlert(message) {
        if (alertContainer.hasChildNodes()) return;

        const alert = document.createElement('div');
        alert.className = 'alert-intrusion';
        alert.textContent = message;
        alertContainer.appendChild(alert);

        startAlarmSound();
    }

    function hideAlert() {
        while (alertContainer.firstChild) {
            alertContainer.removeChild(alertContainer.firstChild);
        }
    }

    function startAlarmSound() {
        if (alarmOscillator) return;

        if (!alarmAudioCtx) {
            alarmAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }

        // Browsers require resume() if context was started before user interaction
        if (alarmAudioCtx.state === 'suspended') {
            alarmAudioCtx.resume();
        }

        alarmOscillator = alarmAudioCtx.createOscillator();
        const gainNode = alarmAudioCtx.createGain();

        alarmOscillator.type = 'sawtooth';
        alarmOscillator.frequency.setValueAtTime(880, alarmAudioCtx.currentTime);

        // Siren oscillation
        alarmFreqOsc = alarmAudioCtx.createOscillator();
        const freqGain = alarmAudioCtx.createGain();
        alarmFreqOsc.frequency.value = 2; // 2Hz
        freqGain.gain.value = 200;

        alarmFreqOsc.connect(freqGain);
        freqGain.connect(alarmOscillator.frequency);
        alarmFreqOsc.start();

        gainNode.gain.setValueAtTime(0.5, alarmAudioCtx.currentTime);
        alarmOscillator.connect(gainNode);
        gainNode.connect(alarmAudioCtx.destination);
        alarmOscillator.start();
    }

    function stopAlarmSound() {
        if (alarmOscillator) {
            try { alarmOscillator.stop(); } catch (e) { }
            alarmOscillator = null;
        }
        if (alarmFreqOsc) {
            try { alarmFreqOsc.stop(); } catch (e) { }
            alarmFreqOsc = null;
        }
        if (alarmAudioCtx) {
            try { alarmAudioCtx.close(); } catch (e) { }
            alarmAudioCtx = null;
        }
    }

    function startClock() {
        const timeEl = document.getElementById('live-time');
        function update() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            const dateStr = now.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
            timeEl.textContent = `${dateStr}, ${timeStr}`;
        }
        update();
        setInterval(update, 1000);
    }

    startClock();

    // ──────────────── Location Management ────────────────
    let locationMap = null;
    let locationMarker = null;

    function initLocationMap(lat, lng) {
        if (locationMap) {
            locationMap.setView([lat, lng], 15);
            if (locationMarker) {
                locationMarker.setLatLng([lat, lng]);
            } else {
                locationMarker = L.marker([lat, lng]).addTo(locationMap);
            }
            return;
        }

        locationMap = L.map('location-map', {
            zoomControl: false,
            attributionControl: false,
            dragging: false,
            scrollWheelZoom: false,
            doubleClickZoom: false,
            boxZoom: false,
            keyboard: false,
            touchZoom: false
        }).setView([lat, lng], 15);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(locationMap);

        locationMarker = L.marker([lat, lng]).addTo(locationMap);
    }

    function updateLocationUI(loc) {
        document.getElementById('location-name').textContent = loc.name || '--';
        document.getElementById('location-lat').textContent = loc.latitude !== 0 ? loc.latitude.toFixed(6) : '--';
        document.getElementById('location-lng').textContent = loc.longitude !== 0 ? loc.longitude.toFixed(6) : '--';

        // Update form placeholders
        document.getElementById('loc-name-input').placeholder = loc.name || 'Site Name';
        document.getElementById('loc-lat-input').placeholder = loc.latitude || '0.0';
        document.getElementById('loc-lng-input').placeholder = loc.longitude || '0.0';

        // Update Google Maps link
        const mapLink = document.getElementById('open-map-link');
        if (loc.latitude !== 0 || loc.longitude !== 0) {
            mapLink.href = `https://www.google.com/maps?q=${loc.latitude},${loc.longitude}`;
            initLocationMap(loc.latitude, loc.longitude);
        } else {
            mapLink.href = '#';
        }
    }

    function fetchLocation() {
        fetch(`${API_BASE}/location`)
            .then(res => res.json())
            .then(data => updateLocationUI(data))
            .catch(err => console.error('Location fetch error:', err));
    }

    fetchLocation();

    // Update location button
    document.getElementById('update-location-btn').addEventListener('click', () => {
        const name = document.getElementById('loc-name-input').value;
        const lat = document.getElementById('loc-lat-input').value;
        const lng = document.getElementById('loc-lng-input').value;

        const payload = {};
        if (name) payload.name = name;
        if (lat) payload.latitude = parseFloat(lat);
        if (lng) payload.longitude = parseFloat(lng);

        fetch(`${API_BASE}/location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                if (data.location) updateLocationUI(data.location);
                // Clear form
                document.getElementById('loc-name-input').value = '';
                document.getElementById('loc-lat-input').value = '';
                document.getElementById('loc-lng-input').value = '';
            });
    });

    // Use My Location (browser geolocation)
    document.getElementById('use-my-location-btn').addEventListener('click', () => {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser.');
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                document.getElementById('loc-lat-input').value = lat.toFixed(6);
                document.getElementById('loc-lng-input').value = lng.toFixed(6);
            },
            (error) => {
                alert('Unable to retrieve your location: ' + error.message);
            }
        );
    });

    // Camera Configuration
    document.getElementById('update-camera-btn').addEventListener('click', () => {
        const url = document.getElementById('camera-url-input').value;
        if (url === "") return;

        fetch(`${API_BASE}/camera`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        })
            .then(res => {
                if (!res.ok) {
                    return res.text().then(text => {
                        throw new Error(`Server returned ${res.status}: ${res.statusText}`);
                    });
                }
                return res.json();
            })
            .then(data => {
                if (data.status === 'updated') {
                    alert('Camera source updated to: ' + data.camera_url);
                } else {
                    alert('Error: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(err => {
                console.error('Camera update failed:', err);
                alert('Failed to update camera. ' + err.message);
            });
    });

    // Help resume AudioContext on first interaction
    document.addEventListener('click', () => {
        if (alarmAudioCtx && alarmAudioCtx.state === 'suspended') {
            alarmAudioCtx.resume();
        }
    }, { once: true });
});
