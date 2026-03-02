import os
from dotenv import load_dotenv
from main import app, db

def initialize_database():
    load_dotenv()
    
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url or "username:password" in db_url:
        print("ERROR: Please update NEON_DATABASE_URL in your .env file with your actual Neon connection string.")
        return

    print("Authenticating with Neon PostgreSQL...")
    
    with app.app_context():
        try:
            print("Creating database tables...")
            # Import models here so SQLAlchemy knows about them
            from main.models import User, Listing, Transaction, EnergyProduction, EnergyPriceHistory, CarbonLog, UserRewards
            db.create_all()
            print("Database schemas created successfully!")
            print("You can now run 'python main.py' to start your upgraded SaaS platform.")
        except Exception as e:
            print("Database initialization failed. Please verify your connection string inside .env!")
            print("Error Details:", str(e))

if __name__ == "__main__":
    initialize_database()
