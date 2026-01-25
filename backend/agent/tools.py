from typing import List, Dict

class AgentTools:
    async def search_youtube(self, topic: str) -> List[Dict]:
        """
        Search for high-quality YouTube videos and courses for a given learning topic.
        """
        topic_lower = topic.lower()
        if "ml" in topic_lower or "machine learning" in topic_lower:
            return [
                {"title": "Machine Learning for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=GwIo3gDZCVQ", "channel": "FreeCodeCamp"},
                {"title": "Deep Learning with Andrew Ng", "url": "https://www.youtube.com/watch?v=CS4cs9xVecg", "channel": "DeepLearningAI"},
                {"title": "StatQuest: Machine Learning Fundamentals", "url": "https://www.youtube.com/watch?v=q607niLWZP4", "channel": "StatQuest"},
            ]
        if "python" in topic_lower:
            return [
                {"title": "Python for Beginners - Full Course", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "channel": "Programming with Mosh"},
                {"title": "Python Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "channel": "FreeCodeCamp"},
            ]
            
        # Generic fallback
        query = topic.replace(" ", "+")
        return [
            {"title": f"Search YouTube for {topic}", "url": f"https://www.youtube.com/results?search_query={query}", "channel": "YouTube Search"},
        ]

    async def search_web_resources(self, topic: str) -> List[Dict]:
        """
        Search for official documentation, tutorials, and high-quality web articles for a topic.
        """
        topic_lower = topic.lower()
        if "ml" in topic_lower or "machine learning" in topic_lower:
            return [
                {"title": "Scikit-Learn Documentation", "url": "https://scikit-learn.org/stable/getting_started.html", "site": "scikit-learn.org"},
                {"title": "TensorFlow Tutorials", "url": "https://www.tensorflow.org/tutorials", "site": "tensorflow.org"},
                {"title": "Machine Learning Roadmap 2024", "url": "https://www.simplilearn.com/tutorials/machine-learning-tutorial/how-to-become-a-machine-learning-engineer", "site": "Simplilearn"},
            ]
        if "python" in topic_lower:
            return [
                {"title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/index.html", "site": "python.org"},
                {"title": "W3Schools Python Tutorial", "url": "https://www.w3schools.com/python/", "site": "w3schools.com"},
            ]
            
        # Generic fallback
        query = topic.replace(" ", "+")
        return [
            {"title": f"Search Google for {topic}", "url": f"https://www.google.com/search?q={topic}+documentation", "site": "Google Search"},
        ]

    async def find_offline_tutors(self, subject: str, city: str) -> List[Dict]:
        """
        Find local offline tutors or coaching centers for a specific subject in a city.
        """
        return [
            {"name": "Excellent Coaching Center", "address": f"123 Main St, {city}", "rating": 4.5},
            {"name": "Best Tutors", "address": f"456 Market Rd, {city}", "rating": 4.8},
        ]

    async def update_goal_progress(self, session_id: int, completed_tasks: int, total_tasks: int = None, status: str = None, db=None) -> Dict:
        """
        Update the progress of a goal associated with a specific chat session.
        """
        from backend.database.models import Goal
        if not db:
            return {"error": "No database session provided"}
            
        goal = db.query(Goal).filter(Goal.session_id == session_id).first()
        if not goal:
            return {"error": "Goal not found for this session"}
        
        if completed_tasks is not None:
            goal.completed_tasks = completed_tasks
        if total_tasks is not None:
            goal.total_tasks = total_tasks
        if status is not None:
            goal.status = status
            
        if goal.total_tasks > 0:
            goal.progress = min(100, int((goal.completed_tasks / goal.total_tasks) * 100))
        else:
            goal.progress = 0
            
        db.commit()
        return {
            "success": True, 
            "new_progress": goal.progress, 
            "completed_tasks": goal.completed_tasks, 
            "total_tasks": goal.total_tasks,
            "status": goal.status
        }

    async def retrieve_current_plan(self, session_id: int, db=None) -> Dict:
        """
        Retrieve the full structured study plan for the current session.
        """
        from backend.database.models import Chat
        if not db:
            return {"error": "No database session provided"}
            
        plan_msg = db.query(Chat).filter(Chat.session_id == session_id, Chat.msg_type == "plan")\
            .order_by(Chat.timestamp.desc()).first()
            
        if not plan_msg or not plan_msg.content:
            return {"error": "No plan found for this session"}
            
        try:
            return json.loads(plan_msg.content)
        except:
            return {"error": "Plan content is not valid JSON", "raw": plan_msg.content}

    async def conduct_quiz(self, topic: str, difficulty: str = "beginner") -> Dict:
        """
        Generate a short quiz/assessment for the user on a specific topic.
        """
        return {
            "status": "ready",
            "instruction": f"Please generate 3-5 {difficulty} questions about {topic}. Provide the answers only after the user responds.",
            "topic": topic
        }

    async def schedule_learning_session(self, title: str, start_time_str: str, duration_minutes: int, goal_id: int = None, db=None) -> Dict:
        """
        Schedule a specific learning session or task in the user's calendar.
        start_time_str should be in ISO format (e.g., 2024-05-01T10:00:00)
        """
        from backend.database.models import CalendarEvent, User
        from datetime import datetime, timedelta
        if not db:
            return {"error": "No database session provided"}
        
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            user_id = db.query(User).first().id 
            
            new_event = CalendarEvent(
                user_id=user_id,
                goal_id=goal_id,
                title=title,
                start_time=start_time,
                end_time=end_time
            )
            db.add(new_event)
            db.commit()
            return {"success": True, "event_id": new_event.id, "scheduled": title, "at": start_time_str}
        except Exception as e:
            return {"error": str(e)}

    async def get_user_schedule(self, date_str: str = None, db=None) -> List[Dict]:
        """
        Retrieve the user's scheduled tasks and sessions for a specific date.
        """
        from backend.database.models import CalendarEvent
        if not db:
            return {"error": "No database session provided"}
        
        query = db.query(CalendarEvent)
        # Add date filtering if provided
        events = query.all()
        return [
            {
                "id": e.id,
                "title": e.title,
                "start": e.start_time.isoformat(),
                "end": e.end_time.isoformat(),
                "completed": e.is_completed
            } for e in events
        ]

    async def create_notification(self, title: str, message: str, type: str = "reminder", scheduled_for: str = None, db=None) -> Dict:
        """
        Create a notification or alert for the user that will appear in the dashboard.
        """
        from backend.database.models import Notification, User
        from datetime import datetime
        if not db:
            return {"error": "No database session provided"}
        
        user_id = db.query(User).first().id # Placeholder
        
        sched_time = datetime.fromisoformat(scheduled_for) if scheduled_for else datetime.now(timezone.utc)
        
        new_note = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            scheduled_for=sched_time
        )
        db.add(new_note)
        db.commit()
        return {"success": True, "notification_id": new_note.id}

