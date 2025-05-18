from app import app, db
from app.models import init_db

if __name__ == "__main__":
    with app.app_context():
        init_db()
        print("SQLite user database initialization complete")
