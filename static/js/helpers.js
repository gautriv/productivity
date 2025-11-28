/**
 * Utility Helper Functions
 */

// Date formatting
window.formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

window.formatDisplayDate = (dateStr) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
};

// Time formatting
window.formatTime = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
};

// Task hierarchy organization
window.organizeTaskHierarchy = (tasks) => {
    const mainTasks = tasks.filter(t => !t.is_subtask);
    const subtasks = tasks.filter(t => t.is_subtask);

    const subtaskMap = {};
    subtasks.forEach(st => {
        if (st.parent_daily_task_id) {
            if (!subtaskMap[st.parent_daily_task_id]) {
                subtaskMap[st.parent_daily_task_id] = [];
            }
            subtaskMap[st.parent_daily_task_id].push(st);
        }
    });

    const result = [];
    mainTasks.forEach(mainTask => {
        result.push(mainTask);
        if (subtaskMap[mainTask.id]) {
            result.push(...subtaskMap[mainTask.id]);
        }
    });

    // Add orphan subtasks at the end
    subtasks.forEach(st => {
        if (!st.parent_daily_task_id || !mainTasks.find(m => m.id === st.parent_daily_task_id)) {
            result.push(st);
        }
    });

    return result;
};
