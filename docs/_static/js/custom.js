// Custom JavaScript for OptiX Documentation

document.addEventListener('DOMContentLoaded', function() {
    
    // Add smooth scrolling to all links
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
    
    // Add copy functionality to code blocks
    function addCopyButtons() {
        const codeBlocks = document.querySelectorAll('.highlight pre');
        codeBlocks.forEach((block, index) => {
            // Skip if copy button already exists
            if (block.parentElement.querySelector('.copy-btn')) return;
            
            const button = document.createElement('button');
            button.className = 'copy-btn';
            button.innerHTML = '📋';
            button.title = 'Copy code';
            button.setAttribute('data-code-index', index);
            
            // Position button
            block.parentElement.style.position = 'relative';
            button.style.position = 'absolute';
            button.style.top = '10px';
            button.style.right = '10px';
            button.style.background = 'var(--optix-gradient-secondary)';
            button.style.border = 'none';
            button.style.borderRadius = '4px';
            button.style.color = 'white';
            button.style.padding = '6px 10px';
            button.style.cursor = 'pointer';
            button.style.fontSize = '12px';
            button.style.zIndex = '10';
            button.style.transition = 'all 0.3s ease';
            
            // Add hover effects
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.background = 'var(--optix-secondary)';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.background = 'var(--optix-gradient-secondary)';
            });
            
            // Copy functionality
            button.addEventListener('click', function() {
                const code = block.textContent;
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = this.innerHTML;
                    this.innerHTML = '✅';
                    this.style.background = 'var(--optix-secondary)';
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.style.background = 'var(--optix-gradient-secondary)';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy code: ', err);
                    this.innerHTML = '❌';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
            });
            
            block.parentElement.appendChild(button);
        });
    }
    
    // Add performance indicators
    function addPerformanceIndicators() {
        const performanceTables = document.querySelectorAll('.performance-table tbody tr');
        performanceTables.forEach(row => {
            const timeCell = row.querySelector('td:last-child');
            if (timeCell) {
                const timeText = timeCell.textContent.toLowerCase();
                let indicator = document.createElement('span');
                indicator.className = 'status-indicator';
                
                if (timeText.includes('second') && !timeText.includes('minutes')) {
                    indicator.classList.add('optimal');
                    indicator.title = 'Fast execution';
                } else if (timeText.includes('minute')) {
                    indicator.classList.add('feasible');
                    indicator.title = 'Moderate execution time';
                } else {
                    indicator.classList.add('infeasible');
                    indicator.title = 'Slow execution';
                }
                
                timeCell.insertBefore(indicator, timeCell.firstChild);
            }
        });
    }
    
    // Add search highlighting
    function highlightSearchTerms() {
        const urlParams = new URLSearchParams(window.location.search);
        const searchTerm = urlParams.get('highlight');
        
        if (searchTerm) {
            const content = document.querySelector('.rst-content');
            if (content) {
                const regex = new RegExp(`(${searchTerm})`, 'gi');
                const walker = document.createTreeWalker(
                    content,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                const textNodes = [];
                let node;
                while (node = walker.nextNode()) {
                    if (node.nodeValue.trim() && !node.parentElement.closest('script, style, code, pre')) {
                        textNodes.push(node);
                    }
                }
                
                textNodes.forEach(textNode => {
                    if (regex.test(textNode.nodeValue)) {
                        const highlighted = textNode.nodeValue.replace(regex, '<span class="highlighted">$1</span>');
                        const wrapper = document.createElement('span');
                        wrapper.innerHTML = highlighted;
                        textNode.parentNode.replaceChild(wrapper, textNode);
                    }
                });
            }
        }
    }
    
    // Add table of contents toggle for mobile
    function addMobileTOC() {
        if (window.innerWidth <= 768) {
            const tocToggle = document.createElement('button');
            tocToggle.innerHTML = '📋 Table of Contents';
            tocToggle.className = 'mobile-toc-toggle';
            tocToggle.style.cssText = `
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1000;
                background: var(--optix-gradient-primary);
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: 600;
                box-shadow: var(--optix-shadow-md);
                cursor: pointer;
            `;
            
            const nav = document.querySelector('.wy-nav-side');
            if (nav) {
                tocToggle.addEventListener('click', function() {
                    nav.style.display = nav.style.display === 'none' ? 'block' : 'none';
                });
                
                document.body.appendChild(tocToggle);
            }
        }
    }
    
    // Add progress indicator for long pages
    function addProgressIndicator() {
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-indicator';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: var(--optix-gradient-primary);
            z-index: 1000;
            transition: width 0.3s ease;
        `;
        
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', function() {
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight - windowHeight;
            const scrolled = window.scrollY;
            const progress = (scrolled / documentHeight) * 100;
            
            progressBar.style.width = Math.min(progress, 100) + '%';
        });
    }
    
    // Add interactive examples
    function addInteractiveExamples() {
        const examples = document.querySelectorAll('.code-example');
        examples.forEach(example => {
            const header = example.querySelector('.code-example-header');
            const codeBlock = example.querySelector('.highlight');
            
            if (header && codeBlock) {
                const runButton = document.createElement('button');
                runButton.innerHTML = '▶️ Run';
                runButton.className = 'run-example-btn';
                runButton.style.cssText = `
                    background: var(--optix-gradient-secondary);
                    color: white;
                    border: none;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    cursor: pointer;
                    margin-left: 10px;
                `;
                
                runButton.addEventListener('click', function() {
                    // For demo purposes, just show a success message
                    const originalText = this.innerHTML;
                    this.innerHTML = '✅ Executed';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
                
                header.appendChild(runButton);
            }
        });
    }
    
    // Add dark mode toggle
    function addDarkModeToggle() {
        const toggle = document.createElement('button');
        toggle.innerHTML = '🌓';
        toggle.className = 'dark-mode-toggle';
        toggle.title = 'Toggle dark mode';
        toggle.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: var(--optix-gradient-primary);
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 16px;
            cursor: pointer;
            box-shadow: var(--optix-shadow-md);
            transition: all 0.3s ease;
        `;
        
        toggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
            
            // Update icon
            this.innerHTML = document.body.classList.contains('dark-mode') ? '☀️' : '🌓';
        });
        
        // Load saved preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            toggle.innerHTML = '☀️';
        }
        
        document.body.appendChild(toggle);
    }
    
    // Add version comparison widget
    function addVersionComparison() {
        const versionWidget = document.createElement('div');
        versionWidget.className = 'version-comparison';
        versionWidget.innerHTML = `
            <h4>📊 Version Comparison</h4>
            <div class="version-grid">
                <div class="version-item">
                    <strong>Current:</strong> 1.0.0
                    <span class="version-badge current">Latest</span>
                </div>
                <div class="version-item">
                    <strong>Previous:</strong> 0.9.0
                    <span class="version-badge previous">Stable</span>
                </div>
            </div>
        `;
        
        versionWidget.style.cssText = `
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1rem;
            margin: 2rem 0;
            box-shadow: var(--optix-shadow-sm);
        `;
        
        // Insert after first h2 if exists
        const firstH2 = document.querySelector('.rst-content h2');
        if (firstH2) {
            firstH2.parentNode.insertBefore(versionWidget, firstH2.nextSibling);
        }
    }
    
    // Initialize all features
    addCopyButtons();
    addPerformanceIndicators();
    highlightSearchTerms();
    addMobileTOC();
    addProgressIndicator();
    addInteractiveExamples();
    addDarkModeToggle();
    
    // Add version comparison only on index page
    if (window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/')) {
        addVersionComparison();
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="text"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // ESC to close mobile navigation
        if (e.key === 'Escape') {
            const nav = document.querySelector('.wy-nav-side');
            if (nav && window.innerWidth <= 768) {
                nav.style.display = 'none';
            }
        }
    });
    
    // Add loading animation
    const loadingOverlay = document.createElement('div');
    loadingOverlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Loading OptiX Documentation...</p>
        </div>
    `;
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
    `;
    
    // Show loading for external links
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        link.addEventListener('click', function() {
            loadingOverlay.style.opacity = '1';
            loadingOverlay.style.pointerEvents = 'all';
            
            setTimeout(() => {
                loadingOverlay.style.opacity = '0';
                loadingOverlay.style.pointerEvents = 'none';
            }, 1000);
        });
    });
    
    document.body.appendChild(loadingOverlay);
    
    console.log('OptiX Documentation enhanced features loaded! 🚀');
});