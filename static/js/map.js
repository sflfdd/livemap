// Initialize map with performance optimizations
const map = L.map('map', {
    preferCanvas: true,
    wheelDebounceTime: 150,
    doubleClickZoom: false,
    zoomControl: false,
    attributionControl: false
}).setView([31.5, 34.5], 8);

// Add custom attribution control
L.control.attribution({
    prefix: false,
    position: 'bottomright'
}).addTo(map);

// Add zoom control to the left side
L.control.zoom({
    position: 'topleft'
}).addTo(map);

// Initialize marker clusters with custom options
const markers = L.markerClusterGroup({
    chunkedLoading: true,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    maxClusterRadius: 50,
    iconCreateFunction: function(cluster) {
        return L.divIcon({
            html: `<div class="cluster-marker">${cluster.getChildCount()}</div>`,
            className: 'custom-cluster',
            iconSize: L.point(40, 40)
        });
    }
});

map.addLayer(markers);

// Custom marker icons for different event types
const markerIcons = {
    urgent: L.divIcon({
        html: '<div class="custom-marker marker-urgent"><i class="fas fa-exclamation"></i></div>',
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    }),
    military: L.divIcon({
        html: '<div class="custom-marker marker-military"><i class="fas fa-fighter-jet"></i></div>',
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    }),
    humanitarian: L.divIcon({
        html: '<div class="custom-marker marker-humanitarian"><i class="fas fa-hands-helping"></i></div>',
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    })
};

// Event handlers
let selectedMarker = null;
let activeFilters = new Set(['all']);

// Load and display events
async function loadEvents(filters = ['all']) {
    try {
        const response = await fetch('/api/events');
        if (!response.ok) throw new Error('Failed to load events');
        
        const events = await response.json();
        markers.clearLayers();
        
        events.forEach(event => {
            if (filters.includes('all') || filters.includes(event.type)) {
                const marker = L.marker([event.location.lat, event.location.lng], {
                    icon: markerIcons[event.type] || markerIcons.default
                });
                
                marker.eventData = event;
                marker.on('click', () => showEventDetails(event));
                markers.addLayer(marker);
                
                // Add to news feed if it's recent (last 24 hours)
                const eventTime = new Date(event.timestamp);
                if (Date.now() - eventTime < 24 * 60 * 60 * 1000) {
                    addNewsItem(event);
                }
            }
        });
    } catch (error) {
        console.error('Error loading events:', error);
        showNotification('فشل تحميل الأحداث', 'error');
    }
}

// Show event details in the side panel
function showEventDetails(event) {
    const panel = document.getElementById('eventDetailsPanel');
    const content = panel.querySelector('.event-details-content');
    
    content.innerHTML = `
        <div class="event-time">${moment(event.timestamp).format('LLLL')}</div>
        <h4 class="event-title">${event.title}</h4>
        <div class="event-description">${event.description}</div>
        ${event.images ? `
            <div class="event-images">
                ${event.images.map(img => `
                    <img src="${img}" alt="صورة الحدث" class="img-fluid rounded mb-2">
                `).join('')}
            </div>
        ` : ''}
        <div class="event-source">
            <small>المصدر: <a href="${event.source}" target="_blank">${event.source}</a></small>
        </div>
    `;
    
    panel.classList.add('active');
}

// Add news item to the feed
function addNewsItem(event) {
    const newsContainer = document.getElementById('newsFeed');
    const newsItem = document.createElement('div');
    newsItem.className = `news-item ${event.type}`;
    newsItem.innerHTML = `
        <div class="news-item-header">
            <span class="news-item-type">${getEventTypeText(event.type)}</span>
            <span class="news-item-time">${moment(event.timestamp).fromNow()}</span>
        </div>
        <div class="news-item-content">
            <h6>${event.title}</h6>
            <p>${event.description}</p>
        </div>
        <div class="news-item-footer">
            <span class="news-item-location">${event.location.name}</span>
            <a href="${event.source}" target="_blank" class="news-item-source">المصدر</a>
        </div>
    `;
    
    newsItem.addEventListener('click', () => {
        map.setView([event.location.lat, event.location.lng], 13);
        showEventDetails(event);
    });
    
    newsContainer.insertBefore(newsItem, newsContainer.firstChild);
}

// Helper function to get event type text
function getEventTypeText(type) {
    const types = {
        urgent: 'عاجل',
        military: 'عسكري',
        humanitarian: 'إنساني'
    };
    return types[type] || type;
}

// Filter events
document.querySelectorAll('.news-filters button').forEach(button => {
    button.addEventListener('click', () => {
        const filter = button.dataset.filter;
        
        // Update active filters
        if (filter === 'all') {
            activeFilters.clear();
            activeFilters.add('all');
        } else {
            activeFilters.delete('all');
            if (activeFilters.has(filter)) {
                activeFilters.delete(filter);
                if (activeFilters.size === 0) {
                    activeFilters.add('all');
                }
            } else {
                activeFilters.add(filter);
            }
        }
        
        // Update button states
        document.querySelectorAll('.news-filters button').forEach(btn => {
            btn.classList.toggle('active', activeFilters.has(btn.dataset.filter));
        });
        
        // Reload events with new filters
        loadEvents(Array.from(activeFilters));
    });
});

// Toggle sidebar
document.getElementById('toggleSidebar').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('collapsed');
    document.querySelector('.map-container').classList.toggle('expanded');
    map.invalidateSize();
});

// Close event details panel
document.getElementById('closeEventDetails').addEventListener('click', () => {
    document.getElementById('eventDetailsPanel').classList.remove('active');
});

// Submit news form handler
document.getElementById('submitNewsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/api/events', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(formData))
        });
        
        if (!response.ok) throw new Error('Failed to submit news');
        
        showNotification('تم إرسال الخبر بنجاح', 'success');
        $('#submitNewsModal').modal('hide');
        loadEvents(Array.from(activeFilters));
    } catch (error) {
        console.error('Error submitting news:', error);
        showNotification('فشل إرسال الخبر', 'error');
    }
});

// Initialize map
loadEvents();

// Update timestamps every minute
setInterval(() => {
    document.querySelectorAll('.news-item-time').forEach(timeElement => {
        const time = timeElement.dataset.time;
        if (time) {
            timeElement.textContent = moment(time).fromNow();
        }
    });
}, 60000);

// Palestine coordinates and bounds
const PALESTINE_CENTER = [31.9522, 35.2332]; // مركز فلسطين
const PALESTINE_BOUNDS = [
    [29.5, 34.2], // جنوب غرب
    [33.4, 35.9]  // شمال شرق
];
const DEFAULT_ZOOM = 8;

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    map.setMaxBounds(PALESTINE_BOUNDS);
    map.setMinZoom(7);
    map.setMaxZoom(18);
    map.setZoom(DEFAULT_ZOOM);
    map.panTo(PALESTINE_CENTER);
});

// Add tile layer with proper attribution and caching
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    crossOrigin: true,
    maxZoom: 19,
    minZoom: 6
}).addTo(map);

// Custom emoji marker function with animation
function createEmojiMarker(emoji, latlng) {
    return L.marker(latlng, {
        icon: L.divIcon({
            html: `<div class="marker-emoji animate__animated animate__bounceIn">${emoji}</div>`,
            className: 'emoji-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        })
    });
}

// Location search functionality
const debouncedSearch = _.debounce(async function(searchQuery) {
    if (!searchQuery) return;
    
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`, {
            headers: {
                'Accept': 'application/json',
                'User-Agent': 'LiveMap Palestine News'
            }
        });
        
        if (!response.ok) throw new Error('Search request failed');
        
        const data = await response.json();
        
        if (data && data.length > 0) {
            const location = data[0];
            map.setView([location.lat, location.lon], 15);
            L.popup()
                .setLatLng([location.lat, location.lon])
                .setContent(DOMPurify.sanitize(`<div class="search-result">${location.display_name}</div>`))
                .openOn(map);
        } else {
            showNotification('لم يتم العثور على الموقع', 'warning');
        }
    } catch (error) {
        console.error('Error searching location:', error);
        showNotification('حدث خطأ أثناء البحث', 'error');
    }
}, 300);

document.getElementById('search-button').addEventListener('click', function() {
    const searchQuery = document.getElementById('location-search').value;
    debouncedSearch(searchQuery);
});

// Google Maps link handler
document.getElementById('google-maps-link').addEventListener('change', function() {
    const link = this.value;
    const coords = extractCoordsFromGoogleMapsLink(link);
    if (coords) {
        map.setView([coords.lat, coords.lng], 15);
        createEmojiMarker('📍', [coords.lat, coords.lng]).addTo(map);
    } else {
        alert('الرجاء إدخال رابط Google Maps صحيح');
    }
});

// Extract coordinates from Google Maps link
function extractCoordsFromGoogleMapsLink(link) {
    try {
        const regex = /@(-?\d+\.\d+),(-?\d+\.\d+)/;
        const match = link.match(regex);
        if (match) {
            return {
                lat: parseFloat(match[1]),
                lng: parseFloat(match[2])
            };
        }
    } catch (error) {
        console.error('Error extracting coordinates:', error);
    }
    return null;
}

// Event type filters
document.querySelectorAll('.event-filters input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const eventType = this.value;
        const isChecked = this.checked;
        // Update markers visibility based on filter
        updateMarkerVisibility(eventType, isChecked);
    });
});

// Function to update marker visibility
function updateMarkerVisibility(eventType, isVisible) {
    // Get all markers of the specified event type
    const markers = document.querySelectorAll(`.marker-${eventType}`);
    markers.forEach(marker => {
        marker.style.display = isVisible ? 'block' : 'none';
    });
}

// Function to add event marker to map
function addEventMarker(event) {
    const marker = createEmojiMarker(getEventEmoji(event.type), [event.latitude, event.longitude]);
    marker.bindPopup(`
        <div class="event-popup">
            <h6>${event.title}</h6>
            <p>${event.description}</p>
            <small>المصدر: ${event.source}</small>
            ${event.is_breaking ? '<span class="badge bg-danger">خبر عاجل</span>' : ''}
        </div>
    `);
    marker.addTo(map);
}

// Function to get emoji based on event type
function getEventEmoji(eventType) {
    const emojiMap = {
        'شهداء': '💔',
        'قصف': '💥',
        'مظاهرات': '👥',
        'اعتقالات': '🚔',
        'حواجز': '🚧',
        'default': '📍'
    };
    return emojiMap[eventType] || emojiMap.default;
}

// Improved event loading with pagination
async function loadEvents(page = 1, limit = 50) {
    try {
        const response = await fetch(`/api/events?page=${page}&limit=${limit}`);
        if (!response.ok) throw new Error('Failed to load events');
        
        const events = await response.json();
        clearMarkers();
        events.forEach(event => addEventMarker(event));
        updateEventsList(events);
    } catch (error) {
        console.error('Error loading events:', error);
        showNotification('فشل تحميل الأحداث', 'error');
    }
}

// Load events when page loads
document.addEventListener('DOMContentLoaded', loadEvents);

// Function to update events list
function updateEventsList(events) {
    const eventsList = document.getElementById('eventsList');
    if (!eventsList) return;

    eventsList.innerHTML = '';
    events
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .forEach(event => {
            const eventElement = document.createElement('a');
            eventElement.className = 'list-group-item list-group-item-action';
            eventElement.innerHTML = `
                <div class="event-title">${event.title}</div>
                <small class="event-timestamp">${new Date(event.timestamp).toLocaleString('ar-EG')}</small>
            `;
            eventElement.onclick = () => focusEvent(event.id);
            eventsList.appendChild(eventElement);
        });
}

// Function to focus event
function focusEvent(eventId) {
    const markerObj = map._layers[Object.keys(map._layers)[Object.keys(map._layers).length - 1]];
    if (markerObj) {
        map.setView(markerObj.getLatLng(), 15);
        markerObj.openPopup();
    }
}

// Function to clear markers
function clearMarkers() {
    map.eachLayer(function (layer) {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
}

// Function to load news
function loadNews() {
    fetch('/api/news')
        .then(response => response.json())
        .then(news => {
            updateNewsFeed(news);
            addNewsToMap(news);
        });
}

// Function to add news to map
function addNewsToMap(news) {
    news.forEach(item => {
        if (item.lat && item.lng) {
            const marker = L.marker([item.lat, item.lng], {
                icon: L.divIcon({
                    className: 'news-marker',
                    html: '<i class="fas fa-newspaper" style="color: #e74c3c;"></i>',
                    iconSize: [20, 20]
                })
            }).addTo(map);

            const popupContent = `
                <div class="news-popup">
                    ${item.image_url ? `<img src="${item.image_url}" style="width:100%;max-height:150px;object-fit:cover;">` : ''}
                    <h3>${item.title}</h3>
                    <p>${item.content}</p>
                    <p class="text-muted">
                        <small>
                            المصدر: ${item.source} - 
                            ${new Date(item.timestamp).toLocaleString('ar-EG')}
                        </small>
                    </p>
                    <a href="${item.url}" target="_blank" class="btn btn-sm btn-primary">اقرأ المزيد</a>
                </div>
            `;

            marker.bindPopup(popupContent);
        }
    });
}

// Function to update news feed
function updateNewsFeed(news) {
    const feed = $('#news-feed');
    feed.empty();

    news.forEach(item => {
        const newsElement = $(`
            <div class="news-card" data-id="${item.id}">
                ${item.image_url ? `
                    <div class="news-image">
                        <img src="${item.image_url}" alt="${item.title}">
                    </div>
                ` : ''}
                <div class="news-content">
                    <h4>${item.title}</h4>
                    <p>${item.content}</p>
                    <div class="news-meta">
                        <span class="news-source">${item.source}</span>
                        <span class="news-time">${new Date(item.timestamp).toLocaleString('ar-EG')}</span>
                    </div>
                    <div class="news-footer">
                        <a href="${item.url}" target="_blank" class="btn btn-sm btn-link">اقرأ المزيد</a>
                        ${item.lat && item.lng ? `
                            <button class="btn btn-sm btn-secondary show-on-map" data-lat="${item.lat}" data-lng="${item.lng}">
                                عرض على الخريطة
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `);

        newsElement.find('.show-on-map').click(function() {
            const lat = $(this).data('lat');
            const lng = $(this).data('lng');
            map.setView([lat, lng], 12);
            const marker = map._layers[Object.keys(map._layers)[Object.keys(map._layers).length - 1]];
            if (marker) {
                marker.openPopup();
            }
        });

        feed.append(newsElement);
    });
}

// Search news
$('#searchNews').on('input', function() {
    const searchText = $(this).val().toLowerCase();
    $('.news-card').each(function() {
        const newsText = $(this).text().toLowerCase();
        if (newsText.includes(searchText)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});

// Event type filter
document.getElementById('eventTypeFilter')?.addEventListener('change', function(e) {
    const type = e.target.value;
    fetch(`/api/events${type ? `?type=${type}` : ''}`)
        .then(response => response.json())
        .then(data => {
            clearMarkers();
            data.events.forEach(addEventMarker);
            updateEventsList(data.events);
        });
});

// Date filter
document.getElementById('dateFilter')?.addEventListener('change', function(e) {
    const date = e.target.value;
    fetch(`/api/events${date ? `?date=${date}` : ''}`)
        .then(response => response.json())
        .then(data => {
            clearMarkers();
            data.events.forEach(addEventMarker);
            updateEventsList(data.events);
        });
});
