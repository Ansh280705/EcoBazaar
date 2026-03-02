from main.models import CarbonLog, Transaction
from main import db

class CarbonService:
    CO2_SAVED_PER_KWH = 0.82 # kg
    TREE_ABSORPTION_YEAR = 21.0 # kg/year

    @staticmethod
    def log_transaction(transaction):
        """Calculate and log CO2 saved for a transaction."""
        co2_saved = transaction.units * CarbonService.CO2_SAVED_PER_KWH
        
        log = CarbonLog(
            user_id=transaction.buyer_id,
            transaction_id=transaction.id,
            kwh=transaction.units,
            co2_saved=co2_saved
        )
        db.session.add(log)
        db.session.commit()
        return co2_saved

    @staticmethod
    def get_user_stats(user_id):
        logs = CarbonLog.query.filter_by(user_id=user_id).all()
        total_co2 = sum(log.co2_saved for log in logs)
        total_kwh = sum(log.kwh for log in logs)
        trees_eq = total_co2 / CarbonService.TREE_ABSORPTION_YEAR
        
        return {
            'total_co2_saved': round(total_co2, 2),
            'total_kwh_traded': total_kwh,
            'trees_equivalent': round(trees_eq, 2),
            'sustainability_score': min(100, int(total_co2 / 10)) # Simple score
        }
    
    @staticmethod
    def get_global_stats():
        logs = CarbonLog.query.all()
        total_co2 = sum(log.co2_saved for log in logs)
        return round(total_co2, 2)
