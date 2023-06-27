from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.sql import func

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
    saldo = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    ever_dormant = db.Column(db.Boolean, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

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
    if not user :
        return False
    if user:
        return user
        

@app.get('/')
def home():
    return {"message":"welcome to saku bank API"}

@app.post('/member')
def register():
    data = request.get_json()
    valid_telp =  User.query.filter_by(telp=data["telp"]).first()
    if valid_telp :
        return {"error": f"Telp with number {valid_telp.telp} is invalid or already exists"},400
    valid_email =  User.query.filter_by(email=data["email"]).first()
    if valid_email :
        return {"error": f"email with {valid_telp.email} is invalid or already exists"},400
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
        ever_dormant = False,
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
    return {"message": f"congratulation {new_member.name} for becoming our new member"},201

@app.put('/member/<int:user_id>')
def put_member(user_id):
    if not login():
        return {"error": "invalid request"},400
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
        return {"message": "your account successfully updated"},200
    else :
        return {"message": "invalid request"},400


@app.post('/branch')
def post_branch():
    if not login():
        return {"error": "invalid request"},400
    user = login()
    if user.type == "admin" :
        data = request.get_json()
        new_branch = Branch(
            name = data['name'],
            address = data['address'])
        db.session.add(new_branch)
        db.session.commit()
        return {"message": f"congratulation {new_branch.name} successfully created"},201
    return {"message": "invalid request"},400

@app.put('/branch/<int:branch_id>')
def put_branch(branch_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    if user.type == "admin" and user.branch_id == branch_id :
        branch =Branch.query.get(branch_id)
        data = request.get_json()
        branch.name = data.get("name", branch.name)
        branch.address = data.get("address", branch.address)
        db.session.commit()
        return {"message": "branch successfully updated"},200
    return {"message": "invalid request"},400

@app.post('/admin')
def post_admin():
    if not login():
        return {"error": "invalid request"},400
    user = login()
    if user.type == "admin":    
        data = request.get_json()
        valid_telp =  User.query.filter_by(telp=data["telp"]).first()
        if valid_telp :
            return {"error": f"Telp with number {valid_telp.telp} is invalid or already exists"},400
        valid_email =  User.query.filter_by(email=data["email"]).first()
        if valid_email :
            return {"error": f"email with {valid_telp.email} is invalid or already exists"},400    
        new_member = User(
            branch_id = user.branch_id,
            name = data['name'],
            telp = data['telp'],
            email = data['email'],
            password = data['password'],
            type = "admin")
        db.session.add(new_member)
        db.session.commit()
        return {"message": f"congratulation {new_member.name} for becoming our new admin"},201
    return {"message": "invalid request"},400

@app.put('/admin/<int:user_id>')
def put_admin(user_id):
    if not login():
        return {"error": "invalid request"},400
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
        return {"message": "your account successfully updated"},200
    return {"message": "invalid request"},400

@app.post('/account')
def post_account():
    if not login():
        return {"error": "invalid request"},400
    user = login()
    if user.type == "member":    
        data = request.get_json()
        new_account = Account(
            user_id = user.user_id,
            branch_id = data['branch_id'],
            status = "active",
            ever_dormant = False,
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
        return {"message": f"congratulation new account with id {new_account.account_id} succesfully created"},201
    return {"message": "invalid request"},400

@app.put('/account/<int:account_id>')
def put_account(account_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :
        data = request.get_json()
        account.branch_id = data.get("branch_id", account.branch_id)
        db.session.commit()
        return {"message": "your account successfully updated"},200
    return {"message": "invalid request"},400

@app.put('/nonactive/<int:account_id>')
def put_nonactive(account_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :
        account.status = "nonactive"
        db.session.commit()
        return {"message": "your account is nonactive"},200
    return {"message": "invalid request"},400

@app.put('/active/<int:account_id>')
def put_active(account_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    account = Account.query.get(account_id)
    if user.type == "admin" and account.branch_id == user.branch_id :
        if account.status == "dormant":
            account.end_date = datetime.today()
        account.status = "active"
        db.session.commit()
        return {"message": f"account {account_id} is active"},200
    return {"message": "invalid request"},400

@app.post('/save/<account_id>')
def post_save(account_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :    
        data = request.get_json()
        days_diff = (datetime.today()-account.last_update).days
        if account.status == "nonactive":
            return {"error" : "your account is nonactive please contact admin to reactivate"},400  
        if account.status == "dormant" or days_diff > 90 :
            account.status = "dormant"
            account.ever_dormant = True
            account.start_date = account.last_update
            account.end_date = None
            db.session.commit()
            return {"error" : "your account is dormant please contact admin to reactivate"},400
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
        return {"message": f"successfully saved {new_activity.credit} now your balance : {new_activity.saldo}"},201
    return {"message": "invalid request"},400

@app.post('/withdraw/<account_id>')
def post_withdraw(account_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    account = Account.query.get(account_id)
    if user.type == "member" and account.user_id == user.user_id :    
        data = request.get_json()
        days_diff = (datetime.today()-account.last_update).days
        if account.status == "nonactive":
            return {"error" : "your account is nonactive please contact admin to reactivate"},400  
        if account.status == "dormant" or days_diff > 90 :
            account.status = "dormant"
            account.ever_dormant = True
            account.start_date = account.last_update
            account.end_date = None
            db.session.commit()
            return {"error" : "your account is dormant please contact admin to reactivate"},400
        if account.saldo - data["debit"] < 50000:
            return {"error" : "your saldo is not enough"},400
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
        return {"message": f"successfully withdrawn {new_activity.debit} now your balance : {new_activity.saldo}"},201
    return {"message": "invalid request"},400

@app.post('/transfer/<account_id>')
def post_transfer(account_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    data = request.get_json()
    sender = Account.query.get(account_id)
    receiver = Account.query.get(data["receiver_id"])
    if user.type == "member" and sender.user_id == user.user_id : 
        days_diff = (datetime.today()-sender.last_update).days
        if sender.status == "nonactive":
            return {"error" : "your account is nonactive please contact admin to reactivate"},400  
        if sender.status == "dormant" or days_diff > 90 :
            sender.status = "dormant"
            sender.ever_dormant = True
            sender.start_date = sender.last_update
            sender.end_date = None
            db.session.commit()
            return {"error" : "your account is dormant please contact admin to reactivate"},400
        if sender.saldo - data["transfer"] < 50000:
            return {"error" : "your saldo is not enough"},400   
        sender.saldo -= data["transfer"]
        sender.last_update = datetime.today()
        db.session.commit()
        if receiver.status == "nonactive":
            return {"error" : "the receiver is nonactive"}
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
        return {"message": f"successfully tranfer {new_send.debit} to {new_send.receiver_id} now your balance : {new_send.saldo}"},201
    return {"message": "invalid request"},400

@app.get('/history/<account_id>')
def get_history(account_id):
    if not login():
        return {"error": "invalid request"},400
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
        return jsonify(results),200
    return {"message": "invalid request"},400

@app.get('/branchreport/<int:branch_id>')
def branch_report(branch_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    if user.type == "admin" and user.branch_id == branch_id :
        data = request.get_json()
        u = User.query.filter_by(branch_id=branch_id, type = "member").all()
        a = Account.query.filter_by(branch_id=branch_id).all()
        b = db.session.query(func.sum(Account.saldo)).filter_by(branch_id=branch_id)[0][0]
        c, d = db.session.query(func.sum(Accountivity.credit), func.sum(Accountivity.debit))\
            .join(Account, Accountivity.account_id == Account.account_id)\
            .filter(Account.branch_id == branch_id, Accountivity.activity_date >= data['start_date'], Accountivity.activity_date <= data['end_date'])[0]
        results = {
                "branch_id" : branch_id,
                "total_user" : len(u),
                "total_account" : len(a),
                "total_balance" : b,
                "total_credit" : c,
                "total_debit" : d,
                "date" : {
                    "start_date": data["start_date"],
                    "end_date": data["end_date"]
                    }
            }
        return jsonify(results),200
    return {"message": "invalid request"},400

@app.get('/dormantreport/<int:branch_id>')
def dormant_report(branch_id):
    if not login():
        return {"error": "invalid request"},400
    user = login()
    if user.type == "admin" and user.branch_id == branch_id:
        list_dormant_false = Account.query.filter_by(branch_id=branch_id, ever_dormant=False).all()
        list_dormant = Account.query.filter_by(branch_id=branch_id, ever_dormant=True).all()

        for acc in list_dormant_false :
            days_diff = (datetime.today()-acc.last_update).days
            if days_diff > 90 :
                acc.status = "dormant"
                acc.ever_dormant = True
                acc.start_date = acc.last_update
                acc.end_date = None
                list_dormant.append(acc)
        db.session.commit()
        results = [
            {
                "account_id" : acc.account_id,
                "user_id" : acc.user_id,
                "last_activity" : acc.last_update,
                "status" : acc.status,
                "dormant_period" : {
                    "start_date" : acc.start_date,
                    "end_date" : acc.end_date
                }
            } for acc in list_dormant]
        db.session.commit()
        return jsonify(results),200
    return {"message": "invalid request"},400

if (__name__) == ("__main__"):
    app.run(debug=True)