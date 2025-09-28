import json
import logging
import os
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types

class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))
        self.model = "gemini-2.5-flash"
        
    def generate_interview_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual interview question"""
        try:
            system_prompt = """You are a warm, experienced Excel technical interviewer conducting a friendly conversation. Generate a thoughtful Excel question that feels natural and engaging.

The question should:
- Be conversational and welcoming in tone
- Test practical Excel knowledge relevant to real work scenarios
- Be appropriate for the candidate's experience level
- Build naturally on previous topics when possible
- Feel like part of a flowing discussion, not an interrogation

Respond with JSON in this format:
{
    "question": "The main question text in a conversational tone",
    "category": "category name", 
    "difficulty": "Beginner/Intermediate/Advanced",
    "expected_topics": ["topic1", "topic2"],
    "follow_up_hints": ["hint1", "hint2"]
}"""
            
            user_prompt = f"""
Context for this interview conversation:
- Candidate experience: {context.get('experience_level', 'Unknown')}
- Questions asked so far: {context.get('questions_count', 0)}
- Previous topics covered: {context.get('previous_topics', [])}
- Current interview phase: {context.get('phase', 'main')}
- Candidate performance trend: {context.get('candidate_performance', {}).get('trend', 'stable')}

Generate an appropriate Excel question that continues our conversation naturally. Make it sound like you're having a friendly discussion about Excel skills, not conducting a formal test.
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._fallback_question(context)
                
        except Exception as e:
            logging.error(f"Error generating question: {e}")
            return self._fallback_question(context)
    
    def evaluate_answer(self, question: str, answer: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate candidate's answer with encouraging feedback"""
        try:
            system_prompt = """You are a supportive Excel interviewer providing constructive evaluation. Your tone should be encouraging and professional, like a mentor helping someone improve.

Provide a detailed evaluation that:
- Acknowledges what the candidate did well first
- Gives specific, actionable feedback
- Maintains an encouraging tone throughout
- Focuses on learning and improvement opportunities

Respond with JSON in this format:
{
    "score": 7,
    "feedback": "Encouraging and detailed feedback text that starts with positives",
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "technical_accuracy": "High/Medium/Low",
    "knowledge_depth": "Surface/Good/Deep",
    "follow_up_needed": true/false
}"""
            
            user_prompt = f"""
Question: {question}
Candidate's Answer: {answer}
Experience Level: {context.get('experience_level', 'Unknown')}

Evaluate this response with an encouraging, mentor-like tone. Start with what they did well, then provide constructive guidance for improvement.
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._fallback_evaluation()
                
        except Exception as e:
            logging.error(f"Error evaluating answer: {e}")
            return self._fallback_evaluation()
    
    def generate_follow_up(self, question: str, answer: str, evaluation: Dict[str, Any]) -> Optional[str]:
        """Generate warm, conversational follow-up"""
        try:
            if not evaluation.get('follow_up_needed', False):
                return self._generate_acknowledgment(evaluation.get('score', 0))
                
            system_prompt = """You are a friendly Excel interviewer continuing a natural conversation. Generate a warm, encouraging follow-up that feels like genuine dialogue.

This could be:
- A positive acknowledgment with a gentle expansion
- An encouraging clarifying question
- A supportive deeper exploration of the topic
- A natural transition with additional context

Keep it conversational, supportive, and limit to 2-3 sentences. Make the candidate feel comfortable and encouraged to elaborate."""
            
            user_prompt = f"""
Original Question: {question}
Candidate's Answer: {answer}
Evaluation Score: {evaluation.get('score', 0)}/10
Feedback: {evaluation.get('feedback', '')}

Generate a warm, encouraging follow-up that continues our conversation naturally. Make the candidate feel comfortable while gently exploring their knowledge further.
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.6
                )
            )
            
            return response.text if response.text else None
            
        except Exception as e:
            logging.error(f"Error generating follow-up: {e}")
            return None
    
    def generate_final_report(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive interview report"""
        try:
            system_prompt = """You are an expert Excel assessment specialist creating a comprehensive, encouraging interview report. Your tone should be professional yet supportive, focusing on growth and development.

Analyze the complete interview and provide:
- Overall score (0-100) that reflects true performance
- Key strengths (3-5 items) - be specific about what they demonstrated well
- Areas for improvement (3-5 items) - frame as opportunities for growth
- Actionable recommendations (3-5 items) - specific steps they can take
- Skills demonstrated - concrete abilities they showed
- Encouraging but honest detailed summary

Be constructive, specific, and growth-oriented in your feedback.

Respond with JSON in this format:
{
    "overall_score": 75,
    "strengths": ["strength1", "strength2", "strength3"],
    "areas_for_improvement": ["area1", "area2", "area3"],
    "recommendations": ["rec1", "rec2", "rec3"],
    "skills_demonstrated": ["skill1", "skill2", "skill3"],
    "detailed_feedback": "Comprehensive paragraph summary with encouraging tone",
    "hiring_recommendation": "Strong Hire/Hire/No Hire/Additional Assessment Needed",
    "confidence_level": "High/Medium/Low"
}"""
            
            # Prepare interview summary
            responses_summary = []
            for i, (response, evaluation) in enumerate(zip(
                interview_data.get('responses', []),
                interview_data.get('evaluations', [])
            )):
                responses_summary.append({
                    "question_num": i + 1,
                    "score": evaluation.get('score', 0),
                    "feedback": evaluation.get('feedback', ''),
                    "answer_length": len(response.get('answer', '')),
                    "technical_accuracy": evaluation.get('technical_accuracy', 'Unknown')
                })
            
            user_prompt = f"""
Interview Summary:
- Candidate: {interview_data.get('candidate_name', 'Unknown')}
- Experience Level: {interview_data.get('experience_level', 'Unknown')}
- Total Questions: {len(interview_data.get('responses', []))}
- Average Score: {sum(e.get('score', 0) for e in interview_data.get('evaluations', [])) / max(len(interview_data.get('evaluations', [])), 1):.1f}

Individual Response Analysis:
{json.dumps(responses_summary, indent=2)}

Generate a comprehensive final assessment report that is encouraging yet honest. Focus on their growth potential and provide specific guidance for improvement.
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.4
                )
            )
            
            if response.text:
                return json.loads(response.text)
            else:
                return self._fallback_report(interview_data)
                
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            return self._fallback_report(interview_data)
    
    def generate_welcome_message(self, candidate_name: str, experience_level: str) -> str:
        """Generate personalized welcome message"""
        try:
            system_prompt = """You are a warm, professional Excel interviewer starting a friendly conversation. Create a welcoming message that:
- Makes the candidate feel comfortable and at ease
- Sounds genuinely interested in their Excel journey
- Explains the process in a reassuring way
- Sets a collaborative, supportive tone
- Shows enthusiasm for learning about their skills

Keep it natural and conversational, like you're genuinely excited to chat with them about Excel. Limit to 3-4 sentences."""
            
            user_prompt = f"""
Create a warm, welcoming message for:
- Candidate Name: {candidate_name}
- Experience Level: {experience_level}

Make them feel comfortable and excited about showcasing their Excel knowledge in our conversation.
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7
                )
            )
            
            return response.text or f"Hello {candidate_name}! It's wonderful to meet you. I'm excited to learn about your Excel expertise and have a great conversation about your skills. This will be relaxed and collaborative - just think of it as a friendly chat about Excel. I'm looking forward to seeing what you know!"
            
        except Exception as e:
            logging.error(f"Error generating welcome message: {e}")
            return f"Hello {candidate_name}! It's wonderful to meet you. I'm excited to learn about your Excel expertise and have a great conversation about your skills. This will be relaxed and collaborative - just think of it as a friendly chat about Excel. I'm looking forward to seeing what you know!"
    
    def generate_closing_message(self, interview_data: Dict[str, Any]) -> str:
        """Generate interview closing message"""
        try:
            system_prompt = """You are concluding a friendly Excel interview conversation. Create a warm closing message that:
- Thanks the candidate genuinely for their time and effort
- Acknowledges their participation positively
- Sounds encouraging and supportive
- Mentions the report generation naturally
- Maintains the warm, professional tone from throughout

Keep it brief, genuine, and positive - like wrapping up a good conversation with a colleague."""
            
            candidate_name = interview_data.get('candidate_name', 'candidate')
            questions_answered = len(interview_data.get('responses', []))
            
            user_prompt = f"""
Create a warm closing message for:
- Candidate: {candidate_name}
- Questions Answered: {questions_answered}

Thank them genuinely and let them know about the report in a natural, encouraging way.
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.6
                )
            )
            
            return response.text or f"Thank you so much, {candidate_name}! That was a fantastic conversation about Excel. You've shown great knowledge and thoughtfulness in your responses. I'm now putting together a detailed report with personalized insights and recommendations to help you continue growing your Excel skills."
            
        except Exception as e:
            logging.error(f"Error generating closing message: {e}")
            return f"Thank you so much for that great conversation about Excel! You've shown wonderful knowledge and I'm now putting together your detailed feedback report."
    
    def _fallback_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback question when AI generation fails"""
        questions_count = context.get('questions_count', 0)
        experience = context.get('experience_level', 'Intermediate')
        
        fallback_questions = [
            {
                "question": "I'd love to hear about how you would use VLOOKUP to find data in a large dataset. Could you walk me through the syntax and share when you might choose it over other lookup methods?",
                "category": "Functions",
                "difficulty": "Intermediate",
                "expected_topics": ["VLOOKUP", "syntax", "data lookup"],
                "follow_up_hints": ["INDEX-MATCH comparison", "approximate vs exact match"]
            },
            {
                "question": "That's great! Now I'm curious about your experience with PivotTables. Could you describe how you would create one to analyze sales data and what insights it might reveal?",
                "category": "Data Analysis",
                "difficulty": "Intermediate", 
                "expected_topics": ["PivotTables", "data analysis", "summarization"],
                "follow_up_hints": ["calculated fields", "grouping data"]
            }
        ]
        
        return fallback_questions[min(questions_count, len(fallback_questions) - 1)]
    
    def _fallback_evaluation(self) -> Dict[str, Any]:
        """Fallback evaluation when AI generation fails"""
        return {
            "score": 6,
            "feedback": "Thank you for sharing your approach! You demonstrate a good understanding of the concept. I'd love to hear you elaborate a bit more on the practical applications and any specific considerations you might have.",
            "strengths": ["Clear explanation", "Good foundational knowledge"],
            "improvements": ["Consider adding specific examples", "Explore advanced applications"],
            "technical_accuracy": "Medium",
            "knowledge_depth": "Good",
            "follow_up_needed": True
        }
    
    def _fallback_report(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback report when AI generation fails"""
        return {
            "overall_score": 70,
            "strengths": ["Demonstrated understanding of Excel concepts", "Clear communication", "Willingness to engage"],
            "areas_for_improvement": ["Expand practical examples", "Explore advanced features", "Practice complex scenarios"],
            "recommendations": ["Practice with real datasets", "Explore advanced functions", "Build sample projects"],
            "skills_demonstrated": ["Basic Excel knowledge", "Logical thinking", "Communication skills"],
            "detailed_feedback": f"Thank you {interview_data.get('candidate_name', '')} for a great conversation! You've shown solid Excel fundamentals and clear thinking. Focus on practicing with real-world scenarios to strengthen your practical application skills.",
            "hiring_recommendation": "Additional Assessment Needed",
            "confidence_level": "Medium"
        }
    
    def _generate_acknowledgment(self, score: int) -> str:
        """Generate positive acknowledgment based on score"""
        if score >= 8:
            return "Excellent answer! That shows really strong understanding of the concept."
        elif score >= 6:
            return "Great explanation! I can see you have a solid grasp of that topic."
        elif score >= 4:
            return "Thank you for that response. You're on the right track with your thinking."
        else:
            return "I appreciate you sharing your thoughts. Let's explore this a bit more together."
