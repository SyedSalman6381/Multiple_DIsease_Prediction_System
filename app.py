import streamlit as st
import sqlite3
import bcrypt
import pickle
from streamlit_option_menu import option_menu

# === Load your models ===
diabetes_model = pickle.load(open("saved_models/diabetes_model.sav", "rb"))
heart_disease_model = pickle.load(open("saved_models/heart_disease_model.sav", "rb"))
parkinsons_model = pickle.load(open("saved_models/parkinsons_model.sav", "rb"))

# === Database helpers ===
DB_PATH = "users.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, email, password):
    conn = get_connection()
    c = conn.cursor()
    # if username or email exists, fail
    c.execute("SELECT 1 FROM users WHERE username=? OR email=?", (username, email))
    if c.fetchone():
        conn.close()
        return False
    # hash & store
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    c.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",
              (username, email, hashed))
    conn.commit()
    conn.close()
    return True

def authenticate(username_or_email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username, password FROM users WHERE username=? OR email=?",
              (username_or_email, username_or_email))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    stored_user, stored_hash = row
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return stored_user
    return None

# === Session state setup ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# === Pages ===
def auth_page():
    st.title("🔐 Please Login or Register")
    tabs = st.tabs(["Login", "Register"])

    with tabs[0]:
        st.subheader("Login")
        login_id = st.text_input("Username or Email", key="login_id")
        login_pw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            user = authenticate(login_id, login_pw)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tabs[1]:
        st.subheader("Register")
        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pw = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Register"):
            if register_user(reg_user, reg_email, reg_pw):
                st.success("Registration successful! Please switch to Login.")
            else:
                st.error("Username or Email already taken")

def app_page():
    # Sidebar profile + logout
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
        st.markdown(f"### {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = ""
            st.rerun()

    choice = option_menu(
        "Multiple Disease Diagnostic System",
        ["Disease Prediction", "Diabetes Prediction", "HeartDisease Prediction", "Parkinsons Prediction"],
        icons=["stethoscope", "activity", "heart", "person"],
        menu_icon="clipboard-data",
        default_index=0,
        orientation="vertical"
    )

    if choice == "Disease Prediction":
        st.title("Disease Prediction")
        symptoms = st.multiselect("What are your symptoms?",
            ["Fever","Cough","Fatigue","Shortness of breath","Chest Pain","Tremors"])
        if st.button("Predict"):
            info, prec, prob = "", "", {}
            if any(s in symptoms for s in ["Fever","Cough"]):
                prob["Flu/Cold/COVID-19"]=80
                info+="**Flu/Cold/COVID-19** (80%)\n"
                prec+="• Rest, hydrate\n"
            if any(s in symptoms for s in ["Fatigue","Shortness of breath"]):
                prob["Anemia/Heart Disease"]=70
                info+="**Anemia/Heart Disease** (70%)\n"
                prec+="• Iron-rich diet, checkup\n"
            if "Chest Pain" in symptoms:
                prob["Heart Disease/Reflux"]=75
                info+="**Heart Disease/Reflux** (75%)\n"
                prec+="• Avoid fatty foods, monitor BP\n"
            if "Tremors" in symptoms:
                prob["Parkinson's"]=60
                info+="**Parkinson's** (60%)\n"
                prec+="• Neurologist consult\n"
            if not info:
                st.warning("No matching disease found.")
            else:
                tab1,tab2,tab3 = st.tabs(["Description","Precautions","Probability"])
                tab1.write(info)
                tab2.write(prec)
                tab3.write(prob)

    elif choice == "Diabetes Prediction":
        st.title("Diabetes Prediction")
        name = st.text_input("Name", key="db_name")
        c1,c2,c3 = st.columns(3)
        with c1: Pregnancies=st.number_input("Pregnancies",key="db_preg")
        with c2: Glucose=st.number_input("Glucose",key="db_gluc")
        with c3: BloodPressure=st.number_input("Blood Pressure",key="db_bp")
        with c1: SkinThickness=st.number_input("Skin Thickness",key="db_skin")
        with c2: Insulin=st.number_input("Insulin",key="db_ins")
        with c3: BMI=st.number_input("BMI",key="db_bmi")
        with c1: DPF=st.number_input("DiabetesPedigreeFunction",key="db_dpf")
        with c2: Age=st.number_input("Age",key="db_age")
        if st.button("Diabetes Test"):
            data=[Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DPF,Age]
            res=diabetes_model.predict([data])[0]
            st.success("Diabetic" if res==1 else "Not Diabetic")

    elif choice == "HeartDisease Prediction":
        st.title("Heart Disease Prediction")
        name = st.text_input("Name", key="hd_name")
        c1,c2,c3 = st.columns(3)
        with c1: age=st.number_input("Age",key="hd_age")
        with c2:
            sex = 1 if st.radio("Sex",["Male","Female"],key="hd_sex")=="Male" else 0
        with c3: cp=st.number_input("Chest Pain Type",0,3,key="hd_cp")
        with c1: trestbps=st.number_input("Rest BP",key="hd_trest")
        with c2: chol=st.number_input("Cholesterol",key="hd_chol")
        with c3: fbs=st.number_input("Fasting Sugar>120",0,1,key="hd_fbs")
        with c1: restecg=st.number_input("Rest ECG",0,2,key="hd_ecg")
        with c2: thalach=st.number_input("Max HR",key="hd_thalach")
        with c3: exang=st.number_input("Exercise Angina",0,1,key="hd_exang")
        with c1: oldpeak=st.number_input("Oldpeak",key="hd_old")
        with c2: slope=st.number_input("Slope",0,2,key="hd_slope")
        with c3: ca=st.number_input("Major Vessels",0,3,key="hd_ca")
        with c1: thal=st.number_input("Thal (0–2)",0,2,key="hd_thal")
        if st.button("Heart Test"):
            d=[age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]
            res=heart_disease_model.predict([d])[0]
            st.success("Heart Disease" if res==1 else "No Heart Disease")

    else:  # Parkinsons
        st.title("Parkinson's Prediction")
        fields=["Fo","Fhi","Flo","Jitter%","JitterAbs","RAP","PPQ","DDP","Shimmer","Shimmer(dB)",
                "APQ3","APQ5","APQ","DDA","NHR","HNR","RPDE","DFA","spread1","spread2","D2","PPE"]
        vals=[]
        for i,f in enumerate(fields):
            vals.append(st.text_input(f, key=f))
        if st.button("Parkinson Test"):
            try:
                arr=[float(v) for v in vals]
                res=parkinsons_model.predict([arr])[0]
                st.success("Parkinson's" if res==1 else "No Parkinson's")
            except:
                st.error("Fill all fields with numbers")

# === Run ===
init_db()
if not st.session_state.logged_in:
    auth_page()
else:
    app_page()
