document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Najdeme všechny obrázky v galeriích
    var images = document.querySelectorAll('.galerie-grid img');
    
    if (images.length === 0) return;

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

    // --- NOVÁ CHYTRÁ FUNKCE ---
    // Získá skutečnou cestu k fotce a rovnou ji "probudí" i v mřížce na pozadí
    function getAndWakeUpImage(index) {
        var img = images[index];
        // Vezme cestu buď z data-src (nenačtená), nebo src (už načtená)
        var realSrc = img.dataset.src || img.src;
        
        // Pokud fotka v mřížce ještě spí, probudíme ji (aby nebyla prázdná, až okno zavřeme)
        if (img.dataset.src) {
            img.src = realSrc;
            img.classList.add("visible");
            delete img.dataset.src; // Už není potřeba ji dál hlídat při scrollování
        }
        
        return realSrc;
    }

    // 3. Funkce pro otevření
    function openLightbox(index) {
        currentIndex = index;
        lightboxImg.src = getAndWakeUpImage(currentIndex);
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
        lightboxImg.src = getAndWakeUpImage(currentIndex);
    }

    function showPrev() {
        currentIndex--;
        if (currentIndex < 0) currentIndex = images.length - 1; // Smyčka na konec
        lightboxImg.src = getAndWakeUpImage(currentIndex);
    }

    // --- EVENT LISTENERS (Klikání) ---

    // Kliknutí na fotku v galerii
    images.forEach((img, index) => {
        img.style.cursor = 'pointer';
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