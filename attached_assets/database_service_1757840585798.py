"""
Database service for Excel Mock Interviewer
Handles persistent storage of interviews, candidates, and analytics
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class Candidate(Base):
    """Candidate information table"""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    experience_level = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to interviews
    interviews = relationship("Interview", back_populates="candidate")
    
class Interview(Base):
    """Interview session table"""
    __tablename__ = 'interviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    experience_level = Column(String(100), nullable=False)
    audio_enabled = Column(Boolean, default=False)
    overall_score = Column(Float, default=0.0)
    status = Column(String(50), default='in_progress')  # in_progress, completed, abandoned
    language = Column(String(10), default='en')
    interview_metadata = Column(JSON)  # Additional data like browser info, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    responses = relationship("InterviewResponse", back_populates="interview", cascade="all, delete-orphan")
    evaluations = relationship("ResponseEvaluation", back_populates="interview", cascade="all, delete-orphan")
    conversation = relationship("ConversationTurn", back_populates="interview", cascade="all, delete-orphan")
    report = relationship("InterviewReport", back_populates="interview", uselist=False, cascade="all, delete-orphan")

class Question(Base):
    """Question bank table"""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    expected_topics = Column(JSON)  # List of expected topics
    follow_up_hints = Column(JSON)  # List of follow-up hints
    is_scenario_based = Column(Boolean, default=False)
    excel_file_required = Column(Boolean, default=False)
    language = Column(String(10), default='en')
    created_at = Column(DateTime, default=datetime.utcnow)
    
class InterviewResponse(Base):
    """Candidate responses to questions"""
    __tablename__ = 'interview_responses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question_text = Column(Text, nullable=False)  # Store actual question asked
    answer_text = Column(Text, nullable=False)
    answer_audio_duration = Column(Float)
    response_time_seconds = Column(Float)
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="responses")
    question = relationship("Question")
    evaluation = relationship("ResponseEvaluation", back_populates="response", uselist=False)

class ResponseEvaluation(Base):
    """AI evaluations of responses"""
    __tablename__ = 'response_evaluations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), nullable=False)
    response_id = Column(Integer, ForeignKey('interview_responses.id'), nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(Text)
    strengths = Column(JSON)  # List of identified strengths
    improvements = Column(JSON)  # List of improvement areas
    technical_accuracy = Column(String(50))
    knowledge_depth = Column(String(50))
    follow_up_needed = Column(Boolean, default=False)
    category_scores = Column(JSON)  # Detailed category-wise scoring
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="evaluations")
    response = relationship("InterviewResponse", back_populates="evaluation")

class ConversationTurn(Base):
    """Conversation history"""
    __tablename__ = 'conversation_turns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), nullable=False)
    speaker = Column(String(50), nullable=False)  # 'interviewer' or 'candidate'
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default='text')  # 'text', 'audio', 'system'
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    turn_metadata = Column(JSON)  # Additional data like audio duration, etc.
    
    # Relationships
    interview = relationship("Interview", back_populates="conversation")

class InterviewReport(Base):
    """Final interview reports"""
    __tablename__ = 'interview_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), nullable=False)
    overall_score = Column(Float, nullable=False)
    strengths = Column(JSON)  # List of strengths
    areas_for_improvement = Column(JSON)  # List of improvement areas
    recommendations = Column(JSON)  # List of recommendations
    skills_demonstrated = Column(JSON)  # List of demonstrated skills
    detailed_feedback = Column(Text)
    hiring_recommendation = Column(String(100))
    confidence_level = Column(String(50))
    category_breakdown = Column(JSON)  # Performance by category
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interview = relationship("Interview", back_populates="report")

class ExcelFile(Base):
    """Uploaded Excel files for scenario-based questions"""
    __tablename__ = 'excel_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    sheet_names = Column(JSON)  # List of sheet names
    column_info = Column(JSON)  # Column information for each sheet
    difficulty_level = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logging.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logging.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def create_or_get_candidate(self, name: str, experience_level: str, email: Optional[str] = None) -> int:
        """Create or get existing candidate"""
        session = self.get_session()
        try:
            # Try to find existing candidate by email if provided
            candidate = None
            if email:
                candidate = session.query(Candidate).filter(Candidate.email == email).first()
            
            if not candidate:
                # Try to find by name and experience level
                candidate = session.query(Candidate).filter(
                    Candidate.name == name,
                    Candidate.experience_level == experience_level
                ).first()
            
            if not candidate:
                # Create new candidate
                candidate = Candidate(
                    name=name,
                    email=email,
                    experience_level=experience_level
                )
                session.add(candidate)
                session.commit()
                session.refresh(candidate)
            
            return getattr(candidate, 'id')
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error creating/getting candidate: {e}")
            raise
        finally:
            session.close()
    
    def create_interview(self, session_id: str, candidate_id: int, experience_level: str, 
                        audio_enabled: bool = False, language: str = 'en') -> int:
        """Create a new interview session"""
        session = self.get_session()
        try:
            interview = Interview(
                session_id=session_id,
                candidate_id=candidate_id,
                start_time=datetime.utcnow(),
                experience_level=experience_level,
                audio_enabled=audio_enabled,
                language=language,
                status='in_progress'
            )
            session.add(interview)
            session.commit()
            session.refresh(interview)
            return getattr(interview, 'id')
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error creating interview: {e}")
            raise
        finally:
            session.close()
    
    def save_response(self, interview_id: int, question_text: str, answer_text: str,
                     sequence_number: int, response_time: Optional[float] = None, 
                     audio_duration: Optional[float] = None, question_id: Optional[int] = None) -> int:
        """Save candidate response"""
        session = self.get_session()
        try:
            response = InterviewResponse(
                interview_id=interview_id,
                question_id=question_id,
                question_text=question_text,
                answer_text=answer_text,
                answer_audio_duration=audio_duration,
                response_time_seconds=response_time,
                sequence_number=sequence_number,
                timestamp=datetime.utcnow()
            )
            session.add(response)
            session.commit()
            session.refresh(response)
            return getattr(response, 'id')
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error saving response: {e}")
            raise
        finally:
            session.close()
    
    def save_evaluation(self, interview_id: int, response_id: int, evaluation_data: Dict[str, Any]) -> int:
        """Save response evaluation"""
        session = self.get_session()
        try:
            evaluation = ResponseEvaluation(
                interview_id=interview_id,
                response_id=response_id,
                score=evaluation_data.get('score', 0),
                feedback=evaluation_data.get('feedback', ''),
                strengths=evaluation_data.get('strengths', []),
                improvements=evaluation_data.get('improvements', []),
                technical_accuracy=evaluation_data.get('technical_accuracy', 'Medium'),
                knowledge_depth=evaluation_data.get('knowledge_depth', 'Good'),
                follow_up_needed=evaluation_data.get('follow_up_needed', False),
                category_scores=evaluation_data.get('category_scores', {}),
                timestamp=datetime.utcnow()
            )
            session.add(evaluation)
            session.commit()
            session.refresh(evaluation)
            return getattr(evaluation, 'id')
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error saving evaluation: {e}")
            raise
        finally:
            session.close()
    
    def save_conversation_turn(self, interview_id: int, speaker: str, message: str,
                              sequence_number: int, message_type: str = 'text',
                              metadata: Optional[Dict] = None) -> int:
        """Save conversation turn"""
        session = self.get_session()
        try:
            turn = ConversationTurn(
                interview_id=interview_id,
                speaker=speaker,
                message=message,
                message_type=message_type,
                sequence_number=sequence_number,
                timestamp=datetime.utcnow(),
                turn_metadata=metadata or {}
            )
            session.add(turn)
            session.commit()
            session.refresh(turn)
            return getattr(turn, 'id')
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error saving conversation turn: {e}")
            raise
        finally:
            session.close()
    
    def complete_interview(self, interview_id: int, overall_score: float) -> None:
        """Mark interview as completed"""
        session = self.get_session()
        try:
            interview = session.query(Interview).filter(Interview.id == interview_id).first()
            if interview is not None:
                # Use setattr to avoid type checker issues with SQLAlchemy attributes
                setattr(interview, 'end_time', datetime.utcnow())
                setattr(interview, 'overall_score', overall_score)
                setattr(interview, 'status', 'completed')
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error completing interview: {e}")
            raise
        finally:
            session.close()
    
    def save_final_report(self, interview_id: int, report_data: Dict[str, Any]) -> int:
        """Save final interview report"""
        session = self.get_session()
        try:
            report = InterviewReport(
                interview_id=interview_id,
                overall_score=report_data.get('overall_score', 0),
                strengths=report_data.get('strengths', []),
                areas_for_improvement=report_data.get('areas_for_improvement', []),
                recommendations=report_data.get('recommendations', []),
                skills_demonstrated=report_data.get('skills_demonstrated', []),
                detailed_feedback=report_data.get('detailed_feedback', ''),
                hiring_recommendation=report_data.get('hiring_recommendation', 'Additional assessment needed'),
                confidence_level=report_data.get('confidence_level', 'Medium'),
                category_breakdown=report_data.get('category_breakdown', {})
            )
            session.add(report)
            session.commit()
            session.refresh(report)
            return getattr(report, 'id')
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error saving report: {e}")
            raise
        finally:
            session.close()
    
    def get_candidate_interviews(self, candidate_id: int) -> List[Dict[str, Any]]:
        """Get all interviews for a candidate"""
        session = self.get_session()
        try:
            interviews = session.query(Interview).filter(
                Interview.candidate_id == candidate_id,
                Interview.status == 'completed'
            ).order_by(Interview.start_time.desc()).all()
            
            result = []
            for interview in interviews:
                result.append({
                    'id': interview.id,
                    'start_time': interview.start_time,
                    'end_time': interview.end_time,
                    'overall_score': interview.overall_score,
                    'experience_level': interview.experience_level,
                    'audio_enabled': interview.audio_enabled,
                    'language': interview.language
                })
            return result
        except SQLAlchemyError as e:
            logging.error(f"Error getting candidate interviews: {e}")
            return []
        finally:
            session.close()
    
    def get_interview_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get interview analytics for the past N days"""
        session = self.get_session()
        try:
            from datetime import timedelta
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get completed interviews
            interviews = session.query(Interview).filter(
                Interview.status == 'completed',
                Interview.start_time >= since_date
            ).all()
            
            if not interviews:
                return {
                    'total_interviews': 0,
                    'average_score': 0,
                    'completion_rate': 0,
                    'score_distribution': {},
                    'category_performance': {},
                    'experience_level_breakdown': {}
                }
            
            total_interviews = len(interviews)
            total_score = sum(getattr(interview, 'overall_score') for interview in interviews)
            average_score = total_score / total_interviews if total_interviews > 0 else 0.0
            
            # Score distribution
            score_ranges = {'0-30': 0, '31-50': 0, '51-70': 0, '71-85': 0, '86-100': 0}
            for interview in interviews:
                score = getattr(interview, 'overall_score')
                if score <= 30:
                    score_ranges['0-30'] += 1
                elif score <= 50:
                    score_ranges['31-50'] += 1
                elif score <= 70:
                    score_ranges['51-70'] += 1
                elif score <= 85:
                    score_ranges['71-85'] += 1
                else:
                    score_ranges['86-100'] += 1
            
            # Experience level breakdown
            exp_breakdown = {}
            for interview in interviews:
                level = interview.experience_level
                exp_breakdown[level] = exp_breakdown.get(level, 0) + 1
            
            return {
                'total_interviews': total_interviews,
                'average_score': round(float(average_score), 2),
                'completion_rate': 100,  # Only completed interviews are counted
                'score_distribution': score_ranges,
                'experience_level_breakdown': exp_breakdown,
                'date_range': f"Last {days} days"
            }
            
        except SQLAlchemyError as e:
            logging.error(f"Error getting analytics: {e}")
            return {}
        finally:
            session.close()
    
    def get_top_candidates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing candidates"""
        session = self.get_session()
        try:
            # Get candidates with their highest scores
            results = session.query(
                Candidate.name,
                Candidate.experience_level,
                Interview.overall_score,
                Interview.start_time
            ).join(Interview).filter(
                Interview.status == 'completed'
            ).order_by(
                Interview.overall_score.desc()
            ).limit(limit).all()
            
            candidates = []
            for result in results:
                candidates.append({
                    'name': result.name,
                    'experience_level': result.experience_level,
                    'highest_score': result.overall_score,
                    'interview_date': result.start_time
                })
            
            return candidates
            
        except SQLAlchemyError as e:
            logging.error(f"Error getting top candidates: {e}")
            return []
        finally:
            session.close()