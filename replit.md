# Overview

AI Excel Mock Interviewer is an intelligent web application that conducts comprehensive Excel skills assessments using Google Gemini AI with voice capabilities. The system provides structured interview experiences with adaptive questioning, real-time evaluation, and detailed performance reporting. It features conversational AI-driven interviews that feel natural and engaging while evaluating candidates across 8 Excel categories with 4 difficulty levels.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application providing interactive UI components
- **State Management**: Session-based state persistence using Streamlit's session state for interview progress tracking
- **Audio Integration**: WebRTC streaming for real-time audio capture with fallback mechanisms for browser compatibility
- **Component Structure**: Modular UI components for audio recording, chat displays, and report generation

## Backend Architecture
- **Service Layer**: Modular service architecture separating concerns across AI, speech, database, and interview management
- **Interview Flow**: Centralized interview manager handling question progression, adaptive questioning, and completion detection
- **AI Integration**: Google Gemini AI service for intelligent question generation, response evaluation, and conversational flow
- **Speech Processing**: Integrated Google Cloud Speech-to-Text and Text-to-Speech APIs for voice interaction capabilities

## Data Models
- **Structured Data**: Dataclass-based models for type safety and clear data contracts
- **Interview State**: Comprehensive session tracking including candidate information, responses, evaluations, and timestamps
- **Question Management**: Categorized question bank with difficulty levels, expected topics, and follow-up capabilities
- **Evaluation System**: Multi-dimensional scoring with technical accuracy, knowledge depth, and improvement recommendations

## Database Architecture
- **ORM Layer**: SQLAlchemy with declarative base for database operations
- **Schema Design**: Normalized tables for candidates, interviews, responses, and evaluations with proper relationships
- **Session Management**: Database session handling with connection pooling and error recovery
- **Analytics Support**: Structured data storage enabling performance analytics and trend analysis

## Audio Processing
- **Real-time Capture**: WebRTC-based audio streaming with browser compatibility detection
- **Format Support**: Multi-format audio handling (WAV, MP3, OGG, WebM) with validation and conversion utilities
- **Processing Pipeline**: Base64 encoding, format validation, and audio quality optimization

## Interview Intelligence
- **Adaptive Questioning**: AI-driven question selection based on candidate experience level and performance trends
- **Context Awareness**: Multi-turn conversation handling with contextual follow-up question generation
- **Performance Tracking**: Real-time evaluation and scoring with category-specific analysis
- **Report Generation**: Comprehensive performance reports with actionable insights and recommendations

# External Dependencies

## AI Services
- **Google Gemini AI**: Primary AI engine using gemini-2.5-flash model for question generation and response evaluation
- **API Integration**: RESTful communication with structured JSON request/response handling

## Speech Services  
- **Google Cloud Speech-to-Text**: Audio transcription with multiple language support and real-time processing
- **Google Cloud Text-to-Speech**: Voice synthesis with Neural voices for natural, engaging audio output
- **Voice Configuration**: Customizable voice parameters including speaking rate, pitch, and audio effects

## Database Systems
- **PostgreSQL**: Primary database for persistent storage of interview data, candidate records, and analytics
- **SQLAlchemy**: ORM layer for database abstraction and relationship management
- **Connection Management**: Database connection pooling and error handling with graceful fallbacks

## Development and Deployment
- **Streamlit**: Web framework for rapid UI development and deployment
- **Python Ecosystem**: Core dependencies including dataclasses, datetime, typing, and logging
- **Environment Management**: Configuration via environment variables for API keys and database connections