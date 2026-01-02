/* 
   WeTech Django Script
   Updated for Multi-Page Application
*/

document.addEventListener("DOMContentLoaded", function() {
   
   // 1. Handle Loading Screen
   const loader = document.getElementById('loadingScreen');
   if (loader) {
       setTimeout(() => {
           loader.classList.add('hidden');
       }, 500); // Reduced time for snappier feel
   }

   // 2. Animate Stats (Only if we are on a page with stats)
   const metricValues = document.querySelectorAll('.metric-value[data-target]');
   if (metricValues.length > 0) {
       animateStats(metricValues);
   }

   // 3. Initialize Filters (Only if on Portfolio page)
   const filterBtns = document.querySelectorAll('.filter-btn');
   if (filterBtns.length > 0) {
       // Set "All" as active by default if none selected
       if (!document.querySelector('.filter-btn.active')) {
           filterBtns[0].classList.add('active');
       }
   }
});


// --- Helper Functions ---

// Animate Stats
function animateStats(elements) {
   elements.forEach((el, index) => {
      setTimeout(() => {
         const target = parseInt(el.dataset.target);
         let current = 0;
         const increment = Math.ceil(target / 40);
         const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
               current = target;
               clearInterval(timer);
            }
            el.textContent = current;
         }, 30);
      }, index * 200);
   });
}

// Tab Switching (Services Page)
// Called directly by onclick in HTML
function switchTab(btn, tabId) {
   // Remove active from all buttons
   document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
   // Add active to clicked button
   btn.classList.add('active');

   // Hide all panes
   document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
   // Show target pane
   const targetPane = document.getElementById(tabId);
   if (targetPane) {
       targetPane.classList.add('active');
   }
}

// Gallery Filter (Portfolio Page)
// Called directly by onclick in HTML
function filterGallery(category, btn) {
   // Update buttons
   document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
   btn.classList.add('active');

   // Filter items
   const items = document.querySelectorAll('.gallery-item');
   items.forEach(item => {
      if (category === 'all' || item.dataset.category === category) {
         item.style.display = 'block';
         // Trigger animation
         item.style.animation = 'none';
         item.offsetHeight; /* trigger reflow */
         item.style.animation = 'tabFade 0.4s ease-out';
      } else {
         item.style.display = 'none';
      }
   });
}


// ============================================
// SKELETON LOADING UTILITIES (#3)
// ============================================

// Show skeleton loader
function showSkeleton(containerId, skeletonType = 'card') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const skeletonHTML = generateSkeletonHTML(skeletonType);
    container.innerHTML = skeletonHTML;
}

// Generate skeleton HTML based on type
function generateSkeletonHTML(type) {
    const skeletons = {
        'card': '<div class="skeleton-card"><div class="skeleton-title"></div><div class="skeleton-text"></div><div class="skeleton-text" style="width: 80%;"></div></div>',
        'table': '<div class="skeleton-table-row"><div class="skeleton-table-cell avatar skeleton"></div><div class="skeleton-table-cell skeleton"></div><div class="skeleton-table-cell skeleton"></div><div class="skeleton-table-cell skeleton"></div><div class="skeleton-table-cell skeleton"></div></div>'.repeat(5),
        'stats': '<div class="skeleton-stat-card"><div class="skeleton-stat-icon skeleton"></div><div class="skeleton-stat-content"><div class="skeleton-title skeleton"></div><div class="skeleton-text skeleton"></div></div></div>',
        'list': '<div class="skeleton-list-item"><div class="skeleton-avatar skeleton"></div><div style="flex: 1;"><div class="skeleton-text skeleton"></div><div class="skeleton-text skeleton" style="width: 60%;"></div></div></div>'.repeat(3)
    };
    return skeletons[type] || skeletons['card'];
}

// Hide skeleton and show content
function hideSkeleton(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        const skeletons = container.querySelectorAll('.skeleton');
        skeletons.forEach(s => s.classList.add('skeleton-hidden'));
    }
}

// ============================================
// ENHANCED DATA TABLE UTILITIES (#5)
// ============================================

// Initialize Enhanced Table
function initEnhancedTable(tableId, options = {}) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const config = {
        searchable: options.searchable !== false,
        sortable: options.sortable !== false,
        pagination: options.pagination !== false,
        pageSize: options.pageSize || 10,
        ...options
    };
    
    if (config.searchable) addTableSearch(table, config);
    if (config.sortable) addTableSorting(table);
    if (config.pagination) addTablePagination(table, config.pageSize);
}

// Add Search Functionality
function addTableSearch(table, config) {
    const wrapper = table.closest('.data-table-wrapper') || table.parentElement;
    const searchHTML = `
        <div class="data-table-controls">
            <div class="table-search-box">
                <i class="bi bi-search"></i>
                <input type="text" placeholder="Search..." id="${table.id}_search">
            </div>
        </div>
    `;
    wrapper.insertAdjacentHTML('beforebegin', searchHTML);
    
    const searchInput = document.getElementById(`${table.id}_search`);
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Add Column Sorting
function addTableSorting(table) {
    const headers = table.querySelectorAll('thead th');
    headers.forEach((header, index) => {
        if (header.textContent.trim()) {
            header.classList.add('sortable-header');
            header.addEventListener('click', () => {
                sortTable(table, index, header);
            });
        }
    });
}

function sortTable(table, columnIndex, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = header.classList.contains('sort-asc');
    
    // Reset all headers
    table.querySelectorAll('thead th').forEach(h => {
        h.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Toggle sort direction
    header.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex]?.textContent.trim() || '';
        const bText = b.cells[columnIndex]?.textContent.trim() || '';
        
        // Try numeric comparison first
        const aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAsc ? bNum - aNum : aNum - bNum;
        }
        
        // String comparison
        return isAsc ? bText.localeCompare(aText) : aText.localeCompare(bText);
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Add Pagination
function addTablePagination(table, pageSize) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const totalPages = Math.ceil(rows.length / pageSize);
    
    if (totalPages <= 1) return;
    
    const wrapper = table.closest('.data-table-wrapper') || table.parentElement;
    let currentPage = 1;
    
    const paginationHTML = `
        <div class="table-pagination">
            <div class="pagination-info">
                Showing <span id="${table.id}_start">1</span>-<span id="${table.id}_end">${Math.min(pageSize, rows.length)}</span> of ${rows.length}
            </div>
            <div class="pagination-controls" id="${table.id}_pagination"></div>
        </div>
    `;
    wrapper.insertAdjacentHTML('afterend', paginationHTML);
    
    function renderPage(page) {
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        
        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });
        
        document.getElementById(`${table.id}_start`).textContent = start + 1;
        document.getElementById(`${table.id}_end`).textContent = Math.min(end, rows.length);
        
        renderPaginationControls(table.id, page, totalPages);
    }
    
    function renderPaginationControls(tableId, current, total) {
        const container = document.getElementById(`${tableId}_pagination`);
        let html = '';
        
        // Previous button
        html += `<button class="pagination-btn" ${current === 1 ? 'disabled' : ''} onclick="changePage('${tableId}', ${current - 1})">‹</button>`;
        
        // Page numbers
        for (let i = 1; i <= total; i++) {
            if (i === 1 || i === total || (i >= current - 1 && i <= current + 1)) {
                html += `<button class="pagination-btn ${i === current ? 'active' : ''}" onclick="changePage('${tableId}', ${i})">${i}</button>`;
            } else if (i === current - 2 || i === current + 2) {
                html += `<span style="color: rgba(255,255,255,0.3); padding: 8px;">...</span>`;
            }
        }
        
        // Next button
        html += `<button class="pagination-btn" ${current === total ? 'disabled' : ''} onclick="changePage('${tableId}', ${current + 1})">›</button>`;
        
        container.innerHTML = html;
    }
    
    window[`changePage_${table.id}`] = function(page) {
        currentPage = page;
        renderPage(page);
    };
    
    renderPage(1);
}

// Global function for pagination
function changePage(tableId, page) {
    if (window[`changePage_${tableId}`]) {
        window[`changePage_${tableId}`](page);
    }
}

// Navbar Scroll Effect
const navbar = document.querySelector('.navbar');
const topBar = document.querySelector('.top-bar');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
        // Optional: Hide top bar on scroll for cleaner look
        if(topBar) topBar.style.display = 'none';
    } else {
        navbar.classList.remove('scrolled');
        if(topBar) topBar.style.display = 'block';
    }
});

// ============================================
// ACTIVITY FEED (#8)
// ============================================

function initActivityFeed(containerId, activities = []) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    function renderActivities(filter = 'all') {
        const filtered = filter === 'all' ? activities : activities.filter(a => a.type === filter);
        
        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="activity-empty">
                    <div class="activity-empty-icon"><i class="bi bi-inbox"></i></div>
                    <p>No activities found</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = filtered.map(activity => `
            <div class="activity-item ${activity.new ? 'new' : ''}" data-type="${activity.type}">
                <div class="activity-icon ${activity.type}">
                    <i class="bi ${getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-meta">
                        <div class="activity-time">
                            <i class="bi bi-clock"></i>
                            <span>${activity.time}</span>
                        </div>
                        ${activity.badge ? `<span class="activity-badge ${activity.badge.type}">${activity.badge.text}</span>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    function getActivityIcon(type) {
        const icons = {
            'product': 'bi-box-seam',
            'invoice': 'bi-receipt-cutoff',
            'client': 'bi-person-plus',
            'message': 'bi-envelope',
            'system': 'bi-gear'
        };
        return icons[type] || 'bi-circle';
    }
    
    // Filter buttons
    document.querySelectorAll('.activity-filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.activity-filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.dataset.filter || 'all';
            renderActivities(filter);
        });
    });
    
    renderActivities();
}

function addActivity(containerId, activity) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    function getActivityIcon(type) {
        const icons = {
            'product': 'bi-box-seam',
            'invoice': 'bi-receipt-cutoff',
            'client': 'bi-person-plus',
            'message': 'bi-envelope',
            'system': 'bi-gear'
        };
        return icons[type] || 'bi-circle';
    }
    
    const activityHTML = `
        <div class="activity-item new" data-type="${activity.type}">
            <div class="activity-icon ${activity.type}">
                <i class="bi ${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-description">${activity.description}</div>
                <div class="activity-meta">
                    <div class="activity-time">
                        <i class="bi bi-clock"></i>
                        <span>${activity.time}</span>
                    </div>
                    ${activity.badge ? `<span class="activity-badge ${activity.badge.type}">${activity.badge.text}</span>` : ''}
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', activityHTML);
    
    // Remove 'new' class after 5 seconds
    setTimeout(() => {
        const item = container.querySelector('.activity-item.new');
        if (item) item.classList.remove('new');
    }, 5000);
}

// ============================================
// ADVANCED FILTERING SYSTEM (#9)
// ============================================

function initAdvancedFilters(panelId) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    
    const toggleBtn = panel.querySelector('.filter-toggle');
    const filterBody = panel.querySelector('.filter-body');
    const filterInputs = panel.querySelectorAll('.filter-input, .filter-select');
    const chipsContainer = panel.querySelector('.filter-chips-container') || createChipsContainer(panel);
    const resetBtn = panel.querySelector('.filter-reset');
    const applyBtn = panel.querySelector('.filter-apply');
    
    // Toggle filter panel
    if (toggleBtn && filterBody) {
        toggleBtn.addEventListener('click', () => {
            filterBody.classList.toggle('active');
            toggleBtn.classList.toggle('active');
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-chevron-down');
                icon.classList.toggle('bi-chevron-up');
            }
        });
    }
    
    // Handle filter changes
    filterInputs.forEach(input => {
        input.addEventListener('change', () => {
            updateFilters(panel, chipsContainer);
        });
    });
    
    // Reset filters
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            resetFilters(panel, chipsContainer);
        });
    }
    
    // Apply filters
    if (applyBtn) {
        applyBtn.addEventListener('click', () => {
            applyFilters(panel);
        });
    }
}

function createChipsContainer(panel) {
    const container = document.createElement('div');
    container.className = 'filter-chips-container';
    const filterBody = panel.querySelector('.filter-body');
    if (filterBody) {
        filterBody.insertAdjacentElement('afterend', container);
    }
    return container;
}

function updateFilters(panel, chipsContainer) {
    const filterInputs = panel.querySelectorAll('.filter-input, .filter-select');
    const chips = [];
    
    filterInputs.forEach(input => {
        if (input.value && input.value !== '' && input.value !== 'all') {
            const label = input.closest('.filter-group')?.querySelector('.filter-label')?.textContent || input.name;
            chips.push({
                key: input.name || input.id,
                label: label,
                value: input.value,
                input: input
            });
        }
    });
    
    renderFilterChips(chipsContainer, chips);
}

function renderFilterChips(container, chips) {
    if (!container) return;
    
    container.innerHTML = chips.map(chip => `
        <div class="filter-chip">
            <span>${chip.label}: ${chip.value}</span>
            <button class="filter-chip-remove" onclick="removeFilterChip('${chip.key}')" title="Remove filter">×</button>
        </div>
    `).join('');
}

function removeFilterChip(key) {
    const input = document.querySelector(`[name="${key}"], #${key}`);
    if (input) {
        input.value = '';
        const panel = input.closest('.filter-panel');
        const chipsContainer = panel?.querySelector('.filter-chips-container');
        if (panel && chipsContainer) {
            updateFilters(panel, chipsContainer);
        }
    }
}

function resetFilters(panel, chipsContainer) {
    const filterInputs = panel.querySelectorAll('.filter-input, .filter-select');
    filterInputs.forEach(input => {
        input.value = '';
    });
    if (chipsContainer) {
        chipsContainer.innerHTML = '';
    }
}

function applyFilters(panel) {
    const filterInputs = panel.querySelectorAll('.filter-input, .filter-select');
    const filters = {};
    
    filterInputs.forEach(input => {
        if (input.value && input.value !== '' && input.value !== 'all') {
            filters[input.name || input.id] = input.value;
        }
    });
    
    // Trigger custom event for filter application
    const event = new CustomEvent('filtersApplied', { detail: filters });
    document.dispatchEvent(event);
    
    console.log('Filters applied:', filters);
}

// Initialize advanced features on DOM ready (extend existing)
document.addEventListener('DOMContentLoaded', function() {
    // Initialize filters if they exist
    document.querySelectorAll('.filter-panel').forEach(panel => {
        if (panel.id) {
            initAdvancedFilters(panel.id);
        } else {
            panel.id = 'filterPanel_' + Math.random().toString(36).substr(2, 9);
            initAdvancedFilters(panel.id);
        }
    });
});