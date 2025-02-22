document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-availability').addEventListener('click', function() {
        // Get the container and last availability entry
        const container = document.getElementById('availabilities-container');
        const lastEntry = document.querySelector('.availability-entry:last-of-type');
        
        // Clone it
        const newEntry = lastEntry.cloneNode(true);
        
        // Update the indices in the new entry's field names
        const currentIndex = document.querySelectorAll('.availability-entry').length;
        newEntry.querySelectorAll('select, input').forEach(input => {
            const oldName = input.getAttribute('name');
            if (oldName) {
                const newName = oldName.replace(/\d+/, currentIndex);
                input.setAttribute('name', newName);
                // Don't clear CSRF token value
                if (!oldName.includes('csrf_token')) {
                    input.value = '';  // Clear only non-csrf values
                }
            }
        });
        
        // Append the new entry to the container
        container.appendChild(newEntry);
    });
}); 