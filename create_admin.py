from werkzeug.security import generate_password_hash
from datetime import datetime
from iebank_api.models import User

def create_admin_user():
    with app.app_context():
        # Define the admin user details
        username = 'adminuser'
        email = 'adminuser@example.com'
        password = 'adminpassword123'
        country = 'USA'
        date_of_birth = '2004-06-29'
        role = 'admin'
        status = 'active'

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Convert date_of_birth to a datetime object
        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')

        # Create the new admin user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            country=country,
            date_of_birth=date_of_birth,
            role=role,
            status=status
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        print(f"Admin user '{username}' created successfully.")

if __name__ == '__main__':
    from iebank_api import db, app
    create_admin_user(app, db)