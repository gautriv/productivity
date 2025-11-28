/**
 * Sidebar Component
 */

import { formatDisplayDate, formatDate } from '../utils/helpers.js';

const { useState } = React;

export function Sidebar({ summary, onRollover, userStats, productivityScore }) {
    return (
        <aside className="sidebar">
            <div className="logo">
                <div className="logo-icon">PT</div>
                <span className="logo-text">Productivity</span>
            </div>

            <div className="summary-card">
                <div className="summary-label">Net Points</div>
                <div className={`summary-value ${summary.net_points >= 0 ? 'positive' : 'negative'}`}>
                    {summary.net_points}
                </div>
                <div className="streak-badge active" title="Current streak">
                    🔥 {summary.current_streak || 0} day streak
                </div>
            </div>

            <div className="summary-card">
                <div className="summary-label">Total Tasks</div>
                <div className="summary-value neutral">
                    {userStats.total_tasks || 0}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px' }}>
                    {userStats.completed_tasks || 0} completed
                </div>
            </div>

            <button
                className="btn-secondary"
                style={{ width: '100%', padding: '10px' }}
                onClick={onRollover}
            >
                Process Rollover →
            </button>
        </aside>
    );
}
