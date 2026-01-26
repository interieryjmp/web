document.addEventListener("DOMContentLoaded", function() {
    
    var mapElement = document.getElementById('mapa');

    if (mapElement) {
        // Souřadnice: Mladoboleslavská 330, Vinoř
        var center = [50.150608, 14.590003];
        var apiKey = 'z9faPG0rWqrloxpsVD8Ii5_RyTi77QTiYpDl3L0n1a4'; // Váš API klíč

        // Definice vrstev
        var zakladni = L.tileLayer(`https://api.mapy.com/v1/maptiles/basic/256/{z}/{x}/{y}?apikey=${apiKey}`, {
            minZoom: 0, maxZoom: 19, attribution: '<a href="https://api.mapy.com/copyright" target="_blank">&copy; Seznam.cz a.s. a další</a>'
        });
        var letecka = L.tileLayer(`https://api.mapy.com/v1/maptiles/aerial/256/{z}/{x}/{y}?apikey=${apiKey}`, {
            minZoom: 0, maxZoom: 19, attribution: '<a href="https://api.mapy.com/copyright" target="_blank">&copy; Seznam.cz a.s. a další</a>'
        });
        var turisticka = L.tileLayer(`https://api.mapy.com/v1/maptiles/outdoor/256/{z}/{x}/{y}?apikey=${apiKey}`, {
            minZoom: 0, maxZoom: 19, attribution: '<a href="https://api.mapy.com/copyright" target="_blank">&copy; Seznam.cz a.s. a další</a>'
        });

        // Inicializace mapy
        var map = L.map('mapa', {
            center: center,
            zoom: 15,
            layers: [zakladni],
            scrollWheelZoom: false
        });

        // Přepínač vrstev
        var baseMaps = { "Základní": zakladni, "Letecká": letecka, "Turistická": turisticka };
        L.control.layers(baseMaps).addTo(map);

        // Logo Mapy.cz
        var logoControl = L.control({position: 'bottomleft'});
        logoControl.onAdd = function(map) {
            var div = L.DomUtil.create('div', 'mapy-logo');
            div.innerHTML = '<a href="https://mapy.com/" target="_blank"><img src="https://api.mapy.com/img/api/logo.svg" alt="Mapy.cz" style="height: 30px;"></a>';
            return div;
        };
        logoControl.addTo(map);

        // Špendlík s bublinou
        var popupContent = `
            <div style="text-align:center;">
                <b style="font-size:1.1em; color: #1976d2;">Interiery JMP</b><br>
                Mladoboleslavská 330<br>
                190 17  Praha 9 – Vinoř<br><br>
                <a href="https://mapy.com/cs/zakladni?planovani-trasy&rc=9h10lxYPQj&rs=&rs=firm&ri=&ri=13869785&mrp=%7B%22c%22%3A111%2C%22dt%22%3A%22%22%2C%22d%22%3Atrue%7D&xc=%5B%5D&rut=1&x=14.5899058&y=50.1507289&z=17" target="_blank" 
                   style="color: white; background: #1976d2; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-size: 0.9em;">
                   Naplánovat trasu ➜
                </a>
            </div>
        `;

        L.marker(center).addTo(map)
            .bindPopup(popupContent)
            .openPopup();
            
        // Povolení zoomování kolečkem až po kliknutí (UX)
        map.on('focus', function() { map.scrollWheelZoom.enable(); });
    }
});