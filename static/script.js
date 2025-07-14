let currentIndex = 0;
const cardsPerPage = 2;

function showProductCards(start) {
  const container = document.getElementById('galleryContainer');
  const cards = container.getElementsByClassName('product-card');
  for (let i = 0; i < cards.length; i++) {
    cards[i].classList.remove('visible');
  }
  for (let i = start; i < start + cardsPerPage && i < cards.length; i++) {
    cards[i].classList.add('visible');
  }
}

function scrollGallery(direction) {
  const container = document.getElementById('galleryContainer');
  const cards = container.getElementsByClassName('product-card');
  const maxIndex = cards.length - cardsPerPage;
  currentIndex += direction * cardsPerPage;
  if (currentIndex < 0) currentIndex = 0;
  if (currentIndex > maxIndex) currentIndex = maxIndex;
  showProductCards(currentIndex);
}

// Lazy load images on scroll using IntersectionObserver
document.addEventListener("DOMContentLoaded", () => {
  // Wait for hero animation to finish (0.8s + 0.8s = 1.6s for all hero elements)
  setTimeout(() => {
    document.getElementById('galleryContainer').classList.add('animate-products');
  }, 1600);

  const lazyImages = document.querySelectorAll('img.lazy');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          observer.unobserve(img);
        }
      });
    });
    lazyImages.forEach(img => observer.observe(img));
  } else {
    lazyImages.forEach(img => {
      img.src = img.dataset.src;
      img.classList.remove('lazy');
    });
  }
});

// Image preview modal
function openImgPreview(src) {
  let modal = document.getElementById('imgPreviewModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'imgPreviewModal';
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <button class="close" onclick="closeImgPreview()">&times;</button>
        <img src="${src}" alt="Preview" />
      </div>
    `;
    document.body.appendChild(modal);
  } else {
    modal.querySelector('img').src = src;
    modal.style.display = 'block';
  }
  modal.style.display = 'block';
}

function closeImgPreview() {
  const modal = document.getElementById('imgPreviewModal');
  if (modal) modal.style.display = 'none';
}

// Attach click event to product images
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.product-card img').forEach(img => {
    img.addEventListener('click', () => openImgPreview(img.src));
    img.addEventListener('load', () => {
      img.classList.add('loaded');
    });
    // If already cached
    if (img.complete) {
      img.classList.add('loaded');
    }
  });
});

function scrollToProducts() {
  const productsSection = document.querySelector('.product-list');
  if (productsSection) {
    productsSection.scrollIntoView({ behavior: 'smooth' });
  }
}

// Show initial product cards
document.addEventListener("DOMContentLoaded", () => {
  showProductCards(0); // Show first 2 cards on load
});
