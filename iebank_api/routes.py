from flask import Flask, request, abort, session, render_template
from iebank_api import db, app
from iebank_api.models import Account, User, Transaction
from werkzeug.security import generate_password_hash, check_password_hash

app.secret_key = 'your_secret_key'

@app.route('/')
def hello_world():
    # Basic route to check if the server is running
    return 'Hello, World!'

@app.route('/skull', methods=['GET'])
def skull():
    # Route to display database connection details
    text = 'Hi! This is the BACKEND SKULL! 💀 '
    text = text +'<br/>Database URL:' + db.engine.url.database
    if db.engine.url.host:
        text = text +'<br/>Database host:' + db.engine.url.host
    if db.engine.url.port:
        text = text +'<br/>Database port:' + db.engine.url.port
    if db.engine.url.username:
        text = text +'<br/>Database user:' + db.engine.url.username
    if db.engine.url.password:
        text = text +'<br/>Database password:' + db.engine.url.password
    return text

@app.route('/register', methods=['POST'])
def register():
    # Route to register a new user
    data = request.get_json()
    required_fields = ['username', 'email', 'password', 'country', 'state', 'date_of_birth', 'role', 'status']
    if not data or not all(field in data for field in required_fields):
        abort(500)
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        country=data['country'],
        state=data['state'],
        date_of_birth=data['date_of_birth'],
        role=data['role'],
        status=data['status']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return format_user(new_user)

@app.route('/login', methods=['POST'])
def login():
    # Route to log in a user
    data = request.get_json()
    required_fields = ['username', 'password']
    if not data or not all(field in data for field in required_fields):
        abort(500)
    
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        abort(500)
    
    if check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['user_role'] = user.role
        return format_user(user)
    else:
        abort(500)

@app.route('/logout', methods=['POST'])
def logout():
    # Route to log out a user
    session.pop('user_id', None)
    session.pop('user_role', None)
    return {'message': 'Logged out successfully'}

@app.route('/user_portal', methods=['GET'])
def user_portal():
    # Route to display the user portal with accounts and transactions
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        abort(500)

    accounts = Account.query.filter_by(user_id=user_id).all()
    transactions = Transaction.query.join(Account, Transaction.from_account_id == Account.id).filter(Account.user_id == user_id).all()

    return render_template('user_portal.html', user=user, accounts=accounts, transactions=transactions)

@app.route('/admin_portal', methods=['GET'])
def admin_portal():
    # Route to display the admin portal with all users
    if 'user_id' not in session or session['user_role'] != 'admin':
        abort(401)  # Unauthorized

    users = User.query.all()
    return render_template('admin_portal.html', users=users)

@app.route('/accounts', methods=['POST'])
def create_account():
    # Route to create a new account
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    data = request.get_json()
    required_fields = ['name', 'currency', 'country']
    if not data or not all(field in data for field in required_fields):
        abort(500)  # Abort with 500 Internal Server Error if any field is missing

    name = data['name']
    currency = data['currency']
    country = data['country']
    user_id = session['user_id']

    account = Account(name, currency, country, user_id)
    db.session.add(account)
    db.session.commit()
    return format_account(account)

@app.route('/accounts', methods=['GET'])
def get_accounts():
    # Route to get all accounts for the logged-in user
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    user_id = session['user_id']
    accounts = Account.query.filter_by(user_id=user_id).all()
    return {'accounts': [format_account(account) for account in accounts]}

@app.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):
    # Route to get a specific account by ID
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    account = Account.query.get(id)
    if not account or account.user_id != session['user_id']:
        abort(500)
    return format_account(account)

@app.route('/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    # Route to update a specific account by ID
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    account = Account.query.get(id)
    if not account or account.user_id != session['user_id']:
        abort(500)
    account.name = request.json['name']
    db.session.commit()
    return format_account(account)

@app.route('/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    # Route to delete a specific account by ID
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    account = Account.query.get(id)
    if not account or account.user_id != session['user_id']:
        abort(500)
    db.session.delete(account)
    db.session.commit()
    return format_account(account)

@app.route('/transactions', methods=['POST'])
def create_transaction():
    # Route to create a new transaction
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    data = request.get_json()
    required_fields = ['from_account_id', 'to_account_id', 'amount']
    if not data or not all(field in data for field in required_fields):
        abort(500)
    
    from_account_id = data['from_account_id']
    to_account_id = data['to_account_id']
    amount = data['amount']
    
    from_account = Account.query.get(from_account_id)
    to_account = Account.query.get(to_account_id)
    if not from_account or from_account.user_id != session['user_id'] or not to_account:
        abort(500)

    transaction = Transaction(from_account_id=from_account_id, to_account_id=to_account_id, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    
    return format_transaction(transaction)

@app.route('/transactions', methods=['GET'])
def get_transactions():
    # Route to get all transactions for the logged-in user
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    user_id = session['user_id']
    transactions = Transaction.query.join(Account, Transaction.from_account_id == Account.id).filter(Account.user_id == user_id).all()
    return {'transactions': [format_transaction(transaction) for transaction in transactions]}

@app.route('/send_money', methods=['POST'])
def send_money():
    # Route to send money from one account to another
    if 'user_id' not in session:
        abort(401)  # Unauthorized

    data = request.get_json()
    required_fields = ['from_account_id', 'to_account_id', 'amount']
    if not data or not all(field in data for field in required_fields):
        abort(500)

    from_account = Account.query.get(data['from_account_id'])
    to_account = Account.query.get(data['to_account_id'])
    amount = data['amount']

    if not from_account or not to_account or from_account.user_id != session['user_id'] or from_account.balance < amount:
        abort(500)

    from_account.balance -= amount
    to_account.balance += amount

    db.session.commit()

    return {'message': 'Transaction successful'}

@app.route('/admin/users', methods=['POST'])
def create_user():
    # Route for admin to create a new user
    if 'user_id' not in session or session['user_role'] != 'admin':
        abort(401)  # Unauthorized

    data = request.get_json()
    required_fields = ['username', 'email', 'password', 'country', 'state', 'date_of_birth', 'role', 'status']
    if not data or not all(field in data for field in required_fields):
        abort(500)
    
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        country=data['country'],
        state=data['state'],
        date_of_birth=data['date_of_birth'],
        role=data['role'],
        status=data['status']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return format_user(new_user)

@app.route('/admin/users/<int:id>', methods=['PUT'])
def update_user(id):
    # Route for admin to update a user by ID
    if 'user_id' not in session or session['user_role'] != 'admin':
        abort(401)  # Unauthorized

    user = User.query.get(id)
    if not user:
        abort(500)

    user.username = request.json['username']
    user.email = request.json['email']
    user.password = generate_password_hash(request.json['password'], method='sha256')
    user.country = request.json['country']
    user.state = request.json['state']
    user.date_of_birth = request.json['date_of_birth']
    user.role = request.json['role']
    user.status = request.json['status']
    db.session.commit()
    return format_user(user)

@app.route('/admin/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    # Route for admin to delete a user by ID
    if 'user_id' not in session or session['user_role'] != 'admin':
        abort(401)  # Unauthorized

    user = User.query.get(id)
    if not user:
        abort(500)
    db.session.delete(user)
    db.session.commit()
    return format_user(user)

def format_account(account):
    # Helper function to format account data
    return {
        'id': account.id,
        'name': account.name,
        'account_number': account.account_number,
        'balance': account.balance,
        'currency': account.currency,
        'status': account.status,
        'created_at': account.created_at,
        'country': account.country
    }

def format_user(user):
    # Helper function to format user data
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'country': user.country,
        'state': user.state,
        'date_of_birth': user.date_of_birth,
        'role': user.role,
        'status': user.status
    }

def format_transaction(transaction):
    # Helper function to format transaction data
    return {
        'id': transaction.id,
        'amount': transaction.amount,
        'currency': transaction.from_account.currency,
        'status': transaction.status,
        'created_at': transaction.created_at,
        'from_account': transaction.from_account.account_number,
        'to_account': transaction.to_account.account_number
    }
