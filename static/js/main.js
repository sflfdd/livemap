// تحديث الأخبار العاجلة
function updateBreakingNews() {
    fetch('/api/breaking-news')
        .then(response => response.json())
        .then(news => {
            const container = document.getElementById('breaking-news-container');
            container.innerHTML = ''; // مسح المحتوى القديم

            news.forEach((item, index) => {
                const div = document.createElement('div');
                div.className = `carousel-item ${index === 0 ? 'active' : ''}`;
                
                const content = document.createElement('div');
                content.className = 'p-3';
                content.innerHTML = `
                    <div class="d-flex align-items-center">
                        <span class="badge bg-danger me-2">${item.source}</span>
                        <h6 class="mb-0">${item.title}</h6>
                    </div>
                    ${item.link ? `<a href="${item.link}" target="_blank" class="small">اقرأ المزيد</a>` : ''}
                `;
                
                div.appendChild(content);
                container.appendChild(div);
            });

            // تهيئة الـ Carousel
            new bootstrap.Carousel(document.getElementById('breaking-news-carousel'), {
                interval: 5000
            });
        })
        .catch(error => console.error('Error fetching breaking news:', error));
}

// تحديث الأخبار كل 5 دقائق
setInterval(updateBreakingNews, 300000);

// تحديث الأخبار عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', updateBreakingNews);
