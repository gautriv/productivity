/**
 * Task Completion Modal
 * Captures actual time and provides completion feedback
 */

class CompletionModal {
    constructor() {
        this.isOpen = false;
        this.currentTask = null;
        this.onComplete = null;
        this.element = null;
        this.init();
    }

    init() {
        this.createDOM();
        this.bindEvents();
    }

    createDOM() {
        const html = `
            <div id="completion-modal" class="modal-overlay" style="display: none;">
                <div class="modal">
                    <div class="modal-header">
                        <h2 class="modal-title">✓ Complete Task</h2>
                        <button class="modal-close" data-action="close">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="completion-task-info">
                            <div class="completion-task-title"></div>
                            <div class="completion-task-estimate"></div>
                        </div>

                        <form id="completion-form">
                            <div class="form-group">
                                <label class="form-label">Actual Time Spent (minutes) *</label>
                                <input
                                    type="number"
                                    id="actual-time-input"
                                    class="form-input"
                                    placeholder="How long did it take?"
                                    min="1"
                                    step="1"
                                    required
                                    autofocus
                                />
                                <div class="form-hint">Estimated: <span id="estimated-time"></span> minutes</div>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Notes (Optional)</label>
                                <textarea
                                    id="completion-notes"
                                    class="form-input"
                                    placeholder="Any thoughts on this task?"
                                    rows="3"
                                ></textarea>
                            </div>

                            <div class="completion-preview" style="display: none;">
                                <div class="preview-label">Time Accuracy</div>
                                <div class="preview-value" id="time-accuracy"></div>
                            </div>

                            <div class="form-actions">
                                <button type="button" class="btn btn-secondary" data-action="close">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-success">
                                    ✓ Complete Task
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);
        this.element = document.getElementById('completion-modal');
        this.form = document.getElementById('completion-form');
        this.actualTimeInput = document.getElementById('actual-time-input');
    }

    bindEvents() {
        // Close buttons
        this.element.querySelectorAll('[data-action="close"]').forEach(btn => {
            btn.addEventListener('click', () => this.close());
        });

        // Click outside to close
        this.element.addEventListener('click', (e) => {
            if (e.target === this.element) {
                this.close();
            }
        });

        // Form submit
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSubmit();
        });

        // Real-time time accuracy preview
        this.actualTimeInput.addEventListener('input', () => {
            this.updateTimeAccuracyPreview();
        });

        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    open(task, onComplete) {
        this.currentTask = task;
        this.onComplete = onComplete;
        this.isOpen = true;

        // Populate task info
        this.element.querySelector('.completion-task-title').textContent = task.title;
        this.element.querySelector('.completion-task-estimate').textContent =
            `Complexity: ${'⭐'.repeat(task.complexity)} • ${task.cognitive_load?.replace('_', ' ')}`;

        // Set estimated time
        document.getElementById('estimated-time').textContent = task.time_estimate;

        // Pre-fill with estimated time
        this.actualTimeInput.value = task.time_estimate;

        // Show modal
        this.element.style.display = 'flex';

        // Focus input after a short delay
        setTimeout(() => {
            this.actualTimeInput.select();
        }, 100);

        this.updateTimeAccuracyPreview();
    }

    close() {
        this.isOpen = false;
        this.element.style.display = 'none';
        this.form.reset();
        this.currentTask = null;
        this.onComplete = null;
    }

    updateTimeAccuracyPreview() {
        const actualTime = parseInt(this.actualTimeInput.value);
        const estimatedTime = this.currentTask?.time_estimate || 0;

        if (!actualTime || !estimatedTime) {
            document.querySelector('.completion-preview').style.display = 'none';
            return;
        }

        const previewEl = document.querySelector('.completion-preview');
        const accuracyEl = document.getElementById('time-accuracy');

        previewEl.style.display = 'block';

        const ratio = actualTime / estimatedTime;

        if (ratio > 1.5) {
            accuracyEl.innerHTML = `<span style="color: var(--accent-red)">⚠️ Took ${Math.round((ratio - 1) * 100)}% longer than estimated</span>`;
        } else if (ratio < 0.7) {
            accuracyEl.innerHTML = `<span style="color: var(--accent-green)">✓ Completed ${Math.round((1 - ratio) * 100)}% faster than estimated!</span>`;
        } else {
            accuracyEl.innerHTML = `<span style="color: var(--accent-blue)">✓ Close to estimate - good planning!</span>`;
        }
    }

    async handleSubmit() {
        if (!this.currentTask || !this.onComplete) {
            console.error('No task or callback set');
            return;
        }

        const actualTime = parseInt(this.actualTimeInput.value);
        const notes = document.getElementById('completion-notes').value;

        if (!actualTime || actualTime < 1) {
            alert('Please enter a valid time (at least 1 minute)');
            return;
        }

        // Disable submit button to prevent double submission
        const submitBtn = this.form.querySelector('[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Completing...';

        try {
            // Call the completion callback
            await this.onComplete({
                actual_time: actualTime,
                notes: notes
            });

            // Close modal on success
            this.close();
        } catch (error) {
            console.error('Error completing task:', error);
            alert('Failed to complete task. Please try again.');

            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }
}

// Global instance
window.completionModal = new CompletionModal();
