
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy from flask_sqlalchemy
from datetime import datetime, timezone, timedelta,date
from sqlalchemy import CheckConstraint


def time_conversion():
    # Get current time in UTC
    IST = timezone(timedelta(hours=5, minutes=30))
    now_utc = datetime.now(timezone.utc)

    # Convert UTC time to IST
    now_ist = now_utc.astimezone(IST)

    # Remove timezone information (making it naive)
    now_ist = now_ist.replace(tzinfo=None)
    now_ist=now_ist.replace(microsecond=0)
    return(now_ist)


db = SQLAlchemy()  # Create an instance of SQLAlchemy class




class Subject(db.Model):
    __tablename__ = "Subject"
    id = db.Column(db.String(10), primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    description=db.Column(db.Text)
    bg_img=db.Column(db.Text)
    chapters=db.relationship("Chapter",backref="Subject",lazy=True, cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = "Chapter"
    id = db.Column(db.String(20), nullable=False)
    sid=db.Column(db.String(10), db.ForeignKey("Subject.id"),nullable=False)
    name = db.Column(db.Text, nullable=False)
    description=db.Column(db.Text)
    bg_img=db.Column(db.Text)

    __table_args__ = (
        db.PrimaryKeyConstraint('id', 'sid'),
    )

    quizzes=db.relationship("Quiz",backref="Chapter",lazy=True, cascade="all, delete-orphan")

class Quiz(db.Model):
    __tablename__ = "Quiz"
    id = db.Column(db.String(20), nullable=False)
    cid=db.Column(db.String(20), db.ForeignKey("Chapter.id"),nullable=False,index=True)
    date=db.Column(db.DateTime,nullable=False,default=lambda: time_conversion())
    duration=db.Column(db.Time,nullable=False)
    difficulty=db.Column(db.String(7),nullable=False)
    no_of_questions=db.Column(db.Integer,nullable=False)
    start_date=db.Column(db.DateTime,default=datetime(2100, 1, 24,0,0,0))
    delete_date=db.Column(db.DateTime,default=datetime(2100, 1, 24,0,0,0))
    state=db.Column(db.String(10),nullable=False,default="inactive")
    total_attempts=db.Column(db.Integer,default=0)
    avg_score=db.Column(db.Integer,default=0)
    total_marks=db.Column(db.Integer,default=0)

    __table_args__=(
        db.PrimaryKeyConstraint('id','cid'),
        CheckConstraint('difficulty IN ("Easy", "Medium","Hard","Extreme")', name='difficulty_check'),
        CheckConstraint('state IN ("active", "inactive")', name='state_check'),
    )

    questions=db.relationship("Question",backref="Quiz",lazy=True, cascade="all, delete-orphan")

class Question(db.Model):
    __tablename__="Question"
    id = db.Column(db.String(10), nullable=False)
    qid=db.Column(db.String(20), db.ForeignKey("Quiz.id"),nullable=False,index=True)
    statement=db.Column(db.Text,nullable=False)
    option1=db.Column(db.Text,nullable=False)
    option2=db.Column(db.Text,nullable=False)
    option3=db.Column(db.Text)
    option4=db.Column(db.Text)
    correct_option=db.Column(db.Integer,nullable=False)
    difficulty=db.Column(db.String(7),nullable=False)
    explanation=db.Column(db.Text,default="No explanation provided yet")
    explanation_link=db.Column(db.Text,default="https://www.google.com/")
    marks=db.Column(db.Integer,nullable=False)

    __table_args__=(
        db.PrimaryKeyConstraint('id','qid'),
        CheckConstraint('difficulty IN ("Easy", "Medium","Hard","Extreme")', name='difficulty_check'),
        CheckConstraint('correct_option IN (1,2,3,4)', name='option_check'),
    )

class User(db.Model):
    __tablename__="User"
    id = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(20),nullable=False)
    full_name=db.Column(db.String(40),nullable=False)
    DOB=db.Column(db.Date,nullable=False,default=date(2003,8,5))
    role=db.Column(db.String(10),nullable=False,default="user")
    status = db.Column(db.String(20), nullable=False,default="unblocked")

    __table_args__ = (
        CheckConstraint('status IN ("blocked", "unblocked")', name='status_check'),
        CheckConstraint('role IN ("admin", "user")', name='role_check'),
    )

    attempts=db.relationship("Attempts",backref="User",lazy=True, cascade="all, delete-orphan")


class Attempts(db.Model):
    __tablename__ = "Attempts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.String(20), db.ForeignKey("Quiz.id"), nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey("User.id"), nullable=False)
    attempt_time = db.Column(db.DateTime, nullable=False, default=time_conversion())
    total_marks_scored = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    wrong = db.Column(db.Integer)

    Attempt_details = db.relationship("Attempt_details", backref="Attempt", lazy=True, cascade="all, delete-orphan")

class Attempt_details(db.Model):
    __tablename__ = "Attempt_details"
    attempt_id = db.Column(db.Integer, db.ForeignKey("Attempts.id"), nullable=False)
    qtid = db.Column(db.String(10), nullable=False)
    qid = db.Column(db.String(20), nullable=False)
    correct = db.Column(db.String(10), default="None")
    selected_option=db.Column(db.Integer,default=5)

    __table_args__ = (
        db.ForeignKeyConstraint(['qtid', 'qid'], ['Question.id', 'Question.qid']),
        db.PrimaryKeyConstraint('attempt_id', 'qtid'),
        CheckConstraint('correct IN ("Yes", "No", "None")', name='correctness_check'),
    )

    

    