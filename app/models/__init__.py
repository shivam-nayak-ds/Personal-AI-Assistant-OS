# ✅ Import ALL models so SQLAlchemy can resolve every relationship
from .user import User
from .goal import Goal
from .task import Task
from .conversation import Conversation
from .message import Message
from .memory import Memory
from .document import Document
from .agent_run import AgentRun
from .review import Review

# ✅ user_profile.py defines: UserProfile, Notification, Routine, Schedule, Habit
# DO NOT import from notification.py / routine.py / schedule.py / habit.py separately
# — they are DUPLICATES and cause "Table already defined" error!
from .user_profile import UserProfile, Notification, Routine, Schedule, Habit

__all__ = [
    "User", "Goal", "Task", "Conversation", "Message",
    "Memory", "Document", "AgentRun", "Review",
    "UserProfile", "Notification", "Routine", "Schedule", "Habit",
]