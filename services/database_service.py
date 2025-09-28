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
    status = Column(String(50), default='in_progress')
    language = Column(String(10), default='en')
    interview_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    responses = relationship("InterviewResponse", back_populates="interview", cascade="all, delete-orphan")
    evaluations = relationship("ResponseEvaluation", back_populates="interview", cascade="all, delete-orphan")

class InterviewResponse(Base):
    """Candidate responses to questions"""
    __tablename__ = 'interview_responses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    question_category = Column(String(100))
    question_difficulty = Column(String(50))
    response_time_seconds = Column(Float)
    score = Column(Float, default=0.0)
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="responses")

class ResponseEvaluation(Base):
    """AI evaluations of responses"""
    __tablename__ = 'response_evaluations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'), nullable=False)
    response_id = Column(Integer, ForeignKey('interview_responses.id'), nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(Text)
    strengths = Column(JSON)
    improvements = Column(JSON)
    technical_accuracy = Column(String(50))
    knowledge_depth = Column(String(50))
    evaluation_details = Column(JSON)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="evaluations")

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
            candidate = None
            if email:
                candidate = session.query(Candidate).filter(Candidate.email == email).first()
            
            if not candidate:
                candidate = session.query(Candidate).filter(
                    Candidate.name == name,
                    Candidate.experience_level == experience_level
                ).first()
            
            if not candidate:
                candidate = Candidate(
                    name=name,
                    email=email,
                    experience_level=experience_level
                )
                session.add(candidate)
                session.commit()
                session.refresh(candidate)
            
            return candidate.id
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error creating/getting candidate: {e}")
            raise
        finally:
            session.close()
    
    def create_interview_session(self, candidate_id: int, experience_level: str, audio_enabled: bool = False) -> int:
        """Create a new interview session"""
        session = self.get_session()
        try:
            import uuid
            interview = Interview(
                session_id=str(uuid.uuid4()),
                candidate_id=candidate_id,
                start_time=datetime.utcnow(),
                experience_level=experience_level,
                audio_enabled=audio_enabled,
                status='in_progress'
            )
            session.add(interview)
            session.commit()
            session.refresh(interview)
            return interview.id
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error creating interview: {e}")
            raise
        finally:
            session.close()
    
    def save_response(self, interview_id: int, question_text: str, response_text: str,
                     question_category: str = None, question_difficulty: str = None,
                     score: float = 0.0, evaluation_details: Dict[str, Any] = None) -> int:
        """Save candidate response with evaluation"""
        session = self.get_session()
        try:
            # Count existing responses for sequence number
            response_count = session.query(InterviewResponse).filter(
                InterviewResponse.interview_id == interview_id
            ).count()
            
            response = InterviewResponse(
                interview_id=interview_id,
                question_text=question_text,
                answer_text=response_text,
                question_category=question_category,
                question_difficulty=question_difficulty,
                score=score,
                sequence_number=response_count + 1,
                timestamp=datetime.utcnow()
            )
            session.add(response)
            session.commit()
            session.refresh(response)
            
            # Save evaluation if provided
            if evaluation_details:
                evaluation = ResponseEvaluation(
                    interview_id=interview_id,
                    response_id=response.id,
                    score=score,
                    feedback=evaluation_details.get('feedback', ''),
                    strengths=evaluation_details.get('strengths', []),
                    improvements=evaluation_details.get('improvements', []),
                    technical_accuracy=evaluation_details.get('technical_accuracy', 'Medium'),
                    knowledge_depth=evaluation_details.get('knowledge_depth', 'Good'),
                    evaluation_details=evaluation_details,
                    timestamp=datetime.utcnow()
                )
                session.add(evaluation)
                session.commit()
            
            return response.id
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error saving response: {e}")
            raise
        finally:
            session.close()
    
    def complete_interview(self, interview_id: int, overall_score: float = 0.0) -> bool:
        """Mark interview as completed"""
        session = self.get_session()
        try:
            interview = session.query(Interview).filter(Interview.id == interview_id).first()
            if interview:
                interview.end_time = datetime.utcnow()
                interview.status = 'completed'
                interview.overall_score = overall_score
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error completing interview: {e}")
            return False
        finally:
            session.close()
    
    def get_interview_stats(self) -> Dict[str, Any]:
        """Get overall interview statistics"""
        session = self.get_session()
        try:
            total_interviews = session.query(Interview).count()
            completed_interviews = session.query(Interview).filter(Interview.status == 'completed').count()
            total_candidates = session.query(Candidate).count()
            
            if completed_interviews > 0:
                avg_score = session.query(Interview).filter(
                    Interview.status == 'completed'
                ).with_entities(Interview.overall_score).all()
                avg_score = sum(score[0] for score in avg_score) / len(avg_score)
            else:
                avg_score = 0.0
            
            return {
                'total_interviews': total_interviews,
                'completed_interviews': completed_interviews,
                'total_candidates': total_candidates,
                'average_score': avg_score
            }
        except SQLAlchemyError as e:
            logging.error(f"Error getting interview stats: {e}")
            return {}
        finally:
            session.close()
