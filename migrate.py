from main import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Force create all tables (missing ones)
        from main.models import User, Listing, Transaction, EnergyProduction, EnergyPriceHistory, CarbonLog, UserRewards
        db.create_all()
        
        # Manually add missing columns if tables exist
        engine = db.engine
        with engine.connect() as conn:
            # Users table
            columns = [
                ("latitude", "DOUBLE PRECISION"),
                ("longitude", "DOUBLE PRECISION"),
                ("energy_type", "VARCHAR(50)")
            ]
            for col, type_ in columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {type_}"))
                    print(f"Added column {col} to users")
                except Exception:
                    pass # Column likely exists
            
            # Transactions table
            columns = [
                ("transaction_hash", "VARCHAR(64)"),
                ("previous_hash", "VARCHAR(64)")
            ]
            for col, type_ in columns:
                try:
                    conn.execute(text(f"ALTER TABLE transactions ADD COLUMN {col} {type_}"))
                    print(f"Added column {col} to transactions")
                except Exception:
                    pass
            
            conn.commit()
    print("Migration check complete.")

if __name__ == "__main__":
    migrate()
