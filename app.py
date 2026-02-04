"""
Flask Web Application for AI Mock Interview System
Complete web-based interview with video, audio controls, and real-time analysis
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

# Import custom modules
from document_parser import DocumentParser
from question_generator import QuestionGenerator
from answer_analyzer import AnswerAnalyzer
from report_generator import ReportGenerator

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize modules
doc_parser = DocumentParser()
question_generator = QuestionGenerator()
answer_analyzer = AnswerAnalyzer()
report_generator = ReportGenerator()

# Store interview sessions
interview_sessions = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page - upload resume and job description"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_documents():
    """Handle resume and job description upload"""
    try:
        # Check if files were uploaded
        if 'resume' not in request.files or 'job_description' not in request.files:
            return jsonify({'error': 'Both resume and job description are required'}), 400
        
        resume_file = request.files['resume']
        jd_file = request.files['job_description']
        
        if resume_file.filename == '' or jd_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not (allowed_file(resume_file.filename) and allowed_file(jd_file.filename)):
            return jsonify({'error': 'Invalid file format. Use PDF, DOCX, or TXT'}), 400
        
        # Save files
        resume_filename = secure_filename(resume_file.filename)
        jd_filename = secure_filename(jd_file.filename)
        
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_filename)
        
        resume_file.save(resume_path)
        jd_file.save(jd_path)
        
        # Parse documents
        resume_text = doc_parser.parse_document(resume_path)
        jd_text = doc_parser.parse_document(jd_path)
        
        if not resume_text or not jd_text:
            return jsonify({'error': 'Failed to parse documents'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate questions - 5 behavioral + 5 technical + 10 resume-based
        print("\nGenerating personalized questions...")
        
        # Generate behavioral questions
        behavioral_questions = question_generator._generate_behavioral_questions(5)
        
        # Generate technical questions based on JD
        technical_questions = question_generator._generate_technical_questions(jd_text, 5)
        
        # Generate resume-specific questions (most important!)
        resume_questions = question_generator.generate_resume_specific_questions(
            resume_text, jd_text, 10
        )
        
        # Combine all questions
        all_questions = behavioral_questions + technical_questions + resume_questions
        
        # Store in session
        interview_sessions[session_id] = {
            'resume_text': resume_text,
            'jd_text': jd_text,
            'questions': all_questions,
            'answers': [],
            'current_question': 0,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'total_questions': len(all_questions),
            'question_breakdown': {
                'behavioral': 5,
                'technical': 5,
                'resume_based': 10
            }
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/interview/<session_id>')
def interview_page(session_id):
    """Interview page with video and questions"""
    if session_id not in interview_sessions:
        return "Invalid session", 404
    
    return render_template('interview.html', session_id=session_id)


@app.route('/api/get-question/<session_id>', methods=['GET'])
def get_question(session_id):
    """Get current question"""
    if session_id not in interview_sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    session_data = interview_sessions[session_id]
    current_idx = session_data['current_question']
    questions = session_data['questions']
    
    if current_idx >= len(questions):
        return jsonify({
            'completed': True,
            'message': 'Interview completed'
        })
    
    question = questions[current_idx]
    
    return jsonify({
        'completed': False,
        'question_number': current_idx + 1,
        'total_questions': len(questions),
        'question': question['question'],
        'category': question['category'],
        'difficulty': question.get('difficulty', 'intermediate'),
        'focus_area': question.get('focus_area', 'general')
    })


@app.route('/api/submit-answer/<session_id>', methods=['POST'])
def submit_answer(session_id):
    """Submit answer for current question"""
    if session_id not in interview_sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    try:
        data = request.json
        answer_text = data.get('answer', '')
        audio_duration = data.get('duration', 0)
        
        session_data = interview_sessions[session_id]
        current_idx = session_data['current_question']
        question = session_data['questions'][current_idx]
        
        # Analyze answer
        analysis = answer_analyzer.analyze_answer(
            answer_text,
            question['question']
        )
        
        feedback = answer_analyzer.get_feedback(analysis)
        
        # Store answer
        session_data['answers'].append({
            'question': question['question'],
            'answer': answer_text,
            'category': question['category'],
            'analysis': analysis,
            'feedback': feedback,
            'duration': audio_duration,
            'timestamp': datetime.now().isoformat()
        })
        
        # Move to next question
        session_data['current_question'] += 1
        
        # Check if interview is complete
        is_complete = session_data['current_question'] >= len(session_data['questions'])
        
        return jsonify({
            'success': True,
            'score': analysis['overall_score'],
            'feedback': feedback[:3],  # Top 3 feedback points
            'is_complete': is_complete,
            'next_question': session_data['current_question'] + 1 if not is_complete else None
        })
        
    except Exception as e:
        print(f"Submit answer error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-report/<session_id>', methods=['POST'])
def generate_report(session_id):
    """Generate final PDF report"""
    if session_id not in interview_sessions:
        return jsonify({'error': 'Invalid session'}), 404
    
    try:
        session_data = interview_sessions[session_id]
        
        # Calculate overall metrics
        answers = session_data['answers']
        
        if not answers:
            return jsonify({'error': 'No answers to generate report'}), 400
        
        # Aggregate scores
        total_content = sum(a['analysis']['content_quality']['quality_score'] for a in answers)
        total_clarity = sum(a['analysis']['clarity']['clarity_score'] for a in answers)
        total_confidence = sum(a['analysis']['sentiment']['confidence_level'] for a in answers)
        total_professional = sum(a['analysis']['professionalism']['professionalism_score'] for a in answers)
        
        n = len(answers)
        
        metrics = {
            'content_score': total_content / n,
            'clarity_score': total_clarity / n,
            'confidence_score': total_confidence / n,
            'professionalism_score': total_professional / n
        }
        
        overall_score = (
            metrics['content_score'] * 0.40 +
            metrics['clarity_score'] * 0.25 +
            metrics['confidence_score'] * 0.20 +
            metrics['professionalism_score'] * 0.15
        )
        
        # Prepare report data
        report_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': overall_score,
            'metrics': metrics,
            'questions': [
                {
                    'question': a['question'],
                    'answer': a['answer'],
                    'category': a['category'],
                    'analysis': a['analysis'],
                    'feedback': a['feedback']
                }
                for a in answers
            ],
            'detailed_metrics': {
                'content': {
                    'avg_word_count': sum(a['analysis']['text_metrics']['word_count'] for a in answers) / n,
                    'has_examples': any(a['analysis']['content_quality']['has_examples'] for a in answers),
                    'has_quantification': any(a['analysis']['content_quality']['has_quantification'] for a in answers)
                },
                'communication': {
                    'clarity': metrics['clarity_score'],
                    'filler_words': sum(a['analysis']['clarity']['filler_word_count'] for a in answers) / n,
                    'professionalism': 'Good' if metrics['professionalism_score'] > 70 else 'Needs improvement'
                },
                'audio': {
                    'avg_duration': sum(a.get('duration', 0) for a in answers) / n,
                    'speaking_rate': 0,  # Placeholder
                    'confidence': metrics['confidence_score']
                }
            },
            'strengths': [],
            'improvements': []
        }
        
        # Identify strengths and improvements
        if metrics['content_score'] >= 75:
            report_data['strengths'].append('Strong content quality with good examples')
        else:
            report_data['improvements'].append('Provide more specific examples and quantifiable achievements')
        
        if metrics['clarity_score'] >= 75:
            report_data['strengths'].append('Clear and articulate communication')
        else:
            report_data['improvements'].append('Improve clarity by reducing filler words')
        
        if metrics['confidence_score'] >= 75:
            report_data['strengths'].append('Confident and positive demeanor')
        else:
            report_data['improvements'].append('Speak with more confidence and conviction')
        
        # Generate PDF
        report_filename = f'interview_report_{session_id}.pdf'
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        success = report_generator.generate_report(report_data, report_path)
        
        if success:
            return jsonify({
                'success': True,
                'report_url': f'/download-report/{session_id}',
                'overall_score': overall_score,
                'metrics': metrics
            })
        else:
            return jsonify({'error': 'Failed to generate report'}), 500
        
    except Exception as e:
        print(f"Generate report error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/download-report/<session_id>')
def download_report(session_id):
    """Download generated report"""
    report_filename = f'interview_report_{session_id}.pdf'
    report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
    
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return "Report not found", 404


@app.route('/results/<session_id>')
def results_page(session_id):
    """Results page showing summary and download option"""
    if session_id not in interview_sessions:
        return "Invalid session", 404
    
    return render_template('results.html', session_id=session_id)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 AI MOCK INTERVIEW WEB APPLICATION")
    print("="*70)
    print("\n📱 Starting web server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("\n✨ Features:")
    print("   - Upload resume and job description")
    print("   - Real-time video interview")
    print("   - Record and analyze answers")
    print("   - Generate detailed PDF reports")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)