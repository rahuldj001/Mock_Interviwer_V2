import streamlit as st
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time
import base64

# Import services and models
from services.gemini_service import GeminiService
from services.database_service import DatabaseService
from services.speech_service import SpeechService
from services.interview_manager import InterviewManager
from models.interview_models import InterviewState, Response
from utils.audio_utils import AudioUtils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Excel Mock Interviewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize all services with error handling"""
    try:
        gemini_service = GeminiService()
        speech_service = SpeechService()
        audio_utils = AudioUtils()
        
        # Try to initialize database service
        try:
            database_service = DatabaseService()
        except Exception as e:
            st.warning(f"Database service unavailable: {e}. Continuing without database persistence.")
            database_service = None
        
        interview_manager = InterviewManager(
            gemini_service=gemini_service,
            database_service=database_service
        )
        
        return {
            'gemini': gemini_service,
            'database': database_service,
            'speech': speech_service,
            'audio': audio_utils,
            'interview_manager': interview_manager
        }
    except Exception as e:
        st.error(f"Failed to initialize services: {e}")
        return None

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'services' not in st.session_state:
        st.session_state.services = initialize_services()
    
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = None
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    
    if 'interview_completed' not in st.session_state:
        st.session_state.interview_completed = False
    
    if 'voice_mode' not in st.session_state:
        st.session_state.voice_mode = False
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def create_audio_player(audio_data: bytes, autoplay: bool = False):
    """Create an HTML audio player for TTS output"""
    if not audio_data:
        return None
    
    audio_base64 = base64.b64encode(audio_data).decode()
    audio_html = f"""
    <audio {'autoplay' if autoplay else ''} controls style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

def display_welcome_screen():
    """Display the welcome screen with interview setup"""
    st.title("🎯 AI Excel Mock Interviewer")
    
    st.markdown("""
    ### Welcome to Your Personal Excel Skills Assessment!
    
    I'm your AI interviewer, and I'm excited to help you evaluate and improve your Excel proficiency. 
    This assessment is designed to be conversational and comprehensive, covering various Excel topics 
    from basic functions to advanced data analysis techniques.
    
    **What to expect:**
    - 8-10 thoughtful questions tailored to your experience level
    - Real-time feedback and evaluation
    - Detailed performance report with personalized recommendations
    - Option for voice interaction for a more natural experience
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Setup Your Interview")
        candidate_name = st.text_input(
            "Your Name",
            placeholder="Enter your full name",
            help="This will be used in your interview report"
        )
        
        experience_level = st.selectbox(
            "Excel Experience Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"],
            index=1,
            help="This helps me tailor questions to your skill level"
        )
        
        voice_mode = st.checkbox(
            "🎤 Enable Voice Mode",
            help="Use speech-to-text and text-to-speech for a more natural interview experience"
        )
    
    with col2:
        st.subheader("🗣️ Interview Guidelines")
        st.markdown("""
        **Tips for success:**
        - Explain your reasoning and thought process
        - Ask for clarification if needed
        - Provide specific examples when possible
        - Take your time to think through your answers
        
        **Technical requirements:**
        - Stable internet connection
        - Microphone access (for voice mode)
        - Modern web browser
        """)
    
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        if not candidate_name.strip():
            st.error("Please enter your name to continue.")
            return
        
        # Initialize interview state
        st.session_state.interview_state = InterviewState(
            session_id=str(uuid.uuid4()),
            candidate_name=candidate_name,
            experience_level=experience_level,
            start_time=datetime.now(),
            voice_mode=voice_mode
        )
        st.session_state.voice_mode = voice_mode
        st.session_state.interview_started = True
        
        # Generate welcome message
        if st.session_state.services and st.session_state.services['interview_manager']:
            welcome_msg = st.session_state.services['interview_manager'].start_interview(
                candidate_name, experience_level
            )
            st.session_state.conversation_history.append({
                'speaker': 'Interviewer',
                'message': welcome_msg,
                'timestamp': datetime.now()
            })
        
        st.rerun()

def display_interview_interface():
    """Display the main interview interface"""
    if not st.session_state.interview_state:
        st.error("Interview state not found. Please restart the interview.")
        return
    
    interview_state = st.session_state.interview_state
    services = st.session_state.services
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(f"📊 Excel Interview - {interview_state.candidate_name}")
    with col2:
        progress = len(interview_state.responses) / 8  # Assuming 8 questions max
        st.metric("Progress", f"{len(interview_state.responses)}/8")
        st.progress(progress)
    with col3:
        if st.button("🏁 End Interview", type="secondary"):
            st.session_state.interview_completed = True
            st.rerun()
    
    # Conversation display
    st.subheader("💬 Interview Conversation")
    
    # Display conversation history in a chat-like format
    for entry in st.session_state.conversation_history:
        if entry['speaker'] == 'Interviewer':
            with st.chat_message("assistant", avatar="🤖"):
                st.write(entry['message'])
                # Add TTS if voice mode is enabled
                if st.session_state.voice_mode and services['speech']:
                    audio_data = services['speech'].text_to_speech(entry['message'])
                    if audio_data:
                        audio_html = create_audio_player(audio_data, autoplay=True)
                        if audio_html:
                            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(entry['message'])
    
    # Get next question if needed
    if not st.session_state.current_question and len(interview_state.responses) < 8:
        try:
            question = services['interview_manager'].get_next_question(interview_state)
            if question:
                st.session_state.current_question = question
                st.session_state.conversation_history.append({
                    'speaker': 'Interviewer',
                    'message': question['question'],
                    'timestamp': datetime.now()
                })
                st.rerun()
        except Exception as e:
            st.error(f"Error generating question: {e}")
    
    # Answer input section
    if st.session_state.current_question and len(interview_state.responses) < 8:
        st.subheader("🎯 Your Response")
        
        # Voice input option
        if st.session_state.voice_mode:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🎤 Voice Response**")
                # Note: Streamlit WebRTC would be implemented here for real voice recording
                st.info("Voice recording feature would be implemented with streamlit-webrtc component")
            with col2:
                st.markdown("**⌨️ Text Response**")
                answer_text = st.text_area(
                    "Type your answer here:",
                    height=150,
                    placeholder="Provide your detailed response..."
                )
        else:
            answer_text = st.text_area(
                "Your Answer:",
                height=200,
                placeholder="Please provide a detailed response explaining your approach, reasoning, and any specific Excel features you would use..."
            )
        
        if st.button("📤 Submit Answer", type="primary"):
            if not answer_text.strip():
                st.error("Please provide an answer before submitting.")
                return
            
            # Create response object
            response = Response(
                answer=answer_text,
                timestamp=datetime.now(),
                audio_duration=None  # Would be set if voice input was used
            )
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                'speaker': 'Candidate',
                'message': answer_text,
                'timestamp': datetime.now()
            })
            
            # Evaluate response
            try:
                evaluation = services['interview_manager'].evaluate_response(
                    st.session_state.current_question,
                    response,
                    interview_state
                )
                
                # Add response and evaluation to interview state
                interview_state.responses.append(response)
                interview_state.evaluations.append(evaluation)
                
                # Generate follow-up if needed
                follow_up = services['interview_manager'].generate_follow_up(
                    st.session_state.current_question,
                    response,
                    evaluation,
                    interview_state
                )
                
                if follow_up:
                    st.session_state.conversation_history.append({
                        'speaker': 'Interviewer',
                        'message': follow_up,
                        'timestamp': datetime.now()
                    })
                
                # Clear current question for next one
                st.session_state.current_question = None
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error evaluating response: {e}")
    
    elif len(interview_state.responses) >= 8:
        # Interview completed
        st.success("🎉 Interview completed! Generating your detailed report...")
        st.session_state.interview_completed = True
        st.rerun()

def display_interview_report():
    """Display the final interview report"""
    if not st.session_state.interview_state:
        st.error("Interview state not found.")
        return
    
    interview_state = st.session_state.interview_state
    services = st.session_state.services
    
    st.title("📋 Interview Report")
    
    try:
        # Generate closing message
        closing_msg = services['interview_manager'].generate_closing_message(interview_state)
        st.info(closing_msg)
        
        # Generate final report
        with st.spinner("Analyzing your responses and generating detailed feedback..."):
            report = services['interview_manager'].generate_final_report(interview_state)
        
        # Display report sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Overall Performance")
            st.metric("Overall Score", f"{report.overall_score}/100")
            
            st.subheader("💪 Key Strengths")
            for strength in report.strengths:
                st.write(f"✅ {strength}")
        
        with col2:
            st.subheader("📈 Areas for Improvement")
            for improvement in report.areas_for_improvement:
                st.write(f"🔸 {improvement}")
            
            st.subheader("🎓 Recommendations")
            for recommendation in report.recommendations:
                st.write(f"💡 {recommendation}")
        
        st.subheader("📝 Detailed Feedback")
        st.write(report.detailed_feedback)
        
        st.subheader("🏆 Skills Demonstrated")
        skills_cols = st.columns(3)
        for i, skill in enumerate(report.skills_demonstrated):
            with skills_cols[i % 3]:
                st.write(f"🔹 {skill}")
        
        # Interview statistics
        st.subheader("📊 Interview Statistics")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric("Questions Answered", len(interview_state.responses))
        with stats_col2:
            duration = (datetime.now() - interview_state.start_time).total_seconds() / 60
            st.metric("Duration (min)", f"{duration:.1f}")
        with stats_col3:
            avg_score = sum(e.get('score', 0) for e in interview_state.evaluations) / max(len(interview_state.evaluations), 1)
            st.metric("Average Score", f"{avg_score:.1f}/10")
        with stats_col4:
            st.metric("Hiring Recommendation", report.hiring_recommendation)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Start New Interview", type="primary"):
                # Reset session state
                for key in ['interview_state', 'current_question', 'interview_started', 
                           'interview_completed', 'conversation_history']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            # Export functionality could be added here
            st.button("📥 Export Report", disabled=True, help="Export functionality coming soon")
        
        with col3:
            # Feedback functionality could be added here
            st.button("💬 Provide Feedback", disabled=True, help="Feedback system coming soon")
            
    except Exception as e:
        st.error(f"Error generating report: {e}")
        if st.button("🔄 Retry Report Generation"):
            st.rerun()

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Check if services are initialized
    if not st.session_state.services:
        st.error("Failed to initialize application services. Please check your configuration and refresh the page.")
        return
    
    # Sidebar with application info
    with st.sidebar:
        st.header("🎯 AI Excel Interviewer")
        st.markdown("---")
        
        if st.session_state.interview_started and not st.session_state.interview_completed:
            st.subheader("📊 Current Session")
            if st.session_state.interview_state:
                st.write(f"**Candidate:** {st.session_state.interview_state.candidate_name}")
                st.write(f"**Level:** {st.session_state.interview_state.experience_level}")
                st.write(f"**Questions:** {len(st.session_state.interview_state.responses)}/8")
                st.write(f"**Voice Mode:** {'✅' if st.session_state.voice_mode else '❌'}")
        
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        This AI-powered interviewer uses advanced language models to:
        - Generate contextual Excel questions
        - Evaluate your responses in real-time
        - Provide personalized feedback
        - Create comprehensive performance reports
        """)
        
        st.markdown("---")
        st.subheader("🛠️ System Status")
        services = st.session_state.services
        st.write(f"🤖 AI Service: {'✅' if services['gemini'] else '❌'}")
        st.write(f"🗄️ Database: {'✅' if services['database'] else '❌'}")
        st.write(f"🎤 Speech: {'✅' if services['speech'] else '❌'}")
    
    # Main application flow
    try:
        if not st.session_state.interview_started:
            display_welcome_screen()
        elif st.session_state.interview_completed:
            display_interview_report()
        else:
            display_interview_interface()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
