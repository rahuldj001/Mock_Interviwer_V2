from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Response:
    """Represents a candidate's response to an interview question"""
    answer: str
    timestamp: datetime
    audio_duration: Optional[float] = None
    confidence_score: Optional[float] = None

@dataclass
class Question:
    """Represents an interview question"""
    id: str
    text: str
    category: str
    difficulty: str
    expected_topics: List[str]
    follow_up_hints: List[str]
    order: int
    timestamp: datetime

@dataclass
class InterviewState:
    """Maintains the state of an ongoing interview"""
    session_id: str
    candidate_name: str
    experience_level: str
    start_time: datetime
    voice_mode: bool = False
    responses: List[Response] = None
    evaluations: List[Dict[str, Any]] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.responses is None:
            self.responses = []
        if self.evaluations is None:
            self.evaluations = []

@dataclass
class InterviewReport:
    """Represents the final interview assessment report"""
    candidate_name: str
    interview_date: datetime
    overall_score: int
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    skills_demonstrated: List[str]
    detailed_feedback: str
    hiring_recommendation: str
    confidence_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format"""
        return {
            'candidate_name': self.candidate_name,
            'interview_date': self.interview_date.isoformat(),
            'overall_score': self.overall_score,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement,
            'recommendations': self.recommendations,
            'skills_demonstrated': self.skills_demonstrated,
            'detailed_feedback': self.detailed_feedback,
            'hiring_recommendation': self.hiring_recommendation,
            'confidence_level': self.confidence_level
        }

@dataclass
class ConversationTurn:
    """Represents a single turn in the interview conversation"""
    speaker: str  # 'interviewer' or 'candidate'
    message: str
    timestamp: datetime
    message_type: str = 'text'  # 'text', 'audio', 'system'
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class EvaluationCriteria:
    """Defines evaluation criteria for responses"""
    technical_accuracy: float
    completeness: float
    clarity: float
    practical_application: float
    depth_of_knowledge: float
