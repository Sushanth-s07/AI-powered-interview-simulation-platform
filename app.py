"""
AI-Powered Interview Simulation Platform
Production-Grade Flask Backend
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from datetime import datetime
import os
from functools import wraps
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-' + str(uuid.uuid4())

DATABASE = 'database.db'

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database schema"""
    if not os.path.exists(DATABASE):
        db = get_db()
        cursor = db.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Interviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                interview_type TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                overall_score REAL,
                total_questions INTEGER DEFAULT 0,
                status TEXT DEFAULT 'in_progress',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Answers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id INTEGER NOT NULL,
                question_number INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                score REAL,
                feedback TEXT,
                depth_score REAL DEFAULT 0,
                clarity_score REAL DEFAULT 0,
                technical_score REAL DEFAULT 0,
                reasoning_score REAL DEFAULT 0,
                confidence_score REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (interview_id) REFERENCES interviews(id)
            )
        ''')
        
        db.commit()
        db.close()

# ============================================================================
# AI QUESTION GENERATION ENGINE
# ============================================================================

class AIQuestionGenerator:
    """Intelligent question generation system"""
    
    INTERVIEW_TYPES = {
        'hr': {
            'name': 'HR Interview',
            'description': 'Focus on soft skills and past experiences'
        },
        'technical': {
            'name': 'Technical Interview',
            'description': 'Deep dive into technical knowledge'
        },
        'product': {
            'name': 'Product Management Interview',
            'description': 'Product thinking and problem-solving'
        }
    }
    
    HR_QUESTIONS = [
        "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
        "Describe a situation where you failed and how you recovered from it.",
        "Give me an example of when you showed leadership.",
        "Tell me about a time you had to learn something new quickly.",
        "Describe a project where you had to collaborate across teams.",
        "Tell me about your proudest professional achievement.",
        "How do you handle stress and prioritize when overwhelmed?"
    ]
    
    TECHNICAL_QUESTIONS = [
        "Explain the difference between SQL and NoSQL databases. When would you use each?",
        "What are the key principles of object-oriented programming?",
        "Explain REST API design principles.",
        "How would you optimize a slow database query?",
        "What is the importance of code documentation and testing?",
        "Explain the concept of microservices architecture.",
        "How do you approach debugging complex issues?"
    ]
    
    PRODUCT_QUESTIONS = [
        "Walk me through your approach to launching a new product feature.",
        "How would you prioritize features when you have limited resources?",
        "Describe your framework for making product trade-off decisions.",
        "How do you gather and analyze user feedback?",
        "Tell me about a product you love and why.",
        "How would you measure success for a new feature?"
    ]
    
    def __init__(self):
        self.question_index = {}
    
    def generate_next_question(self, interview_type, question_count, previous_answers):
        """Generate next question based on context"""
        if interview_type == 'hr':
            questions = self.HR_QUESTIONS
        elif interview_type == 'technical':
            questions = self.TECHNICAL_QUESTIONS
        elif interview_type == 'product':
            questions = self.PRODUCT_QUESTIONS
        else:
            questions = self.HR_QUESTIONS
        
        # Cycle through questions intelligently
        next_idx = question_count % len(questions)
        question = questions[next_idx]
        
        # Add difficulty context based on previous performance
        difficulty = self._calculate_difficulty(previous_answers, question_count)
        
        return {
            'question': question,
            'question_number': question_count + 1,
            'difficulty': difficulty,
            'type': interview_type
        }
    
    def _calculate_difficulty(self, previous_answers, question_count):
        """Calculate difficulty based on performance"""
        if question_count < 2:
            return 'medium'
        
        if previous_answers:
            avg_score = sum([a.get('score', 50) for a in previous_answers]) / len(previous_answers)
            if avg_score > 80:
                return 'hard'
            elif avg_score > 60:
                return 'medium'
        
        return 'easy'
    
    def should_end_interview(self, question_count, average_score):
        """Determine if interview should end"""
        # End after 5-7 questions or if user requests
        if question_count >= 7:
            return True
        
        if question_count >= 5 and average_score > 0:
            return True
        
        return False

# ============================================================================
# AI ANSWER EVALUATION ENGINE
# ============================================================================

class AIAnswerEvaluator:
    """Intelligent answer evaluation and scoring system"""
    
    TECHNICAL_KEYWORDS = {
        'technical': ['algorithm', 'database', 'api', 'framework', 'architecture', 
                     'optimization', 'implementation', 'protocol', 'data structure'],
        'hr': ['team', 'challenge', 'solution', 'communication', 'leadership',
                      'collaboration', 'learning', 'improvement'],
        'product': ['user', 'feature', 'metric', 'strategy', 'analysis', 'impact',
                   'decision', 'research']
    }
    
    def evaluate_answer(self, answer, question, interview_type):
        """Comprehensive answer evaluation"""
        scores = {
            'depth': self._evaluate_depth(answer),
            'clarity': self._evaluate_clarity(answer),
            'technical': self._evaluate_technical_quality(answer, interview_type),
            'reasoning': self._evaluate_reasoning(answer),
            'confidence': self._evaluate_confidence(answer)
        }
        
        # Calculate overall score
        weights = {'depth': 0.25, 'clarity': 0.20, 'technical': 0.25, 
                   'reasoning': 0.20, 'confidence': 0.10}
        overall_score = sum(scores[key] * weights[key] for key in scores)
        overall_score = min(100, max(0, overall_score))
        
        feedback = self._generate_feedback(scores, answer)
        
        return {
            'overall_score': round(overall_score, 1),
            'depth_score': round(scores['depth'], 1),
            'clarity_score': round(scores['clarity'], 1),
            'technical_score': round(scores['technical'], 1),
            'reasoning_score': round(scores['reasoning'], 1),
            'confidence_score': round(scores['confidence'], 1),
            'feedback': feedback
        }
    
    def _evaluate_depth(self, answer):
        """Evaluate answer depth and completeness"""
        words = answer.split()
        sentences = answer.count('.') + answer.count('!') + answer.count('?')
        
        base_score = min(100, len(words) * 2)
        
        if sentences >= 3 and len(words) > 50:
            base_score = 85
        elif sentences >= 2 and len(words) > 30:
            base_score = 70
        elif len(words) < 20:
            base_score = 40
        
        return max(0, min(100, base_score))
    
    def _evaluate_clarity(self, answer):
        """Evaluate clarity of explanation"""
        words = answer.split()
        
        # Check for common clarity indicators
        clarity_cost = 0
        
        # Penalize very short answers
        if len(words) < 10:
            clarity_cost += 30
        
        # Check for run-on sentences (many commas without periods)
        commas = answer.count(',')
        periods = answer.count('.') + answer.count('!') + answer.count('?')
        
        if periods == 0 and commas > 3:
            clarity_cost += 20
        
        clarity_score = 70 + (len(words) // 5) - clarity_cost
        
        return max(0, min(100, clarity_score))
    
    def _evaluate_technical_quality(self, answer, interview_type):
        """Evaluate technical terminology and accuracy"""
        answer_lower = answer.lower()
        keywords = self.TECHNICAL_KEYWORDS.get(interview_type, [])
        
        keyword_count = sum(1 for keyword in keywords if keyword in answer_lower)
        
        # Base score on keyword usage
        score = 40 + (keyword_count * 10)
        
        # Boost if specific technical terms are used
        if any(term in answer_lower for term in ['implementation', 'algorithm', 'optimization']):
            score += 15
        
        return min(100, score)
    
    def _evaluate_reasoning(self, answer):
        """Evaluate logical reasoning presence"""
        reasoning_words = ['because', 'reason', 'why', 'therefore', 'thus', 'result',
                          'impact', 'approach', 'process', 'method', 'solution']
        
        answer_lower = answer.lower()
        reasoning_count = sum(1 for word in reasoning_words if word in answer_lower)
        
        score = 50 + (reasoning_count * 8)
        
        return min(100, score)
    
    def _evaluate_confidence(self, answer):
        """Evaluate confidence and commitment"""
        # Presence of uncertain language
        uncertain_words = ['maybe', 'possibly', 'i think', 'i guess', 'not sure']
        answer_lower = answer.lower()
        
        uncertainty_count = sum(1 for word in uncertain_words if word in answer_lower)
        
        base_score = 70
        confidence_score = base_score - (uncertainty_count * 15)
        
        # Boost for assertive language
        if any(word in answer_lower for word in ['definitely', 'clearly', 'absolutely', 'successfully']):
            confidence_score += 10
        
        return max(0, min(100, confidence_score))
    
    def _generate_feedback(self, scores, answer):
        """Generate intelligent feedback"""
        feedback_parts = []
        
        # Positive feedback
        if scores['depth'] > 75:
            feedback_parts.append("✓ Strong depth and detailed explanation")
        
        if scores['clarity'] > 75:
            feedback_parts.append("✓ Clear and well-structured response")
        
        if scores['technical'] > 75:
            feedback_parts.append("✓ Good use of technical terminology")
        
        if scores['reasoning'] > 75:
            feedback_parts.append("✓ Logical reasoning and solid examples")
        
        # Improvement areas
        if scores['depth'] < 60:
            feedback_parts.append("⚠ Consider providing more detailed examples and elaboration")
        
        if scores['clarity'] < 60:
            feedback_parts.append("⚠ Try to structure your answer more clearly with distinct points")
        
        if scores['technical'] < 60:
            feedback_parts.append("⚠ Include more relevant technical terminology and specific concepts")
        
        if len(feedback_parts) == 0:
            feedback_parts.append("Good response. Focus on deeper technical details.")
        
        return " | ".join(feedback_parts[:3])

# ============================================================================
# ANALYTICS ENGINE
# ============================================================================

class AnalyticsEngine:
    """Performance analytics and insights generation"""
    
    def generate_analytics(self, interview_id):
        """Generate comprehensive analytics for an interview"""
        db = get_db()
        
        # Fetch interview and answers
        interview = db.execute(
            'SELECT * FROM interviews WHERE id = ?', (interview_id,)
        ).fetchone()
        
        answers = db.execute(
            'SELECT * FROM answers WHERE interview_id = ? ORDER BY question_number',
            (interview_id,)
        ).fetchall()
        
        db.close()
        
        if not answers:
            return None
        
        # Calculate metrics
        scores = [dict(a)['score'] for a in answers if dict(a)['score']]
        
        analytics = {
            'overall_score': round(sum(scores) / len(scores), 1) if scores else 0,
            'total_questions': len(answers),
            'average_score': round(sum(scores) / len(scores), 1) if scores else 0,
            'performance_percentage': round((sum(scores) / (len(scores) * 100)) * 100, 1) if scores else 0,
            'skill_breakdown': self._calculate_skill_breakdown(answers),
            'strengths': self._identify_strengths(answers),
            'weaknesses': self._identify_weaknesses(answers),
            'suggestions': self._generate_suggestions(answers),
            'score_distribution': [dict(a)['score'] for a in answers]
        }
        
        return analytics
    
    def _calculate_skill_breakdown(self, answers):
        """Calculate skill-based breakdown"""
        if not answers:
            return {}
        
        scores_dict = {}
        for answer in answers:
            a = dict(answer)
            scores_dict['communication'] = a.get('clarity_score', 0)
            scores_dict['technical_knowledge'] = a.get('technical_score', 0)
            scores_dict['problem_solving'] = a.get('reasoning_score', 0)
            scores_dict['clarity'] = a.get('clarity_score', 0)
            scores_dict['confidence'] = a.get('confidence_score', 0)
        
        return scores_dict
    
    def _identify_strengths(self, answers):
        """Identify performance strengths"""
        strengths = []
        
        clarity_avg = sum([dict(a).get('clarity_score', 0) for a in answers]) / len(answers)
        technical_avg = sum([dict(a).get('technical_score', 0) for a in answers]) / len(answers)
        reasoning_avg = sum([dict(a).get('reasoning_score', 0) for a in answers]) / len(answers)
        
        if clarity_avg > 70:
            strengths.append("Clear and articulate communication")
        
        if technical_avg > 70:
            strengths.append("Strong technical vocabulary")
        
        if reasoning_avg > 70:
            strengths.append("Logical problem-solving approach")
        
        avg_score = sum([dict(a).get('score', 0) for a in answers]) / len(answers)
        if avg_score > 80:
            strengths.append("Consistent high-quality responses")
        
        return strengths if strengths else ["Solid foundational skills"]
    
    def _identify_weaknesses(self, answers):
        """Identify areas for improvement"""
        weaknesses = []
        
        depth_avg = sum([dict(a).get('depth_score', 0) for a in answers]) / len(answers)
        clarity_avg = sum([dict(a).get('clarity_score', 0) for a in answers]) / len(answers)
        technical_avg = sum([dict(a).get('technical_score', 0) for a in answers]) / len(answers)
        
        if depth_avg < 60:
            weaknesses.append("Answers could be more detailed and comprehensive")
        
        if clarity_avg < 60:
            weaknesses.append("Improve structure and clarity of explanations")
        
        if technical_avg < 60:
            weaknesses.append("Strengthen technical terminology usage")
        
        return weaknesses if weaknesses else []
    
    def _generate_suggestions(self, answers):
        """Generate AI improvement suggestions"""
        suggestions = [
            "Practice providing real-world examples and case studies",
            "Focus on structured answer frameworks (STAR method)",
            "Read technical documentation and stay updated with industry trends",
            "Record yourself answering and review for clarity improvements"
        ]
        
        return suggestions

# Initialize components
question_generator = AIQuestionGenerator()
answer_evaluator = AIAnswerEvaluator()
analytics_engine = AnalyticsEngine()

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        try:
            db = get_db()
            db.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            db.close()
            
            return jsonify({'success': True, 'message': 'Registration successful'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))

# ============================================================================
# DASHBOARD & MAIN ROUTES
# ============================================================================

def login_required(f):
    """Login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page redirect"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    db = get_db()
    
    # Get user interviews
    interviews = db.execute(
        'SELECT * FROM interviews WHERE user_id = ? ORDER BY start_time DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()
    
    # Get statistics
    stats = db.execute(
        'SELECT COUNT(*) as total, AVG(overall_score) as avg_score FROM interviews WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()
    
    db.close()
    
    return render_template('dashboard.html', 
                         interviews=interviews,
                         username=session.get('username', 'User'),
                         stats=dict(stats) if stats else {'total': 0, 'avg_score': 0})

# ============================================================================
# INTERVIEW ROUTES
# ============================================================================

@app.route('/api/start-interview', methods=['POST'])
@login_required
def start_interview():
    """Start a new interview"""
    data = request.get_json()
    interview_type = data.get('interview_type', 'behavioral')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO interviews (user_id, interview_type, status) VALUES (?, ?, ?)',
        (session['user_id'], interview_type, 'in_progress')
    )
    db.commit()
    
    interview_id = cursor.lastrowid
    db.close()
    
    # Get first question
    question_data = question_generator.generate_next_question(interview_type, 0, [])
    
    return jsonify({
        'success': True,
        'interview_id': interview_id,
        'question': question_data
    }), 201

@app.route('/interview/<int:interview_id>')
@login_required
def interview(interview_id):
    """Interview interface"""
    db = get_db()
    interview = db.execute(
        'SELECT * FROM interviews WHERE id = ? AND user_id = ?',
        (interview_id, session['user_id'])
    ).fetchone()
    db.close()
    
    if not interview:
        return redirect(url_for('dashboard'))
    
    return render_template('interview.html', interview_id=interview_id)

@app.route('/api/submit-answer', methods=['POST'])
@login_required
def submit_answer():
    """Submit answer and get evaluation"""
    data = request.get_json()
    interview_id = data.get('interview_id')
    question = data.get('question', '')
    answer = data.get('answer', '').strip()
    question_number = data.get('question_number', 0)
    interview_type = data.get('interview_type', 'behavioral')
    
    if not answer:
        return jsonify({'success': False, 'error': 'Answer cannot be empty'}), 400
    
    # Evaluate answer
    evaluation = answer_evaluator.evaluate_answer(answer, question, interview_type)
    
    # Store in database
    db = get_db()
    db.execute(
        '''INSERT INTO answers 
           (interview_id, question_number, question, answer, score, feedback, 
            depth_score, clarity_score, technical_score, reasoning_score, confidence_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (interview_id, question_number, question, answer, 
         evaluation['overall_score'], evaluation['feedback'],
         evaluation['depth_score'], evaluation['clarity_score'],
         evaluation['technical_score'], evaluation['reasoning_score'],
         evaluation['confidence_score'])
    )
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'evaluation': evaluation
    }), 200

@app.route('/api/next-question', methods=['POST'])
@login_required
def next_question():
    """Get next interview question"""
    data = request.get_json()
    interview_id = data.get('interview_id')
    question_count = data.get('question_count', 0)
    previous_answers = data.get('previous_answers', [])
    interview_type = data.get('interview_type', 'hr')
    
    db = get_db()
    interview = db.execute(
        'SELECT * FROM interviews WHERE id = ? AND user_id = ?',
        (interview_id, session['user_id'])
    ).fetchone()
    db.close()
    
    if not interview:
        return jsonify({'success': False, 'error': 'Interview not found'}), 404
    
    # Check if interview should end
    avg_score = sum([a.get('score', 0) for a in previous_answers]) / len(previous_answers) if previous_answers else 0
    
    if question_generator.should_end_interview(question_count, avg_score):
        return jsonify({
            'success': True,
            'end_interview': True,
            'message': 'Interview complete'
        }), 200
    
    # Generate next question
    question_data = question_generator.generate_next_question(
        interview_type, question_count, previous_answers
    )
    
    return jsonify({
        'success': True,
        'question': question_data
    }), 200

@app.route('/api/end-interview', methods=['POST'])
@login_required
def end_interview():
    """End interview and calculate results"""
    data = request.get_json()
    interview_id = data.get('interview_id')
    
    db = get_db()
    interview = db.execute(
        'SELECT * FROM interviews WHERE id = ? AND user_id = ?',
        (interview_id, session['user_id'])
    ).fetchone()
    
    # Get all answers for this interview
    answers = db.execute(
        'SELECT * FROM answers WHERE interview_id = ?',
        (interview_id,)
    ).fetchall()
    
    if not answers:
        db.close()
        return jsonify({'success': False, 'error': 'No answers found'}), 404
    
    # Calculate overall score
    scores = [dict(a)['score'] for a in answers]
    overall_score = sum(scores) / len(scores)
    
    # Update interview record
    db.execute(
        'UPDATE interviews SET end_time = ?, overall_score = ?, status = ?, total_questions = ? WHERE id = ?',
        (datetime.now(), overall_score, 'completed', len(answers), interview_id)
    )
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'interview_id': interview_id,
        'redirect': url_for('results', interview_id=interview_id)
    }), 200

# ============================================================================
# RESULTS & ANALYTICS ROUTES
# ============================================================================

@app.route('/results/<int:interview_id>')
@login_required
def results(interview_id):
    """Results page with analytics"""
    db = get_db()
    interview = db.execute(
        'SELECT * FROM interviews WHERE id = ? AND user_id = ?',
        (interview_id, session['user_id'])
    ).fetchone()
    db.close()
    
    if not interview:
        return redirect(url_for('dashboard'))
    
    return render_template('results.html', interview_id=interview_id)

@app.route('/api/interview-results/<int:interview_id>')
@login_required
def get_interview_results(interview_id):
    """Get interview results and analytics"""
    db = get_db()
    interview = db.execute(
        'SELECT * FROM interviews WHERE id = ? AND user_id = ?',
        (interview_id, session['user_id'])
    ).fetchone()
    
    answers = db.execute(
        'SELECT * FROM answers WHERE interview_id = ? ORDER BY question_number',
        (interview_id,)
    ).fetchall()
    db.close()
    
    if not interview or not answers:
        return jsonify({'success': False, 'error': 'Results not found'}), 404
    
    # Generate analytics
    analytics = analytics_engine.generate_analytics(interview_id)
    
    return jsonify({
        'success': True,
        'interview': dict(interview),
        'analytics': analytics,
        'answers': [dict(a) for a in answers]
    }), 200

@app.route('/api/history')
@login_required
def get_history():
    """Get interview history"""
    db = get_db()
    interviews = db.execute(
        'SELECT * FROM interviews WHERE user_id = ? ORDER BY start_time DESC',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return jsonify({
        'success': True,
        'interviews': [dict(i) for i in interviews]
    }), 200

# ============================================================================
# HISTORY PAGE
# ============================================================================

@app.route('/history')
@login_required
def history():
    """Interview history page"""
    db = get_db()
    interviews = db.execute(
        'SELECT * FROM interviews WHERE user_id = ? ORDER BY start_time DESC',
        (session['user_id'],)
    ).fetchall()
    
    # Calculate statistics
    stats = db.execute(
        '''SELECT 
           COUNT(*) as total,
           AVG(overall_score) as avg_score,
           MAX(overall_score) as best_score
           FROM interviews WHERE user_id = ?''',
        (session['user_id'],)
    ).fetchone()
    db.close()
    
    return render_template('history.html', 
                          interviews=interviews,
                          username=session.get('username', 'User'),
                          stats=dict(stats) if stats else {'total': 0, 'avg_score': 0, 'best_score': 0})

# ============================================================================
# ANALYTICS PAGE
# ============================================================================

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    db = get_db()
    
    # Get all completed interviews
    interviews = db.execute(
        'SELECT * FROM interviews WHERE user_id = ? AND status = ? ORDER BY start_time DESC',
        (session['user_id'], 'completed')
    ).fetchall()
    
    # Calculate detailed statistics
    stats = {
        'total_interviews': len(interviews),
        'average_score': 0,
        'best_score': 0,
        'worst_score': 0,
        'type_stats': {},
        'scoring_breakdown': {
            'depth': 0, 'clarity': 0, 'technical': 0, 
            'reasoning': 0, 'confidence': 0
        },
        'total_questions': 0,
        'score_distribution': [0, 0, 0, 0, 0]
    }
    
    if interviews:
        # Get all answers for these interviews
        interview_ids = [dict(i)['id'] for i in interviews]
        placeholders = ','.join('?' * len(interview_ids))
        
        answers = db.execute(
            f'SELECT * FROM answers WHERE interview_id IN ({placeholders})',
            interview_ids
        ).fetchall()
        
        # Calculate scores
        scores = [dict(i)['overall_score'] for i in interviews if dict(i)['overall_score']]
        if scores:
            stats['average_score'] = round(sum(scores) / len(scores), 1)
            stats['best_score'] = round(max(scores), 1)
            stats['worst_score'] = round(min(scores), 1)
            
            # Score distribution
            for score in scores:
                if score < 20:
                    stats['score_distribution'][0] += 1
                elif score < 40:
                    stats['score_distribution'][1] += 1
                elif score < 60:
                    stats['score_distribution'][2] += 1
                elif score < 80:
                    stats['score_distribution'][3] += 1
                else:
                    stats['score_distribution'][4] += 1
        
        # Type-based statistics
        interview_types = {}
        for interview in interviews:
            itype = dict(interview)['interview_type']
            if itype not in interview_types:
                interview_types[itype] = []
            interview_types[itype].append(dict(interview)['overall_score'])
        
        for itype, scs in interview_types.items():
            stats['type_stats'][itype] = {
                'avg': round(sum(scs) / len(scs), 1) if scs else 0,
                'total': len(scs)
            }
        
        # Scoring breakdown from answers
        if answers:
            stats['total_questions'] = len(answers)
            depth_scores = [dict(a).get('depth_score', 0) for a in answers if dict(a).get('depth_score')]
            clarity_scores = [dict(a).get('clarity_score', 0) for a in answers if dict(a).get('clarity_score')]
            technical_scores = [dict(a).get('technical_score', 0) for a in answers if dict(a).get('technical_score')]
            reasoning_scores = [dict(a).get('reasoning_score', 0) for a in answers if dict(a).get('reasoning_score')]
            confidence_scores = [dict(a).get('confidence_score', 0) for a in answers if dict(a).get('confidence_score')]
            
            stats['scoring_breakdown']['depth'] = round(sum(depth_scores) / len(depth_scores), 1) if depth_scores else 0
            stats['scoring_breakdown']['clarity'] = round(sum(clarity_scores) / len(clarity_scores), 1) if clarity_scores else 0
            stats['scoring_breakdown']['technical'] = round(sum(technical_scores) / len(technical_scores), 1) if technical_scores else 0
            stats['scoring_breakdown']['reasoning'] = round(sum(reasoning_scores) / len(reasoning_scores), 1) if reasoning_scores else 0
            stats['scoring_breakdown']['confidence'] = round(sum(confidence_scores) / len(confidence_scores), 1) if confidence_scores else 0
    
    db.close()
    
    return render_template('analytics.html',
                          username=session.get('username', 'User'),
                          stats=stats)

# ============================================================================
# SETTINGS PAGE
# ============================================================================

@app.route('/settings')
@login_required
def settings():
    """User settings page"""
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    db.close()
    
    return render_template('settings.html',
                          username=session.get('username', 'User'),
                          user=dict(user) if user else {})

@app.route('/api/update-password', methods=['POST'])
@login_required
def update_password():
    """Update user password"""
    data = request.get_json()
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'success': False, 'error': 'All fields required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'error': 'New passwords do not match'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    
    if not user or not check_password_hash(user['password_hash'], current_password):
        db.close()
        return jsonify({'success': False, 'error': 'Current password is incorrect'}), 401
    
    db.execute(
        'UPDATE users SET password_hash = ? WHERE id = ?',
        (generate_password_hash(new_password), session['user_id'])
    )
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'message': 'Password updated successfully'}), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ============================================================================
# INITIALIZATION & STARTUP
# ============================================================================

if __name__ == '__main__':
    init_db()
    print("🚀 AI Interview Simulation Platform - Starting...")
    print("📊 Backend: Flask | Database: SQLite | AI Engines: Active")
    print("🌐 Server running on: http://localhost:5000")
    print("📖 Login at: http://localhost:5000/login")
    app.run(debug=True, host='0.0.0.0', port=5000)
