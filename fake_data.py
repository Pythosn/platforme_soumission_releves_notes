import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
from datetime import datetime

# Initialize Firebase app and Firestore client
cred = credentials.Certificate("C:/Users/Utilizador/OneDrive/Bureau/SFE2/sfe-m-c3982-firebase-adminsdk-yps5y-df7fc0833f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to generate fake student data
def generate_fake_student():
    code_appoge = ''.join(random.choices('0123456789', k=6))
    code_massar = 'G' + ''.join(random.choices('0123456789', k=9))
    date = datetime.now().strftime("%d-%m-%Y")
    first_name = random.choice(['Fatima', 'Mohamed', 'Amina', 'Youssef', 'Hafsa', 'Karim'])
    last_name = random.choice(['Aitelyassfi', 'Zahiri', 'Ouahbi', 'Saidi', 'El Bouhali', 'Chakir'])
    lieu = random.choice(['Marrakech', 'Casablanca', 'Rabat', 'Fes', 'Tangier', 'Agadir'])
    return {
        'code_appoge': code_appoge,
        'code_massar': code_massar,
        'date': date,
        'first_name': first_name,
        'last_name': last_name,
        'lieu': lieu
    }

# Add fake student data to Firestore
def add_fake_students():
    collection_ref = db.collection('students')
    for _ in range(10):  # Add 10 fake students
        fake_student_data = generate_fake_student()
        collection_ref.add(fake_student_data)
    print("Fake students added successfully!")

if __name__ == '__main__':
    add_fake_students()
