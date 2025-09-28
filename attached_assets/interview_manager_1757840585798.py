import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from models.interview_models import InterviewState, Question, Response, InterviewReport
from data.sample_questions import SAMPLE_QUESTIONS, QUESTION_CATEGORIES

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
                    audio_enabled=False  # Will update this based on user choice
                )
            except Exception as e:
                print(f"Database error during interview start: {e}")
                # Continue without database if there's an error
        
        try:
            welcome_message = self.gemini_service.generate_welcome_message(
                candidate_name, 
                experience_level
            )
            return welcome_message
        except Exception as e:
            return f"Hello {candidate_name}! Welcome to your Excel skills assessment. I'll be asking you a series of questions to evaluate your proficiency across different Excel features and functions. Please feel free to explain your reasoning and ask for clarification if needed. Let's begin with our first question!"
    
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
            
            # Save to database if available
            if self.database_service and self.current_interview_id:
                try:
                    # Save response
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
            
            
            evaluation["timestamp"] = datetime.now().isoformat()
            evaluation["category"] = question.get("category", "General")
            
            return evaluation
            
        except Exception as e:
            # Fallback evaluation
            return {
                "score": 5,
                "feedback": "Thank you for your response. Your answer shows understanding of the topic.",
                "strengths": ["Provided a clear response"],
                "improvements": ["Consider adding more specific examples"],
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
                len(response.answer) < 50  # Very short answers might need clarification
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
                return "Great answer! That shows good understanding of the concept."
            elif score >= 5:
                return "Good response. Can you elaborate a bit more on the practical application?"
            else:
                return "I see. Let me ask a related question to help clarify this concept."
    
    def generate_final_report(self, interview_state: InterviewState) -> InterviewReport:
        """Generate comprehensive interview report"""
        try:
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
            return f"Thank you, {interview_state.candidate_name}, for completing the Excel assessment! You've demonstrated your knowledge across {len(interview_state.responses)} questions. I'm now generating your detailed feedback report with personalized recommendations for improving your Excel skills."
    
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
        for category, scores in category_scores.items():
            avg = sum(scores) / len(scores)
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
        questions_count = context.get("questions_count", 0)
        experience_level = context.get("experience_level", "Intermediate")
        covered_topics = context.get("previous_topics", [])
        
        # Select appropriate category
        available_categories = [cat for cat in QUESTION_CATEGORIES if cat not in covered_topics]
        if not available_categories:
            available_categories = QUESTION_CATEGORIES
        
        category = available_categories[questions_count % len(available_categories)]
        
        # Get questions for this category and experience level
        suitable_questions = [
            q for q in SAMPLE_QUESTIONS 
            if q["category"] == category and 
            (experience_level.lower() in q["difficulty"].lower() or q["difficulty"] == "All")
        ]
        
        if not suitable_questions:
            suitable_questions = [q for q in SAMPLE_QUESTIONS if q["category"] == category]
        
        if not suitable_questions:
            suitable_questions = SAMPLE_QUESTIONS
        
        # Select question
        question = suitable_questions[questions_count % len(suitable_questions)]
        
        # Add metadata
        question_copy = question.copy()
        question_copy["id"] = str(uuid.uuid4())
        question_copy["order"] = questions_count + 1
        question_copy["timestamp"] = datetime.now().isoformat()
        
        return question_copy
    
    def _generate_acknowledgment(self, score: int) -> Optional[str]:
        """Generate simple acknowledgment based on score"""
        if score >= 8:
            acknowledgments = [
                "Excellent answer! You clearly have strong Excel knowledge.",
                "Perfect! That's exactly the kind of detailed response I was looking for.",
                "Outstanding explanation. Your Excel expertise is evident."
            ]
        elif score >= 6:
            acknowledgments = [
                "Good response! You demonstrate solid understanding.",
                "Nice work. That shows good practical knowledge.",
                "Well done. Your answer covers the key points effectively."
            ]
        else:
            return None  # No acknowledgment for lower scores, just move on
        
        import random
        return random.choice(acknowledgments)
    
    def _generate_fallback_report(self, interview_state: InterviewState) -> InterviewReport:
        """Generate fallback report when AI generation fails"""
        scores = [e.get("score", 0) for e in interview_state.evaluations]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Analyze categories
        category_performance = {}
        for evaluation in interview_state.evaluations:
            category = evaluation.get("category", "General")
            score = evaluation.get("score", 0)
            if category not in category_performance:
                category_performance[category] = []
            category_performance[category].append(score)
        
        strengths = []
        improvements = []
        for category, scores in category_performance.items():
            avg = sum(scores) / len(scores)
            if avg >= 7:
                strengths.append(f"Strong performance in {category}")
            elif avg < 5:
                improvements.append(f"Review {category} concepts and practice")
        
        if not strengths:
            strengths = ["Completed the full interview", "Demonstrated willingness to learn"]
        
        if not improvements:
            improvements = ["Continue practicing Excel regularly", "Explore advanced features"]
        
        recommendations = [
            "Practice Excel functions with real datasets",
            "Take online Excel courses for skill development",
            "Review Excel documentation and help resources",
            "Work on explaining technical concepts clearly"
        ]
        
        return InterviewReport(
            candidate_name=interview_state.candidate_name,
            interview_date=interview_state.start_time,
            overall_score=int(avg_score * 10),
            strengths=strengths[:5],
            areas_for_improvement=improvements[:5],
            recommendations=recommendations[:5],
            skills_demonstrated=[cat for cat in category_performance.keys()],
            detailed_feedback=f"The candidate completed {len(interview_state.responses)} questions with an average score of {avg_score:.1f}/10. This demonstrates {('strong' if avg_score >= 7 else 'good' if avg_score >= 5 else 'basic')} Excel knowledge with room for continued learning and development.",
            hiring_recommendation="Strong Hire" if avg_score >= 8 else "Hire" if avg_score >= 6 else "Additional assessment recommended",
            confidence_level="High" if len(scores) >= 6 else "Medium"
        )
    
    def save_conversation_turn(self, speaker: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Save a conversation turn to the database"""
        if self.database_service and self.current_interview_id:
            try:
                self.database_service.save_conversation_turn(
                    interview_id=self.current_interview_id,
                    speaker=speaker,
                    message=message,
                    metadata=metadata or {}
                )
            except Exception as e:
                print(f"Database error saving conversation turn: {e}")
    
    def complete_interview_session(self, interview_state: InterviewState, final_report: InterviewReport):
        """Complete the interview session in the database"""
        if self.database_service and self.current_interview_id:
            try:
                # Calculate overall score from evaluations
                scores = [e.get("score", 0) for e in interview_state.evaluations]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                
                self.database_service.complete_interview(
                    interview_id=self.current_interview_id,
                    overall_score=avg_score,
                    detailed_feedback=final_report.detailed_feedback
                )
            except Exception as e:
                print(f"Database error completing interview: {e}")
    
    def update_audio_preference(self, audio_enabled: bool):
        """Update the audio preference for the current interview"""
        if self.database_service and self.current_interview_id:
            try:
                # This would require adding a method to the database service
                # For now, we'll just track it locally
                pass
            except Exception as e:
                print(f"Database error updating audio preference: {e}")
