import json
from mistralai import Mistral
import os

class Planner:
    async def generate_plan(self, goal: str, timeframe: str = "2 weeks", weak_topics: list = [], client: Mistral = None) -> dict:
        """
        Generates a detailed, structured study plan for a specific goal and timeframe.
        """
        if not client:
            return {"error": "Mistral API client or key missing"}

        prompt = f"""
Create a detailed, highly structured study plan for "{goal}" in {timeframe}.
Focus on these weak areas if provided: {", ".join(weak_topics) if weak_topics else "None"}.

Return ONLY a valid JSON object with this exact structure:
{{
  "overview": "A clear summary of what will be achieved.",
  "duration": "e.g. 4 weeks",
  "weekly_schedule": [
    {{
      "week": 1,
      "topics": ["Topic 1", "Topic 2"],
      "activities": ["Read...", "Practice...", "Build..."]
    }}
  ],
  "tips": ["Tip 1", "Tip 2"]
}}
"""

        try:
            # Using async chat completion
            response = await client.chat.complete_async(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": "You are a professional education planner. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print("Planner error:", e)
            return {
                "overview": f"I standard plan generation failed for {goal}, but I recommend starting with the basics and practicing daily.",
                "weekly_schedule": [],
                "tips": ["Try breaking down your goal into daily small tasks.", "Search for documentation online."]
            }
        except Exception as e:
            print("Planner error:", e)
            return {
                "overview": f"I standard plan generation failed for {goal}, but I recommend starting with the basics and practicing daily.",
                "weekly_schedule": [],
                "tips": ["Try breaking down your goal into daily small tasks.", "Search for documentation online."]
            }
