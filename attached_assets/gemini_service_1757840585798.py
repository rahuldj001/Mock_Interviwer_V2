import json
import logging
import os
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel

class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))
        self.model = "gemini-2.5-flash"
        
    def generate_interview_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual interview question"""
        try:
            system_prompt = """You are an experienced Excel technical interviewer. Generate a thoughtful Excel question based on the context provided. 

The question should:
- Be specific and practical
- Test real Excel knowledge
- Be appropriate for the candidate's experience level
- Include follow-up potential
- Focus on one main concept

Respond with JSON in this format:
{
    "question": "The main question text",
    "category": "category name",
    "difficulty": "Beginner/Intermediate/Advanced",
    "expected_topics": ["topic1", "topic2"],
    "follow_up_hints": ["hint1", "hint2"]
}"""
            
            user_prompt = f"""
Context:
- Candidate experience: {context.get('experience_level', 'Unknown')}
- Questions asked so far: {context.get('questions_count', 0)}
- Previous topics covered: {context.get('previous_topics', [])}
- Current interview phase: {context.get('phase', 'main')}

Generate an appropriate Excel question for this context.
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
        """Evaluate candidate's answer"""
        try:
            system_prompt = """You are an expert Excel interviewer evaluating a candidate's response.

Provide a detailed evaluation with:
- Numerical score (0-10)
- Specific feedback
- Strengths identified
- Areas for improvement
- Technical accuracy assessment

Respond with JSON in this format:
{
    "score": 7,
    "feedback": "Detailed feedback text",
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

Evaluate this response comprehensively.
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
        """Generate contextual follow-up question or comment"""
        try:
            if not evaluation.get('follow_up_needed', False):
                return None
                
            system_prompt = """You are an Excel interviewer providing follow-up. Based on the candidate's response and evaluation, generate an appropriate follow-up.

This could be:
- A clarifying question
- A deeper dive into the topic
- A related scenario
- Positive acknowledgment with expansion
- A gentle correction with guidance

Keep it conversational and encouraging. Limit to 2-3 sentences."""
            
            user_prompt = f"""
Original Question: {question}
Candidate's Answer: {answer}
Evaluation Score: {evaluation.get('score', 0)}/10
Feedback: {evaluation.get('feedback', '')}
Areas for improvement: {evaluation.get('improvements', [])}

Generate an appropriate follow-up response.
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
            system_prompt = """You are an expert Excel assessment specialist creating a comprehensive interview report.

Analyze the complete interview and provide:
- Overall score (0-100)
- Key strengths (3-5 items)
- Areas for improvement (3-5 items)
- Specific recommendations (3-5 items)
- Skills demonstrated
- Detailed summary

Be constructive, specific, and actionable in your feedback.

Respond with JSON in this format:
{
    "overall_score": 75,
    "strengths": ["strength1", "strength2", "strength3"],
    "areas_for_improvement": ["area1", "area2", "area3"],
    "recommendations": ["rec1", "rec2", "rec3"],
    "skills_demonstrated": ["skill1", "skill2", "skill3"],
    "detailed_feedback": "Comprehensive paragraph summary",
    "hiring_recommendation": "Strong Hire/Hire/No Hire",
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

Generate a comprehensive final assessment report.
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
            system_prompt = """You are a professional and friendly Excel interviewer. Create a warm, encouraging welcome message that:
- Welcomes the candidate by name
- Explains the interview process briefly
- Sets expectations
- Encourages the candidate
- Maintains professionalism

Keep it conversational and limit to 3-4 sentences."""
            
            user_prompt = f"""
Create a welcome message for:
- Candidate Name: {candidate_name}
- Experience Level: {experience_level}
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7
                )
            )
            
            return response.text or f"Hello {candidate_name}! Welcome to your Excel skills assessment. I'll be asking you a series of questions to evaluate your proficiency. Please feel free to explain your reasoning and ask for clarification if needed. Let's begin!"
            
        except Exception as e:
            logging.error(f"Error generating welcome message: {e}")
            return f"Hello {candidate_name}! Welcome to your Excel skills assessment. I'll be asking you a series of questions to evaluate your proficiency. Please feel free to explain your reasoning and ask for clarification if needed. Let's begin!"
    
    def generate_closing_message(self, interview_data: Dict[str, Any]) -> str:
        """Generate interview closing message"""
        try:
            system_prompt = """You are an Excel interviewer concluding an interview. Create a professional closing message that:
- Thanks the candidate
- Acknowledges their effort
- Mentions next steps (report generation)
- Remains encouraging
- Maintains professionalism

Keep it brief and positive, 2-3 sentences."""
            
            candidate_name = interview_data.get('candidate_name', 'candidate')
            questions_answered = len(interview_data.get('responses', []))
            
            user_prompt = f"""
Create a closing message for:
- Candidate: {candidate_name}
- Questions Answered: {questions_answered}
"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(role="user", parts=[types.Part(text=user_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.6
                )
            )
            
            return response.text or f"Thank you, {candidate_name}, for completing the Excel assessment! You've answered {questions_answered} questions and demonstrated your knowledge well. I'm now generating your detailed feedback report with personalized recommendations."
            
        except Exception as e:
            logging.error(f"Error generating closing message: {e}")
            return f"Thank you for completing the Excel assessment! You've answered {len(interview_data.get('responses', []))} questions. I'm now generating your detailed feedback report."
    
    def _fallback_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback question when AI generation fails"""
        questions_count = context.get('questions_count', 0)
        experience = context.get('experience_level', 'Intermediate')
        
        fallback_questions = [
            {
                "question": "How would you use VLOOKUP to find data in a large dataset? Can you explain the syntax and when you might use it?",
                "category": "Functions",
                "difficulty": "Intermediate",
                "expected_topics": ["VLOOKUP", "syntax", "data lookup"],
                "follow_up_hints": ["INDEX-MATCH comparison", "approximate vs exact match"]
            },
            {
                "question": "Describe how you would create a pivot table and what insights it can provide for data analysis.",
                "category": "Data Analysis",
                "difficulty": "Intermediate",
                "expected_topics": ["pivot tables", "data analysis", "summarization"],
                "follow_up_hints": ["calculated fields", "filtering options"]
            },
            {
                "question": "What are some methods to remove duplicate data in Excel, and when would you use each approach?",
                "category": "Data Cleaning",
                "difficulty": "Beginner",
                "expected_topics": ["duplicates", "data cleaning", "remove duplicates tool"],
                "follow_up_hints": ["conditional formatting", "advanced filter"]
            }
        ]
        
        return fallback_questions[questions_count % len(fallback_questions)]
    
    def _fallback_evaluation(self) -> Dict[str, Any]:
        """Fallback evaluation when AI generation fails"""
        return {
            "score": 5,
            "feedback": "Your response shows understanding of the topic. Consider providing more specific details and examples.",
            "strengths": ["Shows basic understanding"],
            "improvements": ["Provide more specific examples", "Explain reasoning in detail"],
            "technical_accuracy": "Medium",
            "knowledge_depth": "Good",
            "follow_up_needed": True
        }
    
    def _fallback_report(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback report when AI generation fails"""
        avg_score = sum(e.get('score', 0) for e in interview_data.get('evaluations', [])) / max(len(interview_data.get('evaluations', [])), 1)
        
        return {
            "overall_score": int(avg_score * 10),
            "strengths": ["Participated fully in the interview", "Demonstrated willingness to learn"],
            "areas_for_improvement": ["Practice explaining Excel concepts", "Provide more detailed examples"],
            "recommendations": ["Review Excel documentation", "Practice with real datasets", "Take online Excel courses"],
            "skills_demonstrated": ["Basic Excel knowledge", "Communication skills"],
            "detailed_feedback": f"The candidate completed the interview and demonstrated foundational Excel knowledge. With focused practice on the recommended areas, they can significantly improve their proficiency.",
            "hiring_recommendation": "Hire with training" if avg_score >= 6 else "Additional assessment needed",
            "confidence_level": "Medium"
        }
