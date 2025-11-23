from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import random
from utils.resume_parser import parse_resume
from utils.voice_processor import speech_to_text, text_to_speech

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# No CORS needed since we're serving everything from same origin

# Store interview sessions
interview_sessions = {}

class FreeInterviewAgent:
    def __init__(self):
        self.role_questions = {
            'Software Engineer': [
                "Tell me about your experience with programming languages.",
                "Describe a challenging technical problem you solved.",
                "How do you approach code testing and debugging?",
                "What's your experience with version control systems?",
                "Tell me about a project you're particularly proud of.",
                "How do you stay updated with new technologies?",
                "Describe your experience with agile development."
            ],
            'Data Scientist': [
                "What machine learning algorithms are you most comfortable with?",
                "Describe a data analysis project from start to finish.",
                "How do you handle missing or incomplete data?",
                "What's your experience with data visualization?",
                "Tell me about a time you used statistics to solve a problem.",
                "How do you validate your models?",
                "What Python libraries are you familiar with for data science?"
            ],
            'Sales Representative': [
                "Describe your sales process from lead to close.",
                "How do you handle customer objections?",
                "What's your experience with CRM software?",
                "Tell me about a challenging sale you made.",
                "How do you build relationships with clients?",
                "What strategies do you use for prospecting?",
                "How do you measure your sales performance?"
            ],
            'Marketing Manager': [
                "Describe a successful marketing campaign you led.",
                "How do you measure marketing ROI?",
                "What's your experience with digital marketing channels?",
                "How do you develop a marketing strategy?",
                "Tell me about a time you had to work with a tight budget.",
                "How do you analyze market trends?",
                "What tools do you use for marketing analytics?"
            ],
            'Product Manager': [
                "How do you prioritize features in a product roadmap?",
                "Describe a product you managed from concept to launch.",
                "How do you gather and analyze customer requirements?",
                "What metrics do you track for product success?",
                "How do you handle conflicts between engineering and design teams?",
                "Tell me about a time you had to make a tough product decision."
            ],
            'UX Designer': [
                "Walk me through your design process.",
                "How do you conduct user research?",
                "What tools do you use for prototyping?",
                "Describe a design challenge you faced and how you solved it.",
                "How do you measure the success of your designs?",
                "How do you incorporate user feedback into your designs?"
            ]
        }
        
        self.follow_up_questions = [
            "Can you give me a specific example?",
            "What was the outcome of that?",
            "What did you learn from that experience?",
            "How would you approach that differently now?",
            "What was the most challenging part?",
            "How did you measure success in that situation?",
            "What feedback did you receive?",
            "How did that experience prepare you for this role?"
        ]
    
    def generate_question(self, role, conversation_history, resume_data=None):
        # If no questions asked yet, start with role-specific question
        if not conversation_history:
            questions = self.role_questions.get(role, self.role_questions['Software Engineer'])
            question = random.choice(questions)
            
            # If resume data available, customize first question
            if resume_data and 'skills' in resume_data and resume_data['skills']:
                skills = resume_data['skills'][:3]  # Take first 3 skills
                question = f"I see you have experience with {', '.join(skills)}. {question}"
            
            return question
        
        # If there's conversation history, ask follow-up questions
        last_user_answer = None
        for msg in reversed(conversation_history):
            if msg.get('type') == 'answer':
                last_user_answer = msg.get('content')
                break
        
        if last_user_answer:
            # Smart follow-up based on user's answer content
            answer_lower = last_user_answer.lower()
            
            if any(word in answer_lower for word in ['project', 'developed', 'built', 'created', 'designed']):
                return "What were the main technologies or tools used in that project?"
            elif any(word in answer_lower for word in ['team', 'collaborat', 'worked with', 'colleagues']):
                return "What was your specific role and responsibilities in the team?"
            elif any(word in answer_lower for word in ['problem', 'challenge', 'issue', 'difficult']):
                return "What steps did you take to overcome that challenge?"
            elif any(word in answer_lower for word in ['result', 'outcome', 'achieved', 'success']):
                return "How did you measure the impact or success of that outcome?"
            elif any(word in answer_lower for word in ['learn', 'grow', 'improve', 'develop']):
                return "How have you applied what you learned in other situations?"
            elif any(word in answer_lower for word in ['data', 'analysis', 'metrics', 'numbers']):
                return "Can you share specific numbers or metrics that demonstrate the impact?"
        
        # Fallback to random follow-up question
        return random.choice(self.follow_up_questions)
    
        def generate_feedback(self, conversation_history, role):
        # Analyze conversation and provide detailed feedback
            user_answers = [msg['content'] for msg in conversation_history if msg.get('type') == 'answer']
        
            if not user_answers:
                return "No answers provided during the interview. Please try to engage with the questions."
        
            # Analyze answer characteristics
            total_answers = len(user_answers)
            answer_lengths = [len(answer.split()) for answer in user_answers]
            avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
            
            # Simple content analysis
            has_examples = any('example' in answer.lower() or 'specific' in answer.lower() for answer in user_answers)
            has_metrics = any(any(char.isdigit() for char in answer) for answer in user_answers)
            has_team_mention = any('team' in answer.lower() for answer in user_answers)
            
            # Generate personalized feedback - using regular strings to avoid syntax issues
            feedback_lines = [
                "📊 Interview Feedback for " + role + " Position",
                "",
                "✅ STRENGTHS:",
                "• Provided " + str(total_answers) + " substantial answers",
                "• Average answer length: " + str(round(avg_length, 1)) + " words - " + ("Good detail" if avg_length > 20 else "Could use more detail"),
                "• " + ("Used specific examples effectively" if has_examples else "Included some examples"),
                "• " + ("Included measurable results" if has_metrics else "Could add more metrics"),
                "• " + ("Demonstrated teamwork experience" if has_team_mention else "Mentioned individual contributions"),
                "",
                "📈 AREAS FOR IMPROVEMENT:",
                "1. Structure answers using STAR method (Situation, Task, Action, Result)",
                "2. Include more specific numbers and metrics",
                "3. Connect experiences to the target role", 
                "4. Practice concise but comprehensive answers",
                "",
                "💡 TECHNICAL KNOWLEDGE:",
                "• Showed understanding of " + role + " requirements",
                "• Demonstrated relevant experience", 
                "• Could benefit from more technical specifics",
                "",
                "🗣️ COMMUNICATION SKILLS:",
                "• Good engagement level",
                "• Clear expression of ideas",
                "• Work on making answers more structured",
                "",
                "🎯 SPECIFIC TIPS FOR NEXT TIME:",
                "1. Prepare 3-5 detailed accomplishment stories",
                "2. Research common " + role + " interview questions",
                "3. Practice explaining technical concepts simply",
                "4. Record yourself to improve delivery",
                "5. Use the STAR method for behavioral questions",
                "",
                "Remember: Practice makes perfect! Each mock interview helps you improve."
            ]
            
            return "\n".join(feedback_lines)

# Initialize the free agent
interview_agent = FreeInterviewAgent()

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# API Routes
@app.route('/api/start_interview', methods=['POST'])
def start_interview():
    try:
        data = request.json
        session_id = data.get('session_id')
        role = data.get('role', 'Software Engineer')
        
        interview_sessions[session_id] = {
            'role': role,
            'conversation': [],
            'resume_data': None
        }
        
        # Generate first question
        first_question = interview_agent.generate_question(role, [])
        
        interview_sessions[session_id]['conversation'].append({
            'type': 'question',
            'content': first_question
        })
        
        return jsonify({
            'success': True,
            'question': first_question,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    try:
        data = request.json
        session_id = data.get('session_id')
        answer = data.get('answer')
        
        if session_id not in interview_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        # Add user's answer to conversation
        interview_sessions[session_id]['conversation'].append({
            'type': 'answer',
            'content': answer
        })
        
        # Generate next question
        session = interview_sessions[session_id]
        next_question = interview_agent.generate_question(
            session['role'],
            session['conversation'],
            session['resume_data']
        )
        
        session['conversation'].append({
            'type': 'question',
            'content': next_question
        })
        
        return jsonify({
            'success': True,
            'question': next_question
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        session_id = request.form.get('session_id')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Parse resume
        resume_data = parse_resume(file)
        
        if session_id in interview_sessions:
            interview_sessions[session_id]['resume_data'] = resume_data
        
        return jsonify({
            'success': True,
            'resume_data': resume_data,
            'message': 'Resume parsed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/end_interview', methods=['POST'])
def end_interview():
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in interview_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = interview_sessions[session_id]
        feedback = interview_agent.generate_feedback(
            session['conversation'],
            session['role']
        )
        
        return jsonify({
            'success': True,
            'feedback': feedback,
            'full_conversation': session['conversation']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def handle_text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        audio_data = text_to_speech(text)
        return jsonify({'audio': audio_data, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/process-voice-answer', methods=['POST'])
def process_voice_answer():
    """
    Process voice answer - simplified version
    """
    try:
        session_id = request.form.get('session_id')
        
        if session_id not in interview_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        # Since speech-to-text isn't working reliably, we'll use a placeholder
        answer_text = "[Voice answer recorded - please use text mode for accurate transcription]"
        
        # Add user's answer to conversation
        interview_sessions[session_id]['conversation'].append({
            'type': 'answer', 
            'content': answer_text
        })
        
        # Generate next question
        session = interview_sessions[session_id]
        next_question = interview_agent.generate_question(
            session['role'],
            session['conversation'],
            session['resume_data']
        )
        
        session['conversation'].append({
            'type': 'question',
            'content': next_question
        })
        
        # Generate speech for the next question
        question_audio = text_to_speech(next_question)
        
        return jsonify({
            'success': True,
            'answer_text': answer_text,
            'next_question': next_question,
            'question_audio': question_audio,
            'note': 'Speech-to-text requires additional setup. Use text mode for accurate transcription.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'version': '1.0.0',
        'message': 'Interview Practice API is running'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')