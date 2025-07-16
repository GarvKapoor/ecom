let currentIndex = 0;
const cardsPerPage = 2;

function showProductCards(start) {
	const container = document.getElementById("galleryContainer");
	const cards = container.getElementsByClassName("product-card");
	for (let i = 0; i < cards.length; i++) {
		cards[i].classList.remove("visible");
	}
	for (let i = start; i < start + cardsPerPage && i < cards.length; i++) {
		cards[i].classList.add("visible");
	}
}

function scrollGallery(direction) {
	const container = document.getElementById("galleryContainer");
	const cards = container.getElementsByClassName("product-card");
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
		document
			.getElementById("galleryContainer")
			.classList.add("animate-products");
	}, 1600);

	const lazyImages = document.querySelectorAll("img.lazy");

	if ("IntersectionObserver" in window) {
		const observer = new IntersectionObserver((entries, observer) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					const img = entry.target;
					img.src = img.dataset.src;
					img.classList.remove("lazy");
					observer.unobserve(img);
				}
			});
		});
		lazyImages.forEach((img) => observer.observe(img));
	} else {
		lazyImages.forEach((img) => {
			img.src = img.dataset.src;
			img.classList.remove("lazy");
		});
	}
});

// Image preview modal
function openImgPreview(src) {
	let modal = document.getElementById("imgPreviewModal");
	if (!modal) {
		modal = document.createElement("div");
		modal.id = "imgPreviewModal";
		modal.className = "modal";
		modal.innerHTML = `
      <div class="modal-content">
        <button class="close" onclick="closeImgPreview()">&times;</button>
        <img src="${src}" alt="Preview" />
      </div>
    `;
		document.body.appendChild(modal);
	} else {
		modal.querySelector("img").src = src;
	}
	modal.style.display = "block";

	// Close modal when clicking outside the image
	modal.addEventListener("click", (e) => {
		if (e.target === modal) {
			closeImgPreview();
		}
	});
}

function closeImgPreview() {
	const modal = document.getElementById("imgPreviewModal");
	if (modal) modal.style.display = "none";
}

// Attach click event to product images using event delegation
document.addEventListener("DOMContentLoaded", () => {
	const galleryContainer = document.getElementById("galleryContainer");

	// Use event delegation to handle clicks on any product image
	galleryContainer.addEventListener("click", (e) => {
		if (e.target.tagName === "IMG") {
			// Use src if available, otherwise fallback to data-src
			const imgSrc = e.target.src || e.target.dataset.src;
			if (imgSrc) {
				openImgPreview(imgSrc);
			}
		}
	});

	// Handle image load events for fade-in effect
	galleryContainer.addEventListener(
		"load",
		(e) => {
			if (e.target.tagName === "IMG") {
				e.target.classList.add("loaded");
			}
		},
		true
	);

	// Check for already cached images
	document.querySelectorAll(".product-card img").forEach((img) => {
		if (img.complete) {
			img.classList.add("loaded");
		}
	});
});

function scrollToProducts() {
	const productsSection = document.querySelector(".product-list");
	if (productsSection) {
		productsSection.scrollIntoView({ behavior: "smooth" });
	}
}

// Show initial product cards
document.addEventListener("DOMContentLoaded", () => {
	showProductCards(0); // Show first 2 cards on load

	// Handle size selection and price updates
	document.addEventListener("click", (e) => {
		if (e.target.classList.contains("size-btn")) {
			// Remove active class from all size buttons in the same product
			const productCard = e.target.closest(".product-card");
			const sizeBtns = productCard.querySelectorAll(".size-btn");
			sizeBtns.forEach((btn) => btn.classList.remove("active"));

			// Add active class to clicked size button
			e.target.classList.add("active");

			// Update price if size has a specific price
			const sizePrice = e.target.dataset.price;
			if (sizePrice) {
				const priceElement = productCard.querySelector(".product-price");
				priceElement.textContent = `₹${sizePrice}`;
			}
		}
	});
});
