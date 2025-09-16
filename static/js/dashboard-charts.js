/**
 * DASHBOARD CHARTS - CHART MANAGEMENT
 * ==================================
 * Handles all chart-related functionality
 */

class DashboardCharts {
    constructor() {
        this.charts = new Map();
        this.animationDuration = 1000;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize charts
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupBarChart();
            this.setupCounters();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('Dashboard Charts initialized successfully');
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    /**
     * Setup bar chart
     */
    setupBarChart() {
        const chartContainer = document.getElementById('grafico-barras');
        if (!chartContainer) return;

        const bars = chartContainer.querySelectorAll('.bar-chart');
        bars.forEach(bar => {
            const value = parseInt(bar.dataset.value) || 0;
            this.animateBar(bar, value);
        });
    }

    /**
     * Animate bar chart
     */
    animateBar(bar, value) {
        const maxHeight = 120; // Maximum height in pixels
        const percentage = Math.min((value / 100) * 100, 100); // Cap at 100%
        const height = (percentage / 100) * maxHeight;
        
        // Set initial height
        bar.style.height = '0%';
        
        // Animate to target height
        setTimeout(() => {
            bar.style.height = `${percentage}%`;
            
            // Add color based on value
            if (percentage < 30) {
                bar.style.background = 'var(--color-bajo)';
            } else if (percentage < 70) {
                bar.style.background = 'var(--color-medio)';
            } else {
                bar.style.background = 'var(--color-alto)';
            }
        }, 100);
    }

    /**
     * Setup animated counters
     */
    setupCounters() {
        const counters = document.querySelectorAll('.counter-animation');
        counters.forEach(counter => {
            this.animateCounter(counter);
        });
    }

    /**
     * Animate counter
     */
    animateCounter(element) {
        const target = parseInt(element.textContent) || 0;
        const duration = this.animationDuration;
        const start = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(progress * target);
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    /**
     * Bind chart events
     */
    bindEvents() {
        // Property selector change
        const propertySelect = document.getElementById('propiedad-select');
        if (propertySelect) {
            propertySelect.addEventListener('change', (e) => {
                this.updateChart(e.target.value);
            });
        }

        // Bar hover effects
        const bars = document.querySelectorAll('.bar-chart');
        bars.forEach(bar => {
            bar.addEventListener('mouseenter', () => {
                bar.style.transform = 'scale(1.05)';
                bar.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
            });
            
            bar.addEventListener('mouseleave', () => {
                bar.style.transform = 'scale(1)';
                bar.style.boxShadow = 'none';
            });
        });
    }

    /**
     * Update chart data
     */
    async updateChart(propertyId) {
        const chartContainer = document.getElementById('grafico-barras');
        if (!chartContainer) return;

        try {
            // Show loading state
            chartContainer.classList.add('loading');
            
            // Fetch new data (this would be an API call in real implementation)
            const data = await this.fetchChartData(propertyId);
            
            // Update chart
            this.updateChartBars(data);
            
            // Update total counter
            this.updateTotalCounter(data.total);
            
        } catch (error) {
            console.error('Error updating chart:', error);
        } finally {
            chartContainer.classList.remove('loading');
        }
    }

    /**
     * Fetch chart data (mock implementation)
     */
    async fetchChartData(propertyId) {
        // This would be a real API call
        return new Promise((resolve) => {
            setTimeout(() => {
                const mockData = {
                    total: Math.floor(Math.random() * 1000) + 100,
                    months: [
                        { month: 'Ene', clicks: Math.floor(Math.random() * 100) },
                        { month: 'Feb', clicks: Math.floor(Math.random() * 100) },
                        { month: 'Mar', clicks: Math.floor(Math.random() * 100) },
                        { month: 'Abr', clicks: Math.floor(Math.random() * 100) },
                        { month: 'May', clicks: Math.floor(Math.random() * 100) },
                        { month: 'Jun', clicks: Math.floor(Math.random() * 100) }
                    ]
                };
                resolve(mockData);
            }, 500);
        });
    }

    /**
     * Update chart bars
     */
    updateChartBars(data) {
        const bars = document.querySelectorAll('.bar-chart');
        const months = document.querySelectorAll('.chart-month');
        
        data.months.forEach((monthData, index) => {
            if (bars[index]) {
                bars[index].dataset.value = monthData.clicks;
                this.animateBar(bars[index], monthData.clicks);
            }
            
            if (months[index]) {
                months[index].textContent = monthData.month;
            }
        });
    }

    /**
     * Update total counter
     */
    updateTotalCounter(total) {
        const counter = document.getElementById('total-clicks');
        if (counter) {
            counter.textContent = total.toLocaleString();
        }
    }

    /**
     * Refresh all charts
     */
    refresh() {
        this.setupBarChart();
        this.setupCounters();
    }

    /**
     * Destroy charts
     */
    destroy() {
        this.charts.clear();
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.DashboardCharts = DashboardCharts;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardCharts = new DashboardCharts();
});
