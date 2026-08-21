document.addEventListener('DOMContentLoaded', function() {
    const viewAllLinks = document.querySelectorAll('.view-all-link');
    
    viewAllLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.closest('section');
            console.log('section', section);
            const hiddenItems = section.querySelectorAll('.hideable');
            console.log('hiddenitems', hiddenItems);
            
            if (this.textContent.includes('View all')) {
                hiddenItems.forEach(item => {
                    item.classList.remove('hidden-item');
                });
                this.textContent = 'Show less';
            } else {
                hiddenItems.forEach(item => {
                    item.classList.add('hidden-item');
                });
                this.textContent = 'View all';
            }

        });
    });
});