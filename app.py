import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta




app = Flask(__name__)

def connect_db():
    try:
        print("se incearca conectarea")
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=ZENBOOK\\SQLEXPRESS;'
            'DATABASE=FitnessCenter;'
            'Trusted_Connection=yes;'
        )
        print("Conexiune reusita!")
        return conn
    except pyodbc.Error as e:
        print(f"Eroare de conectare: {e}")
        return None

def get_user_role(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Rol FROM Users WHERE Username=? AND Parola=?", (username, password))
    result = cursor.fetchone()
    
    if result:
        return result[0]  
    return None  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_redirect')
def test_redirect():
    return redirect('/client')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        role = get_user_role(username, password)
        
        if role:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT UserID FROM Users WHERE Username=? AND Parola=?", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['client_id'] = user[0]  # Setăm client_id în sesiune
                
            if role == 'admin':
                return redirect('/admin')
            else:
                return redirect('/client')
        else:
            flash("Username-ul sau parola sunt incorecte. Dacă nu aveți cont, veți fi redirecționat către pagina de înregistrare.", "error")
            return redirect('/register')  # Redirecționează către pagina de înregistrare
    
    return render_template('login.html')


app.secret_key = 'o_cheie_secreta_aleatoare'

@app.route('/admin')
def admin_dashboard():
    """Pagină pentru admin."""
    return render_template('admin_dashboard.html')

@app.route('/client')
def client_dashboard():
    client_id = session.get('client_id')
    print(f"Client ID în sesiune: {client_id}")  # Debugging
    if client_id:
        return render_template('client_dashboard.html')
    else:
        return "Eroare: Utilizatorul nu este autentificat."


@app.route('/view_prices')
def view_prices():
    conn = connect_db()
    cursor = conn.cursor()
    # Modificăm interogarea pentru a elimina duplicatele
    cursor.execute("""
        SELECT TipAbonament, MIN(Pret) AS Pret
        FROM Abonament
        GROUP BY TipAbonament
        ORDER BY TipAbonament
    """)
    prices = cursor.fetchall()  # Extrage toate rezultatele
    conn.close()  # Închide conexiunea
    return render_template('view_prices.html', prices=prices)  # Trimite datele către șablon


@app.route('/client_my_subscription')
def client_my_subscription():
    client_id = session.get('client_id')
    if not client_id:
        return "Error: User not authenticated.", 401

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Obține abonamentele utilizatorului din UserDetails
        cursor.execute("""
            SELECT TipAbonament, PretAbonament, DataInscrierii
            FROM UserDetails
            WHERE UserID = ?
        """, (client_id,))
        subscriptions = cursor.fetchall()

        conn.close()

        # Verificăm dacă există abonamente
        if not subscriptions:
            message = "You don't have any subscriptions."
            return render_template('client_my_subscription.html', message=message)
        
        # Trimite abonamentele către șablon
        return render_template('client_my_subscription.html', subscriptions=subscriptions)

    except Exception as e:
        conn.close()
        return f"Error retrieving subscriptions: {e}"

@app.route('/client_classes')
def client_classes():
    """Programul claselor și înscrierea la ele."""
    client_id = session.get('client_id')
    if not client_id:
        return "Error: User not authenticated.", 401

    conn = connect_db()
    cursor = conn.cursor()

    # Obține programul tuturor claselor
    cursor.execute("""
        SELECT c.ClasaID, c.Denumire, c.Ora, CONCAT(a.Nume, ' ', a.Prenume) AS Trainer
        FROM Clase c
        JOIN Antrenori a ON c.AntrenorID = a.AntrenorID
        ORDER BY c.Ora ASC;
    """)
    program_classes = cursor.fetchall()

    # Formatarea timpului HH:MM
    formatted_program_classes = []
    for clasa in program_classes:
        ora_str = clasa[2][:5]  # Extrage doar HH:MM
        formatted_program_classes.append((clasa[0], clasa[1], ora_str, clasa[3]))

    # Obține clasele la care utilizatorul este înscris
    cursor.execute("""
        SELECT c.Denumire, c.Ora, CONCAT(a.Nume, ' ', a.Prenume) AS Trainer
        FROM DetaliiClase dc
        JOIN Clase c ON dc.ClasaID = c.ClasaID
        JOIN Antrenori a ON c.AntrenorID = a.AntrenorID
        WHERE dc.UserID = ?;
    """, (client_id,))
    enrolled_classes = cursor.fetchall()

    # Formatarea timpului HH:MM
    formatted_enrolled_classes = []
    for clasa in enrolled_classes:
        ora_str = clasa[1][:5]  # Extrage doar HH:MM
        formatted_enrolled_classes.append((clasa[0], ora_str, clasa[2]))

    # Obține clasele disponibile
    cursor.execute("""
        SELECT c.ClasaID, c.Denumire, c.Ora, CONCAT(a.Nume, ' ', a.Prenume) AS Trainer
        FROM Clase c
        JOIN Antrenori a ON c.AntrenorID = a.AntrenorID
        WHERE c.ClasaID NOT IN (
            SELECT ClasaID FROM DetaliiClase WHERE UserID = ?
        );
    """, (client_id,))
    available_classes = cursor.fetchall()

    # Formatarea timpului HH:MM
    formatted_available_classes = []
    for clasa in available_classes:
        ora_str = clasa[2][:5]  # Extrage doar HH:MM
        formatted_available_classes.append((clasa[0], clasa[1], ora_str, clasa[3]))

    conn.close()
    return render_template('client_classes.html', 
                           program_classes=formatted_program_classes, 
                           enrolled_classes=formatted_enrolled_classes, 
                           available_classes=formatted_available_classes)

@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        client_id = session.get('client_id')
        feedback = request.form.get('feedback')

        if client_id and feedback:
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Feedback (UserID, Comentarii, DataFeedback) VALUES (?, ?, GETDATE())",
                    (client_id, feedback)
                )
                conn.commit()
                conn.close()
                return render_template('submit_feedback.html', message="Feedback-ul tău a fost trimis cu succes!")
            except Exception as e:
                return render_template('submit_feedback.html', error=f"Eroare la trimiterea feedback-ului: {e}")
        else:
            return render_template('submit_feedback.html', error="Eroare: Feedback-ul sau autentificarea lipsesc.")
    
    return render_template('submit_feedback.html')

@app.route('/logout', methods=['GET'])
def logout():
    """Gestionarea deconectării utilizatorului."""
    session.clear()  # Șterge toate datele din sesiune
    return redirect('/login')  # Redirecționează utilizatorul către pagina de login



@app.route('/admin_feedback')
def admin_feedback():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.FeedbackID, u.Nume, f.Comentarii, f.DataFeedback
        FROM Feedback f
        JOIN Users u ON f.UserID = u.UserID
        ORDER BY f.DataFeedback DESC;
    """)
    feedbacks = cursor.fetchall()
    conn.close()
    return render_template('admin_feedback.html', feedbacks=feedbacks)

@app.route('/admin_classes')
def admin_classes():
    conn = connect_db()
    cursor = conn.cursor()

    # Obține clasele existente
    cursor.execute("""
        SELECT c.ClasaID, c.Denumire, c.Descriere, c.Ora, 
               CONCAT(a.Nume, ' ', a.Prenume) AS Trainer
        FROM Clase c
        JOIN Antrenori a ON c.AntrenorID = a.AntrenorID
        ORDER BY c.Ora ASC;
    """)
    classes = cursor.fetchall()

    # Conversia timpului în format HH:MM (fără strftime)
    formatted_classes = []
    for clasa in classes:
        ora_str = clasa[3][:5]  # Ia doar primele 5 caractere (HH:MM)
        formatted_classes.append((clasa[0], clasa[1], clasa[2], ora_str, clasa[4]))

    # Obține lista de antrenori pentru dropdown
    cursor.execute("SELECT AntrenorID, CONCAT(Nume, ' ', Prenume) AS FullName FROM Antrenori")
    trainers = cursor.fetchall()

    conn.close()
    return render_template('admin_classes.html', classes=formatted_classes, trainers=trainers)


@app.route('/create_client_subscription', methods=['GET', 'POST'])
def create_client_subscription():
    client_id = session.get('client_id')  # Obține ID-ul utilizatorului autentificat
    if not client_id:
        return "Error: User not authenticated.", 401

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        tip_abonament = request.form.get('tip_abonament')

        if not tip_abonament:
            flash("Please select a subscription type.", "error")
            return redirect(url_for('create_client_subscription'))

        try:
            # Obține detaliile abonamentului selectat
            cursor.execute("""
                SELECT AbonamentID, TipAbonament, Pret, Valabilitate
                FROM Abonament
                WHERE TipAbonament = ?
            """, (tip_abonament,))
            abonament = cursor.fetchone()

            if not abonament:
                flash("Invalid subscription type.", "error")
                return redirect(url_for('create_client_subscription'))

            abonament_id, tip_abonament, pret, valabilitate = abonament

            # Calculează datele de început și sfârșit
            data_inceput = datetime.now().date()
            data_sfarsit = data_inceput + timedelta(days=valabilitate)

            # Introduce detaliile abonamentului în UserDetails
            cursor.execute("""
                INSERT INTO UserDetails (UserID, Nume, TipAbonament, PretAbonament)
                SELECT u.UserID, u.Nume, ?, ?
                FROM Users u
                WHERE u.UserID = ?
            """, (tip_abonament, pret, client_id))
            conn.commit()

            flash("Subscription created successfully!", "success")
            return redirect(url_for('client_my_subscription'))

        except Exception as e:
            conn.rollback()
            flash(f"Error creating subscription: {e}", "error")

    # Dacă metoda este GET, afișează formularul
    cursor.execute("SELECT DISTINCT TipAbonament FROM Abonament")
    tipuri_abonamente = cursor.fetchall()
    conn.close()
    return render_template('create_client_subscription.html', tipuri_abonamente=tipuri_abonamente)


@app.route('/admin_subscriptions')
def admin_subscriptions():
    """Vizualizează toate abonamentele utilizatorilor."""
    conn = connect_db()
    cursor = conn.cursor()

    # Selectăm toate abonamentele din UserDetails
    cursor.execute("""
        SELECT ud.UserID, ud.Nume, ud.TipAbonament, ud.PretAbonament, ud.DataInscrierii
        FROM UserDetails ud
        WHERE ud.TipAbonament IS NOT NULL
        ORDER BY ud.UserID, ud.DataInscrierii ASC;
    """)
    subscriptions = cursor.fetchall()
    conn.close()

    return render_template('admin_subscriptions.html', subscriptions=subscriptions)


@app.route('/enroll_class', methods=['POST'])
def enroll_class():
    client_id = session.get('client_id')
    clasa_id = request.form.get('class')

    print(f"Client ID: {client_id}, Clasa ID: {clasa_id}")

    if not client_id or not clasa_id:
        return "Eroare: ID-ul clientului sau al clasei nu este valid.", 400

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Verifică dacă clientul este deja înscris la această clasă
        cursor.execute("""
            SELECT * FROM DetaliiClase WHERE UserID = ? AND ClasaID = ?
        """, (client_id, clasa_id))
        existing_entry = cursor.fetchone()

        if existing_entry:
            flash("Eroare: Ești deja înscris la această clasă!", "error")
            return redirect(url_for('client_classes'))

        # Inserează o nouă înregistrare dacă nu există
        cursor.execute("""
            INSERT INTO DetaliiClase (UserID, ClasaID, DataInscrierii)
            VALUES (?, ?, GETDATE())
        """, (client_id, clasa_id))
        conn.commit()

        flash("Înscriere realizată cu succes!", "success")
        return redirect(url_for('client_classes'))

    except Exception as e:
        return f"Eroare la înscriere: {e}", 500
    

@app.route('/admin_view_users')
def admin_view_users():
    try:
        conn = connect_db()  # Conexiunea la baza de date
        cursor = conn.cursor()

        # Obține utilizatorii
        cursor.execute("SELECT UserID, Username, Rol, Nume, Email, DataNasterii FROM Users")
        users = cursor.fetchall()

        conn.close()

        # Trimite lista către șablonul HTML
        return render_template('admin_users.html', users=users)
    except Exception as e:
        return f"Eroare la afișarea utilizatorilor: {e}", 500

@app.route('/admin_echipamente', methods=['GET', 'POST'])
def admin_echipamente():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        
        # Adaugare echipament
        if action == 'add':
            name = request.form.get('name')
            eq_type = request.form.get('type')
            status = request.form.get('status')

            try:
                cursor.execute("""
                    INSERT INTO Echipamente (Denumire, Tip, Status)
                    VALUES (?, ?, ?)
                """, (name, eq_type, status))
                conn.commit()
                flash("Equipment added successfully!", "success")
            except Exception as e:
                flash(f"Error adding equipment: {e}", "error")

        # Modificare status echipament
        elif action == 'update':
            eq_id = request.form.get('id')
            status = request.form.get('status')

            try:
                cursor.execute("""
                    UPDATE Echipamente
                    SET Status = ?
                    WHERE EchipamentID = ?
                """, (status, eq_id))
                conn.commit()
                flash("Equipment updated successfully!", "success")
            except Exception as e:
                flash(f"Error updating equipment: {e}", "error")

        # Ștergere echipament
        elif action == 'delete':
            eq_id = request.form.get('id')

            try:
                cursor.execute("""
                    DELETE FROM Echipamente
                    WHERE EchipamentID = ?
                """, (eq_id,))
                conn.commit()
                flash("Equipment deleted successfully!", "success")
            except Exception as e:
                flash(f"Error deleting equipment: {e}", "error")

    # Obține toate echipamentele
    cursor.execute("SELECT * FROM Echipamente")
    echipamente = cursor.fetchall()
    conn.close()

    return render_template('admin_echipamente.html', echipamente=echipamente)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Verifică dacă username-ul sau email-ul există deja
            cursor.execute("SELECT * FROM Users WHERE Username = ? OR Email = ?", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username or email already exists. Please choose a different one.", "error")
                return redirect('/register')

            # Adaugă noul utilizator în baza de date
            cursor.execute("""
                INSERT INTO Users (Username, Parola, Rol, Nume, Email, NumarTelefon, Adresa)
                VALUES (?, ?, 'client', ?, ?, ?, ?)
            """, (username, password, name, email, phone, address))
            conn.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect('/login')
        except Exception as e:
            conn.rollback()
            flash(f"Error creating account: {e}", "error")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/delete_class/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Ștergere clasa din baza de date
        cursor.execute("DELETE FROM Clase WHERE ClasaID = ?", (class_id,))
        conn.commit()
        flash("Class deleted successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting class: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('admin_classes'))

@app.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Preluăm datele din formular
        name = request.form.get('name')
        description = request.form.get('description')
        time = request.form.get('time')
        trainer_id = request.form.get('trainer_id')

        try:
            # Actualizare clasă în baza de date
            cursor.execute("""
                UPDATE Clase 
                SET Denumire = ?, Descriere = ?, Ora = ?, AntrenorID = ?
                WHERE ClasaID = ?
            """, (name, description, time, trainer_id, class_id))
            conn.commit()
            flash("Class updated successfully!", "success")
            return redirect(url_for('admin_classes'))
        except Exception as e:
            conn.rollback()
            flash(f"Error updating class: {e}", "error")
    else:
        # Obținem detaliile clasei pentru formular
        cursor.execute("SELECT Denumire, Descriere, Ora, AntrenorID FROM Clase WHERE ClasaID = ?", (class_id,))
        class_details = cursor.fetchone()

        # Obținem lista de antrenori
        cursor.execute("SELECT AntrenorID, Nume, Prenume FROM Antrenori")
        trainers = cursor.fetchall()

        conn.close()
        return render_template('edit_class.html', class_details=class_details, trainers=trainers)
    
@app.route('/client_equipment')
def client_equipment():
    """Vizualizare echipamente disponibile și statusul lor."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EchipamentID, Denumire, Tip, Status
        FROM Echipamente
        ORDER BY EchipamentID ASC
    """)
    echipamente = cursor.fetchall()
    conn.close()
    return render_template('client_equipment.html', echipamente=echipamente)

@app.route('/add_class', methods=['GET', 'POST'])
def add_class():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        time = request.form['time']
        trainer_id = request.form['trainer']

        try:
            cursor.execute("""
                INSERT INTO Clase (Denumire, Descriere, Ora, AntrenorID)
                VALUES (?, ?, ?, ?)
            """, (name, description, time, trainer_id))
            conn.commit()
            return redirect(url_for('admin_classes'))
        except Exception as e:
            conn.rollback()
            return f"Error adding the class: {e}", 500
        finally:
            conn.close()

    # Dacă metoda este GET, obținem lista de antrenori
    cursor.execute("SELECT AntrenorID, CONCAT(Nume, ' ', Prenume) AS FullName FROM Antrenori")
    trainers = cursor.fetchall()

    print(trainers)  # Debugging - verifică dacă lista conține antrenori

    conn.close()

    return render_template('add_class.html', trainers=trainers)

if __name__ == '__main__':
    app.run(debug=True)
