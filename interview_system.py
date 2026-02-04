"""
Main Interview System
Coordinates all modules to conduct a complete AI-powered mock interview
"""
from dotenv import load_dotenv
load_dotenv()  # This loads the variables from .env into os.environ
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import threading

# Import custom modules
from document_parser import DocumentParser
from question_generator import QuestionGenerator
from audio_handler import AudioHandler
from video_analyzer import VideoAnalyzer
from answer_analyzer import AnswerAnalyzer
from report_generator import ReportGenerator


class InterviewSystem:
    """Main AI-powered mock interview system"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize interview system
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._get_default_config()
        
        # Initialize modules
        print("🔧 Initializing AI Mock Interview System...")
        
        self.doc_parser = DocumentParser()
        self.question_generator = QuestionGenerator(
            api_key=os.getenv('OPENAI_API_KEY'),
            provider='openai'
        )
        self.audio_handler = AudioHandler()
        self.video_analyzer = VideoAnalyzer(
            camera_index=self.config.get('camera_index', 0)
        )
        self.answer_analyzer = AnswerAnalyzer()
        self.report_generator = ReportGenerator()
        
        # Interview data
        self.interview_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'questions': [],
            'overall_score': 0,
            'metrics': {},
            'detailed_metrics': {},
            'video_analysis': {},
            'strengths': [],
            'improvements': []
        }
        
        self.video_thread = None
        self.video_running = False
        
        print("✅ System initialized successfully!\n")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'max_questions': 5,
            'question_time_limit': 120,
            'camera_index': 0,
            'enable_video': True,
            'enable_audio': True,
            'content_weight': 0.40,
            'clarity_weight': 0.25,
            'confidence_weight': 0.20,
            'visual_weight': 0.15
        }
    
    def setup_interview(self, resume_path: str = None, 
                       job_description_path: str = None) -> bool:
        """
        Setup interview by parsing documents and generating questions
        
        Args:
            resume_path: Path to resume file
            job_description_path: Path to job description file
            
        Returns:
            True if setup successful, False otherwise
        """
        print("📄 Setting up interview...")
        
        # Parse resume
        resume_text = ""
        if resume_path and os.path.exists(resume_path):
            print(f"  Reading resume: {resume_path}")
            resume_text = self.doc_parser.parse_document(resume_path)
            if resume_text:
                print(f"  ✅ Resume parsed ({len(resume_text.split())} words)")
            else:
                print("  ⚠️ Could not parse resume")
        else:
            print("  ⚠️ No resume provided")
            resume_text = "Candidate with relevant experience"
        
        # Parse job description
        jd_text = ""
        if job_description_path and os.path.exists(job_description_path):
            print(f"  Reading job description: {job_description_path}")
            jd_text = self.doc_parser.parse_document(job_description_path)
            if jd_text:
                print(f"  ✅ Job description parsed ({len(jd_text.split())} words)")
            else:
                print("  ⚠️ Could not parse job description")
        else:
            print("  ⚠️ No job description provided")
            jd_text = "General software engineering position"
        
        # Generate questions
        print(f"\n🤖 Generating {self.config['max_questions']} interview questions...")
        questions = self.question_generator.generate_questions(
            jd_text, 
            resume_text, 
            self.config['max_questions']
        )
        
        if not questions:
            print("❌ Failed to generate questions")
            return False
        
        self.interview_data['questions'] = [
            {
                'question': q['question'],
                'category': q.get('category', 'general'),
                'difficulty': q.get('difficulty', 'intermediate'),
                'focus_area': q.get('focus_area', 'general'),
                'answer': '',
                'analysis': {},
                'feedback': []
            }
            for q in questions
        ]
        
        print(f"✅ Generated {len(questions)} questions")
        print("\n" + "="*60)
        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q.get('category', 'general')}] {q['question']}")
        print("="*60 + "\n")
        
        return True
    
    def run_interview(self) -> bool:
        """
        Run the complete interview process
        
        Returns:
            True if interview completed, False otherwise
        """
        print("\n🎬 Starting AI Mock Interview")
        print("="*60)
        
        # System check
        if not self._system_check():
            print("❌ System check failed. Please fix issues before continuing.")
            return False
        
        # Start video analysis if enabled
        if self.config.get('enable_video', True):
            self._start_video_analysis()
        
        # Welcome message
        self.audio_handler.speak(
            "Welcome to your AI-powered mock interview. "
            "I will ask you several questions. Please answer each question clearly. "
            "Take your time and speak naturally. Let's begin."
        )
        
        time.sleep(2)
        
        # Ask each question
        for i, q_data in enumerate(self.interview_data['questions'], 1):
            print(f"\n{'='*60}")
            print(f"Question {i} of {len(self.interview_data['questions'])}")
            print(f"Category: {q_data['category']} | Difficulty: {q_data['difficulty']}")
            print(f"{'='*60}\n")
            
            # Ask question
            question = q_data['question']
            print(f"❓ Question: {question}\n")
            
            self.audio_handler.speak(f"Question {i}. {question}")
            time.sleep(1)
            
            self.audio_handler.speak("You may begin your answer now.")
            
            # Listen to answer
            print("🎤 Recording your answer...")
            answer_text, audio_analysis = self.audio_handler.listen(
                timeout=self.config['question_time_limit'],
                phrase_time_limit=self.config['question_time_limit']
            )
            
            if answer_text:
                print(f"\n✅ Answer recorded: {answer_text[:100]}...")
                
                # Analyze answer
                print("🔍 Analyzing your answer...")
                analysis = self.answer_analyzer.analyze_answer(
                    answer_text, 
                    question
                )
                
                # Get feedback
                feedback = self.answer_analyzer.get_feedback(analysis)
                
                # Store results
                q_data['answer'] = answer_text
                q_data['analysis'] = analysis
                q_data['feedback'] = feedback
                q_data['audio_analysis'] = audio_analysis
                
                print(f"   Score: {analysis['overall_score']:.1f}/100")
                print(f"   Top feedback: {feedback[0] if feedback else 'N/A'}")
                
            else:
                print("⚠️ No answer recorded")
                q_data['answer'] = ""
                q_data['analysis'] = self.answer_analyzer._get_empty_analysis()
                q_data['feedback'] = ["No answer provided"]
            
            # Brief pause between questions
            if i < len(self.interview_data['questions']):
                time.sleep(2)
        
        # Stop video analysis
        if self.video_running:
            self._stop_video_analysis()
        
        # Closing message
        print("\n" + "="*60)
        self.audio_handler.speak(
            "Thank you for completing the interview. "
            "I'm now generating your detailed performance report."
        )
        
        # Calculate final scores
        self._calculate_final_scores()
        
        print("\n✅ Interview completed!")
        return True
    
    def _system_check(self) -> bool:
        """
        Perform system check before interview
        
        Returns:
            True if all systems ready, False otherwise
        """
        print("\n🔍 Performing system check...\n")
        
        all_good = True
        
        # Check audio
        if self.config.get('enable_audio', True):
            print("Testing audio system...")
            audio_test = self.audio_handler.test_audio_setup()
            if not audio_test['microphone'] or not audio_test['speakers']:
                print("⚠️ Audio system issues detected")
                all_good = False
            else:
                print("✅ Audio system ready")
        
        # Check video
        if self.config.get('enable_video', True):
            print("\nTesting video system...")
            if self.video_analyzer.start_camera():
                print("✅ Camera ready")
                self.video_analyzer.stop_camera()
            else:
                print("⚠️ Camera not available")
                all_good = False
        
        # Check questions
        if not self.interview_data['questions']:
            print("\n⚠️ No questions loaded")
            all_good = False
        else:
            print(f"\n✅ {len(self.interview_data['questions'])} questions ready")
        
        print()
        return all_good
    
    def _start_video_analysis(self):
        """Start video analysis in background thread"""
        if not self.video_analyzer.start_camera():
            print("⚠️ Could not start video analysis")
            return
        
        self.video_running = True
        
        def video_loop():
            """Background video analysis loop"""
            frame_count = 0
            while self.video_running:
                ret, frame = self.video_analyzer.capture_frame()
                if ret:
                    analysis = self.video_analyzer.analyze_frame(frame)
                    frame_count += 1
                    
                    # Display every 10th frame to reduce overhead
                    if frame_count % 10 == 0:
                        vis_frame = self.video_analyzer.visualize_frame(frame, analysis)
                        # Note: cv2.imshow not used here to avoid blocking
                time.sleep(0.033)  # ~30 FPS
        
        self.video_thread = threading.Thread(target=video_loop, daemon=True)
        self.video_thread.start()
        print("✅ Video analysis started")
    
    def _stop_video_analysis(self):
        """Stop video analysis"""
        self.video_running = False
        if self.video_thread:
            self.video_thread.join(timeout=2)
        
        # Get video summary
        self.interview_data['video_analysis'] = self.video_analyzer.get_session_summary()
        self.video_analyzer.stop_camera()
        print("✅ Video analysis completed")
    
    def _calculate_final_scores(self):
        """Calculate final scores and metrics"""
        print("\n📊 Calculating final scores...")
        
        questions = self.interview_data['questions']
        
        if not questions:
            return
        
        # Aggregate scores
        total_content = 0
        total_clarity = 0
        total_confidence = 0
        total_professional = 0
        
        for q in questions:
            analysis = q.get('analysis', {})
            total_content += analysis.get('content_quality', {}).get('quality_score', 0)
            total_clarity += analysis.get('clarity', {}).get('clarity_score', 0)
            total_confidence += analysis.get('sentiment', {}).get('confidence_level', 0)
            total_professional += analysis.get('professionalism', {}).get('professionalism_score', 0)
        
        n = len(questions)
        
        # Average scores
        avg_content = total_content / n if n > 0 else 0
        avg_clarity = total_clarity / n if n > 0 else 0
        avg_confidence = total_confidence / n if n > 0 else 0
        avg_professional = total_professional / n if n > 0 else 0
        
        # Store metrics
        self.interview_data['metrics'] = {
            'content_score': avg_content,
            'clarity_score': avg_clarity,
            'confidence_score': avg_confidence,
            'professionalism_score': avg_professional
        }
        
        # Calculate weighted overall score
        weights = {
            'content': self.config.get('content_weight', 0.40),
            'clarity': self.config.get('clarity_weight', 0.25),
            'confidence': self.config.get('confidence_weight', 0.20),
            'visual': self.config.get('visual_weight', 0.15)
        }
        
        overall = (
            avg_content * weights['content'] +
            avg_clarity * weights['clarity'] +
            avg_confidence * weights['confidence'] +
            self.interview_data['video_analysis'].get('engagement_score', 50) * weights['visual']
        )
        
        self.interview_data['overall_score'] = round(overall, 2)
        
        # Identify strengths and improvements
        self._identify_strengths_improvements()
        
        print(f"✅ Overall Score: {self.interview_data['overall_score']:.1f}/100")
    
    def _identify_strengths_improvements(self):
        """Identify strengths and areas for improvement"""
        metrics = self.interview_data['metrics']
        video = self.interview_data['video_analysis']
        
        strengths = []
        improvements = []
        
        # Content
        if metrics.get('content_score', 0) >= 75:
            strengths.append("Strong content quality with good examples and details")
        elif metrics.get('content_score', 0) < 60:
            improvements.append("Provide more specific examples and quantifiable achievements")
        
        # Clarity
        if metrics.get('clarity_score', 0) >= 75:
            strengths.append("Clear and articulate communication")
        elif metrics.get('clarity_score', 0) < 60:
            improvements.append("Improve clarity by reducing filler words and organizing thoughts better")
        
        # Confidence
        if metrics.get('confidence_score', 0) >= 75:
            strengths.append("Confident and positive demeanor")
        elif metrics.get('confidence_score', 0) < 60:
            improvements.append("Build confidence through more preparation and practice")
        
        # Professionalism
        if metrics.get('professionalism_score', 0) >= 75:
            strengths.append("Professional language and tone")
        elif metrics.get('professionalism_score', 0) < 60:
            improvements.append("Use more professional language and avoid casual expressions")
        
        # Video
        if video.get('eye_contact_percentage', 0) >= 70:
            strengths.append("Good eye contact and engagement")
        elif video.get('eye_contact_percentage', 0) < 50:
            improvements.append("Maintain better eye contact with the camera")
        
        self.interview_data['strengths'] = strengths if strengths else ["Shows potential for growth"]
        self.interview_data['improvements'] = improvements if improvements else ["Continue practicing"]
    
    def generate_report(self, output_path: str = None) -> str:
        """
        Generate detailed PDF report
        
        Args:
            output_path: Path to save report
            
        Returns:
            Path to generated report
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'/home/claude/interview_report_{timestamp}.pdf'
        
        print(f"\n📝 Generating detailed report: {output_path}")
        
        success = self.report_generator.generate_report(
            self.interview_data,
            output_path
        )
        
        if success:
            return output_path
        else:
            return None


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("   AI-POWERED MOCK INTERVIEW SYSTEM")
    print("="*60 + "\n")
    
    # Get file paths from user
    print("Please provide the following information:")
    print("(Press Enter to skip if not available)\n")
    
    resume_path = input("Resume file path: ").strip().strip('"')
    jd_path = input("Job description file path: ").strip().strip('"')
    
    # Initialize system
    system = InterviewSystem()
    
    # Setup interview
    if not system.setup_interview(resume_path, jd_path):
        print("\n❌ Interview setup failed")
        return
    
    # Confirm to start
    print("\nPress Enter to start the interview (or 'q' to quit): ", end='')
    response = input().strip().lower()
    
    if response == 'q':
        print("Interview cancelled.")
        return
    
    # Run interview
    if system.run_interview():
        # Generate report
        report_path = system.generate_report()
        
        if report_path:
            print(f"\n{'='*60}")
            print("📄 INTERVIEW COMPLETE!")
            print(f"{'='*60}")
            print(f"\nOverall Score: {system.interview_data['overall_score']:.1f}/100")
            print(f"\nReport saved to: {report_path}")
            print("\nThank you for using AI Mock Interview System!")
            print("Good luck with your real interview! 🎉\n")
        else:
            print("\n⚠️ Report generation failed")
    else:
        print("\n❌ Interview process failed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interview interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()