/**
 * TaskItem Component
 */

import { formatTime, cognitiveLoadConfig } from '../utils/helpers.js';

const { useState, useEffect } = React;

export function TaskItem({ task, onStatusChange, onDelete, index, onDragStart, onDragEnd, onDragOver, onDragLeave, onDrop, onMakeSubtask, onMakeMainTask, allTasks }) {
    const handleCheck = () => {
        const newStatus = task.status === 'completed' ? 'pending' : 'completed';
        onStatusChange(task.id, newStatus);
    };

    const netPoints = task.status === 'completed'
        ? task.points - task.penalty_points
        : -task.penalty_points;

    // Get potential parent tasks (main tasks that are not the current task)
    const potentialParents = allTasks.filter(t =>
        t.id !== task.id &&
        !t.is_subtask
    );

    // Check if current task can become a subtask (fix: handle undefined/null subtask_count)
    const canBecomeSubtask = (task.subtask_count || 0) === 0;

    const [showParentMenu, setShowParentMenu] = useState(false);
    const dropdownRef = React.useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        if (!showParentMenu) return;

        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowParentMenu(false);
            }
        };

        // Add event listener with a small delay to prevent immediate closing
        setTimeout(() => {
            document.addEventListener('click', handleClickOutside);
        }, 0);

        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, [showParentMenu]);

    return (
        <div
            className={`task-item ${task.status} ${task.is_subtask ? 'is-subtask' : ''} animate-fade-in`}
            style={{ animationDelay: `${index * 0.05}s` }}
            draggable="true"
            onDragStart={(e) => onDragStart(e, task, index)}
            onDragEnd={onDragEnd}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={(e) => onDrop(e, task, index)}
            data-task-id={task.id}
        >
            <div
                className={`task-checkbox ${task.status === 'completed' ? 'completed' : ''}`}
                onClick={handleCheck}
            />

            <div className="task-content">
                <div className="task-title">
                    {task.is_subtask && <span className="subtask-icon">↳</span>}
                    {task.title}
                </div>
                <div className="task-meta">
                    <span className={`task-badge ${task.cognitive_load}`}>
                        {cognitiveLoadConfig[task.cognitive_load]?.label || task.cognitive_load}
                    </span>
                    <span className="complexity-dots">
                        {[1,2,3,4,5].map(i => (
                            <span key={i} className={`complexity-dot ${i <= task.complexity ? 'filled' : ''}`} />
                        ))}
                    </span>
                    <span>{formatTime(task.time_estimate)}</span>
                    {task.rolled_over_count > 0 && (
                        <span className="penalty-badge">
                            ↩ {task.rolled_over_count}x rolled
                        </span>
                    )}
                    {task.subtask_count > 0 && (
                        <span className="subtask-count-badge">
                            📁 {task.subtask_count} subtask{task.subtask_count > 1 ? 's' : ''}
                        </span>
                    )}
                </div>
            </div>

            <div className={`task-points ${netPoints >= 0 ? 'positive' : 'negative'}`}>
                {netPoints >= 0 ? '+' : ''}{netPoints} pts
            </div>

            <div className={`task-actions ${showParentMenu ? 'menu-open' : ''}`}>
                {task.is_subtask ? (
                    <button
                        className="task-action-btn promote"
                        onClick={(e) => {
                            e.stopPropagation();
                            onMakeMainTask(task.id);
                        }}
                        title="Convert to main task"
                    >
                        ↑
                    </button>
                ) : (
                    <div className="subtask-dropdown" ref={dropdownRef}>
                        <button
                            className="task-action-btn demote"
                            onClick={(e) => {
                                e.stopPropagation();
                                setShowParentMenu(!showParentMenu);
                            }}
                            title={!canBecomeSubtask ? "This task has subtasks" : "Make subtask of..."}
                            disabled={potentialParents.length === 0 || !canBecomeSubtask}
                        >
                            ↓
                        </button>
                        {showParentMenu && potentialParents.length > 0 && (
                            <div className="parent-menu" onClick={(e) => e.stopPropagation()}>
                                <div className="parent-menu-header">Make subtask of:</div>
                                {potentialParents.map(parent => (
                                    <button
                                        key={parent.id}
                                        className="parent-menu-item"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onMakeSubtask(task.id, parent.id);
                                            setShowParentMenu(false);
                                        }}
                                    >
                                        {parent.title}
                                    </button>
                                ))}
                                <button
                                    className="parent-menu-item cancel"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setShowParentMenu(false);
                                    }}
                                >
                                    Cancel
                                </button>
                            </div>
                        )}
                    </div>
                )}
                <button className="task-action-btn delete" onClick={(e) => {
                    e.stopPropagation();
                    onDelete(task.id);
                }}>
                    ×
                </button>
            </div>
        </div>
    );
}
