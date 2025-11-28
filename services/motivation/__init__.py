"""
Motivation Package
World-class gamification, challenges, quotes, achievement, and points systems

Modules:
- challenges: DailyChallengeEngine - 45+ unique daily challenges
- quotes: MotivationQuotesEngine - 120+ context-aware motivational quotes
- gamification: GamificationEngine - Level, XP, ranks, and progression
- achievements: AchievementEngine - 45+ achievements with tiers and progress
- points: PointsEngine - Net points with combos, multipliers, and bonuses
"""

from .challenges import DailyChallengeEngine
from .quotes import MotivationQuotesEngine
from .gamification import GamificationEngine
from .achievements import AchievementEngine
from .points import PointsEngine


class MotivationEngine:
    """
    Legacy compatibility class - delegates to modular components
    
    For new code, use:
    - GamificationEngine for Level/XP
    - MotivationQuotesEngine for quotes
    - DailyChallengeEngine for challenges
    - AchievementEngine for achievements
    """
    
    # Re-export for backward compatibility
    ACHIEVEMENTS = AchievementEngine.ACHIEVEMENTS
    QUOTES = MotivationQuotesEngine.QUOTES
    
    @staticmethod
    def check_achievements(user_id='default'):
        """Check and unlock achievements - delegates to AchievementEngine"""
        return AchievementEngine.check_achievements(user_id)
    
    @staticmethod
    def calculate_current_streak():
        """Calculate current streak - delegates to GamificationEngine"""
        return GamificationEngine._calculate_current_streak()
    
    @staticmethod
    def calculate_level_and_xp(total_points):
        """Calculate level and XP - delegates to GamificationEngine"""
        progress = GamificationEngine.get_xp_progress(total_points)
        return {
            'level': progress['level'],
            'current_xp': progress['current_xp'],
            'xp_needed': progress['xp_needed'],
            'xp_percentage': progress['percentage']
        }
    
    @staticmethod
    def get_motivational_message(context='general'):
        """Get motivational quote - delegates to MotivationQuotesEngine"""
        return MotivationQuotesEngine.get_quote(context)
    
    @staticmethod
    def get_daily_challenge(date_str):
        """Get daily challenge - delegates to DailyChallengeEngine"""
        challenge = DailyChallengeEngine.get_daily_challenge(date_str)
        completion_status = DailyChallengeEngine.check_challenge_completion(date_str)
        
        challenge['completed'] = completion_status['completed']
        challenge['just_completed'] = completion_status.get('just_completed', False)
        
        # Format for backward compatibility
        return {
            'id': challenge['id'],
            'challenge': challenge['description'],
            'title': challenge['title'],
            'description': challenge['description'],
            'icon': challenge['icon'],
            'type': challenge['category'],
            'category': challenge['category'],
            'difficulty': challenge['difficulty'],
            'difficulty_color': challenge['difficulty_color'],
            'bonus_points': challenge['bonus_points'],
            'requirement': challenge['requirement'],
            'completed': challenge['completed'],
            'just_completed': challenge.get('just_completed', False),
            'tags': challenge['tags']
        }
    
    @staticmethod
    def get_user_stats():
        """Get comprehensive user stats - delegates to GamificationEngine"""
        return GamificationEngine.get_user_stats()


__all__ = [
    'DailyChallengeEngine',
    'MotivationQuotesEngine', 
    'GamificationEngine',
    'AchievementEngine',
    'PointsEngine',
    'MotivationEngine'  # Legacy compatibility
]

# Version info
__version__ = '3.0.0'
__description__ = 'World-class motivation system for productivity tracking'

