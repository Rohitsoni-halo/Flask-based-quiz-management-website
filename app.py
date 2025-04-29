from flask import Flask
from models.models import *
from datetime import date
from controllers.controllers import controllers
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rohit.db"
app.config['SECRET_KEY'] = "dsfaiuhefwhiefwojfewlo"

db.init_app(app)

app.register_blueprint(controllers,url_prefix='/')

def create_admin():
    with app.app_context():
        admin_email="Admin@gmail.com"
        admin_user=User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_username="admin"
            admin_password="admin123"
            admin_user=User(id=admin_username,email=admin_email,password=generate_password_hash(admin_password, method='pbkdf2:sha256'),full_name="admin",role="admin",DOB=date(2003,8,5))
            db.session.add(admin_user)
            db.session.commit()
            print("Admin created successfully")

            
        else:
            print("Admin already exists")

with app.app_context():
    db.drop_all()
    db.create_all()
    create_admin()
    
    #dummy user1
    user=User(id="rohit",email="rohitsoni0805@gmail.com",password=generate_password_hash('new', method='pbkdf2:sha256'),full_name="Rohit Soni")
    db.session.add(user)
    db.session.commit()

    #dummy user2
    user=User(id="halo",email="halo@gmail.com",password=generate_password_hash('old', method='pbkdf2:sha256'),full_name="Master Cheif")
    db.session.add(user)
    db.session.commit()

    #dummy subject
    subject=Subject(id="CS20",name="Programming in C",description="basics of C")
    db.session.add(subject)
    db.session.commit()

    #dummy chapter
    chapter=Chapter(id="C2",sid="CS20",name="C",description="programming")
    db.session.add(chapter)
    db.session.commit()
    print("Admin created successfully")

    #dummy quiz
    #quiz=Quiz(id="Q20",cid="C2",duration=(datetime.min + timedelta(minutes=30)).time(),difficulty="Medium",state='active',no_of_questions=10)
    #db.session.add(quiz)
    #db.session.commit()

    #dummy question
    #question=Question(id="QT2",qid="Q20",statement="What is your name",option1="Rohit Soni",option2="Mahan Rohit Soni",option3="Sabse Badhiya Rohit Soni",option4="no one",correct_option=3,difficulty="Extreme",marks="100")
    #db.session.add(question)
    #db.session.commit()

    users = [
        User(id="alex", email="alex123@gmail.com", password=generate_password_hash('pass1', method='pbkdf2:sha256'), full_name="Alex Johnson"),
        User(id="jane_doe", email="jane.doe@example.com", password=generate_password_hash('pass2', method='pbkdf2:sha256'), full_name="Jane Doe"),
        User(id="michael", email="michael_456@gmail.com", password=generate_password_hash('pass3', method='pbkdf2:sha256'), full_name="Michael Smith"),
        User(id="linda", email="linda23@yahoo.com", password=generate_password_hash('pass4', method='pbkdf2:sha256'), full_name="Linda Williams"),
        User(id="samuel", email="samuel99@hotmail.com", password=generate_password_hash('pass5', method='pbkdf2:sha256'), full_name="Samuel Brown"),
        User(id="natalie", email="natalie456@gmail.com", password=generate_password_hash('pass6', method='pbkdf2:sha256'), full_name="Natalie Adams"),
        User(id="david_k", email="david.k@example.com", password=generate_password_hash('pass7', method='pbkdf2:sha256'), full_name="David King"),
        User(id="emily_r", email="emily.r@gmail.com", password=generate_password_hash('pass8', method='pbkdf2:sha256'), full_name="Emily Roberts"),
        User(id="ryan_p", email="ryan_peters@gmail.com", password=generate_password_hash('pass9', method='pbkdf2:sha256'), full_name="Ryan Peterson"),
        User(id="sophia_m", email="sophia.m@example.com", password=generate_password_hash('pass10', method='pbkdf2:sha256'), full_name="Sophia Miller")
    ]

    db.session.add_all(users)
    db.session.commit()

    # Dummy Subjects
    subjects = [
        Subject(id="CS21", name="Data Structures", description="Learn about arrays, linked lists, and more."),
        Subject(id="CS22", name="Algorithms", description="Sorting, searching, and graph algorithms."),
        Subject(id="CS23", name="Database Systems", description="Relational databases and SQL."),
        Subject(id="CS24", name="Operating Systems", description="Processes, threads, and memory management."),
        #Subject(id="CS25", name="Computer Networks", description="TCP/IP, routing, and network security."),
        #Subject(id="CS26", name="Machine Learning", description="Supervised and unsupervised learning techniques."),
        #Subject(id="CS27", name="Cyber Security", description="Ethical hacking, encryption, and cybersecurity protocols."),
        #Subject(id="CS28", name="Software Engineering", description="Agile methodologies and software development life cycle."),
        #Subject(id="CS29", name="Artificial Intelligence", description="Neural networks, NLP, and AI applications."),
        #Subject(id="CS30", name="Cloud Computing", description="AWS, Azure, and cloud architecture.")
    ]

    db.session.add_all(subjects)
    db.session.commit()

    # Dummy Chapters
    chapters = [
        Chapter(id="C3", sid="CS21", name="Stacks and Queues", description="Introduction to stack and queue operations."),
        #Chapter(id="C4", sid="CS21", name="Trees and Graphs", description="Binary trees, graphs, and traversals."),
        #Chapter(id="C5", sid="CS22", name="Sorting Algorithms", description="Bubble sort, merge sort, and quicksort."),
        Chapter(id="C6", sid="CS22", name="Graph Algorithms", description="Dijkstra's, Floyd Warshall, and Bellman Ford."),
        Chapter(id="C7", sid="CS23", name="SQL Basics", description="Introduction to SQL and queries."),
        Chapter(id="C8", sid="CS24", name="Process Management", description="Threads, scheduling, and synchronization."),
        #Chapter(id="C9", sid="CS25", name="Network Protocols", description="Understanding TCP/IP and OSI model."),
        #Chapter(id="C10", sid="CS26", name="Supervised Learning", description="Linear regression, decision trees, and SVM."),
        #Chapter(id="C11", sid="CS27", name="Cyber Threats", description="Common cyber threats and mitigations."),
        #Chapter(id="C12", sid="CS28", name="Software Development Models", description="Waterfall, Agile, and Scrum methodologies.")
    ]

    db.session.add_all(chapters)
    db.session.commit()

    # Dummy Quizzes
    quizzes = [
        Quiz(id="Q21", cid="C3", duration=(datetime.min + timedelta(minutes=30)).time(), difficulty="Easy",state="active", no_of_questions=5,start_date=time_conversion()),
        Quiz(id="Q22", cid="C3", duration=(datetime.min + timedelta(minutes=30)).time(), difficulty="Medium",state="active", no_of_questions=2,start_date=time_conversion()),
        Quiz(id="Q23", cid="C3", duration=(datetime.min + timedelta(minutes=25)).time(), difficulty="Hard",state="active", no_of_questions=2,start_date=time_conversion()),
        Quiz(id="Q24", cid="C6", duration=(datetime.min + timedelta(minutes=40)).time(), difficulty="Extreme", no_of_questions=2,start_date=time_conversion()),
        Quiz(id="Q25", cid="C7", duration=(datetime.min + timedelta(minutes=15)).time(), difficulty="Easy", no_of_questions=2,start_date=time_conversion()),
        Quiz(id="Q26", cid="C8", duration=(datetime.min + timedelta(minutes=35)).time(), difficulty="Medium", no_of_questions=2,start_date=time_conversion()),
        #Quiz(id="Q27", cid="C9", duration=(datetime.min + timedelta(minutes=45)).time(), difficulty="Hard", no_of_questions=10),
        #Quiz(id="Q28", cid="C10", duration=(datetime.min + timedelta(minutes=50)).time(), difficulty="Extreme", no_of_questions=20),
        #Quiz(id="Q29", cid="C11", duration=(datetime.min + timedelta(minutes=30)).time(), difficulty="Medium", no_of_questions=7),
        #Quiz(id="Q30", cid="C12", duration=(datetime.min + timedelta(minutes=20)).time(), difficulty="Easy", no_of_questions=5)
    ]

    db.session.add_all(quizzes)
    db.session.commit()

    # Dummy Questions
    questions = [
    Question(id="QT11", qid="Q21", statement="What is the main characteristic of a stack?", 
             option1="FIFO", option2="LIFO", option3="Random", option4="None", correct_option=2, 
             difficulty="Easy", marks="5", 
             explanation="LIFO (Last In First Out) because the last element that goes in is the first one to come out.", 
             explanation_link="https://www.geeksforgeeks.org/stack-data-structure/"),
    
    Question(id="QT12", qid="Q21", statement="Which data structure follows FIFO?", 
             option1="Queue", option2="Stack", option3="Heap", option4="Tree", correct_option=1, 
             difficulty="Easy", marks="5", 
             explanation="FIFO (First In First Out) is followed by queues where elements are removed in the order they were added.", 
             explanation_link="https://www.geeksforgeeks.org/queue-data-structure/"),

    Question(id="QT13", qid="Q21", statement="Which operation removes an element from the top of the stack?",  
            option1="Push", option2="Pop", option3="Peek", option4="Enqueue", correct_option=2,  
            difficulty="Easy", marks="5",  
            explanation="The 'pop' operation removes the top element of the stack following the LIFO principle.",  
            explanation_link="https://www.geeksforgeeks.org/stack-set-2-infix-to-postfix/"),  

    Question(id="QT14", qid="Q21", statement="Which of the following applications use a stack?",  
            option1="Recursion", option2="Queue Implementation", option3="Graph Traversal", option4="Heap Sort", correct_option=1,  
            difficulty="Medium", marks="10",  
            explanation="Recursion uses an implicit stack to store function calls, allowing functions to execute in a last-in, first-out order.",  
            explanation_link="https://www.geeksforgeeks.org/recursion-in-python/"),  

    Question(id="QT15", qid="Q21", statement="What is the time complexity of the push operation in a stack?",  
            option1="O(1)", option2="O(n)", option3="O(log n)", option4="O(n^2)", correct_option=1,  
            difficulty="Medium", marks="10",  
            explanation="The push operation in a stack runs in O(1) time because it simply adds an element to the top.",  
            explanation_link="https://www.geeksforgeeks.org/time-complexity-of-stack-operations/"),

    Question(id="QT13", qid="Q22", statement="Which graph traversal uses a queue?", 
             option1="DFS", option2="BFS", option3="Dijkstra", option4="Kruskal", correct_option=2, 
             difficulty="Medium", marks="10", 
             explanation="BFS (Breadth-First Search) uses a queue to explore nodes level by level.", 
             explanation_link="https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/"),
    
    Question(id="QT14", qid="Q22", statement="Which algorithm finds the shortest path in graphs?", 
             option1="Bellman-Ford", option2="Prim's", option3="Floyd-Warshall", option4="Kruskal", correct_option=1, 
             difficulty="Medium", marks="10", 
             explanation="The Bellman-Ford algorithm finds the shortest path even in graphs with negative weights.", 
             explanation_link="https://www.geeksforgeeks.org/bellman-ford-algorithm/"),
    
    Question(id="QT15", qid="Q23", statement="Which sorting algorithm has O(n^2) worst-case complexity?", 
             option1="Merge Sort", option2="Heap Sort", option3="Quick Sort", option4="Bubble Sort", correct_option=4, 
             difficulty="Hard", marks="8", 
             explanation="Bubble Sort has a worst-case time complexity of O(n^2).", 
             explanation_link="https://www.geeksforgeeks.org/bubble-sort/"),
    
    Question(id="QT16", qid="Q23", statement="Which sorting algorithm is the fastest in the average case?", 
             option1="Bubble Sort", option2="Insertion Sort", option3="Quick Sort", option4="Selection Sort", correct_option=3, 
             difficulty="Hard", marks="8", 
             explanation="Quick Sort has an average time complexity of O(n log n), making it faster in general cases.", 
             explanation_link="https://www.geeksforgeeks.org/quick-sort/"),
    
    Question(id="QT17", qid="Q24", statement="What is the time complexity of BFS?", 
             option1="O(V+E)", option2="O(VE)", option3="O(V log V)", option4="O(E log V)", correct_option=1, 
             difficulty="Extreme", marks="15", 
             explanation="BFS runs in O(V+E) time, where V is vertices and E is edges.", 
             explanation_link="https://www.geeksforgeeks.org/time-complexity-of-bfs/"),
    
    Question(id="QT18", qid="Q24", statement="Which algorithm is used for minimum spanning tree?", 
             option1="Dijkstra", option2="Prim's", option3="Kruskal", option4="Floyd-Warshall", correct_option=3, 
             difficulty="Extreme", marks="15", 
             explanation="Kruskal’s algorithm is used to find the minimum spanning tree.", 
             explanation_link="https://www.geeksforgeeks.org/kruskals-algorithm/"),
    
    Question(id="QT19", qid="Q25", statement="Which SQL command removes all rows from a table?", 
             option1="DROP", option2="DELETE", option3="TRUNCATE", option4="REMOVE", correct_option=3, 
             difficulty="Easy", marks="4", 
             explanation="TRUNCATE removes all rows from a table but keeps the structure.", 
             explanation_link="https://www.geeksforgeeks.org/difference-between-delete-drop-and-truncate/"),
    
    Question(id="QT20", qid="Q25", statement="Which SQL command removes a table?", 
             option1="DROP", option2="DELETE", option3="TRUNCATE", option4="REMOVE", correct_option=1, 
             difficulty="Easy", marks="4", 
             explanation="DROP removes the entire table including its structure.", 
             explanation_link="https://www.geeksforgeeks.org/difference-between-delete-drop-and-truncate/"),
    
    Question(id="QT21", qid="Q26", statement="Which scheduling algorithm is preemptive?", 
             option1="FCFS", option2="SJF", option3="Round Robin", option4="None", correct_option=3, 
             difficulty="Medium", marks="12", 
             explanation="Round Robin scheduling is preemptive and allows time-sharing.", 
             explanation_link="https://www.geeksforgeeks.org/round-robin-scheduling/"),
    
    Question(id="QT22", qid="Q26", statement="What is a critical section in OS?", 
             option1="A section that executes concurrently", option2="A section where shared resources are accessed", 
             option3="A protected memory section", option4="A locked state", correct_option=2, 
             difficulty="Medium", marks="12", 
             explanation="A critical section is a segment where shared resources are accessed.", 
             explanation_link="https://www.geeksforgeeks.org/introduction-of-critical-section-problem-in-process-synchronization/"),
]


    db.session.add_all(questions)
    db.session.commit()

    print("Dummy data inserted successfully!")

if __name__ == "__main__":
    app.run(debug=True)