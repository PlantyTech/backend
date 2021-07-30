from app import db
# Database ORMs


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))
    telefon = db.Column(db.String(50))
    locatie = db.Column(db.String(100))
    image = db.relationship("Image", back_populates="user")
    notification = db.relationship("Notification", back_populates="user")
    comanda = db.relationship("Comanda", back_populates="user")
    detaliicomanda = db.relationship("DetaliiComanda", back_populates="user")


class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    image = db.Column(db.String, nullable=False)
    disease = db.Column(db.String(80))
    treatment = db.Column(db.String(100))
    data1 = db.Column(db.DateTime)
    data2 = db.Column(db.DateTime)
    categorie = db.Column(db.String(80), nullable=False)
    user = db.relationship("User", back_populates="image")


class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    titlu = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String)
    data = db.Column(db.DateTime)
    citit = db.Column(db.Boolean, nullable=False)
    categorie = db.Column(db.String(80))
    user = db.relationship("User", back_populates="notification")


class Produs(db.Model):
    __tablename__ = 'produs'
    produs_id = db.Column(db.Integer, primary_key=True)
    producator = db.Column(db.String(80), nullable=False)
    nume = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String)
    descriere = db.Column(db.String)
    pret = db.Column(db.Float)
    furnizor = db.Column(db.String(80))
    stoc = db.Column(db.Integer)
    detalii_produs = db.relationship("Detalii_Produs", back_populates="produs")
    produse_comandate = db.relationship("Produse_Comandate", back_populates="produs")


class Detalii_Produs(db.Model):
    __tablename__ = 'detalii_produs'
    detalii_produs_id = db.Column(db.Integer, primary_key=True)
    produs_id = db.Column(db.Integer, db.ForeignKey('produs.produs_id'), nullable=False)
    cultura = db.Column(db.String(80), nullable=False)
    daunatori = db.Column(db.String(80), nullable=False)
    doza_Ha = db.Column(db.Float)
    doza_l_mp = db.Column(db.Float)
    timp_pauza = db.Column(db.String(80))
    produs = db.relationship("Produs", back_populates="detalii_produs")


class Comanda(db.Model):
    __tablename__ = 'comanda'
    comanda_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    total_pret = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    data1 = db.Column(db.DateTime)
    detaliicomanda_id_l = db.Column(db.Integer, db.ForeignKey('detaliicomanda.detaliicomanda_id'), nullable=False)
    detaliicomanda_id_f = db.Column(db.Integer, db.ForeignKey('detaliicomanda.detaliicomanda_id'), nullable=False)
    mod_plata = db.Column(db.String(80))
    user = db.relationship("User", back_populates="comanda")
    produse_comandate = db.relationship("Produse_Comandate", back_populates="comanda")


class Produse_Comandate(db.Model):
    __tablename__ = 'produse_comandate'
    produse_comandate_id = db.Column(db.Integer, primary_key=True)
    comanda_id = db.Column(db.Integer, db.ForeignKey('comanda.comanda_id'), nullable=False)
    produs_id = db.Column(db.Integer, db.ForeignKey('produs.produs_id'), nullable=False)
    cantitate = db.Column(db.Integer, nullable=False)
    comanda = db.relationship("Comanda", back_populates="produse_comandate")
    produs = db.relationship("Produs", back_populates="produse_comandate")


class DetaliiComanda(db.Model):
    __tablename__ = 'detaliicomanda'
    detaliicomanda_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    tip_comanda = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(70))
    FirstName = db.Column(db.String(50))
    SecondName = db.Column(db.String(50))
    telefon = db.Column(db.String(50))
    judet = db.Column(db.String(50))
    oras = db.Column(db.String(50))
    strada = db.Column(db.String(50))
    numar = db.Column(db.String(30))
    bloc = db.Column(db.String(30))
    scara = db.Column(db.String(30))
    apartament = db.Column(db.String(30))
    user = db.relationship("User", back_populates="detaliicomanda")


class Fitofarmacii(db.Model):
    __tablename__ = 'fitofarmacii'
    fitofarmacii_id = db.Column(db.Integer, primary_key=True)
    locatie = db.Column(db.String(100))
    nume = db.Column(db.String(100))
    judet = db.Column(db.String(100))
    email = db.Column(db.String(70))
    telefon = db.Column(db.String(50))
    orar = db.Column(db.String(100))
