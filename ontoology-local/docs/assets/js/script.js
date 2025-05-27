
// OnToology Local Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add copy functionality to URI links
    document.querySelectorAll('.uri-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                navigator.clipboard.writeText(this.textContent).then(() => {
                    // Show temporary feedback
                    const original = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = original;
                    }, 1000);
                });
            }
        });
    });
    
    // Add search functionality if search box exists
    const searchBox = document.getElementById('search');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const cards = document.querySelectorAll('.ontology-card');
            
            cards.forEach(card => {
                const title = card.querySelector('.ontology-title').textContent.toLowerCase();
                const description = card.querySelector('.ontology-description').textContent.toLowerCase();
                
                if (title.includes(query) || description.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});
