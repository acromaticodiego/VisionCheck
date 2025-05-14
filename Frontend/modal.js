// Elementos del modal y del carrusel
const modal = document.getElementById('modal');
const closeModal = document.getElementById('closeModal');
const carouselImages = document.getElementById('carouselImages');
const prevButton = document.getElementById('prev');
const nextButton = document.getElementById('next');
let currentIndex = 0;

// Función para limpiar el contenedor del carrusel
function clearModalContent() {
    carouselImages.innerHTML = "";
}

// Función para actualizar el carrusel: muestra 3 imágenes a la vez.
function updateCarousel() {
    const imgs = carouselImages.querySelectorAll('img');
    const total = imgs.length;
    
    // Oculta todas las imágenes
    imgs.forEach((img) => {
        img.style.display = 'none';
    });
    
    // Si hay 3 o menos imágenes, mostrar todas
    if (total <= 3) {
        imgs.forEach((img) => {
            img.style.display = 'block';
        });
    } else {
        // Muestra 3 imágenes consecutivas utilizando aritmética modular para envolver al final
        for (let offset = 0; offset < 3; offset++) {
            const index = (currentIndex + offset) % total;
            imgs[index].style.display = 'block';
        }
    }
}

// Nueva función para cargar y mostrar las imágenes desde un endpoint específico
async function displayImages(endpoint) {
    try {
        const response = await fetch(`http://localhost:8000/${endpoint}`);
        const data = await response.json();
        
        // Determinamos la clave del JSON y la ruta base de las imágenes según el endpoint
        let imagesKey, baseImageUrl;
        if (endpoint === "list_detected_images1") {
            imagesKey = "detected_images1";
            baseImageUrl = "http://localhost:8000/images/esquejescortos/";
        } else if (endpoint === "list_detected_images2") {
            imagesKey = "detected_images2";
            baseImageUrl = "http://localhost:8000/images/esquejesargos/";  // Revisa si el nombre es correcto
        } else {
            imagesKey = "detected_images";
            baseImageUrl = "http://localhost:8000/images/";
        }
        
        const detectedImages = data[imagesKey];
        let htmlContent = "";
        const timestamp = new Date().getTime(); // Para evitar caché
        
        if (detectedImages && detectedImages.length > 0) {
            detectedImages.forEach(imgName => {
                // Puedes agregar .trim() si sospechas espacios extras:
                const trimmedName = imgName.trim();
                htmlContent += `<img src="${baseImageUrl}${trimmedName}?t=${timestamp}" alt="${trimmedName}" style="width: 100%; display: none;">`;
            });
        } else {
            htmlContent = "<p>No hay imágenes detectadas</p>";
        }
        
        carouselImages.innerHTML = htmlContent;
        currentIndex = 0;
        updateCarousel();
    } catch (error) {
        console.error('Error al obtener imágenes:', error);
    }
}

// Configuración de los botones del carrusel
prevButton.addEventListener('click', () => {
    if (carouselImages.children.length === 0) return;
    currentIndex = currentIndex > 0 ? currentIndex - 1 : carouselImages.children.length - 1;
    updateCarousel();
});

nextButton.addEventListener('click', () => {
    if (carouselImages.children.length === 0) return;
    currentIndex = currentIndex < carouselImages.children.length - 1 ? currentIndex + 1 : 0;
    updateCarousel();
});

// Event listener para abrir el modal según el contenedor clickeado
document.addEventListener("DOMContentLoaded", function() {
    // Seleccionamos todos los elementos con la clase openModal
    const openModalElements = document.querySelectorAll(".openModal");
    openModalElements.forEach((element) => {
        element.addEventListener("click", () => {
            modal.style.display = 'block';
            clearModalContent();
            // Obtenemos el endpoint desde el atributo data-endpoint
            const endpoint = element.getAttribute("data-endpoint");
            displayImages(endpoint);
        });
    });
    
    // Cerrar modal con el botón de cerrar
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Cerrar modal si se hace clic fuera de este
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});



