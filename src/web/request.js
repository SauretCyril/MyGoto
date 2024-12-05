// Add URL parameters handling when page loads
window.addEventListener('load', function() {
    let ispdf = false;  // Changed to let
    const urlParams = new URLSearchParams(window.location.search);
    const typed = urlParams.get('ispdf');
    const value = decodeURIComponent(urlParams.get('value') || '');
    const description = decodeURIComponent(urlParams.get('description') || '');
    
    // Petit délai pour s'assurer que tous les éléments sont chargés
    setTimeout(() => {
        document.getElementById('title').textContent = description;
        
        if (typed === "pdf") {
            ispdf = true;
        } 

        if (value !== "") {
            document.querySelectorAll('.input-container').forEach(container => {
                container.classList.remove('active');
            });

            if (ispdf) {
                document.getElementById('pdf-source').checked = true;   
                document.getElementById('file-input').value = value;
                document.getElementById('pdf-input').classList.add('active');
                // Déclencher l'événement change
                document.getElementById('pdf-source').dispatchEvent(new Event('change'));
            } else {
                document.getElementById('url-source').checked = true;
                document.getElementById('url-input').classList.add('active');
                document.getElementById('url-input-field').value = value;
                // Déclencher l'événement change
                document.getElementById('url-source').dispatchEvent(new Event('change'));
            }
        }
    }, 100);  // Délai de 100ms
});
