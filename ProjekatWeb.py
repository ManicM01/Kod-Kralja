from flask import Flask, render_template, url_for, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
import mariadb
import mysql.connector
import ast

app = Flask(__name__)
app.secret_key = "tajni_kljuc_aplikacije"

konekcija = mysql.connector.connect(
passwd="",
user="root",
database="webdizajn",
port=3306,
)

kursor = konekcija.cursor(dictionary=True)

def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False

def opis():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).pop("opis")  
        



@app.route('/login', methods=["GET", "POST"] )
def login():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        forma = request.form
        upit = "SELECT * FROM korisnici WHERE email = %s"
        vrednost = (forma['email'],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        if korisnik != None:
            if check_password_hash(korisnik["lozinka"], forma["lozinka"]):
                session["ulogovani_korisnik"] = str(korisnik)
                return redirect(url_for("home"))
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")   


@app.route('/logout')
def logout():
    session.pop('ulogovani_korisnik', None)
    return redirect(url_for('login'))                    



@app.route('/', methods=["GET", "POST"] )
def home():
    return render_template('home.html')


@app.route('/korisnici', methods=['GET'] )
def korisnici():
    upit="select * from korisnici"
    kursor.execute(upit)
    korisnici= kursor.fetchall()
    return render_template('korisnici.html', korisnici = korisnici)


@app.route('/novi_korisnik', methods=["GET", "POST"])
def novi_korisnik():
    if request.method == "GET":
        return render_template('novi_korisnik.html')

    if request.method == "POST":
        forma = request.form
        hesovana_lozinka = generate_password_hash(forma["lozinka"])
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["email"],
            forma["opis"],
            hesovana_lozinka
        )
    
        upit = """insert into 
                    korisnici(ime, prezime, email, opis, lozinka)
                    values (%s, %s, %s, %s, %s)"""

        kursor.execute(upit, vrednosti)
        konekcija.commit()

        return redirect(url_for("korisnici"))

@app.route('/pice', methods=["GET", "POST"] )
def pice():
    return render_template('pice.html')


@app.route('/burgeri', methods=["GET", "POST"] )
def burgeri():
    return render_template('burgeri.html')


@app.route('/korisnik_brisanje/<id>', methods={"POST"})
def korisnik_brisanje(id):
    upit="""
            DELETE FROM korisnici WHERE id=%s
     """
    vrednost = (id, )
    kursor.execute(upit, vrednost)
    konekcija.commit()
    return redirect(url_for("korisnici"))


@app.route('/korisnik_izmena/<id>', methods=["GET", "POST"] )
def korisnik_izmena(id):
    if request.method == "GET":
        upit = "select * from korisnici where id=%s"
        vrednost = (id, )
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()

        return render_template("korisnik_izmena.html", korisnik = korisnik )

    if request.method == "POST":
        upit = """ update korisnici set
                    ime = %s, prezime = %s, email = %s, opis = %s, lozinka = %s
                     where id = %s
        """
        forma = request.form
        vrednosti = (
            forma["ime"],
            forma["prezime"],
            forma["email"],
            forma["opis"],
            forma["lozinka"],
            id
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()
        return redirect(url_for('korisnici'))





app.run(debug=True)