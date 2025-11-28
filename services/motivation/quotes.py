"""
Motivation Quotes Engine
World-class quote system with 120+ unique motivational messages
Smart context-aware selection with anti-repetition
"""
from datetime import datetime, date, timedelta
from models.database import get_db
import random


class MotivationQuotesEngine:
    """
    World-class Motivational Quotes System
    120+ unique quotes with smart context-aware selection
    """
    
    # World-Class Motivational Quotes System - 120+ unique quotes
    QUOTES = {
        # ===== TIME-BASED QUOTES =====
        'early_morning': [
            "The world is still quiet. Use this golden hour wisely. 🌅",
            "Early risers don't just see the sunrise—they create their day. ☀️",
            "While others sleep, you're building your empire. 🏰",
            "5 AM thoughts become 5 PM results. Rise and conquer. 💪",
            "The dawn belongs to those with the courage to show up. 🌄"
        ],
        'morning': [
            "Today is a blank canvas. Paint something extraordinary. 🎨",
            "Good morning, champion! Your best work awaits. 🏆",
            "Coffee's ready, goals are set—let's make magic happen. ☕",
            "Every sunrise is an invitation to rewrite your story. 📖",
            "The morning breeze carries the energy of possibility. Let's go! 🌬️",
            "Your morning routine is your launchpad. 3, 2, 1... 🚀",
            "Start strong, finish stronger. That's the morning mindset. 💎",
            "The first step of a productive day? Opening this app. Done! ✅"
        ],
        'midday': [
            "Noon check: Are you winning? (Yes, you are!) 🎯",
            "Halfway through the day, all the way committed. Keep going! ⚡",
            "Lunch break pro tip: Refuel your body, refocus your mind. 🍃",
            "The afternoon slump is a myth for focused achievers like you. 💪",
            "Midday momentum: You're closer to your goals than this morning! 📈",
            "The second half of the day is where legends are made. 🦸",
            "Sun's at its peak, and so is your potential. Shine on! ☀️"
        ],
        'afternoon': [
            "Afternoon power hour: Make these next 60 minutes count. ⏰",
            "The 3 PM version of you is stronger than the 9 AM one. Prove it! 💪",
            "Energy dipping? One task completed and you'll feel recharged. ⚡",
            "You've come too far today to quit now. Push through! 🏃",
            "Afternoon thoughts: You're doing better than you think. 🌟",
            "Between lunch and dinner lies your window of greatness. 🪟",
            "The sun hasn't set on your potential yet. Keep building! 🌇"
        ],
        'evening': [
            "Tonight's small wins are tomorrow's big momentum. 🌙",
            "End the day proud. Finish what you started. ✨",
            "The night shift of productivity begins. You've got this! 🦉",
            "One more task before rest. Your future self applauds you. 👏",
            "Evening reflection: Today you moved closer to your dreams. 💫",
            "Stars are coming out, and so is your inner champion. ⭐",
            "Close today's chapter strong. Tomorrow's is unwritten. 📚",
            "The quiet evening hours are when magic happens. 🔮"
        ],
        
        # ===== PERFORMANCE-BASED QUOTES =====
        'winning': [
            "You're absolutely crushing it! Keep that energy! 🔥",
            "Look at you go! This is your season of success! 🏆",
            "Unstoppable force meets achievable goals. You win! 💪",
            "This momentum? It's not luck—it's your hard work paying off. 💎",
            "You're in the zone! Don't stop, don't slow down! 🚀",
            "Peak performance unlocked. The world better watch out! 👑",
            "Excellence isn't an act, it's a habit. And you're proving it! ⭐",
            "Winners don't wait for motivation—they create it. Like you! 🎯",
            "You're not just meeting expectations—you're shattering them! 💥",
            "This is what success looks like. Soak it in, then keep going! 🌊"
        ],
        'struggling': [
            "Tough day? Tomorrow you'll be stronger for it. 🌱",
            "Even the greatest climbers slip. What matters is you keep climbing. 🧗",
            "Progress isn't always visible. Trust the process. 🔄",
            "Your struggles today are training for tomorrow's triumphs. 💪",
            "One small step forward is still forward. Keep moving. 🐢",
            "Diamonds are made under pressure. You're becoming invaluable. 💎",
            "Bad days build character. Great days are coming. 🌈",
            "The only failure is giving up. You're still here—you're winning. ✨",
            "Even slow progress beats standing still. You've got this! 🚶",
            "Your persistence will outlast any obstacle. Stay strong! 🛡️"
        ],
        'recovering': [
            "Welcome back! Starting again takes real courage. 🦁",
            "Breaks happen. Comebacks are what define champions. 💪",
            "The best time to start was yesterday. The second best? Right now. ⏰",
            "Every master was once a beginner who refused to give up. 🌟",
            "Your restart button is pressed. Let's build new momentum! 🔄",
            "Yesterday's missed tasks? Forget them. Today is your day! 🌅",
            "Returning stronger is a superpower. Welcome to your new beginning. 🦸"
        ],
        
        # ===== STREAK & CONSISTENCY QUOTES =====
        'streak_building': [
            "Day by day, you're building something incredible. Keep stacking! 🧱",
            "Streaks aren't about perfection—they're about showing up. You did! ✅",
            "Consistency is your superpower. Flex it daily! 💪",
            "Another day, another link in your chain of success. 🔗",
            "Your streak is proof that small actions create big results. 📈",
            "The compound effect of daily effort is unstoppable. Like you! 🚀"
        ],
        'streak_long': [
            "Your dedication is legendary! This streak is inspiring! 🔥",
            "Day after day, you keep showing up. That's elite behavior! 👑",
            "This streak represents your discipline, focus, and grit. Respect! 💎",
            "Months of consistency have transformed you. Keep going! 🏆",
            "Your streak isn't just a number—it's a testament to who you've become. ⭐"
        ],
        
        # ===== DAY-SPECIFIC QUOTES =====
        'monday': [
            "Monday: The day winners reset and reload. Let's go! 🚀",
            "New week, new opportunities. Monday is your launchpad! 🎯",
            "Monday motivation: Make this week your masterpiece. 🎨",
            "The start of something great. Monday was made for you! 💪",
            "While others dread Monday, you embrace it. That's the difference. 👑",
            "52 Mondays a year. 52 chances to change everything. This is one! 🔥"
        ],
        'friday': [
            "Friday: Finish strong and enjoy a well-deserved weekend! 🎉",
            "End the week on a high note. You've earned it! 🏆",
            "Friday vibes: Crush these last tasks and celebrate! 🥳",
            "The weekend is calling, but first—let's close this week out right! 📞",
            "TGIF: Thank Goodness I Finished (everything on my list)! ✅"
        ],
        'weekend': [
            "Weekend warrior mode: Activated! 💪",
            "Rest is productive too. But if you're here—you're a legend! 🦸",
            "Saturday productivity hits different. Make it count! ⚡",
            "Sunday prep: Today's effort is Monday's head start. 🏃",
            "Weekend tasks? That's dedication right there! 🌟",
            "Balance is key, but a little weekend progress never hurt! ⚖️"
        ],
        
        # ===== FOCUS & DEEP WORK QUOTES =====
        'deep_focus': [
            "Deep work time: Where ordinary becomes extraordinary. 🧠",
            "Focus is a muscle. Every deep work session makes you stronger. 💪",
            "The quality of your focus determines the quality of your life. 🎯",
            "Distractions are optional. Excellence is your choice. ⭐",
            "One hour of focused work beats eight hours of scattered effort. ⏰",
            "Your brain in flow state is the most powerful tool in existence. 🔮",
            "Depth over breadth. Quality over quantity. Let's go deep! 🌊"
        ],
        
        # ===== MILESTONE & ACHIEVEMENT QUOTES =====
        'milestone': [
            "Another milestone crushed! But you're just getting started. 🏆",
            "Achievement unlocked! Your dedication is paying off. 🎮",
            "Look at how far you've come! But the best is yet to come. 📈",
            "You didn't come this far to only come this far. Keep climbing! 🧗",
            "This milestone is proof of what's possible when you commit. 💎"
        ],
        
        # ===== INSPIRATIONAL & PHILOSOPHICAL QUOTES =====
        'inspirational': [
            "The only limit is the one you accept. Reject limits today. 🚀",
            "Success is rented, and rent is due every day. Pay up! 💰",
            "Your potential is infinite. Your day is finite. Make it count. ∞",
            "What you do today echoes in eternity. Make it meaningful. 🔔",
            "Be the person who decided to go for it. That's your story. 📖",
            "Action is the foundational key to all success. Take action now! 🔑",
            "Dreams don't work unless you do. Let's get to work! 🛠️",
            "The future belongs to those who believe in their to-do list. ✨",
            "Your only competition is who you were yesterday. Beat them! 🥊",
            "Discipline is choosing between what you want now and what you want most. 🎯"
        ],
        
        # ===== HUMOR & LIGHT-HEARTED QUOTES =====
        'playful': [
            "Plot twist: You're about to have your most productive day ever. 📖",
            "Your to-do list fears you. As it should. 😤",
            "Today's forecast: 100% chance of productivity. ☁️",
            "Task management? More like task domination. 👊",
            "You + This App = Unstoppable Force of Nature. 🌪️",
            "Warning: High levels of productivity detected ahead. ⚠️",
            "Breaking news: Local hero crushes tasks, inspires millions. 📰",
            "Your keyboard is ready. Your coffee is ready. You were born ready! ☕"
        ]
    }
    
    # Quote history tracking to prevent repetition
    _recent_quotes = []
    _max_history = 15  # Remember last 15 quotes shown
    
    @staticmethod
    def get_quote(context='general'):
        """
        World-class context-aware motivational message system
        Analyzes: time of day, day of week, user performance, streak
        Prevents repetition for maximum variety
        """
        db = get_db()
        cursor = db.cursor()
        
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        today = date.today().isoformat()
        
        # Gather user context
        user_context = {
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': day_of_week >= 5,
            'is_monday': day_of_week == 0,
            'is_friday': day_of_week == 4,
            'completion_rate': 0,
            'has_tasks_today': False,
            'current_streak': 0,
            'missed_yesterday': False
        }
        
        # Get today's performance
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM daily_tasks
            WHERE scheduled_date = ?
        ''', (today,))
        
        row = cursor.fetchone()
        if row and row['total'] > 0:
            user_context['has_tasks_today'] = True
            user_context['completion_rate'] = row['completed'] / row['total']
        
        # Get streak info
        user_context['current_streak'] = MotivationQuotesEngine._calculate_streak()
        
        # Check if missed yesterday
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM daily_tasks
            WHERE scheduled_date = ? AND status = 'completed'
        ''', (yesterday,))
        yesterday_result = cursor.fetchone()
        user_context['missed_yesterday'] = (yesterday_result['count'] or 0) == 0
        
        # Determine best contexts
        contexts_to_use = MotivationQuotesEngine._determine_contexts(user_context)
        
        # Collect eligible quotes
        all_eligible_quotes = []
        for ctx in contexts_to_use:
            if ctx in MotivationQuotesEngine.QUOTES:
                all_eligible_quotes.extend(MotivationQuotesEngine.QUOTES[ctx])
        
        # Filter out recently shown
        available_quotes = [q for q in all_eligible_quotes 
                          if q not in MotivationQuotesEngine._recent_quotes]
        
        # Reset if exhausted
        if not available_quotes:
            MotivationQuotesEngine._recent_quotes = MotivationQuotesEngine._recent_quotes[-3:]
            available_quotes = [q for q in all_eligible_quotes 
                              if q not in MotivationQuotesEngine._recent_quotes]
        
        if not available_quotes:
            available_quotes = all_eligible_quotes
        
        # Select quote
        selected_quote = random.choice(available_quotes) if available_quotes else "Let's make today count! 🚀"
        
        # Track to prevent repetition
        MotivationQuotesEngine._recent_quotes.append(selected_quote)
        if len(MotivationQuotesEngine._recent_quotes) > MotivationQuotesEngine._max_history:
            MotivationQuotesEngine._recent_quotes.pop(0)
        
        return selected_quote
    
    @staticmethod
    def _calculate_streak():
        """Calculate current streak"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT DISTINCT scheduled_date
            FROM daily_tasks
            WHERE status = 'completed'
            ORDER BY scheduled_date DESC
        ''')
        
        completed_dates = [row['scheduled_date'] for row in cursor.fetchall()]
        
        if not completed_dates:
            return 0
        
        streak = 0
        check_date = date.today()
        
        if check_date.isoformat() not in completed_dates and streak == 0:
            check_date = check_date - timedelta(days=1)
        
        while check_date.isoformat() in completed_dates:
            streak += 1
            check_date = check_date - timedelta(days=1)
        
        return streak
    
    @staticmethod
    def _determine_contexts(user_context):
        """Smart algorithm to determine relevant quote categories"""
        contexts = []
        hour = user_context['hour']
        
        # Time-based primary context
        if 5 <= hour < 7:
            contexts.append('early_morning')
        elif 7 <= hour < 12:
            contexts.append('morning')
        elif 12 <= hour < 14:
            contexts.append('midday')
        elif 14 <= hour < 18:
            contexts.append('afternoon')
        elif 18 <= hour < 23:
            contexts.append('evening')
        else:
            contexts.append('evening')
        
        # Day-specific context
        if user_context['is_monday']:
            contexts.append('monday')
        elif user_context['is_friday']:
            contexts.append('friday')
        elif user_context['is_weekend']:
            contexts.append('weekend')
        
        # Performance-based context
        if user_context['has_tasks_today']:
            if user_context['completion_rate'] >= 0.7:
                contexts.append('winning')
            elif user_context['completion_rate'] < 0.3:
                contexts.append('struggling')
        
        # Recovery context
        if user_context['missed_yesterday'] and not user_context['has_tasks_today']:
            contexts.append('recovering')
        
        # Streak context
        if user_context['current_streak'] >= 7:
            contexts.append('streak_long')
        elif user_context['current_streak'] >= 2:
            contexts.append('streak_building')
        
        # Always include variety
        contexts.append('inspirational')
        
        # Occasionally add playful (20% chance)
        if random.random() < 0.2:
            contexts.append('playful')
        
        # Occasionally add deep focus during work hours (15% chance)
        if 9 <= hour <= 17 and random.random() < 0.15:
            contexts.append('deep_focus')
        
        return contexts
    
    @staticmethod
    def get_quote_count():
        """Get total number of unique quotes"""
        return sum(len(q) for q in MotivationQuotesEngine.QUOTES.values())
    
    @staticmethod
    def get_categories():
        """Get all quote categories"""
        return list(MotivationQuotesEngine.QUOTES.keys())

