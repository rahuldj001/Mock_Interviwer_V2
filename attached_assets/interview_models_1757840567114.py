from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

@dataclass
class Question:
    """Represents an interview question"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    category: str = "General"
    difficulty: str = "Medium"
    expected_topics: List[str] = field(default_factory=list)
    follow_up_hints: List[str] = field(default_factory=list)
    order: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Response:
    """Represents a candidate's response to a question"""
    question_id: str = ""
    answer: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    audio_duration: Optional[float] = None
    response_time: Optional[float] = None

@dataclass
class Evaluation:
    """Represents the evaluation of a response"""
    question_id: str = ""
    score: int = 0
    feedback: str = ""
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    technical_accuracy: str = "Medium"
    knowledge_depth: str = "Good"
    follow_up_needed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    category: str = "General"

@dataclass
class InterviewState:
    """Manages the overall state of an interview session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    candidate_name: str = ""
    experience_level: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    current_question_index: int = 0
    responses: List[Response] = field(default_factory=list)
    evaluations: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    interview_phase: str = "introduction"
    audio_enabled: bool = False
    
    def add_response(self, response: Response) -> None:
        """Add a new response to the interview"""
        self.responses.append(response)
    
    def add_evaluation(self, evaluation: Dict[str, Any]) -> None:
        """Add an evaluation to the interview"""
        self.evaluations.append(evaluation)
    
    def get_average_score(self) -> float:
        """Calculate average score across all evaluations"""
        if not self.evaluations:
            return 0.0
        scores = [e.get("score", 0) for e in self.evaluations]
        return sum(scores) / len(scores)
    
    def get_categories_covered(self) -> List[str]:
        """Get list of categories covered in the interview"""
        categories = set()
        for evaluation in self.evaluations:
            category = evaluation.get("category", "General")
            categories.add(category)
        return list(categories)
    
    def get_duration_minutes(self) -> float:
        """Get interview duration in minutes"""
        if self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 60
        else:
            current_duration = datetime.now() - self.start_time
            return current_duration.total_seconds() / 60
    
    def is_complete(self) -> bool:
        """Check if interview is complete"""
        return self.end_time is not None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of candidate performance"""
        if not self.evaluations:
            return {
                "average_score": 0,
                "total_questions": 0,
                "categories_covered": [],
                "duration_minutes": self.get_duration_minutes()
            }
        
        scores = [e.get("score", 0) for e in self.evaluations]
        return {
            "average_score": sum(scores) / len(scores),
            "total_questions": len(self.responses),
            "categories_covered": self.get_categories_covered(),
            "duration_minutes": self.get_duration_minutes(),
            "highest_score": max(scores),
            "lowest_score": min(scores)
        }

@dataclass
class InterviewReport:
    """Comprehensive interview report"""
    candidate_name: str = ""
    interview_date: datetime = field(default_factory=datetime.now)
    overall_score: int = 0
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    skills_demonstrated: List[str] = field(default_factory=list)
    detailed_feedback: str = ""
    hiring_recommendation: str = "Additional assessment needed"
    confidence_level: str = "Medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format"""
        return {
            "candidate_name": self.candidate_name,
            "interview_date": self.interview_date.isoformat(),
            "overall_score": self.overall_score,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "recommendations": self.recommendations,
            "skills_demonstrated": self.skills_demonstrated,
            "detailed_feedback": self.detailed_feedback,
            "hiring_recommendation": self.hiring_recommendation,
            "confidence_level": self.confidence_level
        }
    
    def get_score_grade(self) -> str:
        """Get letter grade based on overall score"""
        if self.overall_score >= 90:
            return "A+"
        elif self.overall_score >= 85:
            return "A"
        elif self.overall_score >= 80:
            return "A-"
        elif self.overall_score >= 75:
            return "B+"
        elif self.overall_score >= 70:
            return "B"
        elif self.overall_score >= 65:
            return "B-"
        elif self.overall_score >= 60:
            return "C+"
        elif self.overall_score >= 55:
            return "C"
        else:
            return "Needs Improvement"
    
    def get_recommendation_summary(self) -> str:
        """Get hiring recommendation summary"""
        if self.overall_score >= 85:
            return "Strong hire - Excellent Excel skills demonstrated"
        elif self.overall_score >= 70:
            return "Hire - Good Excel proficiency with minor gaps"
        elif self.overall_score >= 55:
            return "Conditional hire - Basic skills present, training recommended"
        else:
            return "Additional assessment needed - Significant skill gaps identified"

@dataclass
class InterviewMetrics:
    """Metrics and analytics for interview performance"""
    total_interviews: int = 0
    average_score: float = 0.0
    completion_rate: float = 0.0
    average_duration_minutes: float = 0.0
    top_performing_categories: List[str] = field(default_factory=list)
    challenging_categories: List[str] = field(default_factory=list)
    candidate_feedback_scores: List[float] = field(default_factory=list)
    
    def update_metrics(self, interview_state: InterviewState) -> None:
        """Update metrics with new interview data"""
        self.total_interviews += 1
        
        # Update average score
        current_score = interview_state.get_average_score()
        self.average_score = ((self.average_score * (self.total_interviews - 1)) + current_score) / self.total_interviews
        
        # Update duration
        duration = interview_state.get_duration_minutes()
        self.average_duration_minutes = ((self.average_duration_minutes * (self.total_interviews - 1)) + duration) / self.total_interviews
        
        # Update completion rate (assume completed if we have evaluations)
        completed_interviews = self.total_interviews if interview_state.evaluations else self.total_interviews - 1
        self.completion_rate = completed_interviews / self.total_interviews

@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""
    speaker: str  # "interviewer" or "candidate"
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "text"  # "text", "audio", "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "speaker": self.speaker,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "metadata": self.metadata
        }
