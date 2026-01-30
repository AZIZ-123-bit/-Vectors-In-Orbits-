// DOM Elements
const queryInput = document.getElementById('queryInput');
const searchBtn = document.getElementById('searchBtn');
const resultsContainer = document.getElementById('resultsContainer');
const resultsStats = document.getElementById('resultsStats');
const resultsHeader = document.getElementById('resultsHeader');
const loadingIndicator = document.getElementById('loadingIndicator');
const yearFilter = document.getElementById('yearFilter');
const contentTypeFilter = document.getElementById('contentTypeFilter');
const resultsCount = document.getElementById('resultsCount');
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
const navbar = document.getElementById('navbar');

// Upload elements
const imageUploadBtn = document.getElementById('imageUploadBtn');
const sequenceUploadBtn = document.getElementById('sequenceUploadBtn');
const imageInput = document.getElementById('imageInput');
const sequenceInput = document.getElementById('sequenceInput');
const uploadPreview = document.getElementById('uploadPreview');
const previewName = document.getElementById('previewName');
const previewType = document.getElementById('previewType');
const previewImage = document.getElementById('previewImage');
const removeUpload = document.getElementById('removeUpload');

// Upload state
let uploadedFile = null;
let uploadType = null;
let uploadedImageData = null;

// Backend API endpoint - CORRIGÉ ICI
const API_BASE = 'http://localhost:8000/api';
const API_ENDPOINT = `${API_BASE}/search`;

// Mobile Menu Toggle
hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('active');
});

// Close mobile menu when clicking a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    });
});

// Image upload handling
imageUploadBtn.addEventListener('click', () => {
    imageInput.click();
});

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        uploadedFile = file;
        uploadType = 'image';
        
        const reader = new FileReader();
        reader.onload = (event) => {
            uploadedImageData = event.target.result;
            
            previewName.textContent = file.name;
            previewType.textContent = 'Image';
            previewImage.innerHTML = `<img src="${event.target.result}" alt="Uploaded image" style="max-width: 100%; border-radius: 8px;">`;
            uploadPreview.style.display = 'flex';
            
            imageUploadBtn.classList.add('active');
            sequenceUploadBtn.classList.remove('active');
        };
        reader.readAsDataURL(file);
    }
});

// Sequence upload handling
sequenceUploadBtn.addEventListener('click', () => {
    sequenceInput.click();
});

sequenceInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        uploadedFile = file;
        uploadType = 'sequence';
        
        const reader = new FileReader();
        reader.onload = (event) => {
            const sequenceText = event.target.result;
            
            previewName.textContent = file.name;
            previewType.textContent = 'Sequence';
            previewImage.innerHTML = `<pre style="max-height: 150px; overflow-y: auto; background: #1a1a2e; padding: 10px; border-radius: 8px; color: #00ff88;">${sequenceText.substring(0, 500)}${sequenceText.length > 500 ? '...' : ''}</pre>`;
            uploadPreview.style.display = 'flex';
            
            sequenceUploadBtn.classList.add('active');
            imageUploadBtn.classList.remove('active');
        };
        reader.readAsText(file);
    }
});

// Remove upload
removeUpload.addEventListener('click', () => {
    clearUpload();
});

function clearUpload() {
    uploadedFile = null;
    uploadedImageData = null;
    uploadType = null;
    imageInput.value = '';
    sequenceInput.value = '';
    uploadPreview.style.display = 'none';
    previewImage.innerHTML = '';
    
    imageUploadBtn.classList.remove('active');
    sequenceUploadBtn.classList.remove('active');
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Scroll reveal animation
const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -80px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('revealed');
            }, index * 100);
        }
    });
}, observerOptions);

// Observe all scroll reveal elements
document.addEventListener('DOMContentLoaded', () => {
    const revealElements = document.querySelectorAll(
        '.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right, .scroll-reveal-scale, .search-section, .feature-card-3d, .tech-showcase'
    );
    
    revealElements.forEach(el => {
        observer.observe(el);
    });
    
    // Check API health
    checkAPIHealth();
});

// 3D Tilt Effect for Feature Cards
document.querySelectorAll('[data-tilt]').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
});

// Search Event Listeners
searchBtn.addEventListener('click', performSearch);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        performSearch();
    }
});

// Check API health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('✅ API Status:', data.message);
    } catch (error) {
        console.error('❌ API Connection Error:', error);
        showNotification('Unable to connect to backend. Please ensure the server is running.', 'error');
    }
}

// Perform Search
async function performSearch() {
    const query = queryInput.value.trim();
    const year = yearFilter.value;
    const contentType = contentTypeFilter ? contentTypeFilter.value : null;
    
    if (!query && !uploadedImageData) {
        showNotification('Please enter a search query or upload an image', 'warning');
        return;
    }
    
    // Show loading
    loadingIndicator.style.display = 'flex';
    resultsContainer.innerHTML = '';
    
    try {
        const requestData = {
            query: query,
            top_k: 10,
            year: year ? parseInt(year) : null,
            content_type: contentType
        };
        
        // Add image data if available
        if (uploadedImageData) {
            requestData.image = uploadedImageData;
        }
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';
        
        if (data.success) {
            displayResults(data.results);
            showNotification(`Found ${data.count} results`, 'success');
        } else {
            throw new Error(data.error || 'Search failed');
        }
        
    } catch (error) {
        loadingIndicator.style.display = 'none';
        console.error('Search error:', error);
        showNotification(`Search failed: ${error.message}`, 'error');
        
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <h4>Search Error</h4>
                <p>${error.message}</p>
                <p style="font-size: 0.9em; color: #666;">Make sure the backend server is running on http://localhost:8000</p>
            </div>
        `;
    }
}

// Format similarity score
function formatSimilarity(score) {
    return Math.round(score * 100) + '%';
}

// Get content type icon
function getContentTypeIcon(type) {
    const icons = {
        'text': '📄',
        'image': '🖼️',
        'sequence': '🧬',
        'experiment': '🔬'
    };
    return icons[type] || '📋';
}

// Get content type color
function getContentTypeColor(type) {
    const colors = {
        'text': '#4a9eff',
        'image': '#ff6b9d',
        'sequence': '#00ff88',
        'experiment': '#ffd93d'
    };
    return colors[type] || '#888';
}

// Create result card HTML
function createResultCard(result, index) {
    const typeIcon = getContentTypeIcon(result.type);
    const typeColor = getContentTypeColor(result.type);
    
    return `
        <div class="result-card-3d" style="animation-delay: ${index * 0.1}s; border-left: 4px solid ${typeColor}">
            <div class="result-header-3d">
                <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                    <span style="font-size: 1.5em;">${typeIcon}</span>
                    <h3 class="result-title-3d">${index + 1}. ${result.metadata.title || 'Research Result'}</h3>
                </div>
                <div class="similarity-badge" style="background: ${typeColor}">
                    ${formatSimilarity(result.score)}
                </div>
            </div>
            
            <div class="result-meta-3d">
                <span style="background: ${typeColor}20; color: ${typeColor}; padding: 4px 12px; border-radius: 20px; font-weight: 600;">
                    ${result.type.toUpperCase()}
                </span>
                ${result.metadata.year ? `<span><i class="far fa-calendar"></i> ${result.metadata.year}</span>` : ''}
                ${result.metadata.organism ? `<span><i class="fas fa-dna"></i> ${result.metadata.organism}</span>` : ''}
                ${result.metadata.authors ? `<span><i class="fas fa-users"></i> ${Array.isArray(result.metadata.authors) ? result.metadata.authors.join(', ') : result.metadata.authors}</span>` : ''}
                ${result.metadata.journal ? `<span><i class="far fa-newspaper"></i> ${result.metadata.journal}</span>` : ''}
            </div>
            
            <p class="result-abstract-3d">${result.content}</p>
            
            ${result.metadata.keywords ? `
                <div style="margin-top: 12px;">
                    <strong>Keywords:</strong>
                    ${result.metadata.keywords.map(kw => `<span style="background: #1a1a2e; padding: 4px 10px; border-radius: 12px; margin-right: 6px; display: inline-block; margin-top: 4px; font-size: 0.85em;">${kw}</span>`).join('')}
                </div>
            ` : ''}
            
            <div class="result-actions-3d" style="margin-top: 16px;">
                <button class="result-btn" onclick="copyContent('${result.content.replace(/'/g, "\\'")}')">
                    <i class="far fa-copy"></i> Copy
                </button>
                ${result.metadata.doi ? `
                    <button class="result-btn" onclick="window.open('https://doi.org/${result.metadata.doi}', '_blank')">
                        <i class="fas fa-external-link-alt"></i> View DOI
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

// Display results with animation
function displayResults(results) {
    resultsHeader.style.display = 'flex';
    
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h4>No results found</h4>
                <p>Try a different search term or adjust your filters</p>
            </div>
        `;
        resultsStats.textContent = '0 results';
        return;
    }
    
    resultsContainer.innerHTML = results.map((result, index) => 
        createResultCard(result, index)
    ).join('');
    
    resultsStats.textContent = `${results.length} results`;
    
    // Trigger animation
    setTimeout(() => {
        document.querySelectorAll('.result-card-3d').forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }, 100);
}

// Copy content to clipboard
function copyContent(content) {
    navigator.clipboard.writeText(content).then(() => {
        showNotification('Content copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy content', 'error');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#00ff88' : type === 'error' ? '#ff6b9d' : '#4a9eff'};
        color: #0a0a1a;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        font-weight: 600;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .result-card-3d {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
`;
document.head.appendChild(style);

console.log('🧬 BioSemantica Frontend Loaded');
console.log('API Endpoint:', API_ENDPOINT);c