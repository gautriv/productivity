        const { useState, useEffect, useRef, useCallback } = React;

        // API helpers
        const api = {
            async get(url) {
                const res = await fetch(url);
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            },
            async post(url, data) {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            },
            async put(url, data) {
                const res = await fetch(url, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            },
            async delete(url) {
                const res = await fetch(url, { method: 'DELETE' });
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            }
        };

        // Date helpers
        const formatDate = (date) => {
            return date.toISOString().split('T')[0];
        };

        const formatDisplayDate = (date) => {
            const options = { month: 'long', day: 'numeric', year: 'numeric' };
            return date.toLocaleDateString('en-US', options);
        };

        const getDayName = (date) => {
            return date.toLocaleDateString('en-US', { weekday: 'long' });
        };

        const formatTime = (minutes) => {
            if (minutes < 60) return `${minutes}m`;
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
        };

        // Cognitive load config
        const cognitiveLoadConfig = {
            deep_work: { icon: '🧠', label: 'Deep Work', desc: 'Focus-intensive tasks' },
            active_work: { icon: '⚡', label: 'Active Work', desc: 'Meetings, calls, routine' },
            admin: { icon: '🔄', label: 'Admin', desc: 'Emails, scheduling' },
            learning: { icon: '📚', label: 'Learning', desc: 'Self-development' }
        };

        // Helper to organize tasks with subtasks grouped under parents
        const organizeTaskHierarchy = (tasks) => {
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

        // Components
        function Sidebar({ summary, onRollover, userStats, productivityScore }) {
            return (
                <aside className="sidebar">
                    <div className="logo">
                        <div className="logo-icon">PT</div>
                        <span className="logo-text">Productivity</span>
                    </div>

                    <div className="summary-card animate-fade-in">
                        <div className="summary-label">Level & XP</div>
                        <div className="level-badge">
                            ⭐ Level {userStats.level}
                        </div>
                        <div className="xp-bar">
                            <div 
                                className="xp-progress" 
                                style={{ width: `${userStats.xp_percentage}%` }}
                            />
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                            {userStats.current_xp} / {userStats.xp_needed} XP
                        </div>
                    </div>

                    <div className="summary-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
                        <div className="summary-label">Net Points (30d)</div>
                        <div className={`summary-value ${summary.net_points >= 0 ? 'positive' : 'negative'}`}>
                            {summary.net_points >= 0 ? '+' : ''}{summary.net_points}
                        </div>
                        <div className={`streak-badge ${summary.current_streak > 0 ? 'active' : ''}`}>
                            🔥 {summary.current_streak} day streak
                        </div>
                    </div>

                    <div className="productivity-score animate-fade-in" style={{ animationDelay: '0.2s' }}>
                        <div className="summary-label">Productivity Score</div>
                        <div className="score-circle" style={{ '--score': productivityScore.score }}>
                            <div className="score-inner">
                                <div className="score-value">{productivityScore.score}</div>
                                <div className="score-label">/ 100</div>
                            </div>
                        </div>
                        <div style={{ 
                            fontSize: '13px', 
                            fontWeight: 600, 
                            color: productivityScore.color === 'green' ? 'var(--accent-green)' : 
                                   productivityScore.color === 'blue' ? 'var(--accent-blue)' :
                                   productivityScore.color === 'yellow' ? 'var(--accent-yellow)' : 
                                   'var(--accent-red)'
                        }}>
                            {productivityScore.rating}
                        </div>
                    </div>

                    <div className="summary-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
                        <div className="summary-label">Achievements</div>
                        <div className="summary-value neutral">
                            {userStats.achievements_unlocked}/{userStats.total_achievements}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                            {userStats.total_completed} tasks completed
                        </div>
                    </div>

                    <button 
                        className="btn btn-secondary" 
                        style={{ marginTop: 'auto', width: '100%' }}
                        onClick={onRollover}
                    >
                        Process Rollover →
                    </button>
                </aside>
            );
        }

        function TaskItem({ task, onStatusChange, onDelete, index, onDragStart, onDragEnd, onDragOver, onDragLeave, onDrop, onMakeSubtask, onMakeMainTask, allTasks }) {
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
            React.useEffect(() => {
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

        // Time Entry Modal for task completion
        function TimeEntryModal({ isOpen, onClose, onConfirm, taskTitle, estimatedTime }) {
            const [hours, setHours] = useState(0);
            const [minutes, setMinutes] = useState(0);

            useEffect(() => {
                if (isOpen && estimatedTime) {
                    // Pre-fill with estimated time
                    setHours(Math.floor(estimatedTime / 60));
                    setMinutes(estimatedTime % 60);
                }
            }, [isOpen, estimatedTime]);

            const handleConfirm = () => {
                const totalMinutes = (hours * 60) + minutes;

                if (totalMinutes === 0) {
                    alert('Please enter a valid time (at least 1 minute)');
                    return;
                }

                console.log('Confirming time entry:', totalMinutes, 'minutes');
                onConfirm(totalMinutes);

                // Reset state
                setHours(0);
                setMinutes(0);
            };

            if (!isOpen) return null;

            return (
                <div className="modal-overlay" onClick={onClose}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '450px' }}>
                        <div className="modal-header">
                            <h2 className="modal-title">⏱️ Time Spent</h2>
                            <button className="modal-close" onClick={onClose}>&times;</button>
                        </div>

                        <div className="modal-body">
                            <div style={{ marginBottom: '20px' }}>
                                <div style={{ 
                                    fontSize: '14px', 
                                    color: 'var(--text-secondary)', 
                                    marginBottom: '8px' 
                                }}>
                                    Completing: <strong style={{ color: 'var(--text-primary)' }}>{taskTitle}</strong>
                                </div>
                                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                    Estimated: {Math.floor(estimatedTime / 60)}h {estimatedTime % 60}m
                                </div>
                            </div>

                            <div style={{ 
                                fontSize: '13px', 
                                fontWeight: '600', 
                                marginBottom: '12px',
                                color: 'var(--text-primary)' 
                            }}>
                                How much time did you actually spend?
                            </div>

                            <div style={{ 
                                display: 'grid', 
                                gridTemplateColumns: '1fr 1fr', 
                                gap: '12px',
                                marginBottom: '20px' 
                            }}>
                                <div className="form-group" style={{ margin: 0 }}>
                                    <label className="form-label">Hours</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        min="0"
                                        max="24"
                                        value={hours}
                                        onChange={e => setHours(Math.max(0, parseInt(e.target.value) || 0))}
                                        style={{ textAlign: 'center', fontSize: '18px' }}
                                    />
                                </div>
                                <div className="form-group" style={{ margin: 0 }}>
                                    <label className="form-label">Minutes</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        min="0"
                                        max="59"
                                        value={minutes}
                                        onChange={e => setMinutes(Math.max(0, Math.min(59, parseInt(e.target.value) || 0)))}
                                        style={{ textAlign: 'center', fontSize: '18px' }}
                                    />
                                </div>
                            </div>

                            <div style={{ 
                                background: 'var(--bg-tertiary)', 
                                padding: '12px', 
                                borderRadius: '8px',
                                marginBottom: '20px',
                                textAlign: 'center'
                            }}>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                                    Total Time
                                </div>
                                <div style={{ 
                                    fontSize: '24px', 
                                    fontWeight: '700', 
                                    fontFamily: 'JetBrains Mono, monospace',
                                    color: 'var(--accent-green)' 
                                }}>
                                    {hours}h {minutes}m
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button 
                                    className="btn btn-secondary" 
                                    onClick={onClose}
                                    style={{ flex: 1 }}
                                >
                                    Cancel
                                </button>
                                <button 
                                    className="btn btn-primary" 
                                    onClick={handleConfirm}
                                    style={{ flex: 1 }}
                                >
                                    ✓ Complete Task
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        function AddTaskModal({ isOpen, onClose, onAdd, selectedDate, existingTasks = [] }) {
            const [title, setTitle] = useState('');
            const [description, setDescription] = useState('');
            const [complexity, setComplexity] = useState(3);
            const [cognitiveLoad, setCognitiveLoad] = useState('active_work');
            const [timeEstimate, setTimeEstimate] = useState(30);
            const [useCustomTime, setUseCustomTime] = useState(false);
            const [customHours, setCustomHours] = useState(0);
            const [customMinutes, setCustomMinutes] = useState(30);
            const [parentTaskId, setParentTaskId] = useState(null);

            const timeOptions = [15, 30, 60, 120, 240, 480];
            
            // Get potential parent tasks (main tasks only)
            const potentialParents = existingTasks.filter(t => !t.is_subtask);

            const handleSubmit = () => {
                if (!title.trim()) return;

                // Calculate final time estimate
                const finalTimeEstimate = useCustomTime
                    ? (customHours * 60) + customMinutes
                    : timeEstimate;

                if (finalTimeEstimate === 0) {
                    alert('Please enter a valid time estimate (at least 1 minute)');
                    return;
                }

                onAdd({
                    title: title.trim(),
                    description,
                    complexity,
                    cognitive_load: cognitiveLoad,
                    time_estimate: finalTimeEstimate,
                    parent_daily_task_id: parentTaskId
                });

                // Reset form
                setTitle('');
                setDescription('');
                setComplexity(3);
                setCognitiveLoad('active_work');
                setTimeEstimate(30);
                setUseCustomTime(false);
                setCustomHours(0);
                setCustomMinutes(30);
                setParentTaskId(null);
            };

            if (!isOpen) return null;

            return (
                <div className="modal-overlay" onClick={onClose}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">Add Task</h2>
                            <button className="modal-close" onClick={onClose}>&times;</button>
                        </div>

                        <div className="modal-body">
                            <div className="form-group">
                                <label className="form-label">Task Title</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    placeholder="What needs to be done?"
                                    value={title}
                                    onChange={e => setTitle(e.target.value)}
                                    autoFocus
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Description (optional)</label>
                                <textarea
                                    className="form-input"
                                    placeholder="Add details..."
                                    rows={2}
                                    value={description}
                                    onChange={e => setDescription(e.target.value)}
                                />
                            </div>

                            {potentialParents.length > 0 && (
                                <div className="form-group">
                                    <label className="form-label">Task Type</label>
                                    <div className="task-type-selector">
                                        <button
                                            className={`task-type-btn ${parentTaskId === null ? 'selected' : ''}`}
                                            onClick={() => setParentTaskId(null)}
                                        >
                                            <span className="task-type-icon">📋</span>
                                            <span>Main Task</span>
                                        </button>
                                        <button
                                            className={`task-type-btn ${parentTaskId !== null ? 'selected' : ''}`}
                                            onClick={() => setParentTaskId(potentialParents[0]?.id || null)}
                                        >
                                            <span className="task-type-icon">↳</span>
                                            <span>Subtask</span>
                                        </button>
                                    </div>
                                    
                                    {parentTaskId !== null && (
                                        <div className="parent-selector" style={{ marginTop: '12px' }}>
                                            <label className="form-label" style={{ fontSize: '11px' }}>Parent Task</label>
                                            <select
                                                className="form-input form-select"
                                                value={parentTaskId || ''}
                                                onChange={e => setParentTaskId(parseInt(e.target.value))}
                                            >
                                                {potentialParents.map(parent => (
                                                    <option key={parent.id} value={parent.id}>
                                                        {parent.title}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="form-group">
                                <label className="form-label">Cognitive Load</label>
                                <div className="cognitive-load-selector">
                                    {Object.entries(cognitiveLoadConfig).map(([key, config]) => (
                                        <button
                                            key={key}
                                            className={`cognitive-btn ${key} ${cognitiveLoad === key ? 'selected' : ''}`}
                                            onClick={() => setCognitiveLoad(key)}
                                        >
                                            <div className="cognitive-btn-icon">{config.icon}</div>
                                            <div className="cognitive-btn-label">{config.label}</div>
                                            <div className="cognitive-btn-desc">{config.desc}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Complexity (1-5)</label>
                                <div className="complexity-selector">
                                    {[1,2,3,4,5].map(i => (
                                        <button
                                            key={i}
                                            className={`complexity-btn ${complexity === i ? 'selected' : ''}`}
                                            onClick={() => setComplexity(i)}
                                        >
                                            {i}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Time Estimate</label>

                                <div style={{
                                    display: 'flex',
                                    gap: '8px',
                                    alignItems: 'center',
                                    marginBottom: '12px',
                                    padding: '8px',
                                    background: 'var(--bg-elevated)',
                                    borderRadius: '8px'
                                }}>
                                    <button
                                        className={`time-mode-btn ${!useCustomTime ? 'active' : ''}`}
                                        onClick={() => setUseCustomTime(false)}
                                        style={{
                                            flex: 1,
                                            padding: '8px 16px',
                                            border: 'none',
                                            borderRadius: '6px',
                                            background: !useCustomTime ? 'var(--accent-blue)' : 'transparent',
                                            color: !useCustomTime ? 'white' : 'var(--text-secondary)',
                                            fontSize: '13px',
                                            fontWeight: '600',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        Preset
                                    </button>
                                    <button
                                        className={`time-mode-btn ${useCustomTime ? 'active' : ''}`}
                                        onClick={() => setUseCustomTime(true)}
                                        style={{
                                            flex: 1,
                                            padding: '8px 16px',
                                            border: 'none',
                                            borderRadius: '6px',
                                            background: useCustomTime ? 'var(--accent-blue)' : 'transparent',
                                            color: useCustomTime ? 'white' : 'var(--text-secondary)',
                                            fontSize: '13px',
                                            fontWeight: '600',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        Custom
                                    </button>
                                </div>

                                {!useCustomTime ? (
                                    <div className="time-selector">
                                        {timeOptions.map(mins => (
                                            <button
                                                key={mins}
                                                className={`time-btn ${timeEstimate === mins ? 'selected' : ''}`}
                                                onClick={() => setTimeEstimate(mins)}
                                            >
                                                {formatTime(mins)}
                                            </button>
                                        ))}
                                    </div>
                                ) : (
                                    <div>
                                        <div style={{
                                            display: 'grid',
                                            gridTemplateColumns: '1fr 1fr',
                                            gap: '12px',
                                            marginBottom: '12px'
                                        }}>
                                            <div style={{ margin: 0 }}>
                                                <label className="form-label" style={{ fontSize: '12px', marginBottom: '6px' }}>Hours</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    min="0"
                                                    max="24"
                                                    value={customHours}
                                                    onChange={e => setCustomHours(Math.max(0, parseInt(e.target.value) || 0))}
                                                    style={{ textAlign: 'center', fontSize: '16px', padding: '10px' }}
                                                />
                                            </div>
                                            <div style={{ margin: 0 }}>
                                                <label className="form-label" style={{ fontSize: '12px', marginBottom: '6px' }}>Minutes</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    min="0"
                                                    max="59"
                                                    value={customMinutes}
                                                    onChange={e => setCustomMinutes(Math.max(0, Math.min(59, parseInt(e.target.value) || 0)))}
                                                    style={{ textAlign: 'center', fontSize: '16px', padding: '10px' }}
                                                />
                                            </div>
                                        </div>
                                        <div style={{
                                            background: 'var(--bg-tertiary)',
                                            padding: '10px',
                                            borderRadius: '6px',
                                            textAlign: 'center'
                                        }}>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                                                Total Estimate
                                            </div>
                                            <div style={{
                                                fontSize: '18px',
                                                fontWeight: '700',
                                                fontFamily: 'JetBrains Mono, monospace',
                                                color: 'var(--accent-green)'
                                            }}>
                                                {customHours}h {customMinutes}m
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                            <button className="btn btn-primary" onClick={handleSubmit}>Add Task</button>
                        </div>
                    </div>
                </div>
            );
        }

        // Trends Detail Modal
        function TrendsModal({ isOpen, onClose, trends, patterns }) {
            const chartRef = useRef(null);
            const chartInstance = useRef(null);

            useEffect(() => {
                if (isOpen && chartRef.current && trends.length > 0) {
                    if (chartInstance.current) {
                        chartInstance.current.destroy();
                    }

                    const ctx = chartRef.current.getContext('2d');
                    chartInstance.current = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: trends.map(t => {
                                const d = new Date(t.date);
                                return `${d.getMonth()+1}/${d.getDate()}`;
                            }),
                            datasets: [{
                                label: 'Net Points',
                                data: trends.map(t => t.net_points),
                                borderColor: '#22c55e',
                                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                fill: true,
                                tension: 0.4,
                                pointRadius: 4,
                                pointHoverRadius: 6
                            }, {
                                label: 'Completion Rate',
                                data: trends.map(t => t.completion_rate),
                                borderColor: '#3b82f6',
                                backgroundColor: 'transparent',
                                tension: 0.4,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                yAxisID: 'percentage'
                            }, {
                                label: 'Total Tasks',
                                data: trends.map(t => t.total_tasks),
                                borderColor: '#a855f7',
                                backgroundColor: 'transparent',
                                tension: 0.4,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                yAxisID: 'tasks'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'bottom',
                                    labels: {
                                        color: '#a0a0a5',
                                        font: { size: 12 },
                                        padding: 15
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    grid: { color: 'rgba(255,255,255,0.05)' },
                                    ticks: { color: '#606065', font: { size: 11 } }
                                },
                                y: {
                                    title: { display: true, text: 'Points', color: '#a0a0a5' },
                                    grid: { color: 'rgba(255,255,255,0.05)' },
                                    ticks: { color: '#606065', font: { size: 11 } }
                                },
                                percentage: {
                                    position: 'right',
                                    title: { display: true, text: 'Completion %', color: '#a0a0a5' },
                                    min: 0,
                                    max: 100,
                                    grid: { display: false },
                                    ticks: { 
                                        color: '#606065', 
                                        font: { size: 11 },
                                        callback: v => v + '%'
                                    }
                                },
                                tasks: {
                                    position: 'right',
                                    title: { display: true, text: 'Tasks', color: '#a0a0a5' },
                                    grid: { display: false },
                                    ticks: { color: '#606065', font: { size: 11 } }
                                }
                            }
                        }
                    });
                }

                return () => {
                    if (chartInstance.current) {
                        chartInstance.current.destroy();
                    }
                };
            }, [isOpen, trends]);

            if (!isOpen) return null;

            const trendDirection = patterns?.trend || 'stable';
            const trendStrength = patterns?.trend_strength || 0;
            const avgCompletion = patterns?.avg_completion_rate || 0;
            const weeklyPerf = patterns?.weekly_performance || {};

            return (
                <div className="modal-overlay" onClick={onClose}>
                    <div className="modal detail-modal animate-scale" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">📊 Productivity Trends Analysis</h2>
                            <button className="modal-close" onClick={onClose}>&times;</button>
                        </div>
                    
                        <div className="modal-body">
                            <div className="modal-section">
                                <div className="modal-section-title">📈 30-Day Trend Overview</div>
                                <div className="trend-chart-large">
                                    <canvas ref={chartRef} height="250"></canvas>
                                </div>
                    </div>

                            <div className="modal-section">
                                <div className="modal-section-title">📊 Key Metrics</div>
                                <div className="detail-grid">
                                    <div className="detail-card">
                                        <div className="detail-card-label">Trend Direction</div>
                                        <div className={`detail-card-value ${
                                            trendDirection === 'improving' ? 'positive' : 
                                            trendDirection === 'declining' ? 'negative' : 'neutral'
                                        }`}>
                                            {trendDirection === 'improving' ? '↗' : trendDirection === 'declining' ? '↘' : '→'} 
                                            {trendDirection.charAt(0).toUpperCase() + trendDirection.slice(1)}
                                        </div>
                                        <div className="detail-card-sub">
                                            Strength: {(trendStrength * 100).toFixed(1)}%
                                        </div>
                                    </div>
                                    <div className="detail-card">
                                        <div className="detail-card-label">Avg Completion Rate</div>
                                        <div className="detail-card-value positive">{avgCompletion}%</div>
                                        <div className="detail-card-sub">Last 30 days</div>
                                    </div>
                                    <div className="detail-card">
                                        <div className="detail-card-label">Total Data Points</div>
                                        <div className="detail-card-value neutral">{trends.length}</div>
                                        <div className="detail-card-sub">Days tracked</div>
                                    </div>
                                </div>
                            </div>

                            <div className="modal-section">
                                <div className="modal-section-title">📅 Weekly Performance Pattern</div>
                                <div className="weekly-performance">
                                    {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day, idx) => (
                                        <div key={day} className="day-performance">
                                            <div className="day-performance-name">{day.slice(0, 3)}</div>
                                            <div className="day-performance-value" style={{
                                                color: (weeklyPerf[day] || 0) >= 70 ? 'var(--accent-green)' :
                                                       (weeklyPerf[day] || 0) >= 50 ? 'var(--accent-yellow)' : 'var(--accent-red)'
                                            }}>
                                                {(weeklyPerf[day] || 0).toFixed(0)}%
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="recommendation-box">
                                    <div className="recommendation-title">💡 Recommendation</div>
                                    <div className="recommendation-text">
                                        {Object.keys(weeklyPerf).length > 0 ? 
                                            `Your best day is ${Object.entries(weeklyPerf).sort((a, b) => b[1] - a[1])[0][0]}. 
                                            Schedule your most important tasks on this day for optimal results.` :
                                            'Complete more tasks to unlock weekly performance insights.'}
                                    </div>
                                </div>
                            </div>

                            {patterns?.patterns && patterns.patterns.length > 0 && (
                                <div className="modal-section">
                                    <div className="modal-section-title">🔍 Detected Patterns</div>
                                    {patterns.patterns.map((pattern, idx) => (
                                        <div key={idx} className="pattern-card">
                                            <div className="pattern-card-title">
                                                {pattern.type === 'weekly_variance' && '📊 Weekly Performance Variance'}
                                                {pattern.type === 'streak' && '🔥 Active Streak'}
                                            </div>
                                            <div className="pattern-card-content">
                                                {pattern.type === 'weekly_variance' && 
                                                    `${pattern.best_day} (${pattern.difference}% higher) performs significantly better than ${pattern.worst_day}`}
                                                {pattern.type === 'streak' && 
                                                    `You're on a ${pattern.length}-day streak! Keep it going!`}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        }

        // Burnout Analysis Modal
        function BurnoutModal({ isOpen, onClose, burnoutAnalysis }) {
            if (!isOpen) return null;

            const getBurnoutColor = (level) => {
                const colors = {
                    'low': 'var(--accent-green)',
                    'moderate': 'var(--accent-yellow)',
                    'high': 'var(--accent-orange)',
                    'severe': 'var(--accent-red)'
                };
                return colors[level] || 'var(--text-muted)';
            };

            return (
                <div className="modal-overlay" onClick={onClose}>
                    <div className="modal detail-modal animate-scale" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">🔥 Burnout Risk Analysis</h2>
                            <button className="modal-close" onClick={onClose}>&times;</button>
                        </div>

                        <div className="modal-body">
                            {burnoutAnalysis && burnoutAnalysis.risk_level !== 'insufficient_data' ? (
                                <>
                                    <div className="modal-section">
                                        <div className="modal-section-title">📊 Current Risk Assessment</div>
                                        
                                        <div className="detail-grid">
                                            <div className="detail-card" style={{ gridColumn: '1 / -1' }}>
                                                <div className="detail-card-label">Current Risk Level</div>
                                                <div className="detail-card-value" style={{ 
                                                    color: getBurnoutColor(burnoutAnalysis.risk_level),
                                                    fontSize: '32px'
                                                }}>
                                                    {burnoutAnalysis.risk_level.toUpperCase()}
                                                </div>
                                                <div className="detail-card-sub" style={{ fontSize: '14px', marginTop: '8px' }}>
                                                    {burnoutAnalysis.message}
                                                </div>
                                                
                                                <div style={{ 
                                                    marginTop: '16px', 
                                                    background: 'var(--bg-elevated)', 
                                                    borderRadius: '8px',
                                                    overflow: 'hidden',
                                                    height: '24px',
                                                    position: 'relative'
                                                }}>
                                                    <div style={{
                                                        width: `${burnoutAnalysis.percentage}%`,
                                                        height: '100%',
                                                        background: `linear-gradient(90deg, ${getBurnoutColor(burnoutAnalysis.risk_level)}, ${getBurnoutColor(burnoutAnalysis.risk_level)}dd)`,
                                                        transition: 'width 1s ease',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'flex-end',
                                                        paddingRight: '12px',
                                                        fontWeight: '700',
                                                        fontSize: '12px',
                                                        fontFamily: 'JetBrains Mono, monospace'
                                                    }}>
                                                        {burnoutAnalysis.risk_score}/{burnoutAnalysis.max_score}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {burnoutAnalysis.health_metrics && (
                                            <div className="detail-grid" style={{ marginTop: '16px' }}>
                                                <div className="detail-card">
                                                    <div className="detail-card-label">Completion Rate</div>
                                                    <div className="detail-card-value positive">
                                                        {burnoutAnalysis.health_metrics.completion_rate}%
                                                    </div>
                                                </div>
                                                <div className="detail-card">
                                                    <div className="detail-card-label">Rollover Rate</div>
                                                    <div className={`detail-card-value ${
                                                        burnoutAnalysis.health_metrics.rollover_rate > 40 ? 'negative' :
                                                        burnoutAnalysis.health_metrics.rollover_rate > 25 ? 'neutral' : 'positive'
                                                    }`}>
                                                        {burnoutAnalysis.health_metrics.rollover_rate}%
                                                    </div>
                                                </div>
                                                <div className="detail-card">
                                                    <div className="detail-card-label">Weekend Work</div>
                                                    <div className={`detail-card-value ${
                                                        burnoutAnalysis.health_metrics.weekend_work_rate > 60 ? 'negative' :
                                                        burnoutAnalysis.health_metrics.weekend_work_rate > 30 ? 'neutral' : 'positive'
                                                    }`}>
                                                        {burnoutAnalysis.health_metrics.weekend_work_rate}%
                                                    </div>
                                                </div>
                                                <div className="detail-card">
                                                    <div className="detail-card-label">Days Analyzed</div>
                                                    <div className="detail-card-value neutral">
                                                        {burnoutAnalysis.health_metrics.days_analyzed}
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {burnoutAnalysis.factors && burnoutAnalysis.factors.length > 0 && (
                                        <div className="modal-section">
                                            <div className="modal-section-title">⚠️ Risk Factors Detected</div>
                                            <div className="insight-list">
                                                {burnoutAnalysis.factors.map((factor, idx) => (
                                                    <div key={idx} className={`insight-item-large ${
                                                        factor.severity === 'high' ? 'warning' : 'info'
                                                    }`}>
                                                        <div className="insight-item-title">
                                                            {factor.factor}
                                                            <span style={{ 
                                                                fontSize: '11px',
                                                                padding: '2px 8px',
                                                                borderRadius: '4px',
                                                                background: factor.severity === 'high' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(234, 179, 8, 0.2)',
                                                                color: factor.severity === 'high' ? 'var(--accent-red)' : 'var(--accent-yellow)',
                                                                fontWeight: '600',
                                                                marginLeft: 'auto'
                                                            }}>
                                                                {factor.severity.toUpperCase()}
                                                            </span>
                                                        </div>
                                                        <div className="insight-item-message">{factor.description}</div>
                                                        <div className="recommendation-box" style={{ 
                                                            marginTop: '12px',
                                                            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), transparent)'
                                                        }}>
                                                            <div className="recommendation-title" style={{ color: 'var(--accent-blue)' }}>
                                                                💡 Recommendation
                                                            </div>
                                                            <div className="recommendation-text">{factor.recommendation}</div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {burnoutAnalysis.recommendations && burnoutAnalysis.recommendations.length > 0 && (
                                        <div className="modal-section">
                                            <div className="modal-section-title">🎯 Personalized Action Plan</div>
                                            <div className="recommendation-box">
                                                {burnoutAnalysis.recommendations.map((rec, idx) => (
                                                    <div key={idx} style={{ marginBottom: '16px', paddingLeft: '12px', borderLeft: `3px solid ${
                                                        rec.priority === 'urgent' ? 'var(--accent-red)' :
                                                        rec.priority === 'high' ? 'var(--accent-orange)' :
                                                        rec.priority === 'medium' ? 'var(--accent-yellow)' : 'var(--accent-green)'
                                                    }` }}>
                                                        <div style={{ 
                                                            fontWeight: '600', 
                                                            fontSize: '13px',
                                                            marginBottom: '4px',
                                                            color: 'var(--text-primary)'
                                                        }}>
                                                            {rec.title}
                                                            <span style={{ 
                                                                fontSize: '10px',
                                                                marginLeft: '8px',
                                                                padding: '2px 6px',
                                                                borderRadius: '3px',
                                                                background: 'var(--bg-elevated)',
                                                                color: 'var(--text-muted)',
                                                                textTransform: 'uppercase'
                                                            }}>
                                                                {rec.priority}
                                                            </span>
                                                        </div>
                                                        <div className="recommendation-text" style={{ fontSize: '12px' }}>
                                                            {rec.description}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <div className="modal-section">
                                        <div className="modal-section-title">📚 Understanding Burnout</div>
                                        <div className="pattern-card">
                                            <div className="pattern-card-title">What is Burnout?</div>
                                            <div className="pattern-card-content">
                                                Burnout is a state of emotional, physical, and mental exhaustion caused by prolonged stress. 
                                                It can reduce productivity, drain energy, and leave you feeling helpless and resentful.
                                            </div>
                                        </div>
                                        <div className="pattern-card">
                                            <div className="pattern-card-title">How We Detect It</div>
                                            <div className="pattern-card-content">
                                                Our algorithm analyzes 6 key factors: declining performance, task rollover, excessive deep work, 
                                                weekend work patterns, time estimation accuracy, and recent stagnation. Each contributes to your overall risk score.
                                            </div>
                                        </div>
                                        <div className="pattern-card">
                                            <div className="pattern-card-title">Prevention is Key</div>
                                            <div className="pattern-card-content">
                                                Regular breaks, balanced workload, clear boundaries, and adequate rest are essential. 
                                                Monitor your risk level weekly and take action early when you see warning signs.
                                            </div>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div style={{ 
                                    textAlign: 'center', 
                                    padding: '60px 40px',
                                    color: 'var(--text-muted)' 
                                }}>
                                    <div style={{ fontSize: '64px', marginBottom: '20px' }}>📊</div>
                                    <div style={{ fontSize: '16px', marginBottom: '12px', color: 'var(--text-primary)' }}>
                                        Not Enough Data Yet
                                    </div>
                                    <div style={{ fontSize: '14px' }}>
                                        {burnoutAnalysis?.message || 'Complete more tasks over several days to unlock burnout risk analysis.'}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        }

        // Insights Detail Modal
        function InsightsModal({ isOpen, onClose, insights, cognitiveBalance }) {
            if (!isOpen) return null;

            return (
                <div className="modal-overlay" onClick={onClose}>
                    <div className="modal detail-modal animate-scale" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 className="modal-title">💡 Smart Productivity Insights</h2>
                            <button className="modal-close" onClick={onClose}>&times;</button>
                        </div>

                        <div className="modal-body">
                            {cognitiveBalance && (
                                <div className="modal-section">
                                    <div className="modal-section-title">🧠 Cognitive Load Balance</div>
                                    <div className="detail-grid">
                                        <div className="detail-card">
                                            <div className="detail-card-label">Balance Score</div>
                                            <div className={`detail-card-value ${
                                                cognitiveBalance.score >= 70 ? 'positive' : 
                                                cognitiveBalance.score >= 50 ? 'neutral' : 'negative'
                                            }`}>
                                                {cognitiveBalance.score}
                                            </div>
                                            <div className="detail-card-sub">
                                                {cognitiveBalance.balanced ? 'Well balanced' : 'Needs adjustment'}
                                            </div>
                                        </div>
                                    </div>
                                    {cognitiveBalance.recommendations && cognitiveBalance.recommendations.length > 0 && (
                                        <div className="recommendation-box" style={{ marginTop: '16px' }}>
                                            <div className="recommendation-title">💡 Recommendations</div>
                                            {cognitiveBalance.recommendations.map((rec, idx) => (
                                                <div key={idx} className="recommendation-text" style={{ marginBottom: '8px' }}>
                                                    • {rec.message}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="modal-section">
                                <div className="modal-section-title">🎯 Personalized Insights</div>
                    {insights.length === 0 ? (
                                    <div style={{ 
                                        textAlign: 'center', 
                                        padding: '40px',
                                        color: 'var(--text-muted)' 
                                    }}>
                                        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
                                        <div>Complete more tasks to unlock personalized insights about your productivity patterns.</div>
                        </div>
                    ) : (
                                    <div className="insight-list">
                                        {insights.map((insight, i) => (
                                            <div key={i} className={`insight-item-large ${insight.type}`}>
                                                <div className="insight-item-title">
                                                    {insight.type === 'warning' && '⚠️'}
                                                    {insight.type === 'success' && '✅'}
                                                    {insight.type === 'info' && 'ℹ️'}
                                                    {insight.title}
                            </div>
                                                <div className="insight-item-message">{insight.message}</div>
                                                {insight.metric && (
                                                    <div className="insight-item-metric">
                                                        Metric: {typeof insight.metric === 'number' ? insight.metric.toFixed(1) : insight.metric}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="modal-section">
                                <div className="modal-section-title">🎓 Understanding Your Insights</div>
                                <div className="pattern-card">
                                    <div className="pattern-card-title">How We Generate Insights</div>
                                    <div className="pattern-card-content">
                                        Our advanced algorithms analyze your task completion patterns, time estimates, cognitive load distribution, 
                                        and weekly trends to provide actionable recommendations. The more you use the app, the more accurate these insights become.
                                    </div>
                                </div>
                                <div className="pattern-card">
                                    <div className="pattern-card-title">Types of Insights</div>
                                    <div className="pattern-card-content">
                                        <strong>⚠️ Warnings:</strong> Areas needing attention<br/>
                                        <strong>ℹ️ Info:</strong> Observations and patterns<br/>
                                        <strong>✅ Success:</strong> Things you're doing great
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        function InsightsPanel({ insights, trends, achievements, dailyChallenge, motivationalQuote, patterns, cognitiveBalance, burnoutAnalysis }) {
            const [showTrendsModal, setShowTrendsModal] = useState(false);
            const [showInsightsModal, setShowInsightsModal] = useState(false);
            const [showBurnoutModal, setShowBurnoutModal] = useState(false);

            return (
                <>
                    <aside className="insights-panel">
                        {motivationalQuote && (
                            <div className="motivational-quote animate-fade-in">
                                {motivationalQuote}
                            </div>
                        )}

                        {dailyChallenge && (
                            <div className="challenge-card animate-scale">
                                <div className="challenge-title">
                                    🎯 Daily Challenge
                                </div>
                                <div className="challenge-description">
                                    {dailyChallenge.challenge}
                                </div>
                                <div className="challenge-reward">
                                    +{dailyChallenge.bonus_points} bonus points
                                </div>
                            </div>
                        )}

                        <div className="panel-title">
                            🏆 Achievements
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '8px', fontWeight: 400 }}>
                                {achievements.filter(a => a.unlocked).length}/{achievements.length}
                            </span>
                        </div>
                        <div className="achievements-scroll-container">
                            {(() => {
                                // Show all achievements: unlocked first, then locked
                                const unlockedAchievements = achievements.filter(a => a.unlocked);
                                const lockedAchievements = achievements.filter(a => !a.unlocked);
                                const allAchievements = [...unlockedAchievements, ...lockedAchievements];

                                return allAchievements.map((achievement, i) => (
                                    <div
                                        key={achievement.id}
                                        className={`achievement-badge ${achievement.unlocked ? 'unlocked' : 'locked'} animate-slide-right`}
                                        style={{ animationDelay: `${i * 0.02}s` }}
                                        title={achievement.unlocked ? `Unlocked: ${achievement.name}` : `Locked: ${achievement.description}`}
                                    >
                                        <div className="achievement-icon">
                                            {achievement.unlocked ? achievement.icon : '🔒'}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '2px', color: achievement.unlocked ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                                                {achievement.name}
                                            </div>
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                                {achievement.unlocked
                                                    ? (achievement.description_unlocked || achievement.description)
                                                    : achievement.description
                                                }
                                            </div>
                                        </div>
                                        {achievement.unlocked && (
                                            <div style={{ fontSize: '11px', color: 'var(--accent-green)', fontWeight: 600 }}>
                                                +{achievement.points}
                                            </div>
                                        )}
                                        {!achievement.unlocked && (
                                            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>
                                                {achievement.points} pts
                                            </div>
                                        )}
                                    </div>
                                ));
                            })()}
                        </div>

                        <button className="view-btn animate-fade-in" onClick={() => setShowTrendsModal(true)}>
                            <span>📊</span>
                            <span>View Trends</span>
                        </button>

                        <button className="view-btn animate-fade-in" onClick={() => setShowInsightsModal(true)}>
                            <span>💡</span>
                            <span>View Insights</span>
                        </button>

                        <button className="view-btn animate-fade-in" onClick={() => setShowBurnoutModal(true)}>
                            <span>🔥</span>
                            <span>View Burnout Analysis</span>
                        </button>
                </aside>

                    <TrendsModal
                        isOpen={showTrendsModal} 
                        onClose={() => setShowTrendsModal(false)}
                        trends={trends}
                        patterns={patterns}
                    />

                    <InsightsModal 
                        isOpen={showInsightsModal} 
                        onClose={() => setShowInsightsModal(false)}
                        insights={insights}
                        cognitiveBalance={cognitiveBalance}
                    />

                    <BurnoutModal 
                        isOpen={showBurnoutModal} 
                        onClose={() => setShowBurnoutModal(false)}
                        burnoutAnalysis={burnoutAnalysis}
                    />
                </>
            );
        }

        // Toast Notification Component
        function Toast({ message, type = 'success', onClose }) {
            useEffect(() => {
                const timer = setTimeout(onClose, 4000);
                return () => clearTimeout(timer);
            }, [onClose]);

            return (
                <div className={`toast-notification ${type}`}>
                    <div className="toast-title">
                        {type === 'achievement' && '🏆'}
                        {type === 'success' && '✅'}
                        {type === 'levelup' && '⭐'}
                        {message.title || 'Success'}
                    </div>
                    {message.description && (
                        <div className="toast-message">{message.description}</div>
                    )}
                </div>
            );
        }

        function App() {
            const [selectedDate, setSelectedDate] = useState(new Date());
            const [tasks, setTasks] = useState([]);
            const [dailyStats, setDailyStats] = useState(null);
            const [summary, setSummary] = useState({
                net_points: 0,
                completion_rate: 0,
                current_streak: 0,
                active_days: 0,
                total_tasks: 0,
                completed_tasks: 0,
                avg_tasks_per_day: 0
            });
            const [insights, setInsights] = useState([]);
            const [trends, setTrends] = useState([]);
            const [isModalOpen, setIsModalOpen] = useState(false);
            const [loading, setLoading] = useState(true);

            // Time entry modal state
            const [timeEntryModal, setTimeEntryModal] = useState({
                isOpen: false,
                taskId: null,
                taskTitle: '',
                estimatedTime: 0
            });

            // New state for gamification
            const [userStats, setUserStats] = useState({
                level: 1,
                current_xp: 0,
                xp_needed: 50,
                xp_percentage: 0,
                achievements_unlocked: 0,
                total_achievements: 0,
                total_completed: 0
            });
            const [achievements, setAchievements] = useState([]);
            const [productivityScore, setProductivityScore] = useState({
                score: 0,
                rating: 'Fair',
                color: 'yellow'
            });
            const [dailyChallenge, setDailyChallenge] = useState(null);
            const [motivationalQuote, setMotivationalQuote] = useState('');
            const [toast, setToast] = useState(null);
            const [patterns, setPatterns] = useState(null);
            const [cognitiveBalance, setCognitiveBalance] = useState(null);
            const [burnoutAnalysis, setBurnoutAnalysis] = useState(null);

            // Drag and drop state
            const [draggedItem, setDraggedItem] = useState(null);
            const [draggedOverIndex, setDraggedOverIndex] = useState(null);

            const dateStr = formatDate(selectedDate);

            // Load data
            const loadData = useCallback(async () => {
                setLoading(true);
                try {
                    const [
                        tasksData, 
                        statsData, 
                        summaryData, 
                        insightsData, 
                        trendsData,
                        userStatsData,
                        achievementsData,
                        scoreData,
                        challengeData,
                        quoteData,
                        patternsData,
                        cognitiveBalanceData,
                        burnoutData
                    ] = await Promise.all([
                        api.get(`/api/daily/${dateStr}`),
                        api.get(`/api/analytics/daily/${dateStr}`),
                        api.get('/api/analytics/summary?days=30'),
                        api.get('/api/analytics/insights?days=14'),
                        api.get('/api/analytics/trends?days=30'),
                        api.get('/api/motivation/stats'),
                        api.get('/api/motivation/achievements'),
                        api.get(`/api/analytics/productivity-score/${dateStr}?window=7`),
                        api.get(`/api/motivation/daily-challenge/${dateStr}`),
                        api.get('/api/motivation/quote'),
                        api.get('/api/analytics/patterns?days=30'),
                        api.get(`/api/analytics/cognitive-balance/${dateStr}`),
                        api.get('/api/analytics/burnout-analysis?days=14')
                    ]);

                    setTasks(tasksData);
                    setDailyStats(statsData);
                    setSummary(summaryData);
                    setInsights(insightsData);
                    setTrends(trendsData);
                    setUserStats(userStatsData);
                    setAchievements(achievementsData);
                    setProductivityScore(scoreData);
                    setDailyChallenge(challengeData);
                    setMotivationalQuote(quoteData.quote);
                    setPatterns(patternsData);
                    setCognitiveBalance(cognitiveBalanceData);
                    setBurnoutAnalysis(burnoutData);
                } catch (err) {
                    console.error('Error loading data:', err);
                }
                setLoading(false);
            }, [dateStr]);

            useEffect(() => {
                loadData();
            }, [loadData]);
            
            // Check for achievements when tasks change
            useEffect(() => {
                const checkAchievements = async () => {
                    try {
                        const result = await api.post('/api/motivation/check-achievements', {});
                        if (result.newly_unlocked && result.newly_unlocked.length > 0) {
                            result.newly_unlocked.forEach(achievement => {
                                setToast({
                                    title: `🏆 Achievement Unlocked!`,
                                    description: `${achievement.name} - ${achievement.description}`
                                });
                                setTimeout(() => {
                                    loadData(); // Reload to update achievement list
                                }, 1000);
                            });
                        }
                    } catch (err) {
                        console.error('Error checking achievements:', err);
                    }
                };
                
                if (tasks.length > 0) {
                    checkAchievements();
                }
            }, [tasks.length]);

            // Handlers
            const handlePrevDay = () => {
                setSelectedDate(d => {
                    const newDate = new Date(d);
                    newDate.setDate(newDate.getDate() - 1);
                    return newDate;
                });
            };

            const handleNextDay = () => {
                setSelectedDate(d => {
                    const newDate = new Date(d);
                    newDate.setDate(newDate.getDate() + 1);
                    return newDate;
                });
            };

            const handleToday = () => {
                setSelectedDate(new Date());
            };

            const handleAddTask = async (taskData) => {
                const { parent_daily_task_id, ...restData } = taskData;
                
                // Create the task
                const result = await api.post(`/api/daily/${dateStr}/quick-add`, restData);
                
                // If a parent was selected, set the parent relationship
                if (parent_daily_task_id && result.id) {
                    await api.put(`/api/daily/task/${result.id}/set-parent`, {
                        parent_daily_task_id: parent_daily_task_id
                    });
                }
                
                setIsModalOpen(false);
                loadData();
            };

            const handleStatusChange = async (dailyTaskId, newStatus) => {
                const task = tasks.find(t => t.id === dailyTaskId);

                // If completing a task, show time entry modal
                if (newStatus === 'completed' && task) {
                    setTimeEntryModal({
                        isOpen: true,
                        taskId: dailyTaskId,
                        taskTitle: task.title,
                        estimatedTime: task.time_estimate || 0
                    });
                } else {
                    // For other status changes, update directly
                await api.put(`/api/daily/task/${dailyTaskId}/status`, { status: newStatus });
                    loadData();
                }
            };

            const handleTimeEntryConfirm = async (actualTime) => {
                const { taskId } = timeEntryModal;

                try {
                    console.log('Completing task:', taskId, 'with time:', actualTime);

                    const response = await api.put(`/api/daily/task/${taskId}/status`, {
                        status: 'completed',
                        actual_time: actualTime
                    });

                    console.log('Task completed successfully:', response);

                    // Close modal immediately
                    setTimeEntryModal({
                        isOpen: false,
                        taskId: null,
                        taskTitle: '',
                        estimatedTime: 0
                    });

                    // Trigger confetti celebration!
                    if (window.createConfetti) {
                        window.createConfetti(window.innerWidth / 2, window.innerHeight / 2);
                    }

                    // Reload data
                    await loadData();
                } catch (error) {
                    console.error('Error completing task:', error);
                    alert('Failed to complete task. Please try again.');
                }
            };

            const handleDeleteTask = async (dailyTaskId) => {
                await api.delete(`/api/daily/task/${dailyTaskId}`);
                loadData();
            };

            const handleMakeSubtask = async (dailyTaskId, parentDailyTaskId) => {
                try {
                    await api.put(`/api/daily/task/${dailyTaskId}/set-parent`, {
                        parent_daily_task_id: parentDailyTaskId
                    });
                    loadData();
                } catch (error) {
                    console.error('Error making subtask:', error);
                    alert('Failed to convert task to subtask.');
                }
            };

            const handleMakeMainTask = async (dailyTaskId) => {
                try {
                    await api.put(`/api/daily/task/${dailyTaskId}/set-parent`, {
                        parent_daily_task_id: null
                    });
                    loadData();
                } catch (error) {
                    console.error('Error making main task:', error);
                    alert('Failed to convert to main task.');
                }
            };

            const handleRollover = async () => {
                const yesterday = new Date();
                yesterday.setDate(yesterday.getDate() - 1);

                const result = await api.post('/api/rollover', {
                    from_date: formatDate(yesterday),
                    to_date: formatDate(new Date())
                });

                if (result.rolled_over_count > 0) {
                    alert(`Rolled over ${result.rolled_over_count} tasks with penalties applied.`);
                } else {
                    alert('No tasks to roll over.');
                }
                loadData();
            };

            // Drag and drop handlers
            const handleDragStart = (e, task, index) => {
                setDraggedItem({ task, index });
                e.dataTransfer.effectAllowed = 'move';
                e.currentTarget.classList.add('is-dragging');
                e.dataTransfer.setData('text/html', e.currentTarget);
            };

            const handleDragEnd = (e) => {
                e.currentTarget.classList.remove('is-dragging');
                document.querySelectorAll('.task-item').forEach(item => {
                    item.classList.remove('drag-over');
                });
                setDraggedItem(null);
                setDraggedOverIndex(null);
            };

            const handleDragOver = (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                const taskItem = e.currentTarget;
                if (draggedItem && !taskItem.classList.contains('is-dragging')) {
                    taskItem.classList.add('drag-over');
                }
            };

            const handleDragLeave = (e) => {
                e.currentTarget.classList.remove('drag-over');
            };

            const handleDrop = async (e, targetTask, targetIndex) => {
                e.preventDefault();
                e.currentTarget.classList.remove('drag-over');

                if (!draggedItem) return;

                const sourceTask = draggedItem.task;
                const sourceIndex = draggedItem.index;

                // Regular reorder
                if (sourceIndex === targetIndex) return;

                const newTasks = [...tasks];
                const [movedTask] = newTasks.splice(sourceIndex, 1);
                newTasks.splice(targetIndex, 0, movedTask);
                setTasks(newTasks);

                setTimeout(() => {
                    const reorderedItem = document.querySelector(`[data-task-id="${movedTask.id}"]`);
                    if (reorderedItem) {
                        reorderedItem.classList.add('reorder-success');
                        setTimeout(() => reorderedItem.classList.remove('reorder-success'), 600);
                    }
                }, 100);

                const taskOrders = newTasks.map((task, idx) => ({
                    id: task.id,
                    order: idx
                }));

                try {
                    await api.put(`/api/daily/${dateStr}/reorder`, { task_orders: taskOrders });
                } catch (error) {
                    console.error('Error reordering tasks:', error);
                    // Reload to get correct order if save failed
                    loadData();
                }
            };

            const isToday = dateStr === formatDate(new Date());

            return (
                <div className="app">
                    <Sidebar 
                        summary={summary} 
                        onRollover={handleRollover}
                        userStats={userStats}
                        productivityScore={productivityScore}
                    />

                    <main className="main">
                        <header className="header">
                            <div className="date-nav">
                                <button onClick={handlePrevDay}>←</button>
                                <div className="current-date">
                                    {formatDisplayDate(selectedDate)}
                                    <span className="day">{getDayName(selectedDate)}</span>
                                </div>
                                <button onClick={handleNextDay}>→</button>
                            </div>
                            
                            {!isToday && (
                                <button className="today-btn" onClick={handleToday}>
                                    Today
                                </button>
                            )}
                        </header>

                        {dailyStats && (
                            <div className="daily-stats">
                                <div className="stat-card tasks">
                                    <div className="stat-label">Tasks</div>
                                    <div className="stat-value">{dailyStats.completed_tasks}/{dailyStats.total_tasks}</div>
                                    <div className="stat-sub">{dailyStats.pending_tasks} pending</div>
                                </div>
                                <div className="stat-card points">
                                    <div className="stat-label">Net Points</div>
                                    <div className="stat-value" style={{ color: dailyStats.net_points >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                                        {dailyStats.net_points >= 0 ? '+' : ''}{dailyStats.net_points}
                                    </div>
                                    <div className="stat-sub">-{dailyStats.total_penalties} penalties</div>
                                </div>
                                <div className="stat-card time">
                                    <div className="stat-label">Time</div>
                                    <div className="stat-value">{formatTime(dailyStats.total_actual_time || 0)}</div>
                                    <div className="stat-sub">of {formatTime(dailyStats.total_estimated_time || 0)} planned</div>
                                </div>
                                <div className="stat-card rate">
                                    <div className="stat-label">Completion</div>
                                    <div className="stat-value">{dailyStats.completion_rate}%</div>
                                    <div className="stat-sub">today's rate</div>
                                </div>
                            </div>
                        )}

                        <div className="task-section">
                            <div className="section-header">
                                <h2 className="section-title">Tasks</h2>
                                <div className="section-actions">
                                    <button className="add-task-btn" onClick={() => setIsModalOpen(true)}>
                                        + Add Task
                                    </button>
                                </div>
                            </div>

                            <div className="task-list">
                                {loading ? (
                                    <div className="loading">
                                        <div className="spinner"></div>
                                    </div>
                                ) : tasks.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="empty-state-icon">📋</div>
                                        <div>No tasks for this day</div>
                                        <div style={{ fontSize: '13px', marginTop: '8px' }}>
                                            Click "Add Task" to get started
                                        </div>
                                    </div>
                                ) : (
                                    organizeTaskHierarchy(tasks).map((task, index) => (
                                        <TaskItem
                                            key={task.id}
                                            task={task}
                                            index={index}
                                            onStatusChange={handleStatusChange}
                                            onDelete={handleDeleteTask}
                                            onDragStart={handleDragStart}
                                            onDragEnd={handleDragEnd}
                                            onDragOver={handleDragOver}
                                            onDragLeave={handleDragLeave}
                                            onDrop={handleDrop}
                                            onMakeSubtask={handleMakeSubtask}
                                            onMakeMainTask={handleMakeMainTask}
                                            allTasks={tasks}
                                        />
                                    ))
                                )}
                            </div>
                        </div>
                    </main>

                    <InsightsPanel 
                        insights={insights} 
                        trends={trends}
                        achievements={achievements}
                        dailyChallenge={dailyChallenge}
                        motivationalQuote={motivationalQuote}
                        patterns={patterns}
                        cognitiveBalance={cognitiveBalance}
                        burnoutAnalysis={burnoutAnalysis}
                    />

                    <AddTaskModal
                        isOpen={isModalOpen}
                        onClose={() => setIsModalOpen(false)}
                        onAdd={handleAddTask}
                        selectedDate={selectedDate}
                        existingTasks={tasks}
                    />

                    <TimeEntryModal
                        isOpen={timeEntryModal.isOpen}
                        onClose={() => setTimeEntryModal({ isOpen: false, taskId: null, taskTitle: '', estimatedTime: 0 })}
                        onConfirm={handleTimeEntryConfirm}
                        taskTitle={timeEntryModal.taskTitle}
                        estimatedTime={timeEntryModal.estimatedTime}
                    />

                    {toast && (
                        <Toast 
                            message={toast} 
                            type="achievement" 
                            onClose={() => setToast(null)}
                        />
                    )}
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
