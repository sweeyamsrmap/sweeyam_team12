import chromadb
import time
import hashlib
import os
import json
from chromadb import Documents, EmbeddingFunction, Embeddings
from sqlalchemy.orm import Session
from backend.database.models import Goal, Plan, Preference

class MistralEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str):
        from mistralai.client import MistralClient
        self.client = MistralClient(api_key=api_key)

    def __call__(self, input: Documents) -> Embeddings:
        response = self.client.embeddings(
            model="mistral-embed",
            input=input
        )
        return [data.embedding for data in response.data]

class AgentMemory:
    def __init__(self):
        pass
        
    def add_memory(self, user_id: int, text: str, metadata: dict = None):
        pass

    def retrieve_memory(self, user_id: int, query: str, n_results: int = 5):
        return []

    def get_user_goals(self, db: Session, user_id: int):
        return db.query(Goal).filter(Goal.user_id == user_id).all()

    def get_user_preferences(self, db: Session, user_id: int):
        return db.query(Preference).filter(Preference.user_id == user_id).first()
