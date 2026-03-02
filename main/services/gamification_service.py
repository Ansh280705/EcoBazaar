from main.models import UserRewards
from main import db
import datetime

class GamificationService:
    @staticmethod
    def add_points(user_id, points, badge_name=None):
        rewards = UserRewards.query.filter_by(user_id=user_id).first()
        if not rewards:
            rewards = UserRewards(user_id=user_id, points=0, badges=[])
            db.session.add(rewards)
        
        rewards.points += points
        if badge_name and badge_name not in rewards.badges:
            new_badges = list(rewards.badges)
            new_badges.append(badge_name)
            rewards.badges = new_badges
            
        rewards.last_updated = datetime.datetime.utcnow()
        db.session.commit()
        return rewards

    @staticmethod
    def process_transaction_rewards(transaction):
        # 10 points per renewable transaction
        points = 10
        # Bonus for bulk (e.g. > 50 units)
        if transaction.units > 50:
            points += 20
            
        GamificationService.add_points(transaction.buyer_id, points)
        
        # Check for badges
        total_points = UserRewards.query.filter_by(user_id=transaction.buyer_id).first().points
        if total_points >= 100:
            GamificationService.add_points(transaction.buyer_id, 0, "Solar Champion")
        if total_points >= 500:
            GamificationService.add_points(transaction.buyer_id, 0, "Green Warrior")

    @staticmethod
    def get_leaderboard():
        return UserRewards.query.order_by(UserRewards.points.desc()).limit(10).all()
