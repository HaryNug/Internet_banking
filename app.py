from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hary300697@localhost:5432/Internet_banking'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
    
class Branch(db.Model):
    __tablename__ = "branch"

    branch_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return f"<Branch{self.branch_id}>"
    
class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, autoincrement= True, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    telp = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User{self.user_id}>"

class Account(db.Model):
    __tablename__ = "account"

    account_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=False)
    status = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    saldo = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Account{self.account_id}>"

class Accountivity(db.Model):
    __tablename__ = "account_activity"

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False)
    activity_date = db.Column(db.DateTime, nullable=False)
    credit = db.Column(db.Integer, nullable=True)
    debit = db.Column(db.Integer, nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=True)
    saldo = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Account activity{self.activity_id}>"
    
def login():
    data_email = request.authorization.username
    data_password = request.authorization.password
    user = User.query.filter_by(
        email=data_email, password=data_password).first()

    if user:
        return user
    else :
        return {"error": "invalid request"}

@app.get('/')
def home():
    return {"message":"welcome to saku bank API"}

@app.post('/member')
def register():
    data = request.get_json()
    valid_telp =  User.query.filter_by(telp=data["telp"]).first()
    if valid_telp :
        return {"error": f"Telp with number {valid_telp.telp} is invalid or already exists"}
    valid_email =  User.query.filter_by(email=data["email"]).first()
    if valid_email :
        return {"error": f"email with {valid_telp.email} is invalid or already exists"}
    new_member = User(
        branch_id = data['branch_id'],
        name = data['name'],
        telp = data['telp'],
        email = data['email'],
        password = data['password'],
        type = "member")
    db.session.add(new_member)
    db.session.commit()
    new_account = Account(
        user_id = new_member.user_id,
        branch_id = data['branch_id'],
        status = "active",
        type = data['type'],
        saldo = data['credit'],
        last_update = datetime.today())
    db.session.add(new_account)
    db.session.commit()
    new_activity = Accountivity(
        account_id = new_account.account_id,
        activity_date = datetime.today(),
        credit = data['credit'],
        saldo = data['credit'])
    db.session.add(new_activity)
    db.session.commit()
    return {"message": f"congratulation {new_member.name} for becoming our new member😚"}

@app.put('/member/<int:user_id>')
def put_member(user_id):
    user = login()
    if user.type == "member" and user.user_id == user_id :
        member =User.query.get(user_id)
        data = request.get_json()
        member.branch_id = data.get("branch_id", member.branch_id)
        member.name = data.get("name", member.name)
        member.telp = data.get("telp", member.telp)
        member.email = data.get("email", member.email)
        member.password = data.get("password", member.password)
        db.session.commit()
        return {"message": "your account successfully updated"}
    return {"message": "invalid request"}

@app.post('/branch')
def post_branch():
    user = login()
    if user.type == "admin" :
        data = request.get_json()
        new_branch = Branch(
            name = data['name'],
            address = data['address'])
        db.session.add(new_branch)
        db.session.commit()
        return {"message": f"congratulation {new_branch.name} successfully created😚"}
    return {"message": "invalid request"}

@app.put('/branch/<int:branch_id>')
def put_branch(branch_id):
    user = login()
    if user.type == "admin" and user.branch_id == branch_id :
        branch =Branch.query.get(branch_id)
        data = request.get_json()
        branch.name = data.get("name", branch.name)
        branch.address = data.get("address", branch.address)
        db.session.commit()
        return {"message": "branch successfully updated"}
    return {"message": "invalid request"}

@app.post('/admin')
def post_admin():
    user = login()
    if user.type == "admin":    
        data = request.get_json()
        valid_telp =  User.query.filter_by(telp=data["telp"]).first()
        if valid_telp :
            return {"error": f"Telp with number {valid_telp.telp} is invalid or already exists"}
        valid_email =  User.query.filter_by(email=data["email"]).first()
        if valid_email :
            return {"error": f"email with {valid_telp.email} is invalid or already exists"}    
        new_member = User(
            branch_id = user.branch_id,
            name = data['name'],
            telp = data['telp'],
            email = data['email'],
            password = data['password'],
            type = "admin")
        db.session.add(new_member)
        db.session.commit()
        return {"message": f"congratulation {new_member.name} for becoming our new admin😚"}
    return {"message": "invalid request"}

@app.put('/admin/<int:user_id>')
def put_admin(user_id):
    user = login()
    if user.type == "admin" and user.user_id == user_id :
        admin =User.query.get(user_id)
        data = request.get_json()
        admin.branch_id = data.get("branch_id", admin.branch_id)
        admin.name = data.get("name", admin.name)
        admin.telp = data.get("telp", admin.telp)
        admin.email = data.get("email", admin.email)
        admin.password = data.get("password", admin.password)
        db.session.commit()
        return {"message": "your account successfully updated"}
    return {"message": "invalid request"}

@app.post('/account')
def post_account():
    user = login()
    if user.type == "member":    
        data = request.get_json()
        new_account = Account(
            user_id = user.user_id,
            branch_id = data['branch_id'],
            status = "active",
            type = data['type'],
            saldo = data['credit'],
            last_update = datetime.today())
        db.session.add(new_account)
        db.session.commit()
        new_activity = Accountivity(
            account_id = new_account.account_id,
            activity_date = datetime.today(),
            credit = data['credit'],
            saldo = data['credit'])
        db.session.add(new_activity)
        db.session.commit()
        return {"message": f"congratulation new account with id {new_account.account_id} succesfully created😚"}
    return {"message": "invalid request"}

@app.put('/account/<int:account_id>')
def put_account(account_id):
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :
        data = request.get_json()
        account.branch_id = data.get("branch_id", account.branch_id)
        db.session.commit()
        return {"message": "your account successfully updated"}
    return {"message": "invalid request"}

@app.put('/nonactive/<int:account_id>')
def put_nonactive(account_id):
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :
        account.status = "nonactive"
        db.session.commit()
        return {"message": "your account is nonactive"}
    return {"message": "invalid request"}

@app.put('/active/<int:account_id>')
def put_active(account_id):
    user = login()
    account = Account.query.get(account_id)
    if user.type == "admin" and account.branch_id == user.branch_id :
        account.status = "active"
        db.session.commit()
        return {"message": f"account {account_id} is active"}
    return {"message": "invalid request"}

@app.post('/save/<account_id>')
def post_save(account_id):
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :    
        data = request.get_json()
        account.saldo += data["credit"]
        account.last_update = datetime.today()
        db.session.commit()
        new_activity = Accountivity(
            account_id = account.account_id,
            activity_date = datetime.today(),
            credit = data["credit"],
            saldo = account.saldo)   
        db.session.add(new_activity)
        db.session.commit()
        return {"message": f"successfully saved {new_activity.credit} now your balance : {new_activity.saldo}"}
    return {"message": "invalid request"}

@app.post('/withdraw/<account_id>')
def post_withdraw(account_id):
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :    
        data = request.get_json()
        account.saldo -= data["debit"]
        account.last_update = datetime.today()
        db.session.commit()
        new_activity = Accountivity(
            account_id = account.account_id,
            activity_date = datetime.today(),
            debit = data["debit"],
            saldo = account.saldo)    
        db.session.add(new_activity)
        db.session.commit()
        return {"message": f"successfully withdrawn {new_activity.debit} now your balance : {new_activity.saldo}"}
    return {"message": "invalid request"}

@app.post('/transfer/<account_id>')
def post_transfer(account_id):
    user = login()
    data = request.get_json()
    sender = Account.query.get(account_id)
    receiver = Account.query.get(data["receiver_id"])
    if user.type == "member" and sender.user_id == user.user_id :    
        sender.saldo -= data["transfer"]
        sender.last_update = datetime.today()
        db.session.commit()
        new_send = Accountivity(
            account_id = sender.account_id,
            activity_date = datetime.today(),
            debit = data["transfer"],
            receiver_id = data["receiver_id"],
            saldo = sender.saldo)    
        db.session.add(new_send)
        db.session.commit()
        receiver.saldo += data["transfer"]
        receiver.last_update = datetime.today()
        new_receive = Accountivity(
            account_id = data["receiver_id"],
            activity_date = datetime.today(),
            credit = data["transfer"],
            sender_id = sender.account_id,
            saldo = receiver.saldo)
        db.session.add(new_receive)
        db.session.commit()
        return {"message": f"successfully tranfer {new_send.debit} to {new_send.receiver_id} now your balance : {new_send.saldo}"}
    return {"message": "invalid request"}

@app.get('/history/<account_id>')
def get_history(account_id):
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :
        history = Accountivity.query.filter_by(account_id=account_id).all()
        results = [
            {
                "activity_date" : r.activity_date,
                "credit" : r.credit,
                "debit" : r.debit,
                "receiver_id" : r.receiver_id,
                "sender_id" : r.sender_id,
                "saldo" : r.saldo
            } for r in history]
        return jsonify(results)
    return {"message": "invalid request"}



if (__name__) == ("__main__"):
    app.run(debug=True)