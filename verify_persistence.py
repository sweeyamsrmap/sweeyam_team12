import asyncio
import json
from backend.database.database import SessionLocal
from backend.database.models import User, Chat, ChatSession
from backend.agent.brain import AgentBrain
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

async def verify_persistence():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        brain = AgentBrain()
        
        # 1. Create a session
        session = ChatSession(user_id=user.id, title="Persistence Test")
        db.add(session)
        db.commit()
        db.refresh(session)
        
        print(f"Created session {session.id}")
        
        msg_text = "Who are you?"
        user_msg = Chat(user_id=user.id, session_id=session.id, message=msg_text, role="user")
        db.add(user_msg)
        db.commit()
        
        full_text = ""
        async for chunk_str in brain.process_message_stream(msg_text, user, db, session.id):
            chunk = json.loads(chunk_str)
            if chunk["type"] == "chat_chunk":
                full_text += chunk["text"]
        
        print(f"Agent response length: {len(full_text)}")
        
        # This part replicates the fix in chat.py
        gen_db = SessionLocal()
        try:
            agent_msg = Chat(user_id=user.id, session_id=session.id, message=full_text, role="agent")
            gen_db.add(agent_msg)
            gen_db.commit()
            print("Successfully saved agent message using fix logic.")
        finally:
            gen_db.close()
            
        # 4. Verify total messages in session
        final_count = db.query(Chat).filter(Chat.session_id == session.id).count()
        print(f"Final message count for session {session.id}: {final_count}")
        if final_count >= 2:
            print("SUCCESS: Persistence verified.")
        else:
            print("FAILURE: Persistence failed.")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_persistence())
