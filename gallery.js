document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Najdeme všechny obrázky v galeriích
    var images = document.querySelectorAll('.galerie-grid img');
    
    if (images.length === 0) return; // Pokud na stránce není galerie, nic neděláme

    // 2. Vytvoříme HTML pro Lightbox (černé okno)
    var lightbox = document.createElement('div');
    lightbox.id = 'lightbox';
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <span class="lightbox-close">&times;</span>
        <img class="lightbox-content" id="lightbox-img">
        <a class="lightbox-prev">&#10094;</a>
        <a class="lightbox-next">&#10095;</a>
    `;
    document.body.appendChild(lightbox);

    // Proměnné
    var lightboxImg = document.getElementById('lightbox-img');
    var currentIndex = 0;

    // 3. Funkce pro otevření
    function openLightbox(index) {
        currentIndex = index;
        lightboxImg.src = images[currentIndex].src;
        lightbox.style.display = 'flex';
    }

    // 4. Funkce pro zavření
    function closeLightbox() {
        lightbox.style.display = 'none';
    }

    // 5. Funkce pro další/předchozí
    function showNext() {
        currentIndex++;
        if (currentIndex >= images.length) currentIndex = 0; // Smyčka na začátek
        lightboxImg.src = images[currentIndex].src;
    }

    function showPrev() {
        currentIndex--;
        if (currentIndex < 0) currentIndex = images.length - 1; // Smyčka na konec
        lightboxImg.src = images[currentIndex].src;
    }

    // --- EVENT LISTENERS (Klikání) ---

    // Kliknutí na fotku v galerii
    images.forEach((img, index) => {
        img.style.cursor = 'pointer'; // Aby bylo jasné, že je klikací
        img.addEventListener('click', function() {
            openLightbox(index);
        });
    });

    // Ovládací prvky
    document.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    document.querySelector('.lightbox-next').addEventListener('click', showNext);
    document.querySelector('.lightbox-prev').addEventListener('click', showPrev);

    // Kliknutí mimo obrázek zavře galerii
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) closeLightbox();
    });

    // Ovládání klávesnicí (Šipky a ESC)
    document.addEventListener('keydown', function(e) {
        if (lightbox.style.display === 'flex') {
            if (e.key === 'ArrowLeft') showPrev();
            if (e.key === 'ArrowRight') showNext();
            if (e.key === 'Escape') closeLightbox();
        }
    });
});