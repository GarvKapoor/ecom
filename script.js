function openModal() {
  document.getElementById("modal").style.display = "block";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

// Close modal when clicking outside of it
window.onclick = function(event) {
  const modal = document.getElementById("modal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

let a = 0;

document.querySelectorAll(".addcart").forEach(function(button) {
  button.addEventListener("click", function() {
    console.log("Item added to cart");
    a++;
    document.getElementById("cart").innerText = "🛒 Cart (" + a + ")";
  });
});

function openImgPreview(src) {
  document.getElementById("previewImg").src = src;
  document.getElementById("imgPreviewModal").style.display = "block";
}

function closeImgPreview() {
  document.getElementById("imgPreviewModal").style.display = "none";
}

// Close image modal when clicking outside the image
window.addEventListener("click", function(event) {
  const modal = document.getElementById("imgPreviewModal");
  if (event.target === modal) {
    modal.style.display = "none";
  }
});

// Add click event to all product images
document.querySelectorAll(".product-card img").forEach(function(img) {
  img.style.cursor = "pointer";
  img.addEventListener("click", function() {
    openImgPreview(img.src);
  });
});