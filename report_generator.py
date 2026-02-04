"""
Report Generator Module
Generates comprehensive interview performance reports in PDF format
"""

from fpdf import FPDF
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
import io
import os


class InterviewReport(FPDF):
    """Custom PDF report for interview analysis"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        """Page header"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'AI Mock Interview - Performance Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        """Page footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title: str):
        """Add chapter title"""
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(52, 152, 219)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.set_text_color(0, 0, 0)
        self.ln(4)
    
    def section_title(self, title: str):
        """Add section title"""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(52, 73, 94)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)
    
    def body_text(self, text: str):
        """Add body text"""
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(2)
    
    def add_score_bar(self, label: str, score: float, max_score: float = 100):
        """Add visual score bar"""
        self.set_font('Arial', '', 10)
        self.cell(60, 8, label, 0, 0)
        
        # Draw score bar
        bar_width = 100
        fill_width = (score / max_score) * bar_width
        
        x = self.get_x()
        y = self.get_y()
        
        # Background bar
        self.set_fill_color(220, 220, 220)
        self.rect(x, y + 2, bar_width, 6, 'F')
        
        # Score bar with color based on score
        if score >= 80:
            self.set_fill_color(46, 204, 113)  # Green
        elif score >= 60:
            self.set_fill_color(241, 196, 15)  # Yellow
        else:
            self.set_fill_color(231, 76, 60)  # Red
        
        self.rect(x, y + 2, fill_width, 6, 'F')
        
        # Score text
        self.set_xy(x + bar_width + 5, y)
        self.set_font('Arial', 'B', 10)
        self.cell(20, 8, f'{score:.1f}', 0, 1)


class ReportGenerator:
    """Generate comprehensive interview performance reports"""
    
    def __init__(self):
        """Initialize report generator"""
        self.report_data = {}
    
    def _clean_text(self, text: str) -> str:
        """Clean text for PDF rendering - remove problematic characters"""
        if not text:
            return ""
        # Remove or replace problematic characters
        text = text.replace('–', '-').replace('—', '-')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('…', '...')
        # Remove any non-ASCII characters that might cause issues
        text = ''.join(char if ord(char) < 128 else ' ' for char in text)
        return text.strip()
    
    def generate_report(self, interview_data: Dict, output_path: str) -> bool:
        """
        Generate PDF report from interview data
        
        Args:
            interview_data: Dictionary containing all interview data
            output_path: Path to save PDF report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pdf = InterviewReport()
            pdf.add_page()
            
            # Title and metadata
            self._add_report_header(pdf, interview_data)
            
            # Overall performance summary
            self._add_overall_summary(pdf, interview_data)
            
            # Individual question analysis
            self._add_question_analysis(pdf, interview_data)
            
            # Detailed metrics
            self._add_detailed_metrics(pdf, interview_data)
            
            # Video analysis
            if 'video_analysis' in interview_data:
                self._add_video_analysis(pdf, interview_data['video_analysis'])
            
            # Recommendations
            self._add_recommendations(pdf, interview_data)
            
            # Save PDF
            pdf.output(output_path)
            print(f"✅ Report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return False
    
    def _add_report_header(self, pdf: InterviewReport, data: Dict):
        """Add report header with candidate info"""
        pdf.set_font('Arial', '', 11)
        
        # Date and time
        timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        pdf.cell(0, 8, f'Date: {timestamp}', 0, 1)
        
        # Candidate info if available
        if 'candidate_name' in data:
            pdf.cell(0, 8, f'Candidate: {data["candidate_name"]}', 0, 1)
        
        if 'position' in data:
            pdf.cell(0, 8, f'Position: {data["position"]}', 0, 1)
        
        pdf.ln(5)
    
    def _add_overall_summary(self, pdf: InterviewReport, data: Dict):
        """Add overall performance summary"""
        pdf.chapter_title('Overall Performance Summary')
        
        overall_score = data.get('overall_score', 0)
        
        # Performance rating
        if overall_score >= 85:
            rating = "Excellent"
            color = (46, 204, 113)
        elif overall_score >= 70:
            rating = "Good"
            color = (52, 152, 219)
        elif overall_score >= 50:
            rating = "Average"
            color = (241, 196, 15)
        else:
            rating = "Needs Improvement"
            color = (231, 76, 60)
        
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*color)
        pdf.cell(0, 10, f'Overall Rating: {rating} ({overall_score:.1f}/100)', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        # Key scores
        pdf.section_title('Key Performance Metrics')
        
        metrics = data.get('metrics', {})
        pdf.add_score_bar('Content Quality', metrics.get('content_score', 0))
        pdf.add_score_bar('Communication Clarity', metrics.get('clarity_score', 0))
        pdf.add_score_bar('Confidence Level', metrics.get('confidence_score', 0))
        pdf.add_score_bar('Professionalism', metrics.get('professionalism_score', 0))
        
        pdf.ln(5)
    
    def _add_question_analysis(self, pdf: InterviewReport, data: Dict):
        """Add individual question analysis"""
        pdf.add_page()
        pdf.chapter_title('Question-by-Question Analysis')
        
        questions = data.get('questions', [])
        
        for i, q_data in enumerate(questions, 1):
            pdf.section_title(f'Question {i}')
            
            # Question text
            pdf.set_font('Arial', 'I', 10)
            question_text = self._clean_text(q_data.get("question", "N/A"))
            pdf.multi_cell(0, 6, f'Q: {question_text}')
            pdf.ln(2)
            
            # Answer summary
            pdf.set_font('Arial', '', 10)
            answer = self._clean_text(q_data.get('answer', 'No answer provided'))
            if len(answer) > 200:
                answer = answer[:200] + '...'
            pdf.multi_cell(0, 6, f'A: {answer}')
            pdf.ln(3)
            
            # Scores
            analysis = q_data.get('analysis', {})
            score = analysis.get('overall_score', 0)
            
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(40, 6, 'Score:', 0, 0)
            
            # Color-coded score
            if score >= 80:
                pdf.set_text_color(46, 204, 113)
            elif score >= 60:
                pdf.set_text_color(241, 196, 15)
            else:
                pdf.set_text_color(231, 76, 60)
            
            pdf.cell(30, 6, f'{score:.1f}/100', 0, 1)
            pdf.set_text_color(0, 0, 0)
            
            # Key feedback points
            feedback = q_data.get('feedback', [])
            if feedback:
                pdf.set_font('Arial', '', 9)
                pdf.cell(0, 6, 'Feedback:', 0, 1)
                for fb in feedback[:3]:  # Top 3 feedback points
                    cleaned_fb = self._clean_text(fb)
                    if cleaned_fb:  # Only add if there's content after cleaning
                        pdf.set_x(pdf.l_margin + 5)  # Indent
                        # Use smaller width to prevent overflow
                        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 5, f'- {cleaned_fb}')
            
            pdf.ln(5)
            
            # Add page break if needed
            if i < len(questions) and pdf.get_y() > 240:
                pdf.add_page()
    
    def _add_detailed_metrics(self, pdf: InterviewReport, data: Dict):
        """Add detailed performance metrics"""
        pdf.add_page()
        pdf.chapter_title('Detailed Performance Metrics')
        
        metrics = data.get('detailed_metrics', {})
        
        # Content Analysis
        pdf.section_title('Content Analysis')
        content = metrics.get('content', {})
        pdf.body_text(self._clean_text(f"Average Word Count: {content.get('avg_word_count', 0):.0f} words"))
        pdf.body_text(self._clean_text(f"Examples Provided: {'Yes' if content.get('has_examples', False) else 'No'}"))
        pdf.body_text(self._clean_text(f"Quantifiable Achievements: {'Yes' if content.get('has_quantification', False) else 'No'}"))
        pdf.ln(3)
        
        # Communication Analysis
        pdf.section_title('Communication Analysis')
        comm = metrics.get('communication', {})
        pdf.body_text(self._clean_text(f"Speaking Clarity: {comm.get('clarity', 0):.1f}/100"))
        pdf.body_text(self._clean_text(f"Filler Words (avg per answer): {comm.get('filler_words', 0):.1f}"))
        pdf.body_text(self._clean_text(f"Professional Language: {comm.get('professionalism', 'N/A')}"))
        pdf.ln(3)
        
        # Audio Analysis
        pdf.section_title('Voice Analysis')
        audio = metrics.get('audio', {})
        pdf.body_text(self._clean_text(f"Average Response Duration: {audio.get('avg_duration', 0):.1f} seconds"))
        pdf.body_text(self._clean_text(f"Speaking Rate: {audio.get('speaking_rate', 0):.0f} words per minute"))
        pdf.body_text(self._clean_text(f"Voice Confidence: {audio.get('confidence', 0):.1f}/100"))
        pdf.ln(3)
    
    def _add_video_analysis(self, pdf: InterviewReport, video_data: Dict):
        """Add video analysis section"""
        pdf.section_title('Visual Presence Analysis')
        
        pdf.body_text(self._clean_text(f"Eye Contact: {video_data.get('eye_contact_percentage', 0):.1f}%"))
        pdf.body_text(self._clean_text(f"Dominant Emotion: {video_data.get('dominant_emotion', 'N/A').title()}"))
        pdf.body_text(self._clean_text(f"Posture: {video_data.get('dominant_posture', 'N/A').replace('_', ' ').title()}"))
        pdf.body_text(self._clean_text(f"Engagement Score: {video_data.get('engagement_score', 0):.1f}/100"))
        
        pdf.ln(5)
    
    def _add_recommendations(self, pdf: InterviewReport, data: Dict):
        """Add personalized recommendations"""
        pdf.add_page()
        pdf.chapter_title('Personalized Recommendations')
        
        overall_score = data.get('overall_score', 0)
        
        # Strengths
        pdf.section_title('Key Strengths')
        strengths = data.get('strengths', [
            'Good communication skills',
            'Relevant experience highlighted',
            'Professional demeanor'
        ])
        
        for strength in strengths[:5]:
            pdf.set_font('Arial', '', 10)
            pdf.set_x(pdf.l_margin + 5)
            cleaned_strength = self._clean_text(strength)
            if cleaned_strength:
                pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 6, f'* {cleaned_strength}')
        
        pdf.ln(5)
        
        # Areas for improvement
        pdf.section_title('Areas for Improvement')
        improvements = data.get('improvements', [
            'Provide more specific examples',
            'Reduce use of filler words',
            'Improve eye contact'
        ])
        
        for improvement in improvements[:5]:
            pdf.set_font('Arial', '', 10)
            pdf.set_x(pdf.l_margin + 5)
            cleaned_improvement = self._clean_text(improvement)
            if cleaned_improvement:
                pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 6, f'- {cleaned_improvement}')
        
        pdf.ln(5)
        
        # Action items
        pdf.section_title('Action Items for Next Interview')
        action_items = self._generate_action_items(data)
        
        for i, item in enumerate(action_items, 1):
            pdf.set_font('Arial', '', 10)
            cleaned_item = self._clean_text(item)
            if cleaned_item:
                pdf.multi_cell(0, 6, f'{i}. {cleaned_item}')
                pdf.ln(2)
        
        # Final note
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(52, 73, 94)
        final_note = self._clean_text(
            'Remember: Practice makes perfect! Use this feedback to prepare for your next interview. '
            'Good luck!'
        )
        pdf.multi_cell(0, 6, final_note)
    
    def _generate_action_items(self, data: Dict) -> List[str]:
        """Generate specific action items based on performance"""
        action_items = []
        
        metrics = data.get('metrics', {})
        
        if metrics.get('content_score', 100) < 70:
            action_items.append(
                'Practice using the STAR method (Situation, Task, Action, Result) to structure your answers'
            )
        
        if metrics.get('clarity_score', 100) < 70:
            action_items.append(
                'Record yourself answering common questions and listen for clarity improvements'
            )
        
        if metrics.get('confidence_score', 100) < 70:
            action_items.append(
                'Build confidence by researching the company thoroughly and preparing answers in advance'
            )
        
        video_data = data.get('video_analysis', {})
        if video_data.get('eye_contact_percentage', 100) < 60:
            action_items.append(
                'Practice maintaining eye contact with the camera during mock interviews'
            )
        
        if not action_items:
            action_items = [
                'Continue practicing with diverse question types',
                'Research industry-specific terminology and trends',
                'Refine your personal stories and achievements'
            ]
        
        return action_items[:5]


if __name__ == "__main__":
    # Test the report generator
    print("Report Generator Module - Test Mode")
    print("=" * 50)
    
    # Sample interview data
    sample_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'candidate_name': 'John Doe',
        'position': 'Senior Software Engineer',
        'overall_score': 78.5,
        'metrics': {
            'content_score': 82,
            'clarity_score': 75,
            'confidence_score': 80,
            'professionalism_score': 77
        },
        'questions': [
            {
                'question': 'Tell me about yourself.',
                'answer': 'I am a software engineer with 5 years of experience...',
                'analysis': {'overall_score': 85},
                'feedback': ['Great structure', 'Good examples']
            },
            {
                'question': 'Describe a challenging project.',
                'answer': 'In my previous role, I worked on...',
                'analysis': {'overall_score': 72},
                'feedback': ['Add more quantifiable results', 'Good detail']
            }
        ],
        'detailed_metrics': {
            'content': {'avg_word_count': 95, 'has_examples': True, 'has_quantification': False},
            'communication': {'clarity': 75, 'filler_words': 2.5, 'professionalism': 'Good'},
            'audio': {'avg_duration': 45, 'speaking_rate': 120, 'confidence': 80}
        },
        'video_analysis': {
            'eye_contact_percentage': 65,
            'dominant_emotion': 'confident',
            'dominant_posture': 'centered',
            'engagement_score': 75
        },
        'strengths': [
            'Clear communication',
            'Relevant examples',
            'Professional demeanor'
        ],
        'improvements': [
            'Add more quantifiable achievements',
            'Maintain better eye contact',
            'Reduce filler words'
        ]
    }
    
    generator = ReportGenerator()
    output_file = '/home/claude/sample_interview_report.pdf'
    
    if generator.generate_report(sample_data, output_file):
        print(f"\n✅ Sample report created: {output_file}")
    else:
        print("\n❌ Failed to create sample report")