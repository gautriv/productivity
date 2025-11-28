"""
World-Class Analytics Package
Advanced analytics engines for productivity insights, trend analysis, and burnout detection

Modules:
- legacy: ProductivityAnalytics - Original analytics functions (maintained for compatibility)
- trends: TrendsEngine - Predictive forecasting, momentum, patterns
- insights: InsightsEngine - AI-powered recommendations, productivity DNA
- burnout: BurnoutEngine - Early warning system, resilience scoring
"""

from .legacy import ProductivityAnalytics
from .trends import TrendsEngine
from .insights import InsightsEngine
from .burnout import BurnoutEngine


__all__ = [
    'ProductivityAnalytics',  # Legacy compatibility
    'TrendsEngine',
    'InsightsEngine', 
    'BurnoutEngine'
]

# Version info
__version__ = '2.0.0'
__description__ = 'World-class analytics for productivity tracking'

