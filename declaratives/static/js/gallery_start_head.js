
        // 🚀 DRAG AND DROP IMPLEMENTATION - INSTANT HYPERX PERFORMANCE
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Initializing HyperX Drag & Drop...');
            initializeDragAndDrop();
        });
        
        function initializeDragAndDrop() {
            const sortableContainer = document.getElementById('sortable-list');
            if (!sortableContainer) {
                console.log('❌ Sortable container not found');
                return;
            }
            console.log('✅ Sortable container found:', sortableContainer);
            
            let draggedElement = null;
            let placeholder = null;
            
            // Add drag event listeners to all sortable items
            sortableContainer.querySelectorAll('.sortable-item').forEach(item => {
                item.addEventListener('dragstart', handleDragStart);
                item.addEventListener('dragend', handleDragEnd);
                item.addEventListener('dragover', handleDragOver);
                item.addEventListener('drop', handleDrop);
            });
            
            sortableContainer.addEventListener('dragover', handleContainerDragOver);
            
            function handleDragStart(e) {
                console.log('🎯 Drag started for:', this.getAttribute('data-id'));
                draggedElement = this;
                this.classList.add('dragging');
                
                // Create placeholder
                placeholder = document.createElement('div');
                placeholder.className = 'drag-placeholder';
                
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.outerHTML);
            }
            
            function handleDragEnd(e) {
                this.classList.remove('dragging');
                
                // Remove placeholder
                if (placeholder && placeholder.parentNode) {
                    placeholder.parentNode.removeChild(placeholder);
                }
                
                // Update order and send to server
                updateItemOrder();
                
                draggedElement = null;
                placeholder = null;
            }
            
            function handleDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                
                e.dataTransfer.dropEffect = 'move';
                
                if (this !== draggedElement) {
                    const rect = this.getBoundingClientRect();
                    const midY = rect.top + rect.height / 2;
                    
                    if (e.clientY < midY) {
                        this.parentNode.insertBefore(placeholder, this);
                    } else {
                        this.parentNode.insertBefore(placeholder, this.nextSibling);
                    }
                }
                
                return false;
            }
            
            function handleContainerDragOver(e) {
                if (e.preventDefault) {
                    e.preventDefault();
                }
                return false;
            }
            
            function handleDrop(e) {
                if (e.stopPropagation) {
                    e.stopPropagation();
                }
                
                if (draggedElement !== this && placeholder.parentNode) {
                    placeholder.parentNode.insertBefore(draggedElement, placeholder);
                }
                
                return false;
            }
            
            function updateItemOrder() {
                const items = sortableContainer.querySelectorAll('.sortable-item');
                const orderData = [];
                
                items.forEach((item, index) => {
                    const itemId = item.getAttribute('data-id');
                    orderData.push({
                        id: parseInt(itemId),
                        order: index + 1
                    });
                });
                
                // Send updated order to server via HTMX
                fetch('/declaratives/component/advanced/drag-drop/reorder/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: JSON.stringify({ items: orderData })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('✅ Order updated successfully:', data.message);
                    } else {
                        console.error('❌ Failed to update order:', data.error);
                    }
                })
                .catch(error => {
                    console.error('❌ Error updating order:', error);
                });
            }
        }