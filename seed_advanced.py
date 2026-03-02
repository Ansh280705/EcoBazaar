from main import app, db, bcrypt
from main.models import User, Listing, EnergyPriceHistory, CarbonLog, Transaction
import datetime

def seed():
    with app.app_context():
        # Add some historical price data for AI Prediction
        for i in range(10):
            date = datetime.date.today() - datetime.timedelta(days=i)
            hist = EnergyPriceHistory(
                date=date,
                avg_demand=1.0 + (i * 0.05),
                avg_supply=1.0,
                price_per_kwh=10.5 + (i * 0.2)
            )
            db.session.add(hist)

        # Update existing sellers with coordinates for the Map
        sellers = User.query.filter_by(role='seller').all()
        coords = [
            (28.6139, 77.2090), # Delhi
            (19.0760, 72.8777), # Mumbai
            (13.0827, 80.2707), # Chennai
            (12.9716, 77.5946), # Bangalore
        ]
        
        for i, s in enumerate(sellers):
            if i < len(coords):
                s.latitude = coords[i][0]
                s.longitude = coords[i][1]
                s.seller_status = 'approved'
                
                # Ensure they have an active listing for the map
                if not Listing.query.filter_by(seller_id=s.id, status='active').first():
                    listing = Listing(seller_id=s.id, units_listed=100, price_per_unit=12.5)
                    db.session.add(listing)

        # Create an admin if not exists
        if not User.query.filter_by(role='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(email='admin@ecobazaar.com', password=hashed_pw, role='admin')
            db.session.add(admin)
        
        # Add historical Transactions and CarbonLogs for analytics
        buyer = User.query.filter_by(role='buyer').first()
        if buyer and sellers:
            for i in range(7):
                date = datetime.datetime.utcnow() - datetime.timedelta(days=i)
                units = 50 + (i * 10)
                t = Transaction(
                    buyer_id=buyer.id,
                    seller_id=sellers[0].id,
                    units=units,
                    total_price=units * 12.5,
                    created_at=date
                )
                db.session.add(t)
                db.session.flush() # Get ID
                
                log = CarbonLog(
                    user_id=buyer.id,
                    transaction_id=t.id,
                    kwh=units,
                    co2_saved=units * 0.82,
                    created_at=date
                )
                db.session.add(log)

        db.session.commit()
        print("Advanced seed data added successfully!")

if __name__ == "__main__":
    seed()
