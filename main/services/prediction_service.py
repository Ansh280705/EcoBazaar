import datetime
import random
from main.models import EnergyPriceHistory

class PredictionService:
    @staticmethod
    def predict_next_day_price():
        """
        Predict next-day energy price based on historical data.
        Uses a weighted average approach combined with real, actual marketplace supply and demand.
        """
        from main.models import EnergyPriceHistory, Transaction, Listing
        from sqlalchemy import func
        from main import db
        import datetime
        
        history = EnergyPriceHistory.query.order_by(EnergyPriceHistory.date.desc()).limit(7).all()
        
        if not history:
            return 12.5, 0.0, "stable" # Fallback average price
        
        prices = [h.price_per_kwh for h in history]
        avg_price = sum(prices) / len(prices)
        
        # Base ML prediction factor: Recent prices weighted higher
        weighted_avg = sum(p * (i + 1) for i, p in enumerate(reversed(prices))) / sum(range(1, len(prices) + 1))
        
        # --- REAL DATA METRICS ---
        three_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        six_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=6)
        
        # 1. Real Demand (Units bought recently vs past)
        recent_demand = db.session.query(func.sum(Transaction.units)).filter(Transaction.created_at >= three_days_ago).scalar() or 0
        past_demand = db.session.query(func.sum(Transaction.units)).filter(Transaction.created_at >= six_days_ago, Transaction.created_at < three_days_ago).scalar() or 0
        
        demand_growth = 1.0
        if past_demand > 0:
            demand_growth = recent_demand / past_demand
            
        # 2. Real Supply (Total units currently active in marketplace)
        current_supply = db.session.query(func.sum(Listing.units_listed)).filter(Listing.status == 'active').scalar() or 0
        
        supply_factor = 1.0
        if current_supply > 0 and recent_demand > 0:
            daily_demand = recent_demand / 3.0
            days_of_supply = current_supply / daily_demand
            if days_of_supply < 1.0:
                supply_factor = 1.15 # Scarcity -> higher price
            elif days_of_supply > 5.0:
                supply_factor = 0.85 # Oversupply -> lower price
        elif current_supply == 0 and recent_demand > 0:
            supply_factor = 1.25 # Complete scarcity
            
        # Cap demand influence
        demand_multiplier = max(0.85, min(1.25, demand_growth))
        
        # Calculate real predicted price
        predicted_price = weighted_avg * demand_multiplier * supply_factor
        
        # Cap absolute increase at 25% to prevent wild swings
        if predicted_price > avg_price * 1.25:
            predicted_price = avg_price * 1.25
        if predicted_price < avg_price * 0.7:
            predicted_price = avg_price * 0.7 # Minimum floor
            
        change_pct = ((predicted_price - avg_price) / avg_price) * 100
        trend = "up" if change_pct > 0.5 else "down" if change_pct < -0.5 else "stable"
        
        return {
            "predicted_price": round(predicted_price, 2),
            "change_pct": round(change_pct, 1),
            "trend": trend,
            "real_demand": float(recent_demand),
            "real_supply": float(current_supply)
        }

    @staticmethod
    def log_daily_price(avg_demand, avg_supply, weather_score, price):
        from main import db
        entry = EnergyPriceHistory(
            avg_demand=avg_demand,
            avg_supply=avg_supply,
            weather_score=weather_score,
            price_per_kwh=price
        )
        db.session.add(entry)
        db.session.commit()
