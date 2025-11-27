// Configuración de la API
const API_URL = 'http://ec2-3-235-224-129.compute-1.amazonaws.com:8000';
const POLLING_INTERVAL = 10000; // 3 segundos
const TOTAL_SPOTS = 12; // Total de espacios de parqueo
const DEBUG_MODE = false; // Activar para ver logs de optimización


// Estado de la aplicación con control de cambios
let state = {
    estadias: [],
    eventos: [],
    facturas: [],
    lastEventId: 0,
    lastFacturaId: 0,
    // Mapas para tracking rápido
    estadiasMap: new Map(), // placa -> estadia
    eventosMap: new Map(),  // id -> evento
    facturasMap: new Map(), // id -> factura
    // Flags de cambios
    hasChanges: {
        estadias: false,
        eventos: false,
        facturas: false,
        stats: false
    }
};

// Placas de ejemplo para simulación
const placasEjemplo = [
    'ABC123', 'XYZ789', 'DEF456', 'GHI012', 'JKL345', 
    'MNO678', 'PQR901', 'STU234', 'VWX567', 'YZA890'
];

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚗 Sistema de Parqueo Iniciado');
    initParkingGrid();
    initEventListeners();
    startPolling();
    loadInitialData();
});

// Crear la cuadrícula de espacios de parqueo
function initParkingGrid() {
    const parkingGrid = document.getElementById('parkingGrid');
    parkingGrid.innerHTML = '';
    
    for (let i = 1; i <= TOTAL_SPOTS; i++) {
        const spot = createParkingSpot(i);
        parkingGrid.appendChild(spot);
    }
}

// Crear un espacio de parqueo
function createParkingSpot(number) {
    const spot = document.createElement('div');
    spot.className = 'parking-spot available';
    spot.dataset.spotNumber = number;
    
    spot.innerHTML = `
        <div class="spot-number">Espacio #${number}</div>
        <div class="spot-icon">🚗</div>
        <div class="spot-info">
            <div class="spot-plate">---</div>
            <div class="spot-time">Disponible</div>
        </div>
        <span class="spot-status available">Disponible</span>
    `;
    
    return spot;
}

// Inicializar event listeners
function initEventListeners() {
    // Botón de refrescar
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadAllData();
        showNotification('success', 'Actualizado', 'Datos actualizados correctamente');
    });
    
    // Botones de prueba
    document.getElementById('testEntrada').addEventListener('click', () => {
        simularEntrada();
    });
    
    document.getElementById('testSalida').addEventListener('click', () => {
        simularSalida();
    });
    
    // Cerrar modal
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('invoiceModal').addEventListener('click', (e) => {
        if (e.target.id === 'invoiceModal') closeModal();
    });
}

// Iniciar polling
function startPolling() {
    setInterval(() => {
        loadAllData();
    }, POLLING_INTERVAL);
}

// Cargar datos iniciales
async function loadInitialData() {
    await loadAllData();
}

// Cargar todos los datos
async function loadAllData() {
    try {
        await Promise.all([
            loadEstadias(),
            loadEventos(),
            loadFacturas()
        ]);
        updateUI();
    } catch (error) {
        console.error('Error cargando datos:', error);
    }
}

// Cargar estadías de la API
async function loadEstadias() {
    try {
        const response = await fetch(`${API_URL}/estadias/`);
        if (response.ok) {
            const newEstadias = await response.json();
            
            // Detectar cambios comparando con estado anterior
            const hasChanges = detectEstadiaChanges(newEstadias);
            
            if (hasChanges) {
                state.estadias = newEstadias;
                // Actualizar mapa para búsquedas rápidas
                updateEstadiasMap(newEstadias);
                state.hasChanges.estadias = true;
                state.hasChanges.stats = true;
            }
        }
    } catch (error) {
        console.error('Error cargando estadías:', error);
    }
}

// Detectar cambios en estadías
function detectEstadiaChanges(newEstadias) {
    // Si es la primera carga
    if (state.estadias.length === 0 && newEstadias.length > 0) {
        return true;
    }
    
    // Si cambió el número de estadías
    if (state.estadias.length !== newEstadias.length) {
        return true;
    }
    
    // Verificar cambios en estadías existentes
    for (const newEstadia of newEstadias) {
        const oldEstadia = state.estadiasMap.get(newEstadia.id);
        
        if (!oldEstadia) {
            return true; // Nueva estadía
        }
        
        // Verificar si cambió el estado (salida)
        if (oldEstadia.salida !== newEstadia.salida) {
            return true;
        }
    }
    
    return false;
}

// Actualizar mapa de estadías
function updateEstadiasMap(estadias) {
    state.estadiasMap.clear();
    estadias.forEach(estadia => {
        state.estadiasMap.set(estadia.id, estadia);
    });
}

// Cargar eventos de la API
async function loadEventos() {
    try {
        const response = await fetch(`${API_URL}/eventos/`);
        if (response.ok) {
            const eventos = await response.json();
            
            // Detectar solo eventos NUEVOS (con ID mayor al último conocido)
            const newEvents = eventos.filter(e => e.id > state.lastEventId);
            
            if (newEvents.length > 0) {
                // Actualizar último ID conocido
                state.lastEventId = Math.max(...eventos.map(e => e.id));
                
                // Agregar nuevos eventos al principio de la lista
                state.eventos = [...newEvents.reverse(), ...state.eventos].slice(0, 10);
                
                // Actualizar mapa
                newEvents.forEach(evento => {
                    state.eventosMap.set(evento.id, evento);
                });
                
                state.hasChanges.eventos = true;
                
                // Mostrar notificación solo para eventos nuevos
                newEvents.forEach(evento => {
                    const tipo = evento.tipo === 'entrada' ? 'success' : 'error';
                    const emoji = evento.tipo === 'entrada' ? '🚗 Entrada' : '🚀 Salida';
                    showNotification(tipo, emoji, `Vehículo ${evento.placa}`);
                });
            }
        }
    } catch (error) {
        console.error('Error cargando eventos:', error);
    }
}

// Cargar facturas de la API
async function loadFacturas() {
    try {
        const response = await fetch(`${API_URL}/facturas/`);
        if (response.ok) {
            const facturas = await response.json();
            
            // Detectar solo facturas NUEVAS
            const newInvoices = facturas.filter(f => f.id > state.lastFacturaId);
            
            if (newInvoices.length > 0) {
                // Actualizar último ID conocido
                state.lastFacturaId = Math.max(...facturas.map(f => f.id));
                
                // Agregar nuevas facturas al principio de la lista
                state.facturas = [...newInvoices.reverse(), ...state.facturas].slice(0, 10);
                
                // Actualizar mapa
                newInvoices.forEach(factura => {
                    state.facturasMap.set(factura.id, factura);
                });
                
                state.hasChanges.facturas = true;
                state.hasChanges.stats = true; // Las facturas afectan el total
                
                // Mostrar notificación solo para nuevas facturas
                newInvoices.forEach(factura => {
                    showNotification('success', '💰 Factura Generada', 
                        `${factura.placa} - $${factura.total.toLocaleString()}`);
                });
            }
        }
    } catch (error) {
        console.error('Error cargando facturas:', error);
    }
}

// Actualizar interfaz de usuario solo si hay cambios
function updateUI() {
    let updatesCount = 0;
    
    // Solo actualizar espacios de parqueo si cambiaron las estadías
    if (state.hasChanges.estadias) {
        if (DEBUG_MODE) console.log('🔄 Actualizando espacios de parqueo');
        updateParkingSpots();
        state.hasChanges.estadias = false;
        updatesCount++;
    }
    
    // Solo actualizar eventos si hay nuevos
    if (state.hasChanges.eventos) {
        if (DEBUG_MODE) console.log('🔄 Actualizando lista de eventos');
        updateEventsList();
        state.hasChanges.eventos = false;
        updatesCount++;
    }
    
    // Solo actualizar facturas si hay nuevas
    if (state.hasChanges.facturas) {
        if (DEBUG_MODE) console.log('🔄 Actualizando lista de facturas');
        updateInvoicesList();
        state.hasChanges.facturas = false;
        updatesCount++;
    }
    
    // Solo actualizar estadísticas si cambió algo relevante
    if (state.hasChanges.stats) {
        if (DEBUG_MODE) console.log('🔄 Actualizando estadísticas');
        updateStats();
        state.hasChanges.stats = false;
        updatesCount++;
    }
    
    if (DEBUG_MODE && updatesCount === 0) {
        console.log('✅ Sin cambios - No se actualizó nada');
    }
}

// Actualizar espacios de parqueo (solo los que cambiaron)
function updateParkingSpots() {
    const estadiasActivas = state.estadias.filter(e => e.salida === null);
    const spots = document.querySelectorAll('.parking-spot');
    
    // Crear un mapa de placas activas para búsqueda rápida
    const placasActivasMap = new Map();
    estadiasActivas.forEach((estadia, index) => {
        if (index < TOTAL_SPOTS) {
            placasActivasMap.set(index, estadia);
        }
    });
    
    // Actualizar cada espacio solo si cambió
    spots.forEach((spot, index) => {
        const estadia = placasActivasMap.get(index);
        const currentPlate = spot.querySelector('.spot-plate').textContent;
        const isCurrentlyOccupied = spot.classList.contains('occupied');
        const shouldBeOccupied = estadia !== undefined;
        
        // Detectar si cambió el estado de este espacio
        if (shouldBeOccupied) {
            const newPlate = estadia.placa;
            // Solo actualizar si es un cambio (nueva ocupación o cambio de placa)
            if (!isCurrentlyOccupied || currentPlate !== newPlate) {
                updateSpot(spot, estadia, true);
            }
        } else {
            // Solo actualizar si estaba ocupado y ahora está libre
            if (isCurrentlyOccupied) {
                updateSpot(spot, null, false);
            }
        }
    });
}

// Actualizar un espacio específico
function updateSpot(spot, estadia, occupied) {
    const spotIcon = spot.querySelector('.spot-icon');
    const spotPlate = spot.querySelector('.spot-plate');
    const spotTime = spot.querySelector('.spot-time');
    const spotStatus = spot.querySelector('.spot-status');
    
    if (occupied && estadia) {
        spot.className = 'parking-spot occupied';
        spotPlate.textContent = estadia.placa;
        spotTime.textContent = formatTimeAgo(estadia.entrada);
        spotStatus.textContent = 'Ocupado';
        spotStatus.className = 'spot-status occupied';
    } else {
        spot.className = 'parking-spot available';
        spotPlate.textContent = '---';
        spotTime.textContent = 'Disponible';
        spotStatus.textContent = 'Disponible';
        spotStatus.className = 'spot-status available';
    }
}

// Actualizar lista de eventos (solo agregar nuevos)
function updateEventsList() {
    const eventsList = document.getElementById('eventsList');
    
    // Si no hay eventos, mostrar empty state
    if (state.eventos.length === 0) {
        eventsList.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
                <p>No hay eventos recientes</p>
            </div>
        `;
        return;
    }
    
    // Si es la primera carga, renderizar todo
    const existingEvents = eventsList.querySelectorAll('.event-item');
    if (existingEvents.length === 0) {
        eventsList.innerHTML = state.eventos.map(evento => createEventHTML(evento)).join('');
        return;
    }
    
    // Solo agregar eventos nuevos al inicio
    const existingIds = new Set(
        Array.from(existingEvents).map(el => parseInt(el.dataset.eventId))
    );
    
    const newEventos = state.eventos.filter(e => !existingIds.has(e.id));
    
    if (newEventos.length > 0) {
        // Agregar nuevos eventos al inicio
        newEventos.reverse().forEach(evento => {
            const eventHTML = createEventHTML(evento);
            eventsList.insertAdjacentHTML('afterbegin', eventHTML);
        });
        
        // Mantener solo los últimos 10
        const allEvents = eventsList.querySelectorAll('.event-item');
        if (allEvents.length > 10) {
            for (let i = 10; i < allEvents.length; i++) {
                allEvents[i].remove();
            }
        }
    }
}

// Crear HTML de un evento
function createEventHTML(evento) {
    return `
        <div class="event-item ${evento.tipo}" data-event-id="${evento.id}">
            <div class="event-header">
                <div class="event-type ${evento.tipo}">
                    ${evento.tipo === 'entrada' ? '🚗 Entrada' : '🚀 Salida'}
                </div>
                <div class="event-time">${formatTime(evento.timestamp)}</div>
            </div>
            <div class="event-plate">${evento.placa}</div>
        </div>
    `;
}

// Actualizar lista de facturas (solo agregar nuevas)
function updateInvoicesList() {
    const invoicesList = document.getElementById('invoicesList');
    
    // Si no hay facturas, mostrar empty state
    if (state.facturas.length === 0) {
        invoicesList.innerHTML = `
            <div class="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
                <p>No hay facturas generadas</p>
            </div>
        `;
        return;
    }
    
    // Si es la primera carga, renderizar todo
    const existingInvoices = invoicesList.querySelectorAll('.invoice-card');
    if (existingInvoices.length === 0) {
        invoicesList.innerHTML = state.facturas.map(factura => createInvoiceHTML(factura)).join('');
        return;
    }
    
    // Solo agregar facturas nuevas al inicio
    const existingIds = new Set(
        Array.from(existingInvoices).map(el => parseInt(el.dataset.invoiceId))
    );
    
    const newFacturas = state.facturas.filter(f => !existingIds.has(f.id));
    
    if (newFacturas.length > 0) {
        // Agregar nuevas facturas al inicio
        newFacturas.reverse().forEach(factura => {
            const invoiceHTML = createInvoiceHTML(factura);
            invoicesList.insertAdjacentHTML('afterbegin', invoiceHTML);
        });
        
        // Mantener solo las últimas 10
        const allInvoices = invoicesList.querySelectorAll('.invoice-card');
        if (allInvoices.length > 10) {
            for (let i = 10; i < allInvoices.length; i++) {
                allInvoices[i].remove();
            }
        }
    }
}

// Crear HTML de una factura
function createInvoiceHTML(factura) {
    return `
        <div class="invoice-card" data-invoice-id="${factura.id}" onclick="showInvoiceDetail(${factura.id})">
            <div class="invoice-header">
                <div class="invoice-plate">${factura.placa}</div>
                <div class="invoice-amount">$${factura.total.toLocaleString()}</div>
            </div>
            <div class="invoice-details">
                <span>${factura.minutos} min</span>
                <span>${formatTime(factura.fecha)}</span>
            </div>
        </div>
    `;
}

// Actualizar estadísticas
function updateStats() {
    const ocupados = state.estadias.filter(e => e.salida === null).length;
    const disponibles = TOTAL_SPOTS - ocupados;
    const totalHoy = state.facturas.reduce((sum, f) => sum + f.total, 0);
    
    document.getElementById('ocupados').textContent = ocupados;
    document.getElementById('disponibles').textContent = disponibles;
    document.getElementById('totalHoy').textContent = `$${totalHoy.toLocaleString()}`;
}

// Mostrar detalle de factura
function showInvoiceDetail(facturaId) {
    const factura = state.facturas.find(f => f.id === facturaId);
    if (!factura) return;
    
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="invoice-detail">
            <span class="invoice-detail-label">Placa</span>
            <span class="invoice-detail-value">${factura.placa}</span>
        </div>
        <div class="invoice-detail">
            <span class="invoice-detail-label">Tiempo</span>
            <span class="invoice-detail-value">${factura.minutos} minutos</span>
        </div>
        <div class="invoice-detail">
            <span class="invoice-detail-label">Tarifa/minuto</span>
            <span class="invoice-detail-value">$${factura.tarifa_minuto}</span>
        </div>
        <div class="invoice-detail">
            <span class="invoice-detail-label">Fecha</span>
            <span class="invoice-detail-value">${new Date(factura.fecha).toLocaleString('es-ES')}</span>
        </div>
        <div class="invoice-detail">
            <span class="invoice-detail-label">Total</span>
            <span class="invoice-detail-value">$${factura.total.toLocaleString()}</span>
        </div>
    `;
    
    document.getElementById('invoiceModal').classList.add('active');
}

// Cerrar modal
function closeModal() {
    document.getElementById('invoiceModal').classList.remove('active');
}

// Mostrar notificación
function showNotification(type, title, message) {
    const container = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    notification.innerHTML = `
        <div class="notification-header">${title}</div>
        <div class="notification-body">${message}</div>
    `;
    
    container.appendChild(notification);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'notificationSlide 0.4s ease reverse';
        setTimeout(() => notification.remove(), 400);
    }, 5000);
}

// Simular entrada de vehículo
async function simularEntrada() {
    // Encontrar una placa que no esté en el parqueadero
    const estadiasActivas = state.estadias.filter(e => e.salida === null);
    const placasOcupadas = estadiasActivas.map(e => e.placa);
    const placasDisponibles = placasEjemplo.filter(p => !placasOcupadas.includes(p));
    
    if (placasDisponibles.length === 0) {
        showNotification('error', 'Error', 'Parqueadero lleno - No hay espacios disponibles');
        return;
    }
    
    const placa = placasDisponibles[Math.floor(Math.random() * placasDisponibles.length)];
    
    try {
        const response = await fetch(`${API_URL}/eventos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ placa, tipo: 'entrada' })
        });
        
        if (response.ok) {
            await loadAllData();
            showNotification('success', '🚗 Entrada Simulada', `Vehículo ${placa} ingresó`);
        } else {
            const error = await response.json();
            showNotification('error', 'Error', error.detail || 'Error al registrar entrada');
        }
    } catch (error) {
        showNotification('error', 'Error', 'No se pudo conectar con la API');
        console.error('Error:', error);
    }
}

// Simular salida de vehículo
async function simularSalida() {
    const estadiasActivas = state.estadias.filter(e => e.salida === null);
    
    if (estadiasActivas.length === 0) {
        showNotification('error', 'Error', 'No hay vehículos en el parqueadero');
        return;
    }
    
    const estadia = estadiasActivas[Math.floor(Math.random() * estadiasActivas.length)];
    const placa = estadia.placa;
    
    try {
        // Registrar salida
        const response = await fetch(`${API_URL}/eventos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ placa, tipo: 'salida' })
        });
        
        if (!response.ok) {
            const error = await response.json();
            showNotification('error', 'Error', error.detail || 'Error al registrar salida');
            return;
        }
        
        // Generar factura automáticamente
        const facturaResponse = await fetch(`${API_URL}/facturas/${placa}`, {
            method: 'POST'
        });
        
        if (facturaResponse.ok) {
            const factura = await facturaResponse.json();
            await loadAllData();
            showNotification('success', '🚀 Salida Simulada', 
                `${placa} - Total: $${factura.total.toLocaleString()}`);
        } else {
            await loadAllData();
            showNotification('error', 'Error', 'Error al generar factura');
        }
    } catch (error) {
        showNotification('error', 'Error', 'No se pudo conectar con la API');
        console.error('Error:', error);
    }
}

// Formatear tiempo (hace X minutos)
function formatTimeAgo(timestamp) {
    const now = new Date();
    const date = new Date(timestamp);
    const diff = Math.floor((now - date) / 1000 / 60); // minutos
    
    if (diff < 1) return 'Ahora';
    if (diff === 1) return 'Hace 1 minuto';
    if (diff < 60) return `Hace ${diff} minutos`;
    
    const hours = Math.floor(diff / 60);
    if (hours === 1) return 'Hace 1 hora';
    if (hours < 24) return `Hace ${hours} horas`;
    
    const days = Math.floor(hours / 24);
    if (days === 1) return 'Hace 1 día';
    return `Hace ${days} días`;
}

// Formatear tiempo (HH:MM)
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Exponer función para usar desde HTML
window.showInvoiceDetail = showInvoiceDetail;