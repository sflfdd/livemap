const eventMarkers = {
    MILITARY: {
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div class="marker-pin military"><i class="fas fa-fighter-jet"></i></div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42]
        }),
        color: '#d63031'
    },
    HUMANITARIAN: {
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div class="marker-pin humanitarian"><i class="fas fa-hands-helping"></i></div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42]
        }),
        color: '#00b894'
    },
    PROTEST: {
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div class="marker-pin protest"><i class="fas fa-bullhorn"></i></div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42]
        }),
        color: '#fdcb6e'
    },
    DAMAGE: {
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div class="marker-pin damage"><i class="fas fa-house-damage"></i></div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42]
        }),
        color: '#636e72'
    },
    MEDICAL: {
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div class="marker-pin medical"><i class="fas fa-hospital"></i></div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42]
        }),
        color: '#e17055'
    }
};

function addEventMarker(map, lat, lng, type, title, description) {
    const marker = L.marker([lat, lng], {
        icon: eventMarkers[type].icon
    });
    
    const popupContent = `
        <div class="event-popup">
            <h3>${title}</h3>
            <p>${description}</p>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    marker.addTo(map);
    return marker;
}
