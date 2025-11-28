        const { useState, useEffect, useRef, useCallback } = React;

        // API helpers
        const api = {
            async get(url) {
                const res = await fetch(url);
                return res.json();
            },
            async post(url, data) {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return res.json();
            },
            async put(url, data) {
                const res = await fetch(url, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return res.json();
            },
            async delete(url) {
                const res = await fetch(url, { method: 'DELETE' });
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

        // Components
        function Sidebar({ summary, onRollover, userStats, productivityScore }) {
            return (
                <aside className="sidebar">
                    <div className="logo">
                        <div className="logo-icon">PT</div>
                        <span className="logo-text">Productivity</span>
                    </div>

                    <div className="summary-card level-card animate-fade-in">
                        <div className="summary-label">Level & Rank</div>
                        <div className="level-header">
                            <div className="level-badge" style={{ 
                                background: userStats.rank_color ? 
                                    `linear-gradient(135deg, ${userStats.rank_color}40, ${userStats.rank_color}20)` : 
                                    'linear-gradient(135deg, var(--accent-purple), var(--accent-blue))'
                            }}>
                                <span className="rank-icon">{userStats.rank_icon || '⭐'}</span>
                                <span>Level {userStats.level}</span>
                            </div>
                        </div>
                        <div className="rank-title" style={{ 
                            color: userStats.rank_color || 'var(--accent-purple)',
                            fontSize: '14px',
                            fontWeight: 700,
                            marginTop: '8px',
                            marginBottom: '4px'
                        }}>
                            {userStats.rank || 'Novice'}
                        </div>
                        <div className="tier-badge" style={{
                            fontSize: '10px',
                            textTransform: 'uppercase',
                            letterSpacing: '1px',
                            color: 'var(--text-muted)',
                            marginBottom: '12px'
                        }}>
                            {userStats.tier || 'beginner'} tier
                        </div>
                        <div className="xp-bar">
                            <div 
                                className="xp-progress" 
                                style={{ width: `${userStats.xp_percentage || 0}%` }}
                            />
                        </div>
                        <div style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            fontSize: '11px', 
                            color: 'var(--text-muted)', 
                            marginTop: '6px' 
                        }}>
                            <span>{userStats.current_xp || 0} XP</span>
                            <span>{userStats.xp_needed || 50} XP needed</span>
                        </div>
                        {userStats.streak_multiplier > 1 && (
                            <div className="streak-multiplier" style={{
                                marginTop: '10px',
                                padding: '6px 10px',
                                background: 'rgba(34, 197, 94, 0.15)',
                                borderRadius: '8px',
                                fontSize: '11px',
                                color: 'var(--accent-green)',
                                fontWeight: 600,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px'
                            }}>
                                <span>🔥</span>
                                <span>+{userStats.streak_bonus_percentage || 0}% XP Streak Bonus!</span>
                            </div>
                        )}
                    </div>

                    <div className="summary-card points-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
                        <div className="summary-label">
                            <span>Net Points</span>
                            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>(30d)</span>
                        </div>
                        <div className={`summary-value ${summary.net_points >= 0 ? 'positive' : 'negative'}`}>
                            {summary.net_points >= 0 ? '+' : ''}{summary.net_points}
                        </div>
                        <div className="points-breakdown">
                            <div className="point-stat">
                                <span style={{ color: 'var(--accent-green)' }}>+{summary.points_earned || 0}</span>
                                <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>earned</span>
                            </div>
                            <div className="point-stat">
                                <span style={{ color: 'var(--accent-red)' }}>-{summary.penalties || 0}</span>
                                <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>penalties</span>
                            </div>
                        </div>
                        <div className={`streak-badge ${summary.current_streak > 0 ? 'active' : ''}`}>
                            🔥 {summary.current_streak} day streak
                            {summary.current_streak >= 3 && (
                                <span className="streak-multiplier">+{Math.min(50, summary.current_streak * 5)}% bonus</span>
                            )}
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

                    <div className="summary-card achievements-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
                        <div className="summary-label">Achievements</div>
                        <div className="achievement-progress-header">
                            <div className="summary-value neutral">
                                {userStats.achievements_unlocked || 0}/{userStats.total_achievements || 45}
                            </div>
                            <div className="achievement-tier-badges">
                                <span className="tier-badge diamond" title="Diamond">💎</span>
                                <span className="tier-badge platinum" title="Platinum">💠</span>
                                <span className="tier-badge gold" title="Gold">🥇</span>
                            </div>
                        </div>
                        <div className="achievement-progress-bar">
                            <div 
                                className="achievement-progress-fill" 
                                style={{ 
                                    width: `${((userStats.achievements_unlocked || 0) / (userStats.total_achievements || 45)) * 100}%` 
                                }}
                            />
                        </div>
                        <div className="achievement-points-display">
                            <span style={{ fontSize: '11px', color: 'var(--accent-yellow)' }}>
                                🏆 {userStats.achievement_points || 0} AP
                            </span>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                                {userStats.total_completed || 0} tasks done
                            </span>
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

        function TaskItem({ task, onStatusChange, onDelete, index }) {
            const handleCheck = () => {
                const newStatus = task.status === 'completed' ? 'pending' : 'completed';
                onStatusChange(task.id, newStatus);
            };

            const netPoints = task.status === 'completed' 
                ? task.points - task.penalty_points 
                : -task.penalty_points;

            return (
                <div 
                    className={`task-item ${task.status} animate-fade-in`}
                    style={{ animationDelay: `${index * 0.05}s` }}
                >
                    <div 
                        className={`task-checkbox ${task.status === 'completed' ? 'completed' : ''}`}
                        onClick={handleCheck}
                    />
                    
                    <div className="task-content">
                        <div className="task-title">{task.title}</div>
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
                        </div>
                    </div>

                    <div className={`task-points ${netPoints >= 0 ? 'positive' : 'negative'}`}>
                        {netPoints >= 0 ? '+' : ''}{netPoints} pts
                    </div>

                    <div className="task-actions">
                        <button className="task-action-btn delete" onClick={() => onDelete(task.id)}>
                            ×
                        </button>
                    </div>
                </div>
            );
        }

        function AddTaskModal({ isOpen, onClose, onAdd, selectedDate }) {
            const [title, setTitle] = useState('');
            const [description, setDescription] = useState('');
            const [complexity, setComplexity] = useState(3);
            const [cognitiveLoad, setCognitiveLoad] = useState('active_work');
            const [timeEstimate, setTimeEstimate] = useState(30);

            const timeOptions = [15, 30, 60, 120, 240, 480];

            const handleSubmit = () => {
                if (!title.trim()) return;
                
                onAdd({
                    title: title.trim(),
                    description,
                    complexity,
                    cognitive_load: cognitiveLoad,
                    time_estimate: timeEstimate
                });

                // Reset form
                setTitle('');
                setDescription('');
                setComplexity(3);
                setCognitiveLoad('active_work');
                setTimeEstimate(30);
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

        function InsightsPanel({ insights, trends, achievements, dailyChallenge, motivationalQuote, patterns, cognitiveBalance }) {
            const [showTrendsModal, setShowTrendsModal] = useState(false);
            const [showInsightsModal, setShowInsightsModal] = useState(false);

            useEffect(() => {
                if (chartRef.current && trends.length > 0) {
                    if (chartInstance.current) {
                        chartInstance.current.destroy();
                    }

                    const ctx = chartRef.current.getContext('2d');
                    chartInstance.current = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: trends.slice(-14).map(t => {
                                const d = new Date(t.date);
                                return `${d.getMonth()+1}/${d.getDate()}`;
                            }),
                            datasets: [{
                                label: 'Net Points',
                                data: trends.slice(-14).map(t => t.net_points),
                                borderColor: '#22c55e',
                                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                fill: true,
                                tension: 0.3,
                                pointRadius: 3,
                                pointHoverRadius: 5
                            }, {
                                label: 'Completion %',
                                data: trends.slice(-14).map(t => t.completion_rate),
                                borderColor: '#3b82f6',
                                backgroundColor: 'transparent',
                                tension: 0.3,
                                pointRadius: 3,
                                pointHoverRadius: 5,
                                yAxisID: 'percentage'
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
                                        font: { size: 10 }
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    grid: { color: 'rgba(255,255,255,0.05)' },
                                    ticks: { color: '#606065', font: { size: 10 } }
                                },
                                y: {
                                    grid: { color: 'rgba(255,255,255,0.05)' },
                                    ticks: { color: '#606065', font: { size: 10 } }
                                },
                                percentage: {
                                    position: 'right',
                                    min: 0,
                                    max: 100,
                                    grid: { display: false },
                                    ticks: { 
                                        color: '#606065', 
                                        font: { size: 10 },
                                        callback: v => v + '%'
                                    }
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
            }, [trends]);

            return (
                <>
                    <aside className="insights-panel">
                        {motivationalQuote && (
                            <div className="motivational-quote animate-fade-in">
                                {motivationalQuote}
                            </div>
                        )}

                        {dailyChallenge && (
                            <div className={`challenge-card animate-scale ${dailyChallenge.completed ? 'completed' : ''}`}>
                                <div className="challenge-header">
                                    <div className="challenge-title">
                                        <span className="challenge-icon">{dailyChallenge.icon || '🎯'}</span>
                                        <span>{dailyChallenge.title || 'Daily Challenge'}</span>
                                    </div>
                                    <div className={`challenge-difficulty ${dailyChallenge.difficulty || 'medium'}`}>
                                        {dailyChallenge.difficulty || 'medium'}
                                    </div>
                                </div>
                                <div className="challenge-description">
                                    {dailyChallenge.description || dailyChallenge.challenge}
                                </div>
                                <div className="challenge-footer">
                                    <div className="challenge-reward">
                                        <span className="reward-icon">💎</span>
                                        <span>+{dailyChallenge.bonus_points} bonus</span>
                                    </div>
                                    {dailyChallenge.completed ? (
                                        <div className="challenge-status completed">
                                            <span>✅</span>
                                            <span>Completed!</span>
                                        </div>
                                    ) : (
                                        <div className="challenge-status pending">
                                            <span>🎯</span>
                                            <span>In Progress</span>
                                        </div>
                                    )}
                                </div>
                                {dailyChallenge.category && (
                                    <div className="challenge-category">
                                        {dailyChallenge.category.replace('_', ' ')}
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="panel-title">🏆 Achievements</div>
                        
                        {/* Recently Unlocked Achievements */}
                        {achievements.filter(a => a.unlocked).length > 0 && (
                            <div style={{ marginBottom: '16px' }}>
                                <div style={{ fontSize: '11px', color: 'var(--accent-green)', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <span>✅</span> UNLOCKED
                                </div>
                                <div className="achievements-container">
                                    {achievements.filter(a => a.unlocked).slice(0, 3).map((achievement, i) => (
                                        <div 
                                            key={achievement.id} 
                                            className={`achievement-badge unlocked tier-${achievement.tier || 'bronze'} animate-slide-right`}
                                            style={{ animationDelay: `${i * 0.05}s` }}
                                            title={`Achieved: ${achievement.name}`}
                                        >
                                            <div className="achievement-icon-wrapper">
                                                <div className="achievement-icon">{achievement.icon}</div>
                                                <div className="achievement-checkmark">✓</div>
                                            </div>
                                            <div className="achievement-content" style={{ flex: 1 }}>
                                                <div className="achievement-header">
                                                    <span className="achievement-name" style={{ fontSize: '13px', fontWeight: 600 }}>
                                                        {achievement.name}
                                                    </span>
                                                </div>
                                                <div style={{ fontSize: '11px', color: 'var(--accent-green)', marginTop: '2px' }}>
                                                    ✨ Achieved!
                                                </div>
                                            </div>
                                            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--accent-green)', textAlign: 'right' }}>
                                                +{achievement.points}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        {/* Up Next - Achievements to unlock */}
                        <div style={{ marginBottom: '20px' }}>
                            <div style={{ fontSize: '11px', color: 'var(--accent-yellow)', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <span>🎯</span> UP NEXT
                            </div>
                            <div className="achievements-container">
                                {achievements
                                    .filter(a => !a.unlocked && a.progress && a.progress.percentage > 0)
                                    .sort((a, b) => (b.progress?.percentage || 0) - (a.progress?.percentage || 0))
                                    .slice(0, 3)
                                    .map((achievement, i) => (
                                        <div 
                                            key={achievement.id} 
                                            className={`achievement-badge locked tier-${achievement.tier || 'bronze'} animate-slide-right`}
                                            style={{ animationDelay: `${i * 0.05}s` }}
                                            title={achievement.description}
                                        >
                                            <div className="achievement-icon-wrapper">
                                                <div className="achievement-icon" style={{ opacity: 0.6 }}>{achievement.icon}</div>
                                                <div className="achievement-tier-icon">{achievement.tier_icon || '🥉'}</div>
                                            </div>
                                            <div className="achievement-content" style={{ flex: 1 }}>
                                                <div className="achievement-header">
                                                    <span className="achievement-name" style={{ fontSize: '13px', fontWeight: 600 }}>
                                                        {achievement.name}
                                                    </span>
                                                    <span style={{ 
                                                        fontSize: '9px', 
                                                        textTransform: 'uppercase',
                                                        padding: '2px 6px',
                                                        borderRadius: '3px',
                                                        background: 'var(--bg-secondary)',
                                                        color: 'var(--text-muted)'
                                                    }}>
                                                        {achievement.tier || 'bronze'}
                                                    </span>
                                                </div>
                                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                                                    {achievement.description}
                                                </div>
                                                {achievement.progress && (
                                                    <div className="achievement-progress-mini">
                                                        <div 
                                                            className="achievement-progress-fill-mini" 
                                                            style={{ width: `${achievement.progress.percentage}%` }}
                                                        />
                                                        <span className="achievement-progress-text">
                                                            {achievement.progress.current}/{achievement.progress.target}
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'right' }}>
                                                {achievement.points}
                                                <span style={{ fontSize: '9px', display: 'block', fontWeight: 400 }}>to earn</span>
                                            </div>
                                        </div>
                                    ))}
                            </div>
                        </div>

                        <button className="view-btn animate-fade-in" onClick={() => setShowTrendsModal(true)}>
                            <span>📊</span>
                            <span>View Trends</span>
                        </button>

                        <button className="view-btn animate-fade-in" onClick={() => setShowInsightsModal(true)}>
                            <span>💡</span>
                            <span>View Insights</span>
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
                        cognitiveBalanceData
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
                        api.get(`/api/analytics/cognitive-balance/${dateStr}`)
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
                await api.post(`/api/daily/${dateStr}/quick-add`, taskData);
                setIsModalOpen(false);
                loadData();
            };

            const handleStatusChange = async (dailyTaskId, newStatus) => {
                await api.put(`/api/daily/task/${dailyTaskId}/status`, { status: newStatus });
                loadData();
            };

            const handleDeleteTask = async (dailyTaskId) => {
                await api.delete(`/api/daily/task/${dailyTaskId}`);
                loadData();
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
                                <button className="add-task-btn" onClick={() => setIsModalOpen(true)}>
                                    + Add Task
                                </button>
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
                                    tasks.map((task, index) => (
                                        <TaskItem
                                            key={task.id}
                                            task={task}
                                            index={index}
                                            onStatusChange={handleStatusChange}
                                            onDelete={handleDeleteTask}
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
                    />

                    <AddTaskModal
                        isOpen={isModalOpen}
                        onClose={() => setIsModalOpen(false)}
                        onAdd={handleAddTask}
                        selectedDate={selectedDate}
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
