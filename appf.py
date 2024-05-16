from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os


# Initialize Firebase app and Firestore client
cred = credentials.Certificate("C:/Users/Utilizador/OneDrive/Bureau/SFE2/sfe-m-c3982-firebase-adminsdk-yps5y-df7fc0833f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin_ref = db.collection('admins').document('lLh5eIrSRsxZuCUpwFLy')  
        admin_data = admin_ref.get().to_dict()
        
        if admin_data and admin_data['username'] == username and admin_data['password'] == password:
            return redirect(url_for('admin'))
        
        return render_template('login_admin.html', error=True)
    
    return render_template('login_admin.html')


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        code_appoge = request.form['code_appoge']
        date = request.form['date']
        
        # Référence à la collection groupée des étudiants
        students_ref = db.collection_group('students')
        
        # Parcourir tous les documents étudiants dans toutes les sous-collections
        for doc in students_ref.stream():
            student_data = doc.to_dict()
            # Vérifier si les données du formulaire correspondent aux données de l'étudiant
            if (student_data.get('code_appoge') == code_appoge and
                    student_data.get('date') == date):
                # Récupérer l'ID de l'étudiant (utiliser le code_appoge comme ID)
                student_id = student_data['code_appoge']
                # Stocker l'ID de l'étudiant dans la session Flask
                session['user_id'] = student_id
                # Récupérer le prénom et le nom de l'utilisateur
                first_name = student_data.get('first_name')
                last_name = student_data.get('last_name')
                # Passer le prénom et le nom au modèle HTML
                return render_template('student.html', first_name=first_name, last_name=last_name,code_appoge=code_appoge)
        
        # Si aucun étudiant correspondant n'est trouvé, afficher un message d'erreur
        return render_template('login_student.html', error=True)
    
    # Si la méthode de la requête est GET, afficher le formulaire de connexion
    return render_template('login_student.html')


@app.route('/admin')
def admin():
    # Admin space
    return render_template('admin.html')

@app.route('/student')
def student():
    # Student space
    return render_template('student.html')

@app.route('/list_students.html')
def list_students_html():
    return render_template('list_students.html')
@app.route("/help.html")
def help():
    return render_template("help.html")
@app.route("/settings")
def settings():
    return render_template("settings.html")
@app.route("/all_dommandes")
def all_demmandes():
    demands = [...]
    return render_template("demmande_a.html")
@app.route('/demmande_student')
def demmande_s():
    # Retrieve the code_appoge associated with the logged-in student
    code_appoge = session.get('user_id')
    return render_template("demmande_s.html", code_appoge=code_appoge)


@app.route('/get_students')
def get_students():
    # Fetch students from Firebase
    students_ref = db.collection('students')
    students = students_ref.get()
    # Convert students to a list of dictionaries
    student_list = []
    for student in students:
        student_data = student.to_dict()
        student_list.append({
            'code_appoge': student_data['code_appoge'],
            'date': student_data['date'],
            'code_massar':student_data['code_massar'],
            'first_name':student_data['first_name'],
            'last_name':student_data['last_name'],
            'lieu':student_data['lieu']
            
        })

    # Return students as JSON
    return jsonify(student_list)

from flask import render_template

@app.route('/submit_demande', methods=['POST'])
def submit_demande():
    code_massar = request.form['code_massar']
    programme_academique = request.form['programme_academique']
    annee_a = request.form['annee_a']

    # Récupérer les informations de l'utilisateur à partir de Firebase
    students_ref = db.collection('students')
    query = students_ref.where('code_massar', '==', code_massar).limit(1)
    student_data = query.get()

    if not student_data:
        message = "Code massar non trouvé dans la base de données."
        return render_template('demmande_s.html', message=message)

    # Enregistrer les informations dans la collection "demande_s"
    student_info = student_data[0].to_dict()
    demande_s_ref = db.collection('demande_s')  # Fixed the collection name here
    demande_s_ref.add({
        'code_massar': code_massar,
        'code_appoge': student_info['code_appoge'],
        'programme_academique': programme_academique,
        'annee_a': annee_a,
        #'email': student_info['email'],
        'first_name': student_info['first_name'],
        'last_name': student_info['last_name'],
        'lieu':student_info['lieu'],
        'date': student_info['date'],
    })

    # JavaScript pour afficher la notification
    success_message = "Demande envoyée avec succès !"
    return render_template('demmande_s.html', success_message=success_message)




# Ajoutez cette route Flask pour récupérer les demandes des étudiants
@app.route('/get_student_requests')
def get_student_requests():
    # Référence à la collection "demande_s"
    demande_s_ref = db.collection('demande_s')

    # Récupérer toutes les demandes des étudiants
    demands = demande_s_ref.get()

    # Convertir les demandes en une liste de dictionnaires
    demand_list = []
    for demand in demands:
        demand_data = demand.to_dict()
        demand_list.append(demand_data)

    # Retourner les demandes sous forme de JSON
    return jsonify(demand_list)

@app.route('/submit_admin_response', methods=['POST'])
def submit_admin_response():
    # Extract data from the POST request
    code_massar = request.form['code_massar']
    status = request.form['status']
    reason = request.form['reason'] if status == 'reject' else None
    
    # Check if there's a document with the provided code_massar
    students_ref = db.collection('demande_s')
    query = students_ref.where('code_massar', '==', code_massar).limit(1)
    student_docs = query.get()

    if not student_docs:
        return jsonify({'error': 'Student not found with the provided code_massar.'}), 404

    # Add admin response to Firestore
    admin_responses_ref = db.collection('admin_responses')
    admin_responses_ref.add({
        'code_massar': code_massar,
        'status': status,
        'reason': reason
    })

    # Update the student's document with the admin's response
    student_doc = student_docs[0]
    student_data = student_doc.to_dict()
    student_doc.reference.update({
        'admin_response': {
            'status': status,
            'reason': reason
        }
    })
    return render_template("demmande_a.html")







if __name__ == '__main__':
    app.run(debug=True)
