import os
import json
from typing import List, Dict, Any
from mistralai import Mistral
from sqlalchemy.orm import Session
from backend.database.models import User
from .planner import Planner
from .memory import AgentMemory
from .tools import AgentTools

class AgentBrain:
    def __init__(self):
        self.planner = Planner()
        self.memory = AgentMemory()
        self.tools = AgentTools()
        
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.mock_mode = os.getenv("MOCK_AGENT_MODE", "false").lower() == "true"
        
        if self.mock_mode:
            self.client = "MOCK"
            print("🚀 Agent running in MOCK MODE (No API Key Required)")
        elif not self.api_key:
            self.client = None
            print("⚠️ MISTRAL_API_KEY missing from environment")
        else:
            # Mask key for logging
            masked_key = self.api_key[:5] + "..." + self.api_key[-5:] if len(self.api_key) > 10 else "***"
            print(f"✅ Mistral client initialized with key: {masked_key}")
            self.client = Mistral(api_key=self.api_key)

    def _get_tools_definition(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_study_plan",
                    "description": "Generate a detailed study plan for a specific goal.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string", "description": "The learning goal (e.g. 'Learn React')"},
                            "timeframe": {"type": "string", "description": "Duration (e.g. '4 weeks')"},
                            "weak_topics": {"type": "array", "items": {"type": "string"}, "description": "Topics the user struggles with"}
                        },
                        "required": ["goal"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_youtube_resources",
                    "description": "Search for learning videos on YouTube.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "The topic to search for"}
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_goal_progress",
                    "description": "Update the progress of the current goal when user completes tasks or achieves milestones.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed_tasks": {"type": "integer", "description": "Number of completed tasks/milestones"},
                            "total_tasks": {"type": "integer", "description": "Total tasks/milestones defined in the plan"},
                            "status": {"type": "string", "enum": ["active", "completed", "paused"], "description": "The updated status of the goal"}
                        },
                        "required": ["completed_tasks"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "conduct_quiz",
                    "description": "Generate a short quiz or assessment to test the user's knowledge on a topic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "The subject of the quiz"},
                            "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"], "description": "Complexity level"}
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "schedule_learning_session",
                    "description": "Schedule a specific learning session or task in the user's calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the session"},
                            "start_time_str": {"type": "string", "description": "ISO format date/time (e.g. 2024-05-01T10:00:00)"},
                            "duration_minutes": {"type": "integer", "description": "Length of session in minutes"},
                            "goal_id": {"type": "integer", "description": "Optional goal ID to link to"}
                        },
                        "required": ["title", "start_time_str", "duration_minutes"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_schedule",
                    "description": "Retrieve the user's scheduled tasks and sessions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date_str": {"type": "string", "description": "Optional date to filter by (ISO format)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_notification",
                    "description": "Create a notification or alert for the user on their dashboard.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the alert"},
                            "message": {"type": "string", "description": "Detailed message"},
                            "type": {"type": "string", "enum": ["daily_task", "reminder", "system"]},
                            "scheduled_for": {"type": "string", "description": "Optional ISO format time to show this alert"}
                        },
                        "required": ["title", "message"]
                    }
                }
            }
        ]

    def _process_mock_message(self, user_message: str) -> dict:
        """
        Simulates an autonomous agent response for demonstration.
        """
        msg = user_message.lower()
        if "python" in msg:
            return {
                "type": "plan",
                "content": {
                    "plan": self.planner.generate_plan("Python", timeframe="4 weeks", client=None),
                    "videos": self.tools.search_youtube("Python for Beginners"),
                },
                "text": "I've autonomously created a Python study plan and found resources for you! (Mock Mode)"
            }
        
        return {
            "type": "chat",
            "text": f"I'm in Mock Mode! You said: '{user_message}'. To use the real AI, please add a valid MISTRAL_API_KEY to your .env and set MOCK_AGENT_MODE=false."
        }

    async def process_message_stream(self, user_message: str, user: User, db: Session, session_id: int):
        """
        Streaming version of process_message.
        Yields JSON chunks for the frontend to consume.
        """
        import asyncio
        
        if self.mock_mode:
            # Yield mock response in chunks for simulation
            resp = self._process_mock_message(user_message)
            yield json.dumps({"type": "chat_start", "role": "agent"}) + "\n"
            words = resp["text"].split()
            for i, word in enumerate(words):
                yield json.dumps({"type": "chat_chunk", "text": word + (" " if i < len(words)-1 else "")}) + "\n"
                await asyncio.sleep(0.05)
            
            if resp.get("type") == "plan":
                yield json.dumps({"type": "plan", "content": resp["content"]}) + "\n"
            return

        if not self.client:
            yield json.dumps({"type": "error", "text": "MISTRAL_API_KEY is missing."}) + "\n"
            return

        # Immediate feedback
        yield json.dumps({"type": "status", "text": "Analyzing your goal..."}) + "\n"

        # 1. Retrieve Global Context (Cross-Session Memory)
        from backend.database.models import Chat
        
        # Fetch last 20 messages across OTHER sessions (long-term memory)
        recent_chats = db.query(Chat).filter(Chat.user_id == user.id, Chat.session_id != session_id)\
            .order_by(Chat.timestamp.desc())\
            .limit(20).all()
        
        # Reverse to get chronological order (oldest to newest for LLM)
        recent_chats.reverse()
        
        # 1. Retrieve Global Context (Summary of Other Goals)
        from backend.database.models import Chat, Goal
        
        other_goals = db.query(Goal).filter(Goal.user_id == user.id, Goal.session_id != session_id).all()
        
        global_summary = ""
        if other_goals:
            global_summary = "\n--- YOUR OTHER MISSIONS (LONG-TERM MEMORY) ---\n"
            for g in other_goals:
                global_summary += f"- Mission: {g.text} | Progress: {g.progress}% | Status: {g.status}\n"
            global_summary += "--- END OF LONG-TERM MEMORY ---\n"
        else:
            global_summary = "\n(No other missions recorded in long-term memory.)\n"

        # 2. Specifically look for current session's goal
        from backend.database.models import Goal
        current_goal = db.query(Goal).filter(Goal.session_id == session_id).first()
        current_goal_info = "No specific ACTIVE mission for this chat yet."
        if current_goal:
            current_goal_info = f"CURRENT ACTIVE MISSION: '{current_goal.text}'\nProgress: {current_goal.progress}% ({current_goal.completed_tasks}/{current_goal.total_tasks} milestones completed)\nStatus: {current_goal.status}"

        # 3. Retrieve Current Session History (Focused Context)
        session_chats = db.query(Chat).filter(Chat.session_id == session_id)\
            .order_by(Chat.timestamp.desc())\
            .limit(10).all()
        session_chats.reverse()
        session_context = "\n--- CURRENT SESSION HISTORY ---\n"
        for c in session_chats:
            session_context += f"{c.role.capitalize()}: {c.message}\n"
        session_context += "--- END OF CURRENT SESSION HISTORY ---\n"

        tools = self._get_tools_definition()
        
        # Get current date/time for the agent
        from datetime import datetime
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.now().strftime("%B %d, %Y")
        
        system_msg = f"""You are a PURE AUTONOMOUS AI LEARNING AGENT.
Your core identity is to be PROACTIVE and GOAL-ORIENTED. Don't wait for instructions to be helpful.

--- CURRENT DATE AND TIME ---
Today's Date: {current_date}
Current Time: {current_datetime}
IMPORTANT: When scheduling events or referring to dates, use the year 2026, NOT 2024 or any other year.
--- END OF DATE/TIME INFO ---

{current_goal_info}

{session_context}

{global_summary}

--- AGENT BEHAVIOR GUIDELINES ---
1. ISOLATION: Focus strictly on the CURRENT ACTIVE MISSION shown above.
2. PROACTIVITY: Actively check the user's schedule using 'get_user_schedule'. 
3. SCHEDULING: If a new goal is set or a milestone reached, use 'schedule_learning_session' to book time in their calendar.
4. ALERTS: Use 'create_notification' for daily tasks, reminders, or encouraging messages.
5. ASSESSMENT: Regularly offer to 'conduct_quiz'. If the user's progress is stagnant, proactively ask about their status or if they need resources.
6. AUTONOMY: Don't just respond; lead the user. Use your tools whenever it helps the user stay on track.

Be comprehensive, motivating, and highly organized. 
Update progress using 'update_goal_progress' whenever the user completes a task.
"""

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_message}
        ]

        try:
            # Mistral chat.stream_async returns an async iterator
            stream = await self.client.chat.stream_async(
                model="mistral-large-latest",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            full_text = ""
            tool_calls_collected = []
            
            yield json.dumps({"type": "chat_start", "role": "agent"}) + "\n"

            async for chunk in stream:
                delta = chunk.data.choices[0].delta
                
                # Handle text chunks
                if delta.content:
                    full_text += delta.content
                    yield json.dumps({"type": "chat_chunk", "text": delta.content}) + "\n"
                
                # Handle tool call chunks
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        if len(tool_calls_collected) <= tc_delta.index:
                            tool_calls_collected.append({
                                "id": tc_delta.id,
                                "function": {
                                    "name": tc_delta.function.name,
                                    "arguments": tc_delta.function.arguments or ""
                                }
                            })
                        else:
                            if tc_delta.function.arguments:
                                tool_calls_collected[tc_delta.index]["function"]["arguments"] += tc_delta.function.arguments

            if tool_calls_collected:
                assistant_msg = {
                    "role": "assistant",
                    "content": full_text or None,
                    "tool_calls": tool_calls_collected
                }
                messages.append(assistant_msg)
                
                # Parallelize tool execution
                tool_tasks = []
                for tool_call in tool_calls_collected:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    yield json.dumps({"type": "status", "text": f"Running tool: {function_name}..."}) + "\n"
                    
                    if function_name == "generate_study_plan":
                        task = self.planner.generate_plan(
                            goal=function_args.get("goal"),
                            timeframe=function_args.get("timeframe", "2 weeks"),
                            weak_topics=function_args.get("weak_topics", []),
                            client=self.client
                        )
                    elif function_name == "search_youtube_resources":
                        task = self.tools.search_youtube(function_args.get("topic"))
                    elif function_name == "search_web_resources":
                        task = self.tools.search_web_resources(function_args.get("topic"))
                    elif function_name == "update_goal_progress":
                        task = self.tools.update_goal_progress(
                            session_id=session_id,
                            completed_tasks=function_args.get("completed_tasks"),
                            total_tasks=function_args.get("total_tasks"),
                            status=function_args.get("status"),
                            db=db
                        )
                    elif function_name == "retrieve_current_plan":
                        task = self.tools.retrieve_current_plan(
                            session_id=session_id,
                            db=db
                        )
                    elif function_name == "conduct_quiz":
                        task = self.tools.conduct_quiz(
                            topic=function_args.get("topic"),
                            difficulty=function_args.get("difficulty", "beginner")
                        )
                    elif function_name == "set_reminder":
                        task = self.tools.set_reminder(
                            task=function_args.get("task"),
                            time=function_args.get("time")
                        )
                    elif function_name == "schedule_learning_session":
                        task = self.tools.schedule_learning_session(
                            title=function_args.get("title"),
                            start_time_str=function_args.get("start_time_str"),
                            duration_minutes=function_args.get("duration_minutes"),
                            goal_id=function_args.get("goal_id"),
                            db=db
                        )
                    elif function_name == "get_user_schedule":
                        task = self.tools.get_user_schedule(
                            date_str=function_args.get("date_str"),
                            db=db
                        )
                    elif function_name == "create_notification":
                        task = self.tools.create_notification(
                            title=function_args.get("title"),
                            message=function_args.get("message"),
                            type=function_args.get("type", "reminder"),
                            scheduled_for=function_args.get("scheduled_for"),
                            db=db
                        )
                    else:
                        continue
                    
                    tool_tasks.append((tool_call, function_name, task))

                # Execute all tasks in parallel
                results = await asyncio.gather(*[t[2] for t in tool_tasks])
                
                for (tool_call, function_name, _), result in zip(tool_tasks, results):
                    # Yield result immediately to UI
                    if function_name == "generate_study_plan":
                        yield json.dumps({"type": "plan", "content": result}) + "\n"
                        # Explicitly save roadmap to memory
                        roadmap_text = f"Study Plan/Roadmap: {result.get('overview', '')}\nSchedule: {json.dumps(result.get('weekly_schedule', []))}"
                        self.memory.add_memory(user.id, roadmap_text, {"type": "roadmap", "goal": result.get('overview', '')})
                    elif function_name in ["search_youtube_resources", "search_web_resources"]:
                        key = "videos" if "youtube" in function_name else "web"
                        yield json.dumps({"type": "resources", "content": {key: result}}) + "\n"

                    messages.append({
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result),
                        "tool_call_id": tool_call["id"]
                    })

                # Final follow up
                yield json.dumps({"type": "status", "text": "Wrapping up response..."}) + "\n"
                
                follow_up_stream = await self.client.chat.stream_async(
                    model="mistral-large-latest",
                    messages=messages
                )
                
                async for chunk in follow_up_stream:
                    delta = chunk.data.choices[0].delta
                    if delta.content:
                        full_text += delta.content
                        yield json.dumps({"type": "chat_chunk", "text": delta.content}) + "\n"

            yield json.dumps({"type": "chat_end", "full_text": full_text}) + "\n"

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in Mistral streaming: {error_msg}")
            yield json.dumps({"type": "error", "text": f"Error communicating with Mistral: {error_msg}"}) + "\n"

    def process_message(self, user_message: str, user: User, db: Session, session_id: int) -> dict:
        
        return {"text": "Sync process_message is deprecated. Please use the streaming version."}
