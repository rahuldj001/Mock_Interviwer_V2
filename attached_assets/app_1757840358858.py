import streamlit as st
import streamlit.components.v1 as components
import json
import time
from datetime import datetime
import base64
from io import BytesIO
import threading

from services.gemini_service import GeminiService
from services.speech_service import SpeechService
from services.interview_manager import InterviewManager
from services.database_service import DatabaseService
from models.interview_models import InterviewState, Question, Response, InterviewReport
from utils.audio_utils import AudioUtils

# WebRTC imports and setup
import numpy as np
import wave

# Define base class and imports conditionally
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    from streamlit_webrtc.webrtc import AudioProcessorBase
    import av
    WEBRTC_AVAILABLE = True
    
    # Audio processor class when WebRTC is available
    class WebRTCAudioRecorder(AudioProcessorBase):
        """Audio processor for recording and processing audio from microphone via WebRTC"""
        
        def __init__(self):
            super().__init__()
            self.audio_frames = []
            self.is_recording = False
            self.sample_rate = 16000
            
        def recv(self, frame):
            """Receive audio frame from WebRTC"""
            if self.is_recording:
                # Convert audio frame to numpy array
                audio_array = frame.to_ndarray()
                self.audio_frames.append(audio_array)
                # Store sample rate from first frame
                if self.sample_rate != frame.sample_rate:
                    self.sample_rate = frame.sample_rate
            # Return the original frame unchanged (required by WebRTC API)
            return frame
        
        def start_recording(self):
            """Start recording audio"""
            self.is_recording = True
            self.audio_frames = []
        
        def stop_recording(self):
            """Stop recording and return audio data"""
            self.is_recording = False
            if self.audio_frames:
                try:
                    # Concatenate all frames
                    audio_data = np.concatenate(self.audio_frames, axis=0)
                    
                    # Convert to bytes for speech service
                    from io import BytesIO
                    
                    # Create WAV format audio
                    wav_buffer = BytesIO()
                    with wave.open(wav_buffer, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(self.sample_rate)
                        # Convert float to int16
                        if audio_data.ndim > 1:
                            # If stereo, take first channel
                            audio_data = audio_data[:, 0]
                        audio_int16 = (audio_data * 32767).astype(np.int16)
                        wav_file.writeframes(audio_int16.tobytes())
                    
                    wav_buffer.seek(0)
                    return wav_buffer.getvalue()
                except Exception as e:
                    print(f"Error processing audio: {e}")
                    return None
            return None
    
    # Alias for backward compatibility
    AudioRecorder = WebRTCAudioRecorder

except ImportError:
    WEBRTC_AVAILABLE = False
    # Define placeholder variables when WebRTC is not available
    webrtc_streamer = None
    WebRtcMode = None
    
    # Fallback audio recorder class when WebRTC is not available  
    class FallbackAudioRecorder:
        """Fallback audio processor when WebRTC is not available"""
        
        def __init__(self):
            self.audio_frames = []
            self.is_recording = False
            self.sample_rate = 16000
        
        def recv(self, frame):
            """Receive audio frame from WebRTC - fallback does nothing"""
            return None
        
        def start_recording(self):
            """Start recording audio - fallback does nothing"""
            self.is_recording = True
            self.audio_frames = []
        
        def stop_recording(self):
            """Stop recording and return audio data - fallback returns None"""
            return None
    
    # Alias for backward compatibility
    AudioRecorder = FallbackAudioRecorder

def secure_tts_fallback(text: str) -> str:
    """Create secure TTS fallback HTML with proper script injection protection"""
    # Escape </script> sequences to prevent script injection
    safe_text = text.replace('</script>', '</scr"+"ipt>')
    # Use JSON encoding for additional safety
    json_text = json.dumps(safe_text)
    
    return f'''
    <script>
    if ('speechSynthesis' in window) {{
        const text = {json_text};
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        speechSynthesis.speak(utterance);
    }}
    </script>
    '''

# Initialize services
@st.cache_resource
def get_services():
    gemini_service = GeminiService()
    speech_service = SpeechService()
    database_service = DatabaseService()
    interview_manager = InterviewManager(gemini_service, database_service)
    audio_utils = AudioUtils()
    return gemini_service, speech_service, interview_manager, audio_utils, database_service

def initialize_session_state():
    """Initialize session state variables"""
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = InterviewState()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'interview_completed' not in st.session_state:
        st.session_state.interview_completed = False
    if 'audio_mode' not in st.session_state:
        st.session_state.audio_mode = False
    if 'audio_recorder' not in st.session_state:
        st.session_state.audio_recorder = None
    if 'recording_state' not in st.session_state:
        st.session_state.recording_state = 'stopped'  # stopped, recording, processing

def main():
    st.set_page_config(
        page_title="AI Excel Mock Interviewer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Get services
    gemini_service, speech_service, interview_manager, audio_utils, database_service = get_services()
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 AI-Powered Excel Mock Interviewer")
    st.markdown("### Practice your Excel skills with our intelligent AI interviewer")
    
    # Sidebar
    with st.sidebar:
        st.header("Interview Controls")
        
        # Audio mode toggle
        audio_mode = st.toggle("🎤 Voice Mode", value=st.session_state.audio_mode)
        st.session_state.audio_mode = audio_mode
        
        if audio_mode:
            st.info("🎤 Voice mode enabled. The interviewer will speak questions and listen to your responses.")
        else:
            st.info("💬 Text mode enabled. Type your responses to the interviewer.")
        
        st.divider()
        
        # Interview status
        if st.session_state.interview_started:
            st.success("✅ Interview in progress")
            progress = len(st.session_state.interview_state.responses) / 8
            st.progress(min(progress, 1.0))
            st.write(f"Questions answered: {len(st.session_state.interview_state.responses)}/8")
        else:
            st.info("⏳ Ready to start interview")
        
        # Reset button
        if st.button("🔄 Reset Interview"):
            for key in ['interview_state', 'current_question', 'interview_started', 'interview_completed']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Main content
    if not st.session_state.interview_started:
        show_welcome_screen(interview_manager, speech_service)
    elif st.session_state.interview_completed:
        show_results_screen(interview_manager)
    else:
        conduct_interview(interview_manager, speech_service, audio_utils)

def show_welcome_screen(interview_manager, speech_service):
    """Display welcome screen and start interview"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome to Your Excel Skills Assessment
        
        This AI-powered mock interview will evaluate your Microsoft Excel proficiency across various skill levels.
        
        **What to expect:**
        - 8-10 targeted questions about Excel functions, features, and best practices
        - Real-time evaluation of your responses
        - Detailed feedback on your strengths and areas for improvement
        - Professional interviewer experience with follow-up questions
        
        **Assessment Areas:**
        - Basic Excel operations and navigation
        - Formulas and functions (VLOOKUP, SUMIF, etc.)
        - Data analysis and visualization
        - Advanced features (Pivot Tables, Macros, etc.)
        - Best practices and efficiency tips
        """)
        
        # Candidate information
        st.subheader("Candidate Information")
        col_name, col_exp = st.columns(2)
        with col_name:
            candidate_name = st.text_input("Full Name", placeholder="Enter your full name")
        with col_exp:
            experience_level = st.selectbox(
                "Excel Experience Level",
                ["Beginner (0-1 years)", "Intermediate (1-3 years)", "Advanced (3+ years)"]
            )
        
        # Start interview button
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            if candidate_name:
                st.session_state.interview_state.candidate_name = candidate_name
                st.session_state.interview_state.experience_level = experience_level
                st.session_state.interview_state.start_time = datetime.now()
                st.session_state.interview_started = True
                
                # Generate welcome message
                welcome_msg = interview_manager.start_interview(candidate_name, experience_level)
                st.session_state.interview_state.conversation_history.append({
                    "speaker": "interviewer",
                    "message": welcome_msg,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Save to database
                interview_manager.save_conversation_turn("interviewer", welcome_msg)
                
                # Play welcome message if audio mode
                if st.session_state.audio_mode:
                    try:
                        audio_data = speech_service.text_to_speech(welcome_msg)
                        if audio_data and len(audio_data) > 0:
                            st.audio(audio_data, format="audio/mp3", autoplay=True)
                        else:
                            # Browser-based TTS fallback
                            st.markdown("**🔊 Interviewer says:**")
                            st.info(welcome_msg)
                            # Use secure HTML5 Speech Synthesis fallback
                            tts_html = secure_tts_fallback(welcome_msg)
                            components.html(tts_html, height=0)
                    except Exception as e:
                        st.warning("Audio not available, showing text instead.")
                        st.info(f"🔊 **Interviewer:** {welcome_msg}")
                
                st.rerun()
            else:
                st.error("Please enter your name to continue.")
    
    with col2:
        st.markdown("""
        ### 💡 Tips for Success
        
        - Speak clearly if using voice mode
        - Explain your reasoning
        - Mention specific Excel features
        - Give practical examples
        - Ask for clarification if needed
        """)
        
        # Sample questions preview
        st.markdown("### 📋 Sample Question Types")
        st.info("• How would you remove duplicates from a dataset?")
        st.info("• Explain the difference between VLOOKUP and INDEX-MATCH")
        st.info("• Describe how to create a dynamic chart")

def conduct_interview(interview_manager, speech_service, audio_utils):
    """Main interview interface"""
    st.header("🎯 Interview in Progress")
    
    # Get current question if not exists
    if not st.session_state.current_question:
        question_data = interview_manager.get_next_question(st.session_state.interview_state)
        if question_data:
            st.session_state.current_question = question_data
            # Add to conversation history
            st.session_state.interview_state.conversation_history.append({
                "speaker": "interviewer",
                "message": question_data["question"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Save to database
            interview_manager.save_conversation_turn("interviewer", question_data["question"])
            
            # Play question if audio mode
            if st.session_state.audio_mode:
                try:
                    audio_data = speech_service.text_to_speech(question_data["question"])
                    if audio_data and len(audio_data) > 0:
                        st.audio(audio_data, format="audio/mp3", autoplay=True)
                    else:
                        # Use secure browser-based TTS fallback
                        tts_html = secure_tts_fallback(question_data["question"])
                        components.html(tts_html, height=0)
                except Exception as e:
                    st.info(f"🔊 **Question:** {question_data['question']}")
        else:
            # No more questions, complete interview
            complete_interview(interview_manager)
            return
    
    # Display conversation history
    with st.container():
        st.subheader("Conversation")
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.interview_state.conversation_history[-6:]:  # Show last 6 messages
                if msg["speaker"] == "interviewer":
                    st.chat_message("assistant").write(msg["message"])
                else:
                    st.chat_message("user").write(msg["message"])
    
    # Current question display
    if st.session_state.current_question:
        with st.container():
            st.markdown("---")
            st.markdown("### Current Question:")
            st.info(st.session_state.current_question["question"])
            
            # Response input
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.session_state.audio_mode:
                    st.markdown("**🎤 Voice Input:**")
                    
                    # WebRTC Audio Recording (Primary method)
                    if WEBRTC_AVAILABLE:
                        col_webrtc, col_upload = st.columns([2, 1])
                        
                        with col_webrtc:
                            st.markdown("**🌐 Browser Recording (Recommended):**")
                            
                            # WebRTC streamer for audio recording
                            if WEBRTC_AVAILABLE and webrtc_streamer is not None and WebRtcMode is not None:
                                try:
                                    webrtc_ctx = webrtc_streamer(
                                        key="audio_recorder",
                                        mode=WebRtcMode.SENDONLY,
                                        audio_processor_factory=AudioRecorder,
                                        media_stream_constraints={
                                            "audio": {
                                                "echoCancellation": True,
                                                "noiseSuppression": True,
                                                "autoGainControl": True,
                                                "sampleRate": 16000
                                            },
                                            "video": False
                                        },
                                        rtc_configuration={
                                            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                                        }
                                    )
                                except Exception as e:
                                    st.error(f"WebRTC initialization error: {e}")
                                    st.info("Falling back to file upload for audio input.")
                                    webrtc_ctx = None
                            else:
                                if not WEBRTC_AVAILABLE:
                                    st.info("📌 WebRTC not available. Please use file upload for audio input.")
                                webrtc_ctx = None
                            
                            # Recording controls
                            if webrtc_ctx and webrtc_ctx.audio_processor:
                                rec_button_col1, rec_button_col2 = st.columns(2)
                                
                                with rec_button_col1:
                                    if st.button("🎤 Start Recording", type="primary", disabled=st.session_state.recording_state == 'recording'):
                                        webrtc_ctx.audio_processor.start_recording()
                                        st.session_state.recording_state = 'recording'
                                        st.rerun()
                                
                                with rec_button_col2:
                                    if st.button("⏹️ Stop & Transcribe", disabled=st.session_state.recording_state != 'recording'):
                                        audio_data = webrtc_ctx.audio_processor.stop_recording()
                                        st.session_state.recording_state = 'processing'
                                        
                                        if audio_data:
                                            with st.spinner("Transcribing audio..."):
                                                try:
                                                    gemini_service, speech_service, _, _ = get_services()
                                                    transcription = speech_service.speech_to_text(audio_data)
                                                    
                                                    if transcription:
                                                        st.session_state.transcribed_response = transcription
                                                        st.session_state.recording_state = 'stopped'
                                                        st.success(f"✅ Transcribed: {transcription[:100]}...")
                                                        st.rerun()
                                                    else:
                                                        st.error("Could not transcribe audio. Please try again.")
                                                        st.session_state.recording_state = 'stopped'
                                                except Exception as e:
                                                    st.error(f"Transcription error: {str(e)}")
                                                    st.session_state.recording_state = 'stopped'
                                        else:
                                            st.warning("No audio recorded. Please try again.")
                                            st.session_state.recording_state = 'stopped'
                                
                                # Recording status
                                if st.session_state.recording_state == 'recording':
                                    st.info("🔴 Recording... Click 'Stop & Transcribe' when done.")
                                elif st.session_state.recording_state == 'processing':
                                    st.info("⏳ Processing audio...")
                        
                        with col_upload:
                            st.markdown("**📁 File Upload (Fallback):**")
                            audio_file = st.file_uploader(
                                "Upload audio file", 
                                type=['wav', 'mp3', 'ogg'],  # Removed m4a
                                key="audio_upload",
                                help="Supported: WAV, MP3, OGG"
                            )
                            
                            if audio_file is not None:
                                if st.button("🎯 Transcribe File", type="secondary"):
                                    with st.spinner("Processing file..."):
                                        try:
                                            audio_bytes = audio_file.read()
                                            gemini_service, speech_service, _, _ = get_services()
                                            transcription = speech_service.speech_to_text(audio_bytes)
                                            
                                            if transcription:
                                                st.session_state.transcribed_response = transcription
                                                st.success(f"✅ Transcribed: {transcription[:100]}...")
                                                st.rerun()
                                            else:
                                                st.error("Could not transcribe file.")
                                        except Exception as e:
                                            st.error(f"File processing error: {str(e)}")
                    else:
                        st.warning("⚠️ WebRTC not available. Using file upload only.")
                        audio_file = st.file_uploader(
                            "Upload audio response", 
                            type=['wav', 'mp3', 'ogg'],  # Removed m4a
                            key="audio_upload_fallback"
                        )
                        
                        if audio_file is not None:
                            if st.button("🎯 Process Audio", type="primary"):
                                with st.spinner("Processing audio..."):
                                    try:
                                        audio_bytes = audio_file.read()
                                        gemini_service, speech_service, _, _ = get_services()
                                        transcription = speech_service.speech_to_text(audio_bytes)
                                        
                                        if transcription:
                                            st.session_state.transcribed_response = transcription
                                            st.success(f"Transcribed: {transcription[:100]}...")
                                        else:
                                            st.warning("Could not transcribe audio.")
                                    except Exception as e:
                                        st.error(f"Audio processing error: {str(e)}")
                    
                    # Text input area
                    st.markdown("---")
                    if hasattr(st.session_state, 'transcribed_response') and st.session_state.transcribed_response:
                        response_text = st.text_area(
                            "Your answer (from voice)",
                            value=st.session_state.transcribed_response,
                            height=150,
                            key="response_input",
                            help="Edit transcribed text if needed"
                        )
                        
                        # Clear transcription button
                        if st.button("🗑️ Clear Transcription"):
                            st.session_state.transcribed_response = ""
                            st.rerun()
                    else:
                        st.markdown("**💬 Text Input:**")
                        response_text = st.text_area(
                            "Your answer",
                            placeholder="Record audio above or type your response here...",
                            height=150,
                            key="response_input"
                        )
                else:
                    response_text = st.text_area(
                        "Your answer",
                        placeholder="Type your response here...",
                        height=150,
                        key="response_input"
                    )
            
            with col2:
                st.markdown("**Question Info:**")
                st.write(f"**Category:** {st.session_state.current_question.get('category', 'General')}")
                st.write(f"**Difficulty:** {st.session_state.current_question.get('difficulty', 'Medium')}")
                
                # Submit button
                if st.button("Submit Answer", type="primary", use_container_width=True):
                    if response_text and response_text.strip():
                        process_response(response_text, interview_manager, speech_service)
                    else:
                        st.error("Please provide a response before submitting.")

def process_response(response_text, interview_manager, speech_service):
    """Process user response and generate follow-up"""
    with st.spinner("Evaluating your response..."):
        try:
            # Create response object
            response = Response(
                question_id=st.session_state.current_question["id"],
                answer=response_text,
                timestamp=datetime.now()
            )
            
            # Add to conversation history
            st.session_state.interview_state.conversation_history.append({
                "speaker": "candidate",
                "message": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Save to database
            interview_manager.save_conversation_turn("candidate", response_text)
            
            # Evaluate response
            evaluation = interview_manager.evaluate_response(
                st.session_state.current_question,
                response,
                st.session_state.interview_state
            )
            
            # Add to responses
            st.session_state.interview_state.responses.append(response)
            st.session_state.interview_state.evaluations.append(evaluation)
            
            # Generate follow-up or next question
            follow_up = interview_manager.generate_follow_up(
                st.session_state.current_question,
                response,
                evaluation,
                st.session_state.interview_state
            )
            
            if follow_up:
                # Add follow-up to conversation
                st.session_state.interview_state.conversation_history.append({
                    "speaker": "interviewer",
                    "message": follow_up,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Save to database
                interview_manager.save_conversation_turn("interviewer", follow_up)
                
                # Play follow-up if audio mode
                if st.session_state.audio_mode:
                    try:
                        audio_data = speech_service.text_to_speech(follow_up)
                        if audio_data and len(audio_data) > 0:
                            st.audio(audio_data, format="audio/mp3", autoplay=True)
                        else:
                            # Use secure browser-based TTS fallback
                            tts_html = secure_tts_fallback(follow_up)
                            components.html(tts_html, height=0)
                    except Exception as e:
                        st.info(f"🔊 **Follow-up:** {follow_up}")
            
            # Clear current question to get next one
            st.session_state.current_question = None
            
            # Clear response input and transcribed response
            if "response_input" in st.session_state:
                del st.session_state["response_input"]
            if "transcribed_response" in st.session_state:
                del st.session_state["transcribed_response"]
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")

def complete_interview(interview_manager):
    """Complete the interview and generate report"""
    st.session_state.interview_state.end_time = datetime.now()
    st.session_state.interview_completed = True
    
    # Generate final message
    closing_msg = interview_manager.generate_closing_message(st.session_state.interview_state)
    st.session_state.interview_state.conversation_history.append({
        "speaker": "interviewer",
        "message": closing_msg,
        "timestamp": datetime.now().isoformat()
    })
    
    # Save to database
    interview_manager.save_conversation_turn("interviewer", closing_msg)
    
    # Generate and save final report
    try:
        final_report = interview_manager.generate_interview_report(st.session_state.interview_state)
        interview_manager.complete_interview_session(st.session_state.interview_state, final_report)
    except Exception as e:
        print(f"Error completing interview session: {e}")
    
    st.rerun()

def show_results_screen(interview_manager):
    """Display interview results and feedback"""
    st.header("📊 Interview Complete - Results & Feedback")
    
    with st.spinner("Generating comprehensive feedback report..."):
        try:
            # Generate detailed report
            report = interview_manager.generate_final_report(st.session_state.interview_state)
            
            # Display summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Score", f"{report.overall_score}/100")
            with col2:
                st.metric("Questions Answered", len(st.session_state.interview_state.responses))
            with col3:
                duration = (st.session_state.interview_state.end_time - 
                           st.session_state.interview_state.start_time).total_seconds() / 60
                st.metric("Duration", f"{duration:.1f} min")
            
            # Detailed feedback
            st.subheader("📈 Performance Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ✅ Strengths")
                for strength in report.strengths:
                    st.success(f"• {strength}")
                
                st.markdown("### 📚 Skills Demonstrated")
                for skill in report.skills_demonstrated:
                    st.info(f"• {skill}")
            
            with col2:
                st.markdown("### 🎯 Areas for Improvement")
                for area in report.areas_for_improvement:
                    st.warning(f"• {area}")
                
                st.markdown("### 💡 Recommendations")
                for rec in report.recommendations:
                    st.info(f"• {rec}")
            
            # Detailed breakdown
            st.subheader("📋 Question-by-Question Breakdown")
            for i, (response, evaluation) in enumerate(zip(
                st.session_state.interview_state.responses,
                st.session_state.interview_state.evaluations
            )):
                with st.expander(f"Question {i+1} - Score: {evaluation.get('score', 0)}/10"):
                    st.write(f"**Answer:** {response.answer}")
                    st.write(f"**Feedback:** {evaluation.get('feedback', 'No feedback available')}")
                    if evaluation.get('strengths'):
                        st.success(f"Strengths: {', '.join(evaluation['strengths'])}")
                    if evaluation.get('improvements'):
                        st.warning(f"Improvements: {', '.join(evaluation['improvements'])}")
            
            # Interview transcript
            st.subheader("💬 Full Interview Transcript")
            with st.expander("View Complete Conversation"):
                for msg in st.session_state.interview_state.conversation_history:
                    speaker = "🤖 Interviewer" if msg["speaker"] == "interviewer" else "👤 Candidate"
                    st.write(f"**{speaker}:** {msg['message']}")
                    st.caption(f"Time: {msg['timestamp']}")
                    st.markdown("---")
            
            # Download options
            st.subheader("📥 Download Results")
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate JSON report
                report_data = {
                    "candidate_name": st.session_state.interview_state.candidate_name,
                    "interview_date": st.session_state.interview_state.start_time.isoformat(),
                    "overall_score": report.overall_score,
                    "strengths": report.strengths,
                    "areas_for_improvement": report.areas_for_improvement,
                    "recommendations": report.recommendations,
                    "detailed_feedback": report.detailed_feedback,
                    "conversation_history": st.session_state.interview_state.conversation_history
                }
                
                st.download_button(
                    label="📄 Download Report (JSON)",
                    data=json.dumps(report_data, indent=2),
                    file_name=f"excel_interview_report_{st.session_state.interview_state.candidate_name.replace(' ', '_')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Generate text summary
                text_report = f"""
Excel Mock Interview Report
==========================
Candidate: {st.session_state.interview_state.candidate_name}
Date: {st.session_state.interview_state.start_time.strftime('%Y-%m-%d %H:%M')}
Overall Score: {report.overall_score}/100

STRENGTHS:
{chr(10).join('• ' + s for s in report.strengths)}

AREAS FOR IMPROVEMENT:
{chr(10).join('• ' + a for a in report.areas_for_improvement)}

RECOMMENDATIONS:
{chr(10).join('• ' + r for r in report.recommendations)}

DETAILED FEEDBACK:
{report.detailed_feedback}
"""
                
                st.download_button(
                    label="📝 Download Summary (TXT)",
                    data=text_report,
                    file_name=f"excel_interview_summary_{st.session_state.interview_state.candidate_name.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
            
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            st.info("Interview completed successfully, but there was an issue generating the detailed report.")

if __name__ == "__main__":
    main()
