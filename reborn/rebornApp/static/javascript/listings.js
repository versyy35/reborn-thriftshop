document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const listingsContainer = document.getElementById('listingsContainer');
    const emptyState = document.getElementById('emptyState');
    const listingModal = document.getElementById('listingModal');
    const deleteModal = document.getElementById('deleteModal');
    const listingForm = document.getElementById('listingForm');
    const modalTitle = document.getElementById('modalTitle');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    
    // Buttons
    const addListingBtn = document.getElementById('addListingBtn');
    const emptyStateAddBtn = document.getElementById('emptyStateAddBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const uploadButton = document.getElementById('uploadButton');
    const imageInput = document.getElementById('imageInput');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    // Form fields
    const listingIdInput = document.getElementById('listingId');
    const titleInput = document.getElementById('title');
    const priceInput = document.getElementById('price');
    const descriptionInput = document.getElementById('description');
    const imagePreview = document.getElementById('imagePreview');
    const uploadIcon = document.getElementById('uploadIcon');
    const imageDataInput = document.getElementById('imageData');
    const deleteListingIdInput = document.getElementById('deleteListingId');
    
    // Initialize listings from localStorage or use sample data
    let listings = JSON.parse(localStorage.getItem('listings')) || [];
    if (listings.length === 0) {
        listings = sampleListings;
        saveListings();
    }
    
    // Save listings to localStorage
    function saveListings() {
        localStorage.setItem('listings', JSON.stringify(listings));
    }
    
    // Create SVG image placeholder
    function createSVGImage(color, type) {
        let icon = '';
        
        if (type === 'home') {
            icon = '<path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />';
        } else if (type === 'car') {
            icon = '<path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" /><path d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />';
        } else if (type === 'camera') {
            icon = '<path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />';
        } else {
            icon = '<path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />';
        }
        
        return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="${encodeURIComponent(color)}" stroke-width="1.5">${icon}</svg>`;
    }
    
    // Render listings
    function renderListings(listingsToRender = listings) {
        listingsContainer.innerHTML = '';
        
        if (listingsToRender.length === 0) {
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
            
            listingsToRender.forEach(listing => {
                const listingCard = document.createElement('div');
                listingCard.className = 'listing-card bg-white rounded-lg shadow overflow-hidden';
                
                const imageStyle = listing.image ? 
                    `background-image: url('${listing.image}')` : 
                    'background-color: #e5e7eb';
                
                listingCard.innerHTML = `
                    <div class="h-64 image-preview" style="${imageStyle}"></div>
                    <div class="p-4">
                        <div class="flex justify-between items-start">
                            <h3 class="text-lg font-semibold text-gray-900 mb-1">${listing.title}</h3>
                            <span class="text-lg font-bold text-indigo-600">RM ${parseFloat(listing.price).toFixed(2)}</span>
                        </div>
                        <p class="text-gray-600 text-sm mb-4 line-clamp-2">${listing.description || 'No description provided'}</p>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-gray-500">${new Date(listing.createdAt).toLocaleDateString()}</span>
                            <div class="flex space-x-2">
                                <button class="edit-btn p-2 text-blue-600 hover:text-blue-800" data-id="${listing.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                    </svg>
                                </button>
                                <button class="delete-btn p-2 text-red-600 hover:text-red-800" data-id="${listing.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                listingsContainer.appendChild(listingCard);
            });
            
            // Add event listeners to edit and delete buttons
            document.querySelectorAll('.edit-btn').forEach(btn => {
                btn.addEventListener('click', () => editListing(btn.dataset.id));
            });
            
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', () => showDeleteModal(btn.dataset.id));
            });
        }
    }
    
    // Filter and sort listings
    function filterAndSortListings() {
        const searchTerm = searchInput.value.toLowerCase();
        const sortBy = sortSelect.value;
        
        let filteredListings = listings.filter(listing => 
            listing.title.toLowerCase().includes(searchTerm) || 
            (listing.description && listing.description.toLowerCase().includes(searchTerm))
        );
        
        switch(sortBy) {
            case 'newest':
                filteredListings.sort((a, b) => b.createdAt - a.createdAt);
                break;
            case 'oldest':
                filteredListings.sort((a, b) => a.createdAt - b.createdAt);
                break;
            case 'title':
                filteredListings.sort((a, b) => a.title.localeCompare(b.title));
                break;
            case 'price-high':
                filteredListings.sort((a, b) => b.price - a.price);
                break;
            case 'price-low':
                filteredListings.sort((a, b) => a.price - b.price);
                break;
        }
        
        renderListings(filteredListings);
    }
    
    // Show add listing modal
    function showAddModal() {
        modalTitle.textContent = 'Add New Listing';
        listingForm.reset();
        listingIdInput.value = '';
        imagePreview.style.backgroundImage = '';
        uploadIcon.classList.remove('hidden');
        removeImageBtn.classList.add('hidden');
        imageDataInput.value = '';
        listingModal.classList.remove('hidden');
    }
    
    // Show edit listing modal
    function editListing(id) {
        const listing = listings.find(item => item.id === id);
        if (!listing) return;
        
        modalTitle.textContent = 'Edit Listing';
        listingIdInput.value = listing.id;
        titleInput.value = listing.title;
        priceInput.value = listing.price;
        descriptionInput.value = listing.description || '';
        
        if (listing.image) {
            imagePreview.style.backgroundImage = `url('${listing.image}')`;
            uploadIcon.classList.add('hidden');
            removeImageBtn.classList.remove('hidden');
            imageDataInput.value = listing.image;
        } else {
            imagePreview.style.backgroundImage = '';
            uploadIcon.classList.remove('hidden');
            removeImageBtn.classList.add('hidden');
            imageDataInput.value = '';
        }
        
        listingModal.classList.remove('hidden');
    }
    
    // Show delete confirmation modal
    function showDeleteModal(id) {
        deleteListingIdInput.value = id;
        deleteModal.classList.remove('hidden');
    }
    
    // Save listing (add or update)
    function saveListing(e) {
        e.preventDefault();
        
        const id = listingIdInput.value || Date.now().toString();
        const title = titleInput.value;
        const price = parseFloat(priceInput.value);
        const description = descriptionInput.value;
        const image = imageDataInput.value;
        const createdAt = listingIdInput.value ? 
            listings.find(item => item.id === id).createdAt : 
            Date.now();
        
        const listingData = {
            id,
            title,
            price,
            description,
            image,
            createdAt
        };
        
        if (listingIdInput.value) {
            // Update existing listing
            const index = listings.findIndex(item => item.id === id);
            if (index !== -1) {
                listings[index] = listingData;
            }
        } else {
            // Add new listing
            listings.push(listingData);
        }
        
        saveListings();
        filterAndSortListings();
        listingModal.classList.add('hidden');
    }
    
    // Delete listing
    function deleteListing() {
        const id = deleteListingIdInput.value;
        listings = listings.filter(item => item.id !== id);
        saveListings();
        filterAndSortListings();
        deleteModal.classList.add('hidden');
    }
    
    // Handle image upload
    function handleImageUpload() {
        imageInput.click();
    }
    
    // Process selected image
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const imageData = e.target.result;
            imagePreview.style.backgroundImage = `url('${imageData}')`;
            uploadIcon.classList.add('hidden');
            removeImageBtn.classList.remove('hidden');
            imageDataInput.value = imageData;
        };
        reader.readAsDataURL(file);
    });
    
    // Remove image
    function removeImage() {
        imagePreview.style.backgroundImage = '';
        uploadIcon.classList.remove('hidden');
        removeImageBtn.classList.add('hidden');
        imageDataInput.value = '';
        imageInput.value = '';
    }
    
    // Event Listeners
    addListingBtn.addEventListener('click', showAddModal);
    emptyStateAddBtn.addEventListener('click', showAddModal);
    closeModalBtn.addEventListener('click', () => listingModal.classList.add('hidden'));
    cancelBtn.addEventListener('click', () => listingModal.classList.add('hidden'));
    listingForm.addEventListener('submit', saveListing);
    uploadButton.addEventListener('click', handleImageUpload);
    removeImageBtn.addEventListener('click', removeImage);
    cancelDeleteBtn.addEventListener('click', () => deleteModal.classList.add('hidden'));
    confirmDeleteBtn.addEventListener('click', deleteListing);
    searchInput.addEventListener('input', filterAndSortListings);
    sortSelect.addEventListener('change', filterAndSortListings);
    
    // Initial render
    renderListings();
});