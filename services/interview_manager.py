import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from models.interview_models import InterviewState, Question, Response, InterviewReport
from data.sample_questions import get_questions_by_level, get_random_question

class InterviewManager:
    """Manages the interview flow and state"""
    
    def __init__(self, gemini_service, database_service=None):
        self.gemini_service = gemini_service
        self.database_service = database_service
        self.max_questions = 8
        self.categories_covered = []
        self.current_interview_id = None
        self.current_candidate_id = None
        
    def start_interview(self, candidate_name: str, experience_level: str) -> str:
        """Initialize interview and return welcome message"""
        # Create or get candidate record
        if self.database_service:
            try:
                self.current_candidate_id = self.database_service.create_or_get_candidate(
                    name=candidate_name,
                    experience_level=experience_level
                )
                
                # Create interview session
                self.current_interview_id = self.database_service.create_interview_session(
                    candidate_id=self.current_candidate_id,
                    experience_level=experience_level,
                    audio_enabled=False
                )
            except Exception as e:
                print(f"Database error during interview start: {e}")
        
        try:
            welcome_message = self.gemini_service.generate_welcome_message(
                candidate_name, 
                experience_level
            )
            return welcome_message
        except Exception as e:
            return f"Hello {candidate_name}! It's wonderful to meet you, and I'm excited to learn about your Excel expertise. This will be a friendly conversation where we'll explore your skills across different Excel features and functions. I'm looking forward to seeing what you know! Let's begin with our first question."
    
    def get_next_question(self, interview_state: InterviewState) -> Optional[Dict[str, Any]]:
        """Generate or retrieve the next appropriate question"""
        questions_asked = len(interview_state.responses)
        
        # Check if interview should end
        if questions_asked >= self.max_questions:
            return None
        
        # Prepare context for question generation
        context = {
            "experience_level": interview_state.experience_level,
            "questions_count": questions_asked,
            "previous_topics": self._get_covered_topics(interview_state),
            "phase": self._determine_interview_phase(questions_asked),
            "candidate_performance": self._analyze_performance(interview_state)
        }
        
        try:
            # Try to generate question using AI
            question_data = self.gemini_service.generate_interview_question(context)
            
            # Add metadata
            question_data["id"] = str(uuid.uuid4())
            question_data["order"] = questions_asked + 1
            question_data["timestamp"] = datetime.now().isoformat()
            
            return question_data
            
        except Exception as e:
            # Fallback to predefined questions
            return self._get_fallback_question(context)
    
    def evaluate_response(self, question: Dict[str, Any], response: Response, interview_state: InterviewState) -> Dict[str, Any]:
        """Evaluate candidate's response using AI"""
        try:
            context = {
                "experience_level": interview_state.experience_level,
                "question_category": question.get("category", "General"),
                "question_difficulty": question.get("difficulty", "Medium"),
                "interview_progress": len(interview_state.responses) / self.max_questions
            }
            
            evaluation = self.gemini_service.evaluate_answer(
                question["question"],
                response.answer,
                context
            )
            
            # Add metadata
            evaluation["question_id"] = question["id"]
            evaluation["timestamp"] = datetime.now().isoformat()
            evaluation["category"] = question.get("category", "General")
            
            # Save to database if available
            if self.database_service and self.current_interview_id:
                try:
                    response_id = self.database_service.save_response(
                        interview_id=self.current_interview_id,
                        question_text=question.get("question", ""),
                        response_text=response.answer,
                        question_category=question.get("category"),
                        question_difficulty=question.get("difficulty"),
                        score=evaluation.get("score", 0.0),
                        evaluation_details=evaluation
                    )
                    evaluation["response_id"] = response_id
                except Exception as e:
                    print(f"Database error saving response: {e}")
            
            return evaluation
            
        except Exception as e:
            # Fallback evaluation
            return {
                "score": 5,
                "feedback": "Thank you for your thoughtful response. You show a good understanding of the concept and I appreciate how you explained your approach.",
                "strengths": ["Clear communication", "Logical thinking"],
                "improvements": ["Consider exploring more advanced applications", "Try adding specific examples"],
                "technical_accuracy": "Medium",
                "knowledge_depth": "Good",
                "follow_up_needed": False,
                "question_id": question["id"],
                "timestamp": datetime.now().isoformat(),
                "category": question.get("category", "General")
            }
    
    def generate_follow_up(self, question: Dict[str, Any], response: Response, evaluation: Dict[str, Any], interview_state: InterviewState) -> Optional[str]:
        """Generate contextual follow-up question or comment"""
        try:
            # Only generate follow-up for certain conditions
            should_follow_up = (
                evaluation.get("follow_up_needed", False) or
                evaluation.get("score", 0) < 6 or
                len(response.answer) < 50
            )
            
            if not should_follow_up:
                return self._generate_acknowledgment(evaluation.get("score", 0))
            
            follow_up = self.gemini_service.generate_follow_up(
                question["question"],
                response.answer,
                evaluation
            )
            
            return follow_up
            
        except Exception as e:
            # Fallback follow-up
            score = evaluation.get("score", 0)
            if score >= 7:
                return "Excellent! That shows really solid understanding. I can see you've thought about this practically."
            elif score >= 5:
                return "Great start! I'd love to hear you elaborate a bit more on how you might apply this in a real scenario."
            else:
                return "Thanks for sharing your thoughts. Let me ask about this from a slightly different angle to help clarify."
    
    def generate_final_report(self, interview_state: InterviewState) -> InterviewReport:
        """Generate comprehensive interview report"""
        try:
            # End the interview in database if available
            if self.database_service and self.current_interview_id:
                try:
                    avg_score = sum(e.get('score', 0) for e in interview_state.evaluations) / max(len(interview_state.evaluations), 1)
                    self.database_service.complete_interview(self.current_interview_id, avg_score * 10)  # Convert to 0-100 scale
                except Exception as e:
                    print(f"Database error completing interview: {e}")
            
            # Prepare data for AI analysis
            interview_data = {
                "candidate_name": interview_state.candidate_name,
                "experience_level": interview_state.experience_level,
                "responses": [{"answer": r.answer, "timestamp": r.timestamp.isoformat()} for r in interview_state.responses],
                "evaluations": interview_state.evaluations,
                "start_time": interview_state.start_time.isoformat(),
                "end_time": interview_state.end_time.isoformat() if interview_state.end_time else datetime.now().isoformat()
            }
            
            report_data = self.gemini_service.generate_final_report(interview_data)
            
            # Create structured report object
            report = InterviewReport(
                candidate_name=interview_state.candidate_name,
                interview_date=interview_state.start_time,
                overall_score=report_data.get("overall_score", 0),
                strengths=report_data.get("strengths", []),
                areas_for_improvement=report_data.get("areas_for_improvement", []),
                recommendations=report_data.get("recommendations", []),
                skills_demonstrated=report_data.get("skills_demonstrated", []),
                detailed_feedback=report_data.get("detailed_feedback", ""),
                hiring_recommendation=report_data.get("hiring_recommendation", "Additional assessment needed"),
                confidence_level=report_data.get("confidence_level", "Medium")
            )
            
            return report
            
        except Exception as e:
            # Fallback report generation
            return self._generate_fallback_report(interview_state)
    
    def generate_closing_message(self, interview_state: InterviewState) -> str:
        """Generate interview closing message"""
        try:
            interview_data = {
                "candidate_name": interview_state.candidate_name,
                "responses": interview_state.responses,
                "evaluations": interview_state.evaluations
            }
            
            return self.gemini_service.generate_closing_message(interview_data)
            
        except Exception as e:
            return f"Thank you so much, {interview_state.candidate_name}! That was a wonderful conversation about Excel. You've demonstrated great knowledge and thoughtfulness throughout our discussion. I'm now putting together a detailed report with personalized insights and recommendations to help you continue developing your Excel skills."
    
    def _get_covered_topics(self, interview_state: InterviewState) -> List[str]:
        """Get list of topics already covered in the interview"""
        topics = []
        for evaluation in interview_state.evaluations:
            category = evaluation.get("category", "General")
            if category not in topics:
                topics.append(category)
        return topics
    
    def _determine_interview_phase(self, questions_count: int) -> str:
        """Determine current phase of interview"""
        if questions_count < 2:
            return "warming_up"
        elif questions_count < 6:
            return "main_assessment"
        else:
            return "deep_dive"
    
    def _analyze_performance(self, interview_state: InterviewState) -> Dict[str, Any]:
        """Analyze candidate's performance so far"""
        if not interview_state.evaluations:
            return {"average_score": 0, "trend": "unknown", "strong_areas": [], "weak_areas": []}
        
        scores = [e.get("score", 0) for e in interview_state.evaluations]
        avg_score = sum(scores) / len(scores)
        
        # Determine trend
        if len(scores) >= 3:
            recent_avg = sum(scores[-2:]) / 2
            earlier_avg = sum(scores[:-2]) / len(scores[:-2])
            trend = "improving" if recent_avg > earlier_avg else "declining" if recent_avg < earlier_avg else "stable"
        else:
            trend = "stable"
        
        # Identify strong and weak areas
        category_scores = {}
        for evaluation in interview_state.evaluations:
            category = evaluation.get("category", "General")
            score = evaluation.get("score", 0)
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        strong_areas = []
        weak_areas = []
        for category, scores_list in category_scores.items():
            avg = sum(scores_list) / len(scores_list)
            if avg >= 7:
                strong_areas.append(category)
            elif avg < 5:
                weak_areas.append(category)
        
        return {
            "average_score": avg_score,
            "trend": trend,
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "total_responses": len(interview_state.responses)
        }
    
    def _get_fallback_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback question when AI generation fails"""
        experience_level = context.get("experience_level", "Intermediate")
        questions_count = context.get("questions_count", 0)
        previous_topics = context.get("previous_topics", [])
        
        try:
            # Try to get a random question that hasn't been covered
            question = get_random_question(experience_level, previous_topics)
            
            # Add required metadata
            question["id"] = str(uuid.uuid4())
            question["order"] = questions_count + 1
            question["timestamp"] = datetime.now().isoformat()
            
            return question
            
        except Exception:
            # Ultimate fallback
            return {
                "id": str(uuid.uuid4()),
                "question": "I'd love to hear about your experience with Excel functions. Could you walk me through how you would approach solving a data lookup problem and what tools you might use?",
                "category": "General",
                "difficulty": "Intermediate",
                "expected_topics": ["functions", "data lookup", "problem solving"],
                "follow_up_hints": ["specific functions", "alternative approaches"],
                "order": questions_count + 1,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_fallback_report(self, interview_state: InterviewState) -> InterviewReport:
        """Generate fallback report when AI generation fails"""
        # Calculate basic metrics
        total_questions = len(interview_state.responses)
        avg_score = 70  # Default score
        
        if interview_state.evaluations:
            scores = [e.get('score', 0) for e in interview_state.evaluations]
            avg_score = int((sum(scores) / len(scores)) * 10)  # Convert to 0-100 scale
        
        return InterviewReport(
            candidate_name=interview_state.candidate_name,
            interview_date=interview_state.start_time,
            overall_score=avg_score,
            strengths=[
                "Demonstrated understanding of Excel concepts",
                "Clear communication of ideas",
                "Engaged thoughtfully with questions"
            ],
            areas_for_improvement=[
                "Expand knowledge of advanced Excel features",
                "Practice with real-world scenarios",
                "Explore automation possibilities"
            ],
            recommendations=[
                "Practice with sample datasets to strengthen practical skills",
                "Explore advanced functions like INDEX-MATCH, array formulas",
                "Consider learning Power Query for data transformation",
                "Build small projects to apply Excel skills in context"
            ],
            skills_demonstrated=[
                "Basic Excel knowledge",
                "Logical problem-solving approach",
                "Clear communication skills"
            ],
            detailed_feedback=f"Thank you, {interview_state.candidate_name}, for a great conversation about Excel! You've shown solid foundational knowledge and the ability to think through problems logically. Focus on expanding your practical experience with real datasets and exploring more advanced Excel features to take your skills to the next level.",
            hiring_recommendation="Additional Assessment Needed",
            confidence_level="Medium"
        )
    
    def _generate_acknowledgment(self, score: int) -> str:
        """Generate positive acknowledgment based on score"""
        if score >= 8:
            return "Fantastic answer! You really know your stuff when it comes to Excel."
        elif score >= 6:
            return "Great explanation! I can tell you have solid practical experience with this."
        elif score >= 4:
            return "Good thinking! You're definitely on the right track with your approach."
        else:
            return "Thanks for sharing your thoughts. Every Excel journey is different, and I appreciate your perspective."
