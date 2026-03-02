from main.models import Listing
from flask import current_app

class PricingService:
    @staticmethod
    def calculate_price(base_price, demand_factor, supply_factor, is_peak_hour):
        """
        Price = BasePrice × DemandFactor × SupplyFactor × PeakHourMultiplier
        """
        peak_multiplier = 1.15 if is_peak_hour else 1.0
        
        # Simple dynamic pricing logic
        # High demand (>1.0) increases price
        # High supply (>1.0) decreases price (inverse)
        
        calculated_price = base_price * demand_factor * (1.0 / supply_factor) * peak_multiplier
        
        # Cap price fluctuation ±30%
        min_price = base_price * 0.7
        max_price = base_price * 1.3
        
        return max(min_price, min(max_price, calculated_price))

    @staticmethod
    def get_market_factors():
        # In a real app, these would come from real-time analytics
        # For now, we simulate based on active listings
        active_listings_count = Listing.query.filter_by(status='active').count()
        
        # Example logic: 
        # Low supply (listings < 5) -> higher demand factor
        supply_factor = max(0.5, active_listings_count / 10.0)
        demand_factor = 1.2 if active_listings_count < 5 else 1.0
        
        return demand_factor, supply_factor
