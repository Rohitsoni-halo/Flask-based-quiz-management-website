from models.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash, session,Blueprint
from datetime import time,datetime,timedelta
from sqlalchemy import event
import plotly.graph_objs as go
import plotly.io as pio


controllers = Blueprint('controllers', __name__)

#updating the total marks of quiz while inserting updating and deleting questions
@event.listens_for(Question, 'after_insert')
def update_quiz_total_marks(mapper, connection, target):
    quiz_id = target.qid  # Get the Quiz ID from the newly inserted Question

    # Sum up the marks of all questions related to the quiz
    total_marks_query = db.session.query(db.func.sum(Question.marks)).filter(Question.qid == quiz_id)
    total_marks = total_marks_query.scalar() or 0  # If no marks found, default to 0



    # Update the Quiz's total_marks column
    connection.execute(
        Quiz.__table__.update().
        where(Quiz.id == quiz_id).
        values(total_marks=total_marks)
    )

# After Updating a Question
@event.listens_for(Question, 'after_update')
def update_quiz_marks_after_update(mapper, connection, target):
    update_quiz_total_marks(mapper, connection, target)

# After Deleting a Question
@event.listens_for(Question, 'after_delete')
def update_quiz_marks_after_delete(mapper, connection, target):
    update_quiz_total_marks(mapper, connection, target)


# Function to update Attempt summary
def update_attempt_summary(mapper, connection, target):
    attempt_id = target.attempt_id

    # Fetch total correct and wrong answers
    correct_count = db.session.query(db.func.count()).filter(
        Attempt_details.attempt_id == attempt_id,
        Attempt_details.correct == "Yes"
    ).scalar() or 0

    wrong_count = db.session.query(db.func.count()).filter(
        Attempt_details.attempt_id == attempt_id,
        Attempt_details.correct == "No"
    ).scalar() or 0

    # Calculate total marks for correct answers
    total_marks_scored_query = db.session.query(db.func.sum(Question.marks)).join(
        Attempt_details,
        (Attempt_details.qtid == Question.id) & (Attempt_details.qid == Question.qid)
    ).filter(
        Attempt_details.attempt_id == attempt_id,
        Attempt_details.correct == "Yes"
    )

    total_marks_scored = total_marks_scored_query.scalar() or 0

    # Update the Attempts table
    connection.execute(
        Attempts.__table__.update()
        .where(Attempts.id == attempt_id)
        .values(
            correct=correct_count,
            wrong=wrong_count,
            total_marks_scored=total_marks_scored
        )
    )

# Event listeners for insert, update, delete
@event.listens_for(Attempt_details, 'after_insert')
@event.listens_for(Attempt_details, 'after_update')
@event.listens_for(Attempt_details, 'after_delete')
def trigger_update_attempt(mapper, connection, target):
    update_attempt_summary(mapper, connection, target)

#home page
@controllers.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')


#admin login
@controllers.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email,role='admin').first()
        if user and check_password_hash(user.password, password):
            session['user_id']=user.id
            session['role'] = user.role
            flash("Admin login Succesful")
            return redirect(url_for('controllers.admin_dashboard'))
        else:
            flash("Admin login failed, check your credentials")
    return render_template('admin_login.html')

#admin dashboard
@controllers.route('/admin/dashboard',methods=['GET','POST'])
def admin_dashboard():
    
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))
    
    # Check if the logged-in user is an admin
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id).first()
    
    if user.role != 'admin':
        flash('You are not the admin')
        return redirect(url_for('controllers.login'))

    
    #all_users = User.query.all()

    return render_template('admin_dashboard.html',show="dashboard")

#show all users
@controllers.route('/admin/users')
def show_all_user():
    users=User.query.all()
    return render_template('admin_dashboard.html',show="users",users=users)

#show all subjects
@controllers.route('/admin/subjects')
def show_all_subjects():
    subjects=Subject.query.all()
    return render_template('admin_dashboard.html',show="subjects",subjects=subjects)

#search users
@controllers.route('/admin/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip()  # Get search term
    session['query']=query
    if query:
        users = User.query.filter(
            (User.full_name.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%")) |
            (User.id.ilike(f"%{query}%"))
        ).all()
    else:
        flash("No such user exists")
        users = User.query.all()  # Show all users if no search

    return render_template('admin_dashboard.html', show="users", users=users)

#search subjects
@controllers.route('/admin/search_subjects',methods=['GET'])
def search_subjects():
    query = request.args.get('query', '').strip()  
    session['query']=query
    if query:
        subjects = Subject.query.filter(
            (Subject.name.ilike(f"%{query}%")) |
            (Subject.id.ilike(f"%{query}%"))
        ).all()
    else:
        flash("No such subject exists")
        subjects = Subject.query.all()  # Show all users if no search

    return render_template('admin_dashboard.html', show="subjects", subjects=subjects)

#show chapters indirectly
@controllers.route('/admin/show_chapters/<string:subject_id>', methods=['GET'])
def show_chapters(subject_id):
    subject = Subject.query.filter_by(id=subject_id).first()
    if not subject:
        flash("Subject not found")
        return redirect(url_for('controllers.show_all_subjects'))

    chapters = subject.chapters

    if not chapters:
        flash("There are no chapters in this subject")

    return render_template('admin_dashboard.html', show="chapters", chapters=chapters)

#show quizzes indirectly
@controllers.route('/admin/show_quizzes/<string:chapter_id>', methods=['GET'])
def show_quizzes(chapter_id):
    chapter = Chapter.query.filter_by(id=chapter_id).first()
    if not chapter:
        flash("Chapter not found")
        chapters=Chapter.query.all()
        return redirect(url_for('admin_dashboard.html', show="chapters", chapters=chapters))

    quizzes = chapter.quizzes

    if not quizzes:
        flash("There are no quiz in this subject")

    return render_template('admin_dashboard.html', show="quizzes", quizzes=quizzes)

#show questions indirectly
@controllers.route('/admin/show_questions/<string:quiz_id>', methods=['GET'])
def show_questions(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        flash("Quiz not found")
        quizzes=Quiz.query.all()
        return redirect(url_for('admin_dashboard.html', show="quizzes", quizzes=quizzes))

    questions = quiz.questions

    if not questions:
        flash("There are no questions in this subject")

    return render_template('admin_dashboard.html', show="questions", questions=questions)

#toggle state indirect 
@controllers.route('/admin/toggle_state_indirect/<string:quiz_id>/<string:c_id>',methods=['GET'])
def toggle_state_indirect(quiz_id,c_id):
    quiz=Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        flash('Quiz not found', 'danger')
        return redirect(url_for('controllers.search_all'))  # Redirect if quiz is not found

    if quiz.state == 'inactive':
        quiz.state = 'active'
        flash('Quiz activated successfully', 'success')
    else:
        quiz.state = 'inactive'
        flash('Quiz inactivated successfully', 'warning')

    db.session.commit()
    chapter=Chapter.query.filter_by(id=c_id).first()
    quizzes=chapter.quizzes
    return render_template('admin_dashboard.html', show="quizzes", quizzes=quizzes)

#search anything
@controllers.route('/admin/search_all',methods=['GET'])
def search_all():
    query=request.args.get('query','').strip()

    if(query==""):
        query=session['query']

    session['query']=query
    if query:
        users=User.query.filter(
            (User.full_name.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%")) |
            (User.id.ilike(f"%{query}%"))
        ).all()
        
        subjects=Subject.query.filter(
            (Subject.id.ilike(f"%{query}%")) |
            (Subject.name.ilike(f"%{query}%")) 
        ).all()

        chapters=Chapter.query.filter(
            (Chapter.id.ilike(f"%{query}%")) |
            (Chapter.name.ilike(f"%{query}%"))
        ).all()

        quiz=Quiz.query.filter(
            (Quiz.id.ilike(f"%{query}%")) |
            (Quiz.cid.ilike(f"%{query}%"))
        ).all()
    else:
        users=[]
        subjects=[]
        chapters=[]
        quiz=[]
    return render_template('search_all.html',users=users,subjects=subjects,chapters=chapters,quiz=quiz)

#add subject
@controllers.route('/admin/add_subject',methods=['GET','POST'])
def add_subject():
    if request.method=='POST':
        id=request.form['id']
        name=request.form['name']
        description=request.form['description']

        new_subject = Subject(id=id, name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('new subject added successfully')
        return redirect(url_for('controllers.admin_dashboard'))

    return render_template('add_subject.html')

#edit subject
@controllers.route('/admin/edit_subject',methods=['GET','POST'])
def edit_subject():
    if request.method == 'POST':
        if 'search' in request.form:  
            id = request.form['id']
            subject = Subject.query.filter_by(id=id).first()
            if subject:
                return render_template('edit_subject.html', subject=subject, edit_mode=True)
            else:
                flash('Subject with this ID does not exist.')
                return redirect(url_for('controllers.edit_subject'))
    
        elif 'update' in request.form:  
            id = request.form['id']
            subject = Subject.query.filter_by(id=id).first()
            
            if subject:
                subject.id=request.form['new_id']
                subject.name = request.form['name']
                subject.description = request.form['description']
                db.session.commit()
                flash('Subject updated successfully.')
                return redirect(url_for('controllers.admin_dashboard'))
            else:
                flash('Subject with this ID does not exist.')
                return redirect(url_for('controllers.edit_subject'))

    return render_template('edit_subject.html', edit_mode=False)

#delete subject
@controllers.route('/admin/delete_subject',methods=['POST'])
def delete_subject():
    id = request.form['id']  
    subject = Subject.query.filter_by(id=id).first()
    
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully.')
    else:
        flash('Subject not found.')
    
    return redirect(url_for('controllers.admin_dashboard'))


#add chapter
@controllers.route('/admin/add_chapter',methods=['GET','POST'])
def add_chapter():
    if request.method=='POST':
        cid=request.form['cid']
        sid=request.form['sid']
        name=request.form['name']
        description=request.form['description']
        subject=Subject.query.filter_by(id=sid).first()
        
        if not subject:
            flash('subject id is incorrect')
        else:
            new_chapter = Chapter(id=cid,sid=sid, name=name, description=description)
            db.session.add(new_chapter)
            db.session.commit()
            flash('new chapter added successfully')
            
    return render_template('add_chapter.html')

#edit chapter
@controllers.route('/admin/edit_chapter',methods=['GET','POST'])
def edit_chapter():
    if request.method == 'POST':
        if 'search' in request.form:  
            id = request.form['cid']
            chapter = Chapter.query.filter_by(id=id).first()
            if chapter:
                return render_template('edit_chapter.html', chapter=chapter, edit_mode=True)
            else:
                flash('chapter with this ID does not exist.')
                return redirect(url_for('controllers.edit_chapter'))

        elif 'update' in request.form:  
            id = request.form['cid']
            chapter = Chapter.query.filter_by(id=id).first()
            
            if chapter:
                chapter.id=request.form['new_cid']
                chapter.sid=request.form['new_sid']
                chapter.name = request.form['name']
                chapter.description = request.form['description']

                subject=Subject.query.filter_by(id=chapter.sid).first()
                if not subject:
                    flash('subject does not exist')
                    return redirect(url_for('controllers.edit_chapter'))
                else:
                    db.session.commit()
                    flash('Chapter updated successfully.')
                    return render_template('admin_dashboard.html', show="dashboard")
                
            else:
                flash('Chapter with this ID does not exist.')
                return redirect(url_for('controllers.edit_chapter'))

    return render_template('edit_chapter.html', edit_mode=False)

#delete chapter
@controllers.route('/admin/delete_chapter',methods=['POST'])
def delete_chapter():
    id = request.form['cid']  
    chapter = Chapter.query.filter_by(id=id).first()
    
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully.')
    else:
        flash('Chapter not found.')
    
    return redirect(url_for('controllers.admin_dashboard'))

#add quiz
@controllers.route('/admin/add_quiz',methods=['GET','POST'])
def add_quiz():
    if request.method=='POST':
        qid=request.form['qid']
        cid=request.form['cid']

        hours = int(request.form.get("duration_hours"))  
        minutes = int(request.form.get("duration_minutes"))  
        duration = time(hour=hours, minute=minutes)

        difficulty=request.form['difficulty']
        no_of_q=request.form['no_of_q']

        start_date=request.form['start_date']
        del_date=request.form['del_date']

        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
        del_date = datetime.strptime(del_date, "%Y-%m-%dT%H:%M")
        
        chapter=Chapter.query.filter_by(id=cid).first()
        
        if not chapter:
            flash('chapter id is incorrect')
        else:
            new_quiz = Quiz(id=qid,cid=cid, duration=duration, difficulty=difficulty,no_of_questions=no_of_q,start_date=start_date,delete_date=del_date)
            db.session.add(new_quiz)
            db.session.commit()
            flash('new quiz added successfully')
            
    return render_template('add_quiz.html')

#edit quiz
@controllers.route('/admin/edit_quiz',methods=['GET','POST'])
def edit_quiz():
    if request.method == 'POST':
        if 'search' in request.form:  
            id = request.form['qid']
            quiz = Quiz.query.filter_by(id=id).first()
            if quiz:
                return render_template('edit_quiz.html', quiz=quiz, edit_mode=True)
            else:
                flash('quiz with this ID does not exist.')
                return redirect(url_for('controllers.edit_quiz'))

        elif 'update' in request.form:  
            id = request.form['qid']
            quiz = Quiz.query.filter_by(id=id).first()
            
            if quiz:
                quiz.id=request.form['new_qid']
                quiz.cid=request.form['new_cid']
                hours = int(request.form.get("duration_hours"))  
                minutes = int(request.form.get("duration_minutes"))  
                quiz.duration = time(hour=hours, minute=minutes)
                quiz.difficulty=request.form['difficulty']
                quiz.state=request.form['state']
                quiz.no_of_questions=request.form['no_of_q']
                start_date=request.form['start_date']
                del_date=request.form['del_date']

                quiz.del_date = datetime.strptime(del_date, "%Y-%m-%dT%H:%M")
                quiz.start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")

                chapter=Chapter.query.filter_by(id=quiz.cid).first()
                if not chapter:
                    flash('chapter does not exist')
                    #return redirect(url_for('controllers.edit_chapter'))
                else:
                    db.session.commit()
                    flash('Quiz updated successfully.')
                    return redirect(url_for('controllers.admin_dashboard',show="dashboard"))
                
            else:
                flash('Quiz with this ID does not exist.')
                return redirect(url_for('controllers.edit_quiz'))

    return render_template('edit_quiz.html', edit_mode=False)

#delete quiz
@controllers.route('/admin/delete_quiz',methods=['POST'])
def delete_quiz():
    id = request.form['qid']  
    quiz = Quiz.query.filter_by(id=id).first()
    
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully.')
    else:
        flash('Quiz not found.')
    
    return redirect(url_for('controllers.admin_dashboard'))

#add question
@controllers.route('/admin/add_question',methods=['GET','POST'])
def add_question():
    if request.method=='POST':
        qtid=request.form['qtid']
        qid=request.form['qid']
        statement=request.form['statement']
        option1=request.form['option1']
        option2=request.form['option2']
        option3=request.form['option3']
        option4=request.form['option4']
        correct=request.form['correct']
        difficulty=request.form['difficulty']
        explanation=request.form['explanation']
        marks=request.form['marks']
        
        quiz=Quiz.query.filter_by(id=qid).first()
        
        if not quiz:
            flash('quiz id is incorrect')
        else:
            new_question = Question(id=qtid,qid=qid, statement=statement,option1=option1,option2=option2,option3=option3,option4=option4,correct_option=correct, difficulty=difficulty,explanation=explanation,marks=marks)
            db.session.add(new_question)
            db.session.commit()
            flash('new question added successfully')
            
    return render_template('add_question.html')

#edit question
@controllers.route('/admin/edit_question',methods=['GET','POST'])
def edit_question():
    if request.method == 'POST':
        if 'search' in request.form:  
            id = request.form['qtid']
            question = Question.query.filter_by(id=id).first()
            if question:
                return render_template('edit_question.html', question=question, edit_mode=True)
            else:
                flash('question with this ID does not exist.')
                return redirect(url_for('controllers.edit_question'))

        elif 'update' in request.form:  
            id = request.form['qtid']
            question = Question.query.filter_by(id=id).first()
            
            if question:
                question.id=request.form['new_qtid']
                question.qid=request.form['new_qid']
                question.statement=request.form['statement']
                question.option1=request.form['option1']
                question.option2=request.form['option2']
                question.option3=request.form['option3']
                question.option4=request.form['option4']
                question.correct_option=request.form['correct']
                question.difficulty=request.form['difficulty']
                question.explanation=request.form['explanation']
                question.marks=request.form['marks']

                quiz=Quiz.query.filter_by(id=question.qid).first()
                if not quiz:
                    flash('quiz does not exist')
                    #return redirect(url_for('controllers.edit_chapter'))
                else:
                    db.session.commit()
                    flash('Qestion updated successfully.')
                
            else:
                flash('Question with this ID does not exist.')
                return redirect(url_for('controllers.edit_question'))

    return render_template('edit_question.html', edit_mode=False)

#delete question
@controllers.route('/admin/delete_question',methods=['POST'])
def delete_question():
    id = request.form['qtid']  
    question = Question.query.filter_by(id=id).first()
    
    if question:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully.')
    else:
        flash('Question not found.')
    
    return redirect(url_for('controllers.admin_dashboard'))


#block user
@controllers.route('/admin/block',methods=['GET','POST'])
def block_user():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        
        user = User.query.filter_by(email=email).first()
        if(user.id==username):
            if(user.status=="blocked"):
                flash('This user is already blocked')
            else:
                user.status="blocked"
                db.session.commit()
                flash('User blocked successfully')
        else:
            flash('Such user does not exist')

    return render_template('block_user.html')

#unblock user
@controllers.route('/admin/unblock',methods=['GET','POST'])
def unblock_user():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        
        user = User.query.filter_by(email=email).first()
        if(user.id==username):
            if(user.status=="unblocked"):
                flash('This user was already unblocked')
            else:
                user.status="unblocked"
                db.session.commit()
                flash('User unblocked successfully')
        else:
            flash('Such user does not exist')

    return render_template('unblock_user.html')

#auto_block user
@controllers.route('/admin/auto_block/<string:user_id>', methods=['GET', 'POST'])
def auto_block(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user.status=='blocked':
        user.status='unblocked'
    else:
        user.status='blocked'

    db.session.commit()

    users=User.query.all()

    return render_template('admin_dashboard.html',show="users",users=users)

#toggle state
@controllers.route('/admin/toggle_state/<string:q_id>', methods=['GET', 'POST'])
def toggle_state(q_id):
    quiz = Quiz.query.filter_by(id=q_id).first()

    if not quiz:
        flash('Quiz not found', 'danger')
        return redirect(url_for('controllers.search_all'))  # Redirect if quiz is not found

    if quiz.state == 'inactive':
        quiz.state = 'active'
        flash('Quiz activated successfully', 'success')
    else:
        quiz.state = 'inactive'
        flash('Quiz inactivated successfully', 'warning')

    db.session.commit()
    return redirect(url_for('controllers.search_all'))  # Redirect instead of rendering


#user login
@controllers.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("You have not registered yet. Kindly register first")
            return redirect(url_for('controllers.register'))
        if user.status=="blocked":
            flash("You are temporarily blocked by the admin. Please contact the admint to remove the block")

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            session['role'] = user.role  # Store user role in session
            session['user_state']="dashboard"
            flash('Login successful!')
            if user.role == 'admin':
                return redirect(url_for('controllers.admin_dashboard')) 
            else:
                return redirect(url_for('controllers.user_dashboard'))  # Redirect to user dashboard
        else:
            flash('Login failed. Check your credentials and try again.')
    
    return render_template('user_login.html')



#registration

@controllers.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        full_name= request.form['full_name']
        DOB= request.form['DOB']
        dob = datetime.strptime(DOB, '%Y-%m-%d').date()
        
        new_user = User(id=username, email=email, password=password,full_name=full_name,DOB=dob)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully! Please log in.')
        return redirect(url_for('controllers.login'))
    
    return render_template('registration.html')



#user dashboard 
@controllers.route('/dashboard')
def user_dashboard():
    
    if ('user_id' not in session) or (session['user_state']!="dashboard"):
        flash('Please log in to access the dashboard.')
        return redirect(url_for('controllers.login'))

    user_id = session['user_id']
    user = User.query.filter_by(id=user_id).first()

    if user.status == "blocked":
        flash("You are temporarily blocked by the admin. Please contact the admin to remove the block.")
        return redirect(url_for('controllers.login'))

    # Fetch all subjects
    subjects = Subject.query.all()

    return render_template('user_dashboard.html', subjects=subjects,viewing="subjects",user=user)


# Route for user logout
@controllers.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('role', None)  # Remove user role from session
    session.pop('user_state',None) #removing user state
    flash('You have been logged out.')
    return redirect(url_for('controllers.login'))

# search by user
@controllers.route('/search',methods=['GET','POST'])
def user_search():
    if(session['user_state']=="dashboard"):
        query=request.args.get('query','').strip()
        if query:
            subjects=Subject.query.filter(
                (Subject.id.ilike(f"%{query}%")) |
                (Subject.name.ilike(f"%{query}%")) 
            ).all()

            chapters=Chapter.query.filter(
                (Chapter.id.ilike(f"%{query}%")) |
                (Chapter.name.ilike(f"%{query}%"))
            ).all()

            quiz = Quiz.query.filter(
                (Quiz.id.ilike(f"%{query}%")) |
                (Quiz.cid.ilike(f"%{query}%")) |
                (Quiz.difficulty.ilike(f"%{query}%"))
            ).filter_by(state='active').all()

        else:
            subjects=[]
            chapters=[]
            quiz=[]
    else:
        flash('You seemed to have logged out')
        return redirect(url_for('controllers.login'))
    return render_template('user_search.html',subjects=subjects,chapters=chapters,quiz=quiz)

#on clicking the subject the user will view the chapters inside that subject
@controllers.route('/view_chapters/<string:subject_id>')
def view_chapters(subject_id):
    if(session['user_state']=="dashboard"):
        session['subject_id']=subject_id
        chapters=Chapter.query.filter_by(sid=subject_id).all()
    else:
        flash('You seemed to be logged out')
        return redirect(url_for('controllers.login'))
    return render_template('user_dashboard.html',viewing="chapters",chapters=chapters)

#on clicking the chapter the user will view the quizzes inside that subject
#quiz being activated means the quiz will show up whenever the start date of the quiz comes
#but the quiz will not show up it is activated and its start date is later
@controllers.route('/view_quizzes/<string:chapter_id>')
def view_quizzes(chapter_id):
    if(session['user_state']=="dashboard"):
        session['chapter_id']=chapter_id
        cur_time=time_conversion()

        quizzes = Quiz.query.filter(
            (Quiz.cid == chapter_id) & (Quiz.state == 'active') & (Quiz.start_date < cur_time) & (Quiz.delete_date > cur_time)
        ).all()
    else:
        flash('You seem to be logged out')
        return redirect(url_for('controllers.login'))
    return render_template('user_dashboard.html', viewing="quizzes", quizzes=quizzes)


#on clicking the quiz the user will be prompted to start the quiz
# Route to start the quiz
@controllers.route('/start_quiz/<string:quiz_id>')
def start_quiz(quiz_id):
    if ('user_id' not in session) or (session['user_state']!="dashboard"):
        flash('Please log in to start the quiz.')
        return redirect(url_for('controllers.login'))

    session['quiz_id'] = quiz_id
    session['current_question_index'] = 1  # Start from question 1
    

    quiz=Quiz.query.filter_by(id=quiz_id).first()
    duration = timedelta(
        hours=quiz.duration.hour,
        minutes=quiz.duration.minute,
        seconds=quiz.duration.second
    )

    # Store quiz end time in session
    session['quiz_end_time'] = (datetime.now() + duration).strftime("%Y-%m-%d %H:%M:%S")

    user_id=session['user_id']
    attempt_time=time_conversion()
    attempt=Attempts(user_id=user_id,quiz_id=quiz_id,attempt_time=attempt_time)
    db.session.add(attempt)
    db.session.commit()

    session['attempt_id']=attempt.id

    questions=quiz.questions
    for question in questions:
        attempt_detail = Attempt_details(attempt_id=attempt.id,qid=quiz.id,qtid=question.id)
        db.session.add(attempt_detail)
        db.session.commit()

    return redirect(url_for('controllers.take_quiz', quiz_id=quiz_id, question_number=1))  # Redirect to question 1

# Route to display one question at a time
@controllers.route("/quiz/<string:quiz_id>/<int:question_number>", methods=["GET", "POST"])
def take_quiz(quiz_id, question_number):
    if ('user_id' not in session) or (session['user_state']!='dashboard'):
        if(session['user_state']!='inside quiz'):
            flash('Please log in to start the quiz.')
            return redirect(url_for('controllers.login'))

    if(session['user_state']=='dashboard'):
        session['user_state']='inside quiz'

    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        flash("Quiz not found.")
        return redirect(url_for('controllers.user_dashboard'))

    questions = quiz.questions
    total_questions = len(questions)

    attempt_id = session.get('attempt_id')
    if not attempt_id:
        flash("Quiz attempt not started. Please restart.")
        return redirect(url_for('controllers.user_dashboard'))

    # Redirect if the user exceeds the number of questions
    if question_number > total_questions:
        return redirect(url_for('controllers.user_dashboard'))
    
    question = questions[question_number - 1]
    session['question_id'] = question.id

    quiz_end_time = session.get("quiz_end_time")
    if quiz_end_time:
        end_time = datetime.strptime(quiz_end_time, "%Y-%m-%d %H:%M:%S")
        remaining_time = max(0, (end_time - datetime.now()).seconds)
    else:
        remaining_time = None

    # Auto-submit if time is up
    if remaining_time is not None and remaining_time == 0:
        return redirect(url_for('controllers.submit_quiz'))

    if request.method == 'POST':
        selected_option = request.form.get('selected_option')
        correct = "Yes" if str(selected_option) == str(question.correct_option) else "No"

        # Update attempt details
        attempt_detail = Attempt_details.query.filter_by(attempt_id=attempt_id, qtid=question.id).first()
        attempt_detail.correct = correct  # Update existing record
        attempt_detail.selected_option=selected_option
        db.session.commit()

        # Move to the next question automatically
        if question_number<total_questions:
            return redirect(url_for('controllers.take_quiz', quiz_id=quiz_id, question_number=question_number+1))
        else:
            return redirect(url_for('controllers.take_quiz', quiz_id=quiz_id, question_number=question_number))
        
    return render_template("quiz.html",quiz=quiz,question=question,question_number=question_number,total_questions=total_questions,remaining_time=remaining_time)

@controllers.route('/quiz_feedback/<int:attempt_id>/<int:total_marks>')
def quiz_feedback(attempt_id, total_marks):
    if(session['user_state']!='feedback'):
        if(session['user_state']!='dashboard'):
            flash('please login to view results')
            return redirect(url_for('controllers.login'))

    if(session['user_state']=='feedback'):
        session['user_state']='dashboard'

    attempt = Attempts.query.get(attempt_id)
    attempt_details = Attempt_details.query.filter_by(attempt_id=attempt_id).all()
    questions = Question.query.filter_by(qid=attempt.quiz_id).all()

    correct_answers = sum(1 for detail in attempt_details if detail.correct == "Yes")
    incorrect_answers = sum(1 for detail in attempt_details if detail.correct == "No")
    unattempted_questions = len(questions) - correct_answers - incorrect_answers
    total_marks_scored = attempt.total_marks_scored

    # Pie chart generation
    labels = ['Correct', 'Incorrect', 'Unattempted']
    sizes = [correct_answers, incorrect_answers, unattempted_questions]
    colors = ['#28a745', '#dc3545', '#0000FF']

    if(correct_answers==0):
        labels.remove("Correct")
        sizes.remove(correct_answers)
        colors.remove("#28a745")
    
    if(incorrect_answers==0):
        labels.remove("Incorrect")
        sizes.remove(incorrect_answers)
        colors.remove("#dc3545")

    if(unattempted_questions==0):
        labels.remove("Unattempted")
        sizes.remove(unattempted_questions)
        colors.remove("#0000FF")

    pie_chart = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=sizes,
            marker=dict(colors=colors),
            hole=0.3,
            pull=[0.05, 0.05, 0.05],  # Explode effect
            textinfo='percent+label'
        )]
    )
    pie_chart.update_layout(title='Quiz Performance')

    # Convert Pie Chart to HTML
    pie_chart_html = pio.to_html(pie_chart, full_html=False)

    # Bar Graph for Attempts Over Time
    user_attempts = Attempts.query.filter_by(user_id=attempt.user_id, quiz_id=attempt.quiz_id)\
                                  .order_by(Attempts.attempt_time).all()
    attempt_dates = [att.attempt_time.strftime('%Y-%m-%d %H:%M') for att in user_attempts]
    attempt_scores = [att.total_marks_scored for att in user_attempts]

    bar_chart = go.Figure(
        data=[go.Bar(
            x=attempt_dates,
            y=attempt_scores,
            marker_color='#007bff'
        )]
    )
    bar_chart.update_layout(
    title='Quiz Attempts Over Time',
    xaxis_title='Attempt Date',
    yaxis_title='Marks Scored',
    xaxis_tickangle=-45,
    xaxis=dict(
        tickformat='%Y-%m-%d %H:%M'  
    )
)

    # Convert Bar Graph to HTML
    bar_chart_html = pio.to_html(bar_chart, full_html=False)

    attempt_detail_map = {detail.qtid: detail for detail in attempt_details}

    return render_template('feedback.html',questions=questions,attempt_details=attempt_detail_map,total_marks=total_marks,total_marks_scored=total_marks_scored,pie_chart_html=pie_chart_html,bar_chart_html=bar_chart_html)

# Update the submit_quiz and go to feedback
@controllers.route('/submit_quiz')
def submit_quiz():
    if(session['user_state']!='inside quiz') and (session['user_state']!='feedback'):
        flash('kindly log in to submit the quiz')
        return redirect(url_for('controllers.login'))
    
    elif(session['user_state']=='inside quiz'):
        session['user_state']='feedback'

    attempt_id = session.get('attempt_id')
    attempt = Attempts.query.filter_by(id=attempt_id).first()
    total_score = attempt.total_marks_scored

    quiz_id = session.get('quiz_id')
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    total_attempts = quiz.total_attempts
    old_score = quiz.avg_score * total_attempts

    total_attempts += 1
    new_avg = (old_score + total_score) / total_attempts

    quiz.total_attempts = total_attempts
    quiz.avg_score = new_avg
    db.session.commit()

    total_marks=quiz.total_marks

    session.pop('attempt_id', None)
    session.pop('quiz_id', None)

    flash('Quiz submitted successfully')
    return redirect(url_for('controllers.quiz_feedback', attempt_id=attempt.id,total_marks=total_marks))


@controllers.route('/my_attempts')
def my_attempts():
    if(session['user_state']!='dashboard'):
        flash('kinly login to view your previous attempts')
        return redirect('controllers.login')

    user_id = session.get('user_id') # Assuming you're using Flask-Login
    subjects = Subject.query.all()

    attempts_data = []
    for subject in subjects:
        chapters = Chapter.query.filter_by(sid=subject.id).all()
        chapter_data = []
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(cid=chapter.id).all()
            quiz_data = []
            for quiz in quizzes:
                attempts = Attempts.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
                for attempt in attempts:
                    total_attempts = Attempts.query.filter_by(quiz_id=quiz.id).count()
                    avg_score = quiz.avg_score
                    quiz_data.append({
                        'quiz': quiz,
                        'attempt': attempt,
                        'total_attempts': total_attempts,
                        'avg_score': round(avg_score, 2) if avg_score else 0
                    })
            if quiz_data:
                chapter_data.append({'chapter': chapter, 'quizzes': quiz_data})
        if chapter_data:
            attempts_data.append({'subject': subject, 'chapters': chapter_data})

    return render_template('user_dashboard.html',viewing="scores", attempts_data=attempts_data)
