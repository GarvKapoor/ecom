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

	// Auto-select first size button for single-size products
	document.querySelectorAll(".product-card").forEach((card) => {
		const sizeBtns = card.querySelectorAll(".size-btn");
		if (sizeBtns.length === 1) {
			sizeBtns[0].classList.add("active");
		} else if (sizeBtns.length > 1) {
			// For multi-size products, select the first size and update price
			sizeBtns[0].classList.add("active");
			const firstSizePrice = sizeBtns[0].dataset.price;
			if (firstSizePrice) {
				const priceElement = card.querySelector(".product-price");
				priceElement.textContent = `₹${firstSizePrice}`;
			}
		}
	});

	// Load cart count on page load
	updateCartCount();
});

// Add to Cart functionality
function addToCart(button) {
	const productCard = button.closest(".product-card");
	const productName = productCard.dataset.productName;
	const basePrice = productCard.dataset.basePrice;

	// Get selected size
	const selectedSizeBtn = productCard.querySelector(".size-btn.active");
	if (!selectedSizeBtn) {
		alert("Please select a size first!");
		return;
	}

	const selectedSize = selectedSizeBtn.dataset.size;
	const selectedPrice = selectedSizeBtn.dataset.price;
	const imageUrl =
		productCard.querySelector("img").dataset.src ||
		productCard.querySelector("img").src;

	// Create cart item
	const cartItem = {
		name: productName,
		size: selectedSize,
		price: selectedPrice,
		image_url: imageUrl,
		quantity: 1,
	};

	// Add to cart via API
	fetch("/cart/add", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(cartItem),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				// Show feedback
				button.textContent = "Added!";
				button.style.backgroundColor = "#4CAF50";

				setTimeout(() => {
					button.textContent = "Add to Cart";
					button.style.backgroundColor = "";
				}, 1500);

				// Update cart count
				updateCartCount();
			} else {
				alert("Error adding item to cart: " + data.error);
			}
		})
		.catch((error) => {
			console.error("Error:", error);
			alert("Error adding item to cart");
		});
}

// Update cart count in header
function updateCartCount() {
	fetch("/cart/get")
		.then((response) => response.json())
		.then((data) => {
			const cartCountElement = document.getElementById("cart-count");
			if (cartCountElement) {
				cartCountElement.textContent = data.total_items;
			}
		})
		.catch((error) => {
			console.error("Error updating cart count:", error);
		});
}

// Cart Modal Functions
function openCartModal() {
	const modal = document.getElementById("cartModal");
	modal.style.display = "block";
	loadCartItems();
}

function closeCartModal() {
	const modal = document.getElementById("cartModal");
	modal.style.display = "none";
}

function loadCartItems() {
	fetch("/cart/get")
		.then((response) => response.json())
		.then((data) => {
			renderCartItems(data.cart);
			updateCartSummary(data);
		})
		.catch((error) => {
			console.error("Error loading cart:", error);
		});
}

function renderCartItems(cartItems) {
	const container = document.getElementById("cart-items-container");

	if (cartItems.length === 0) {
		container.innerHTML = `
			<div class="empty-cart">
				<div class="empty-cart-icon">🛒</div>
				<h3>Your cart is empty</h3>
				<p>Add some items to get started!</p>
			</div>
		`;
		return;
	}

	container.innerHTML = cartItems
		.map(
			(item) => `
		<div class="cart-item">
			<input type="checkbox" class="cart-item-checkbox"
				   ${item.selected ? "checked" : ""}
				   onchange="toggleItemSelection('${item.id}', this.checked)">
			<img src="${item.image_url}" alt="${item.name}" class="cart-item-image">
			<div class="cart-item-details">
				<div class="cart-item-name">${item.name}</div>
				<div class="cart-item-info">Size: ${item.size}</div>
				<div class="cart-item-price">₹${item.price}</div>
			</div>
			<div class="cart-item-controls">
				<button class="quantity-btn" onclick="updateQuantity('${item.id}', ${
				item.quantity - 1
			})">-</button>
				<input type="number" class="quantity-input" value="${item.quantity}" min="1"
					   onchange="updateQuantity('${item.id}', this.value)">
				<button class="quantity-btn" onclick="updateQuantity('${item.id}', ${
				item.quantity + 1
			})">+</button>
				<button class="remove-btn" onclick="removeFromCart('${
					item.id
				}')" title="Remove item">×</button>
			</div>
		</div>
	`
		)
		.join("");
}

function updateCartSummary(data) {
	document.getElementById("selected-count").textContent = data.selected_items;
	document.getElementById("total-amount").textContent = `₹${data.total_amount}`;

	const checkoutBtn = document.getElementById("checkout-btn");
	checkoutBtn.disabled = data.selected_items === 0;
}

function toggleItemSelection(itemId, selected) {
	fetch("/cart/update", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			id: itemId,
			selected: selected,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				loadCartItems(); // Refresh cart
			}
		})
		.catch((error) => {
			console.error("Error updating item:", error);
		});
}

function updateQuantity(itemId, newQuantity) {
	newQuantity = parseInt(newQuantity);
	if (newQuantity < 1) return;

	fetch("/cart/update", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			id: itemId,
			quantity: newQuantity,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				loadCartItems(); // Refresh cart
				updateCartCount(); // Update header count
			}
		})
		.catch((error) => {
			console.error("Error updating quantity:", error);
		});
}

function removeFromCart(itemId) {
	if (!confirm("Are you sure you want to remove this item?")) return;

	fetch("/cart/remove", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			id: itemId,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				loadCartItems(); // Refresh cart
				updateCartCount(); // Update header count
			}
		})
		.catch((error) => {
			console.error("Error removing item:", error);
		});
}

function clearCart() {
	if (!confirm("Are you sure you want to clear the entire cart?")) return;

	fetch("/cart/clear", {
		method: "POST",
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				loadCartItems(); // Refresh cart
				updateCartCount(); // Update header count
			}
		})
		.catch((error) => {
			console.error("Error clearing cart:", error);
		});
}

function proceedToCheckout() {
	fetch("/cart/checkout", {
		method: "POST",
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				alert(
					`Order created successfully! Order ID: ${data.order_id}\\nTotal: ₹${data.total_amount}\\n\\n${data.message}`
				);
				// In a real app, you would redirect to the payment gateway
				// window.location.href = data.redirect_url;
			} else {
				alert("Error processing checkout: " + data.error);
			}
		})
		.catch((error) => {
			console.error("Error during checkout:", error);
			alert("Error during checkout");
		});
}

// Modal functionality placeholder
function openModal() {
	alert("Login functionality not implemented yet!");
}

// Close modal when clicking outside
window.onclick = function (event) {
	const cartModal = document.getElementById("cartModal");
	if (event.target === cartModal) {
		closeCartModal();
	}
};
