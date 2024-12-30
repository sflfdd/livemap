// Notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} animate__animated animate__fadeInDown`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('animate__fadeInDown');
        notification.classList.add('animate__fadeOutUp');
        setTimeout(() => notification.remove(), 1000);
    }, 3000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// Dark mode toggle
let darkMode = true;
const darkModeToggle = document.getElementById('toggleDarkMode');

darkModeToggle.addEventListener('click', () => {
    darkMode = !darkMode;
    document.body.classList.toggle('light-mode');
    darkModeToggle.innerHTML = `<i class="fas fa-${darkMode ? 'sun' : 'moon'}"></i>`;
    
    // Update map tiles
    const currentTileLayer = map.getTileLayers()[0];
    currentTileLayer.remove();
    
    if (darkMode) {
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap contributors, © CARTO'
        }).addTo(map);
    } else {
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }
});

// Timeline functionality
function loadTimeline() {
    fetch('/api/events')
        .then(response => response.json())
        .then(events => {
            const timeline = document.getElementById('eventTimeline');
            timeline.innerHTML = '';
            
            events
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .forEach(event => {
                    const timelineItem = document.createElement('div');
                    timelineItem.className = 'timeline-item';
                    timelineItem.innerHTML = `
                        <div class="timeline-item-content">
                            <span class="time">${moment(event.timestamp).format('LLLL')}</span>
                            <h6>${event.title}</h6>
                            <p>${event.description}</p>
                            <span class="location">${event.location.name}</span>
                        </div>
                    `;
                    
                    timelineItem.addEventListener('click', () => {
                        map.setView([event.location.lat, event.location.lng], 13);
                        showEventDetails(event);
                        $('#timelineModal').modal('hide');
                    });
                    
                    timeline.appendChild(timelineItem);
                });
        })
        .catch(error => {
            console.error('Error loading timeline:', error);
            showNotification('فشل تحميل الجدول الزمني', 'error');
        });
}

// Load timeline when modal is shown
$('#timelineModal').on('show.bs.modal', loadTimeline);

// Sources functionality
function loadSources() {
    const sourcesList = document.querySelector('.sources-list');
    sourcesList.innerHTML = `
        <div class="source-item">
            <h6>وكالات أنباء رسمية</h6>
            <ul>
                <li><a href="#" target="_blank">وكالة وفا</a></li>
                <li><a href="#" target="_blank">وكالة معا الإخبارية</a></li>
            </ul>
        </div>
        <div class="source-item">
            <h6>قنوات تلغرام</h6>
            <ul>
                <li><a href="#" target="_blank">القناة 1</a></li>
                <li><a href="#" target="_blank">القناة 2</a></li>
            </ul>
        </div>
        <div class="source-item">
            <h6>مواقع إخبارية</h6>
            <ul>
                <li><a href="#" target="_blank">الموقع 1</a></li>
                <li><a href="#" target="_blank">الموقع 2</a></li>
            </ul>
        </div>
    `;
}

// Load sources when modal is shown
$('#sourcesModal').on('show.bs.modal', loadSources);

// Location picker for submit news form
let selectedLocation = null;

map.on('click', function(e) {
    if ($('#submitNewsModal').is(':visible')) {
        selectedLocation = e.latlng;
        document.querySelector('#submitNewsForm input[placeholder="انقر على الخريطة لتحديد الموقع"]').value = 
            `${selectedLocation.lat.toFixed(6)}, ${selectedLocation.lng.toFixed(6)}`;
    }
});

// Reset form when modal is hidden
$('#submitNewsModal').on('hidden.bs.modal', function() {
    document.getElementById('submitNewsForm').reset();
    selectedLocation = null;
});
