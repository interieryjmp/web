document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Nastavení Intersection Observeru (hlídač viditelnosti)
    var observerOptions = {
        root: null, // Sleduje viewport prohlížeče
        rootMargin: "0px 0px 200px 0px", // Začne načítat 200px PŘEDTÍM, než prvek vyjede na obrazovku (aby to bylo plynulé)
        threshold: 0.01 // Spustí se hned, jak se objeví kousek prvku
    };

    var observer = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var target = entry.target;
                
                // A) Pokud je to OBRÁZEK v galerii
                if (target.tagName === "IMG" && target.dataset.src) {
                    target.src = target.dataset.src; // Přehodíme data-src do src -> prohlížeč začne stahovat
                    target.onload = function() {
                        target.classList.add("visible"); // Animace až po stažení
                    };
                    // Pojistka pro cacheované obrázky (kdyby onload nebliklo)
                    if (target.complete) target.classList.add("visible");
                } 
                
                // B) Pokud je to VIDEO (YouTube)
                else if (target.classList.contains("youtube-player")) {
                    loadYoutubeThumbnail(target);
                    target.classList.add("visible");
                }

                // Už jsme ho načetli, přestáváme ho sledovat
                observer.unobserve(target);
            }
        });
    }, observerOptions);

    // 2. Spuštění sledování pro FOTKY
    var images = document.querySelectorAll('.galerie-grid img');
    images.forEach(function(img) {
        img.classList.add('lazy-scroll'); // Přidáme třídu pro efekt
        observer.observe(img);
    });

    // 3. Spuštění sledování pro VIDEA
    var videos = document.querySelectorAll('.youtube-player');
    videos.forEach(function(video) {
        video.classList.add('lazy-scroll');
        observer.observe(video);
    });

    // --- Funkce pro videa (přeneseno a upraveno z původního lazy-youtube.js) ---
    function loadYoutubeThumbnail(player) {
        var videoId = player.dataset.id;
        var img = new Image();
        img.src = "https://img.youtube.com/vi/" + videoId + "/hqdefault.jpg";
        img.style.width = "100%";
        img.style.height = "100%";
        img.style.objectFit = "cover";
        img.style.display = "block";
        
        img.onload = function() {
            player.appendChild(img);
        };

        player.addEventListener("click", function() {
            player.classList.add("playing");
            var iframe = document.createElement("iframe");
            iframe.setAttribute("src", "https://www.youtube.com/embed/" + videoId + "?autoplay=1&rel=0");
            iframe.setAttribute("frameborder", "0");
            iframe.setAttribute("allowfullscreen", "");
            iframe.style.width = "100%";
            iframe.style.height = "100%";
            iframe.style.position = "absolute";
            iframe.style.top = "0";
            iframe.style.left = "0";
            player.innerHTML = "";
            player.appendChild(iframe);
        });
    }
});