# 🎯 AI Excel Mock Interviewer

An intelligent, conversational Excel skills assessment platform powered by Google Gemini AI. This application conducts human-like interviews to evaluate Excel proficiency and provides detailed, personalized feedback reports.

## ✨ Features

### 🤖 AI-Powered Interview Experience
- **Natural Conversation Flow**: Gemini AI generates contextual questions that feel like a real interview
- **Adaptive Questioning**: Questions adjust to candidate experience level and performance
- **Intelligent Follow-ups**: AI provides encouraging follow-up questions and clarifications
- **Human-like Responses**: Warm, professional tone throughout the interview

### 🎤 Enhanced Voice Capabilities
- **Text-to-Speech**: Clear, natural voice output with Neural voices
- **Speech-to-Text**: Accurate voice input recognition
- **Multiple Voice Styles**: Friendly, professional, and encouraging tones
- **Multi-language Support**: Support for multiple languages and accents

### 📊 Comprehensive Assessment
- **8 Excel Categories**: Functions, Data Analysis, PivotTables, Charts, Macros, and more
- **4 Difficulty Levels**: Beginner, Intermediate, Advanced, Expert
- **Real-time Evaluation**: Instant AI-powered response analysis
- **Detailed Scoring**: Technical accuracy, knowledge depth, and practical application

### 📈 Advanced Reporting
- **Overall Performance Score**: 0-100 scale with detailed breakdown
- **Strengths Analysis**: Specific skills demonstrated
- **Improvement Areas**: Targeted recommendations for growth
- **Action Plan**: Specific next steps for skill development
- **Hiring Recommendations**: Professional assessment outcomes

### 🗄️ Data Management
- **PostgreSQL Integration**: Robust data persistence
- **Interview History**: Complete conversation logs
- **Performance Analytics**: Track progress over time
- **Candidate Profiles**: Maintain user records and preferences

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Google Gemini API key

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your_gemini_api_key

# Optional (for enhanced speech features)
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
