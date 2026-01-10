"""
Realistic seed data generator for exam system.
Generates data as if the system has been running for 4 months.
All data is dynamically generated with no hardcoded fake data.
No Turkish characters in usernames or emails.
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.repositories.teacher_profile_repository import TeacherProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.result_repository import ResultRepository
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.teacher_profile import TeacherProfile, teacher_subjects
from app.models.question import Question, QuestionOption, QuestionTag, QuestionType
from app.models.exam import Exam, ExamQuestion, ExamStatus, GradingPolicy
from app.models.assignment import Assignment, AssignmentStatus
from app.models.attempt import Attempt, AttemptStatus, AttemptQuestionSnapshot, AttemptAnswer
from app.models.result import Result
from datetime import datetime, timezone, timedelta
import random
import json
import string


# English first and last names (no Turkish characters)
ENGLISH_FIRST_NAMES = [
    "John", "Michael", "David", "James", "Robert", "William", "Richard", "Joseph",
    "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
    "Sarah", "Emily", "Jessica", "Jennifer", "Amanda", "Lisa", "Michelle", "Ashley",
    "Melissa", "Nicole", "Stephanie", "Elizabeth", "Lauren", "Rachel", "Rebecca"
]

ENGLISH_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Clark", "Lewis", "Robinson", "Walker", "Young", "King", "Wright"
]

SUBJECTS = [
    {"name": "Mathematics", "description": "Advanced mathematics and calculus"},
    {"name": "Physics", "description": "Classical and modern physics"},
    {"name": "Chemistry", "description": "Organic and inorganic chemistry"},
    {"name": "Biology", "description": "Cell biology and genetics"}
]

QUESTION_TEMPLATES = {
    "Mathematics": [
        {
            "title": "Quadratic Equation",
            "body_template": "Solve the quadratic equation x² - {a}x + {b} = 0. What is the sum of the roots?",
            "options_template": [
                {"text": "{a}", "is_correct": True},
                {"text": "-{a}", "is_correct": False},
                {"text": "{b}", "is_correct": False},
                {"text": "-{b}", "is_correct": False}
            ],
            "explanation_template": "For a quadratic equation ax²+bx+c=0, the sum of roots is -b/a, which equals {a}."
        },
        {
            "title": "Function Evaluation",
            "body_template": "Given f(x) = {a}x + {b}, what is f({c})?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Substitute x={c} into f(x) = {a}x + {b} to get f({c}) = {a}×{c} + {b} = {result}."
        },
        {
            "title": "Exponential Operations",
            "body_template": "Calculate 2^{a} × 2^{b}",
            "options_template": [
                {"text": "2^{sum}", "is_correct": True},
                {"text": "2^{product}", "is_correct": False},
                {"text": "4^{sum}", "is_correct": False},
                {"text": "2^{a+b+1}", "is_correct": False}
            ],
            "explanation_template": "When multiplying powers with the same base, add the exponents: 2^{a} × 2^{b} = 2^{a+b}."
        },
        {
            "title": "Square Root Calculation",
            "body_template": "What is √{a} + √{b}?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "√{a} = {sqrt_a} and √{b} = {sqrt_b}, so the sum is {result}."
        },
        {
            "title": "Linear Equation",
            "body_template": "Solve for x: {a}x + {b} = {c}",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Subtract {b} from both sides: {a}x = {c-b}, then divide by {a}: x = {result}."
        }
    ],
    "Physics": [
        {
            "title": "Kinematics",
            "body_template": "An object moves with velocity {v} m/s. How far does it travel in {t} seconds?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Distance = velocity × time = {v} × {t} = {result} meters."
        },
        {
            "title": "Force Calculation",
            "body_template": "A force of {f} N is applied to a mass of {m} kg. What is the acceleration?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Using F = ma, we get a = F/m = {f}/{m} = {result} m/s²."
        },
        {
            "title": "Energy Conservation",
            "body_template": "A {m} kg object falls from height {h} m. What is its kinetic energy at the bottom? (g=10 m/s²)",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Potential energy converts to kinetic: KE = mgh = {m} × 10 × {h} = {result} J."
        },
        {
            "title": "Ohm's Law",
            "body_template": "A circuit has voltage {v} V and resistance {r} Ω. What is the current?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Using V = IR, we get I = V/R = {v}/{r} = {result} A."
        },
        {
            "title": "Wave Frequency",
            "body_template": "A wave has wavelength {w} m and speed {s} m/s. What is its frequency?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Using v = fλ, we get f = v/λ = {s}/{w} = {result} Hz."
        }
    ],
    "Chemistry": [
        {
            "title": "Molar Mass",
            "body_template": "What is the molar mass of H₂O? (H=1, O=16)",
            "options_template": [
                {"text": "18 g/mol", "is_correct": True},
                {"text": "17 g/mol", "is_correct": False},
                {"text": "19 g/mol", "is_correct": False},
                {"text": "20 g/mol", "is_correct": False}
            ],
            "explanation_template": "H₂O has 2 H atoms (2×1=2) and 1 O atom (16), total = 18 g/mol."
        },
        {
            "title": "pH Calculation",
            "body_template": "A solution has [H⁺] = 1×10⁻{p} M. What is the pH?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "pH = -log[H⁺] = -log(10⁻{p}) = {p}."
        },
        {
            "title": "Balancing Equations",
            "body_template": "Balance: H₂ + O₂ → H₂O. How many H₂ molecules are needed?",
            "options_template": [
                {"text": "2", "is_correct": True},
                {"text": "1", "is_correct": False},
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": False}
            ],
            "explanation_template": "2H₂ + O₂ → 2H₂O balances the equation with 2 H₂ molecules."
        },
        {
            "title": "Avogadro's Number",
            "body_template": "How many atoms are in {m} moles of carbon?",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Number of atoms = moles × Avogadro's number = {m} × 6.022×10²³ = {result}."
        },
        {
            "title": "Ideal Gas Law",
            "body_template": "A gas at {t} K and {p} atm has volume {v} L. How many moles? (R=0.0821)",
            "options_template": [
                {"text": "{result}", "is_correct": True},
                {"text": "{wrong1}", "is_correct": False},
                {"text": "{wrong2}", "is_correct": False},
                {"text": "{wrong3}", "is_correct": False}
            ],
            "explanation_template": "Using PV = nRT, we get n = PV/(RT) = ({p}×{v})/(0.0821×{t}) = {result} mol."
        }
    ],
    "Biology": [
        {
            "title": "Cell Structure",
            "body_template": "Which organelle is responsible for protein synthesis?",
            "options_template": [
                {"text": "Ribosome", "is_correct": True},
                {"text": "Mitochondria", "is_correct": False},
                {"text": "Nucleus", "is_correct": False},
                {"text": "Golgi apparatus", "is_correct": False}
            ],
            "explanation_template": "Ribosomes are the cellular structures responsible for protein synthesis."
        },
        {
            "title": "DNA Structure",
            "body_template": "In DNA, adenine (A) pairs with:",
            "options_template": [
                {"text": "Thymine (T)", "is_correct": True},
                {"text": "Guanine (G)", "is_correct": False},
                {"text": "Cytosine (C)", "is_correct": False},
                {"text": "Uracil (U)", "is_correct": False}
            ],
            "explanation_template": "In DNA, A pairs with T, and G pairs with C through hydrogen bonds."
        },
        {
            "title": "Photosynthesis",
            "body_template": "What is the primary product of photosynthesis?",
            "options_template": [
                {"text": "Glucose", "is_correct": True},
                {"text": "Oxygen", "is_correct": False},
                {"text": "Carbon dioxide", "is_correct": False},
                {"text": "Water", "is_correct": False}
            ],
            "explanation_template": "Glucose (C₆H₁₂O₆) is the primary organic product of photosynthesis."
        },
        {
            "title": "Mitosis",
            "body_template": "How many daughter cells are produced in mitosis?",
            "options_template": [
                {"text": "2", "is_correct": True},
                {"text": "4", "is_correct": False},
                {"text": "1", "is_correct": False},
                {"text": "8", "is_correct": False}
            ],
            "explanation_template": "Mitosis produces 2 genetically identical daughter cells from one parent cell."
        },
        {
            "title": "Enzyme Function",
            "body_template": "Enzymes function by:",
            "options_template": [
                {"text": "Lowering activation energy", "is_correct": True},
                {"text": "Increasing activation energy", "is_correct": False},
                {"text": "Creating new reactions", "is_correct": False},
                {"text": "Consuming energy", "is_correct": False}
            ],
            "explanation_template": "Enzymes are biological catalysts that lower the activation energy required for reactions."
        }
    ]
}


def generate_english_name():
    """Generate a random English first and last name."""
    return random.choice(ENGLISH_FIRST_NAMES), random.choice(ENGLISH_LAST_NAMES)


def generate_username(first_name: str, last_name: str, existing_usernames: set) -> str:
    """Generate a unique username from first and last name."""
    base = f"{first_name.lower()}.{last_name.lower()}"
    username = base
    counter = 1
    while username in existing_usernames:
        username = f"{base}{counter}"
        counter += 1
    return username


def generate_email(first_name: str, last_name: str, domain: str, existing_emails: set) -> str:
    """Generate a unique email from first and last name."""
    base = f"{first_name.lower()}.{last_name.lower()}@{domain}"
    email = base
    counter = 1
    while email in existing_emails:
        email = f"{first_name.lower()}.{last_name.lower()}{counter}@{domain}"
        counter += 1
    return email


def random_timestamp_in_range(start: datetime, end: datetime) -> datetime:
    """Generate a random timestamp between start and end."""
    if end <= start:
        return start
    time_between = end - start
    total_seconds = int(time_between.total_seconds())
    if total_seconds <= 0:
        return start
    random_seconds = random.randint(0, total_seconds)
    return start + timedelta(seconds=random_seconds)


def calculate_exam_dates(base_date: datetime, duration_days: int = 7) -> tuple:
    """Calculate exam start and end dates."""
    start_at = base_date + timedelta(days=random.randint(1, 3))
    end_at = start_at + timedelta(days=duration_days)
    return start_at, end_at


def generate_question_content(subject_name: str, difficulty: int, question_index: int):
    """Generate question content dynamically based on subject."""
    templates = QUESTION_TEMPLATES.get(subject_name, QUESTION_TEMPLATES["Mathematics"])
    template = templates[question_index % len(templates)]
    
    # Generate random values for templates
    a = random.randint(2, 10)
    b = random.randint(1, 10)
    c = random.randint(1, 20)
    v = random.randint(5, 20)
    t = random.randint(1, 10)
    f = random.randint(10, 100)
    m = random.randint(1, 10)
    h = random.randint(5, 50)
    p = random.randint(3, 10)
    w = random.randint(1, 10)
    s = random.randint(10, 100)
    r_val = random.randint(1, 10)
    
    # Replace placeholders in body
    body = template["body_template"]
    body = body.replace("{a}", str(a))
    body = body.replace("{b}", str(b))
    body = body.replace("{c}", str(c))
    body = body.replace("{v}", str(v))
    body = body.replace("{t}", str(t))
    body = body.replace("{f}", str(f))
    body = body.replace("{m}", str(m))
    body = body.replace("{h}", str(h))
    body = body.replace("{p}", str(p))
    body = body.replace("{w}", str(w))
    body = body.replace("{s}", str(s))
    body = body.replace("{r}", str(r_val))
    
    # Process options - calculate correct answers
    options = []
    correct_result = None
    wrong_options = []
    
    if "Quadratic Equation" in template["title"]:
        correct_result = a
        wrong_options = [a + 1, a - 1, b, -a]
    elif "Function Evaluation" in template["title"]:
        correct_result = a * c + b
        wrong_options = [a * c - b, a * c, a + b + c, (a + b) * c]
    elif "Exponential Operations" in template["title"]:
        correct_result = f"2^{a+b}"
        wrong_options = [f"2^{a*b}", f"4^{a+b}", f"2^{a+b+1}", f"2^{a*b}"]
    elif "Square Root Calculation" in template["title"]:
        sqrt_a = int(a**0.5)
        sqrt_b = int(b**0.5)
        correct_result = sqrt_a + sqrt_b
        wrong_options = [int((a+b)**0.5), sqrt_a * sqrt_b, a + b, abs(sqrt_a - sqrt_b)]
    elif "Linear Equation" in template["title"]:
        correct_result = round((c - b) / a, 2)
        wrong_options = [round((c + b) / a, 2), c - b - a, round((c - b) * a, 2), round(c / a, 2)]
    elif "Kinematics" in template["title"]:
        correct_result = v * t
        wrong_options = [v / t, v + t, v - t, v * t + 1]
    elif "Force Calculation" in template["title"]:
        correct_result = round(f / m, 1)
        wrong_options = [round(f * m, 1), f + m, f - m, round(f / (m + 1), 1)]
    elif "Energy Conservation" in template["title"]:
        correct_result = m * 10 * h
        wrong_options = [m * h, m * 5 * h, 0.5 * m * 10 * h, m + h]
    elif "Ohm's Law" in template["title"]:
        correct_result = round(v / r_val, 2)
        wrong_options = [round(v * r_val, 2), v + r_val, v - r_val, round(v / (r_val + 1), 2)]
    elif "Wave Frequency" in template["title"]:
        correct_result = round(s / w, 1)
        wrong_options = [round(s * w, 1), round(w / s, 1), s + w, round(s / (w + 1), 1)]
    elif "pH Calculation" in template["title"]:
        correct_result = p
        wrong_options = [-p, 14 - p, p + 1, p - 1]
    elif "Avogadro's Number" in template["title"]:
        correct_result = f"{m * 6.022e23:.2e}"
        wrong_options = [f"{m * 6.022e22:.2e}", f"{m * 6.022e24:.2e}", str(m), f"{m * 6.022e21:.2e}"]
    elif "Ideal Gas Law" in template["title"]:
        t_k = random.randint(200, 400)
        p_atm = random.randint(1, 5)
        v_l = random.randint(1, 10)
        correct_result = round((p_atm * v_l) / (0.0821 * t_k), 3)
        wrong_options = [
            round((p_atm * v_l) * (0.0821 * t_k), 3),
            round(p_atm + v_l + t_k, 3),
            round(p_atm * v_l * t_k, 3),
            round((p_atm * v_l) / (0.0821 * (t_k + 50)), 3)
        ]
        body = body.replace("{t}", str(t_k))
        body = body.replace("{p}", str(p_atm))
        body = body.replace("{v}", str(v_l))
    
    # Generate options based on template
    wrong_idx = 0
    for opt_template in template["options_template"]:
        text = opt_template["text"]
        
        # Replace placeholders
        if "{a}" in text:
            text = text.replace("{a}", str(a))
        if "{b}" in text:
            text = text.replace("{b}", str(b))
        if "{c}" in text:
            text = text.replace("{c}", str(c))
        if "{sum}" in text:
            text = text.replace("{sum}", str(a + b))
        if "{product}" in text:
            text = text.replace("{product}", str(a * b))
        if "{sqrt_a}" in text:
            text = text.replace("{sqrt_a}", str(int(a**0.5)))
        if "{sqrt_b}" in text:
            text = text.replace("{sqrt_b}", str(int(b**0.5)))
        if "{result}" in text and correct_result is not None:
            text = text.replace("{result}", str(correct_result))
        if "{wrong1}" in text and wrong_options:
            text = text.replace("{wrong1}", str(wrong_options[wrong_idx % len(wrong_options)]))
            wrong_idx += 1
        if "{wrong2}" in text and wrong_options:
            text = text.replace("{wrong2}", str(wrong_options[wrong_idx % len(wrong_options)]))
            wrong_idx += 1
        if "{wrong3}" in text and wrong_options:
            text = text.replace("{wrong3}", str(wrong_options[wrong_idx % len(wrong_options)]))
            wrong_idx += 1
        if "{v}" in text:
            text = text.replace("{v}", str(v))
        if "{t}" in text:
            text = text.replace("{t}", str(t))
        if "{f}" in text:
            text = text.replace("{f}", str(f))
        if "{m}" in text:
            text = text.replace("{m}", str(m))
        if "{h}" in text:
            text = text.replace("{h}", str(h))
        if "{p}" in text:
            text = text.replace("{p}", str(p))
        if "{w}" in text:
            text = text.replace("{w}", str(w))
        if "{s}" in text:
            text = text.replace("{s}", str(s))
        if "{r}" in text:
            text = text.replace("{r}", str(r_val))
        
        # Determine if this is correct
        is_correct = opt_template["is_correct"]
        if correct_result is not None and "{result}" in opt_template["text"]:
            is_correct = True
        elif wrong_options and any(w in opt_template["text"] for w in ["{wrong1}", "{wrong2}", "{wrong3}"]):
            is_correct = False
        
        options.append({
            "text": text,
            "is_correct": is_correct
        })
    
    # Replace placeholders in explanation
    explanation = template["explanation_template"]
    explanation = explanation.replace("{a}", str(a))
    explanation = explanation.replace("{b}", str(b))
    explanation = explanation.replace("{c}", str(c))
    if "{result}" in explanation and correct_result is not None:
        explanation = explanation.replace("{result}", str(correct_result))
    if "{v}" in explanation:
        explanation = explanation.replace("{v}", str(v))
    if "{t}" in explanation:
        explanation = explanation.replace("{t}", str(t))
    if "{f}" in explanation:
        explanation = explanation.replace("{f}", str(f))
    if "{m}" in explanation:
        explanation = explanation.replace("{m}", str(m))
    if "{h}" in explanation:
        explanation = explanation.replace("{h}", str(h))
    if "{p}" in explanation:
        explanation = explanation.replace("{p}", str(p))
    if "{s}" in explanation:
        explanation = explanation.replace("{s}", str(s))
    if "{w}" in explanation:
        explanation = explanation.replace("{w}", str(w))
    if "{r}" in explanation:
        explanation = explanation.replace("{r}", str(r_val))
    
    return {
        "title": template["title"],
        "body": body,
        "options": options,
        "explanation": explanation
    }


def generate_exam_name(subject_name: str, exam_index: int) -> str:
    """Generate exam name based on subject and index."""
    exam_types = ["Midterm Exam", "Final Exam", "Quiz", "Practice Test", "Assessment"]
    exam_type = exam_types[exam_index % len(exam_types)]
    return f"{subject_name} {exam_type} {exam_index + 1}"


def cleanup_database(db: Session):
    """Delete all existing data in correct order."""
    print("Cleaning up existing data...")
    
    # Delete in order respecting foreign keys
    db.query(AttemptAnswer).delete()
    db.query(AttemptQuestionSnapshot).delete()
    db.query(Attempt).delete()
    db.query(Result).delete()
    db.query(Assignment).delete()
    db.query(ExamQuestion).delete()
    db.query(QuestionOption).delete()
    db.query(QuestionTag).delete()
    db.query(Question).delete()
    db.query(Exam).delete()
    
    # Delete teacher profiles and associations
    db.execute(teacher_subjects.delete())
    db.query(TeacherProfile).delete()
    db.query(Subject).delete()
    db.query(User).delete()
    
    db.commit()
    print("Database cleaned.")


def seed_realistic_data():
    """Generate realistic seed data as if system ran for 4 months."""
    db: Session = SessionLocal()
    
    try:
        # Cleanup first
        cleanup_database(db)
        
        # Initialize repositories
        user_repo = UserRepository(db)
        subject_repo = SubjectRepository(db)
        profile_repo = TeacherProfileRepository(db)
        question_repo = QuestionRepository(db)
        exam_repo = ExamRepository(db)
        assignment_repo = AssignmentRepository(db)
        attempt_repo = AttemptRepository(db)
        result_repo = ResultRepository(db)
        
        # Calculate timeline (4 months ago to now)
        now = datetime.now(timezone.utc)
        four_months_ago = now - timedelta(days=120)
        
        existing_usernames = set()
        existing_emails = set()
        
        # Month 1: System setup (Days 1-30)
        print("Generating users...")
        
        # 1. Create Admin (Day 1)
        admin = user_repo.create(
            username="admin",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            email="admin@university.edu"
        )
        admin.created_at = four_months_ago
        existing_usernames.add("admin")
        existing_emails.add("admin@university.edu")
        db.commit()
        print(f"  Created admin: {admin.username}")
        
        # 2. Create 4 Teachers (Days 2-5)
        teachers = []
        teacher_subjects_list = []
        for i in range(4):
            first_name, last_name = generate_english_name()
            username = generate_username(first_name, last_name, existing_usernames)
            email = generate_email(first_name, last_name, "university.edu", existing_emails)
            
            teacher = user_repo.create(
                username=username,
                password_hash=hash_password("teacher123"),
                role=UserRole.TEACHER,
                email=email
            )
            teacher.created_at = four_months_ago + timedelta(days=2 + i)
            existing_usernames.add(username)
            existing_emails.add(email)
            teachers.append(teacher)
            teacher_subjects_list.append(SUBJECTS[i])
            print(f"  Created teacher {i+1}: {username} ({first_name} {last_name})")
        
        db.commit()
        
        # 3. Create 4 Subjects (Days 3-6)
        print("Generating subjects...")
        subjects = []
        for i, subject_data in enumerate(SUBJECTS):
            subject = Subject(
                name=subject_data["name"],
                description=subject_data["description"],
                is_active=True
            )
            subject.created_at = four_months_ago + timedelta(days=3 + i)
            subject.updated_at = subject.created_at
            subject = subject_repo.create(subject)
            subjects.append(subject)
            print(f"  Created subject: {subject.name}")
        
        db.commit()
        
        # 4. Create Teacher Profiles (Days 4-7)
        print("Generating teacher profiles...")
        for i, teacher in enumerate(teachers):
            first_name, last_name = generate_english_name()
            # Ensure unique names
            while f"{first_name.lower()}.{last_name.lower()}" in existing_usernames:
                first_name, last_name = generate_english_name()
            
            profile = TeacherProfile(
                user_id=teacher.id,
                first_name=first_name,
                last_name=last_name,
                bio=f"Experienced {subjects[i].name} instructor with {random.randint(5, 20)} years of teaching experience.",
                phone=f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
            )
            profile.created_at = four_months_ago + timedelta(days=4 + i)
            profile.updated_at = profile.created_at
            profile = profile_repo.create(profile)
            
            # Assign subject to teacher
            db.execute(teacher_subjects.insert().values(
                teacher_id=teacher.id,
                subject_id=subjects[i].id
            ))
            print(f"  Created profile for {teacher.username}: {first_name} {last_name}")
        
        db.commit()
        
        # 5. Create 20 Students (Days 40-60, spread over Month 2)
        print("Generating students...")
        students = []
        for i in range(20):
            first_name, last_name = generate_english_name()
            username = generate_username(first_name, last_name, existing_usernames)
            email = generate_email(first_name, last_name, "student.university.edu", existing_emails)
            
            student = user_repo.create(
                username=username,
                password_hash=hash_password("student123"),
                role=UserRole.STUDENT,
                email=email
            )
            # Students register over month 2 (days 40-60)
            student.created_at = random_timestamp_in_range(
                four_months_ago + timedelta(days=40),
                four_months_ago + timedelta(days=60)
            )
            existing_usernames.add(username)
            existing_emails.add(email)
            students.append(student)
        
        db.commit()
        print(f"  Created {len(students)} students")
        
        # 6. Generate Questions (40 questions, 5 per exam)
        # Questions created over months 1-2 (Days 8-45)
        print("Generating questions...")
        all_questions = []
        question_creation_start = four_months_ago + timedelta(days=8)
        question_creation_end = four_months_ago + timedelta(days=45)
        
        for exam_idx in range(8):
            teacher_idx = exam_idx // 2
            subject = subjects[teacher_idx]
            questions_for_exam = []
            
            for q_idx in range(5):
                question_data = generate_question_content(subject.name, random.randint(1, 5), q_idx)
                
                # Determine question type
                question_type = QuestionType.MULTIPLE_CHOICE if len(question_data["options"]) > 2 else QuestionType.TRUE_FALSE
                
                question = Question(
                    owner_id=teachers[teacher_idx].id,
                    title=question_data["title"],
                    body=question_data["body"],
                    difficulty=random.randint(1, 5),
                    type=question_type,
                    explanation=question_data["explanation"]
                )
                question.created_at = random_timestamp_in_range(question_creation_start, question_creation_end)
                question.updated_at = question.created_at
                question = question_repo.create(question)
                
                # Create options
                for opt_idx, opt_data in enumerate(question_data["options"]):
                    option = QuestionOption(
                        question_id=question.id,
                        text=opt_data["text"],
                        is_correct=1 if opt_data["is_correct"] else 0
                    )
                    db.add(option)
                
                # Add tag
                tag = QuestionTag(
                    question_id=question.id,
                    tag=subject.name.lower()
                )
                db.add(tag)
                
                questions_for_exam.append(question)
                all_questions.append(question)
            
            db.commit()
        
        print(f"  Created {len(all_questions)} questions")
        
        # 7. Generate 8 Exams (2 per teacher, spread over 4 months)
        print("Generating exams...")
        exams = []
        exam_creation_times = [
            # Month 1: Days 15-25
            four_months_ago + timedelta(days=15),
            four_months_ago + timedelta(days=20),
            # Month 2: Days 35-55
            four_months_ago + timedelta(days=35),
            four_months_ago + timedelta(days=45),
            # Month 3: Days 61-80
            four_months_ago + timedelta(days=65),
            four_months_ago + timedelta(days=75),
            # Month 4: Days 91-110
            four_months_ago + timedelta(days=95),
            four_months_ago + timedelta(days=105),
        ]
        
        grading_policies = [GradingPolicy.IMMEDIATE, GradingPolicy.AFTER_END, GradingPolicy.MANUAL]
        exam_statuses = [ExamStatus.PUBLISHED, ExamStatus.DRAFT]
        
        for exam_idx in range(8):
            teacher_idx = exam_idx // 2
            subject = subjects[teacher_idx]
            exam_name = generate_exam_name(subject.name, exam_idx)
            
            created_at = exam_creation_times[exam_idx]
            start_at, end_at = calculate_exam_dates(created_at, duration_days=random.randint(5, 14))
            
            # Some exams in past, some in future
            if exam_idx < 4:
                # Past exams
                end_at = now - timedelta(days=random.randint(1, 30))
                start_at = end_at - timedelta(days=7)
            else:
                # Future exams
                start_at = now + timedelta(days=random.randint(1, 30))
                end_at = start_at + timedelta(days=7)
            
            exam = Exam(
                owner_id=teachers[teacher_idx].id,
                name=exam_name,
                description=f"Comprehensive {subject.name} examination covering key topics and concepts.",
                duration_minutes=random.randint(60, 120),
                start_at=start_at.replace(tzinfo=None),
                end_at=end_at.replace(tzinfo=None),
                attempts_allowed=1,
                shuffle_questions=random.choice([True, False]),
                shuffle_options=random.choice([True, False]),
                grading_policy=random.choice(grading_policies),
                pass_score=random.randint(50, 70),
                status=exam_statuses[0] if exam_idx < 6 else exam_statuses[1]  # Most published
            )
            exam.created_at = created_at.replace(tzinfo=None)
            exam = exam_repo.create(exam)
            
            # Add 5 questions to exam
            questions_for_exam = all_questions[exam_idx * 5:(exam_idx + 1) * 5]
            for sort_order, question in enumerate(questions_for_exam, 1):
                exam_question = ExamQuestion(
                    exam_id=exam.id,
                    question_id=question.id,
                    sort_order=sort_order,
                    points=20  # 5 questions × 20 points = 100
                )
                db.add(exam_question)
            
            exams.append(exam)
            db.commit()
            print(f"  Created exam {exam_idx+1}: {exam.name} (Teacher: {teachers[teacher_idx].username})")
        
        # 8. Generate Assignments (assign students to published exams)
        print("Generating assignments...")
        assignments = []
        published_exams = [e for e in exams if e.status == ExamStatus.PUBLISHED]
        
        for exam in published_exams:
            # Assign 60-80% of students to each exam
            num_assignments = int(len(students) * random.uniform(0.6, 0.8))
            assigned_students = random.sample(students, num_assignments)
            
            for student in assigned_students:
                assignment = Assignment(
                    exam_id=exam.id,
                    student_id=student.id,
                    status=random.choice([
                        AssignmentStatus.ASSIGNED,
                        AssignmentStatus.STARTED,
                        AssignmentStatus.SUBMITTED,
                        AssignmentStatus.GRADED
                    ])
                )
                # Assignment created after exam publication but before exam end
                assignment.assigned_at = random_timestamp_in_range(
                    exam.created_at.replace(tzinfo=timezone.utc),
                    min(exam.end_at.replace(tzinfo=timezone.utc), now)
                ).replace(tzinfo=None)
                assignment = assignment_repo.create(assignment)
                assignments.append(assignment)
        
        db.commit()
        print(f"  Created {len(assignments)} assignments")
        
        # 9. Generate Attempts (for students with SUBMITTED or GRADED assignments)
        print("Generating attempts...")
        attempts = []
        submitted_assignments = [a for a in assignments if a.status in [AssignmentStatus.SUBMITTED, AssignmentStatus.GRADED]]
        
        for assignment in submitted_assignments:
            exam = next(e for e in exams if e.id == assignment.exam_id)
            
            # Attempt started after assignment
            assignment_time = assignment.assigned_at.replace(tzinfo=timezone.utc)
            exam_end_time = exam.end_at.replace(tzinfo=timezone.utc)
            max_start_time = min(exam_end_time, now)
            
            if max_start_time <= assignment_time:
                # Assignment is too recent or exam already ended, skip
                continue
            
            started_at = random_timestamp_in_range(assignment_time, max_start_time)
            ends_at = started_at + timedelta(minutes=exam.duration_minutes)
            
            # Submitted before end (or expired)
            if random.random() < 0.8:  # 80% submitted on time
                submit_end = min(ends_at, now)
                if submit_end > started_at:
                    submitted_at = random_timestamp_in_range(started_at, submit_end)
                    status = AttemptStatus.SUBMITTED
                else:
                    submitted_at = started_at
                    status = AttemptStatus.SUBMITTED
            else:
                submitted_at = None
                status = AttemptStatus.EXPIRED
            
            attempt = Attempt(
                exam_id=exam.id,
                student_id=assignment.student_id,
                assignment_id=assignment.id,
                attempt_no=1,
                started_at=started_at.replace(tzinfo=None),
                ends_at=ends_at.replace(tzinfo=None),
                submitted_at=submitted_at.replace(tzinfo=None) if submitted_at else None,
                status=status
            )
            attempt = attempt_repo.create(attempt)
            
            # Create question snapshots and answers
            exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
            total_points = 0
            earned_points = 0
            
            for eq in exam_questions:
                question = question_repo.get_by_id(eq.question_id)
                if not question:
                    continue
                
                # Get options
                options = db.query(QuestionOption).filter(QuestionOption.question_id == question.id).all()
                options_data = [{"id": opt.id, "text": opt.text, "is_correct": bool(opt.is_correct)} for opt in options]
                correct_answer = [opt for opt in options_data if opt["is_correct"]][0] if options_data else None
                
                # Create snapshot
                snapshot = AttemptQuestionSnapshot(
                    attempt_id=attempt.id,
                    original_question_id=question.id,
                    sort_order=eq.sort_order,
                    points=eq.points,
                    question_title=question.title,
                    question_body=question.body,
                    options_json=json.dumps(options_data),
                    correct_answer_json=json.dumps(correct_answer) if correct_answer else "{}"
                )
                snapshot = attempt_repo.create_snapshot(snapshot)
                
                # Create answer (student selects an option)
                if submitted_at:
                    selected_option = random.choice(options_data)
                    is_correct = selected_option["is_correct"]
                    
                    answer = AttemptAnswer(
                        attempt_id=attempt.id,
                        snapshot_id=snapshot.id,
                        selected_option_json=json.dumps(selected_option),
                        answered_at=submitted_at.replace(tzinfo=None)
                    )
                    attempt_repo.create_or_update_answer(answer)
                    
                    if is_correct:
                        earned_points += eq.points
                    total_points += eq.points
            
            attempts.append(attempt)
            db.commit()
        
        print(f"  Created {len(attempts)} attempts")
        
        # 10. Generate Results (for submitted attempts)
        print("Generating results...")
        submitted_attempts = [a for a in attempts if a.status == AttemptStatus.SUBMITTED and a.submitted_at]
        
        for attempt in submitted_attempts:
            exam = next(e for e in exams if e.id == attempt.exam_id)
            
            # Calculate score from answers
            snapshots = attempt_repo.get_snapshots(attempt.id)
            total_points = sum(s.points for s in snapshots)
            earned_points = 0
            
            for snapshot in snapshots:
                answer = attempt_repo.get_answer(attempt.id, snapshot.id)
                if answer:
                    selected = json.loads(answer.selected_option_json)
                    correct = json.loads(snapshot.correct_answer_json)
                    if selected.get("id") == correct.get("id"):
                        earned_points += snapshot.points
            
            percentage = int((earned_points / total_points * 100)) if total_points > 0 else 0
            
            result = Result(
                attempt_id=attempt.id,
                earned_points=earned_points,
                total_points=total_points,
                percentage=percentage,
                released_at=attempt.submitted_at if exam.grading_policy == GradingPolicy.IMMEDIATE else None
            )
            result = result_repo.create(result)
            db.commit()
        
        print(f"  Created {len(submitted_attempts)} results")
        
        print("\n✅ Realistic seed data generation complete!")
        print(f"   - 1 Admin")
        print(f"   - {len(teachers)} Teachers")
        print(f"   - {len(students)} Students")
        print(f"   - {len(subjects)} Subjects")
        print(f"   - {len(exams)} Exams")
        print(f"   - {len(all_questions)} Questions")
        print(f"   - {len(assignments)} Assignments")
        print(f"   - {len(attempts)} Attempts")
        print(f"   - {len(submitted_attempts)} Results")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating seed data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_realistic_data()

