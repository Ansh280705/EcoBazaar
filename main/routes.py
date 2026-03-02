"""
Routes for Eco Bazzar using Clerk Authentication, RBAC, and Neon PostgreSQL.
"""

import datetime
import os
from flask import flash, redirect, render_template, url_for, request, g, jsonify
from sqlalchemy import or_

from flask_login import login_user, current_user, logout_user
from main import app, db, bcrypt
from main.forms import PurchaseForm, SellOrderForm, GenerateEnergyForm, LoginForm, RegistrationForm
from main.models import Listing, Transaction, User, EnergyProduction, CarbonLog, UserRewards, EnergyPriceHistory
from main.auth import require_auth, require_role
from main.services.carbon_service import CarbonService
from main.services.gamification_service import GamificationService
from main.services.ledger_service import LedgerService
from main.services.prediction_service import PredictionService
from main.services.pricing_service import PricingService

@app.context_processor
def inject_globals():
    return dict(
        current_user=current_user
    )

@app.route('/')
@app.route('/about')
def about():
    """Render the about page."""
    return render_template("about.html")

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    """Render the sign-in page."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
            
    return render_template("sign_in.html", form=form)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """Render the sign-up page."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_pw, role=None)
        db.session.add(user)
        db.session.commit()
        # Automatically log them in
        login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('role_selection'))
        
    return render_template("sign_up.html", form=form)

@app.route('/login')
def login():
    return redirect(url_for('sign_in'))

@app.route('/logout')
def logout():
    """Terminate the local Flask-Login session"""
    logout_user()
    return redirect(url_for('about'))

@app.route('/home')
@require_auth
def home():
    """Intelligent redirect based on role."""
    role = current_user.role
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'buyer':
        return redirect(url_for('buyer_dashboard'))
    elif role == 'seller':
        return redirect(url_for('seller_dashboard'))
    return redirect(url_for('role_selection'))


@app.route('/role-selection', methods=['GET', 'POST'])
@require_auth
def role_selection():
    """First-time login role selection."""
    if current_user.role is not None:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        selected_role = request.form.get('role')
        if selected_role in ['buyer', 'seller']:
            user = User.query.get(current_user.id)
            user.role = selected_role
            if selected_role == 'seller':
                user.seller_status = 'pending'
            db.session.commit()
            flash(f"Successfully joined as {selected_role.capitalize()}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid role selected.", "error")
            
    return render_template("role_selection.html")


# ==========================================
# ADMIN ROUTES
# ==========================================

@app.route('/admin-dashboard')
@require_auth
@require_role(['admin'])
def admin_dashboard():
    users = User.query.all()
    pending_sellers = User.query.filter_by(role='seller', seller_status='pending').all()
    
    total_users = User.query.count()
    total_buyers = User.query.filter_by(role='buyer').count()
    total_sellers = User.query.filter_by(role='seller').count()
    total_units_gen = db.session.query(db.func.sum(EnergyProduction.units_generated)).scalar() or 0
    total_transactions = Transaction.query.count()
    
    stats = {
        'total_users': total_users,
        'total_buyers': total_buyers,
        'total_sellers': total_sellers,
        'pending_sellers': len(pending_sellers),
        'total_units_generated': total_units_gen,
        'total_transactions': total_transactions
    }
    
    return render_template("admin_dashboard.html", stats=stats, pending_sellers=pending_sellers, users=users)

@app.route('/admin/approve-seller/<user_id>', methods=['POST'])
@require_auth
@require_role(['admin'])
def approve_seller(user_id):
    user = User.query.get(user_id)
    if user and user.role == 'seller':
        user.seller_status = 'approved'
        db.session.commit()
        flash(f"Approved seller {user.email}.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject-seller/<user_id>', methods=['POST'])
@require_auth
@require_role(['admin'])
def reject_seller(user_id):
    user = User.query.get(user_id)
    if user and user.role == 'seller':
        user.seller_status = 'rejected'
        db.session.commit()
        flash(f"Rejected seller {user.email}.", "error")
    return redirect(url_for('admin_dashboard'))


# ==========================================
# BUYER ROUTES
# ==========================================

@app.route('/buyer-dashboard')
@require_auth
@require_role(['buyer'])
def buyer_dashboard():
    # Show active listings in the marketplace summary
    # Purchase history
    purchases = Transaction.query.filter_by(buyer_id=current_user.id).order_by(Transaction.created_at.desc()).limit(10).all()
    total_spent = sum(t.total_price for t in purchases)
    
    carbon_stats = CarbonService.get_user_stats(current_user.id)
    rewards = UserRewards.query.filter_by(user_id=current_user.id).first()
    
    return render_template("buyer_dashboard.html", purchases=purchases, total_spent=total_spent, carbon_stats=carbon_stats, rewards=rewards)

@app.route('/energy-map')
@require_auth
@require_role(['buyer', 'admin'])
def energy_map():
    return render_template("energy_map.html")

@app.route('/leaderboard')
@require_auth
def leaderboard():
    return render_template("leaderboard.html")

@app.route('/marketplace')
@require_auth
@require_role(['buyer', 'admin'])
def marketplace():
    """View active listings"""
    # Active listings from sellers who have units available
    listings = Listing.query.filter_by(status='active').all()
    
    return render_template("marketplace.html", listings=listings)

@app.route('/checkout_page', methods=["GET", "POST"])
@require_auth
@require_role(['buyer'])
def checkout_page():
    listing_id = request.args.get("order_id") # maintaining backwards compat arg name
    if not listing_id:
        return redirect(url_for("marketplace"))

    listing = Listing.query.filter_by(id=listing_id).first()
    if not listing:
        flash("Listing not found.", "error")
        return redirect(url_for("marketplace"))

    seller = listing.seller
    form = PurchaseForm()

    if form.validate_on_submit():
        if form.units.data <= listing.units_listed:
            total_price = listing.price_per_unit * form.units.data
            buyer = User.query.get(current_user.id)
            units = form.units.data

            if buyer.available_units + units <= buyer.battery_capacity:
                buyer.available_units += units
                listing.units_listed -= units
                # Seller units already subtracted during listing creation
                
                t = Transaction(
                    buyer_id=buyer.id, seller_id=seller.id,
                    units=units, total_price=total_price, status='completed'
                )
                db.session.add(t)
                if listing.units_listed <= 0:
                    listing.status = 'sold'
                db.session.commit()

                # ADVANCED HACKATHON FEATURES INTEGRATION
                try:
                    # 1. Blockchain Ledger
                    LedgerService.seal_transaction(t)
                    # 2. Carbon Footprint
                    CarbonService.log_transaction(t)
                    # 3. Gamification
                    GamificationService.process_transaction_rewards(t)
                except Exception as e:
                    print(f"Error in background features: {e}")

                flash(f"Successfully purchased {units} units for {total_price}.", "success")
                return redirect(url_for('buyer_dashboard'))
            else:
                flash(f"Purchase failed. Your battery capacity is max {buyer.battery_capacity}.", "error")
        else:
            flash(f'Cannot purchase more than {listing.units_listed} units.', 'error')

    return render_template("checkout_page.html", order=listing, seller=seller, form=form)


# ==========================================
# SELLER ROUTES
# ==========================================

@app.route('/seller-dashboard')
@require_auth
@require_role(['seller'])
def seller_dashboard():
    if current_user.seller_status != 'approved':
        return render_template("seller_pending.html")
        
    productions = EnergyProduction.query.filter_by(user_id=current_user.id).order_by(EnergyProduction.timestamp.desc()).limit(10).all()
    total_generated = sum(p.units_generated for p in productions)
    
    active_listings = Listing.query.filter_by(seller_id=current_user.id, status='active').all()
    listed_units = sum(l.units_listed for l in active_listings)
    
    sales = Transaction.query.filter_by(seller_id=current_user.id).all()
    total_earnings = sum(t.total_price for t in sales)
    
    return render_template("seller_dashboard.html", 
        productions=productions, 
        total_generated=total_generated,
        active_listings=active_listings,
        listed_units=listed_units,
        total_earnings=total_earnings,
        sales=sales[:5]
    )


@app.route("/generate_energy", methods=["GET", "POST"])
@require_auth
@require_role(['seller'])
def generate_energy():
    form = GenerateEnergyForm()
    if form.validate_on_submit():
        generated = form.kwh.data
        user = User.query.get(current_user.id)
        if user.available_units + generated > user.battery_capacity:
            flash(f"Generation failed! Battery full.", "error")
        else:
            user.available_units += generated
            prod = EnergyProduction(user_id=user.id, units_generated=generated)
            db.session.add(prod)
            db.session.commit()
            flash(f"Generated {generated} Units!", "success")
            return redirect(url_for('seller_dashboard'))
            
    return render_template("generate_energy.html", form=form)


@app.route("/seller_page", methods=['GET', 'POST']) # the listing page
@require_auth
@require_role(['seller'])
def seller_page():
    form = SellOrderForm()
    if form.validate_on_submit():
        units, price = form.unit.data, form.price.data
        user = User.query.get(current_user.id)
        if user.available_units >= units:
            user.available_units -= units # Lock instantly
            listing = Listing(seller_id=user.id, units_listed=units, price_per_unit=price)
            db.session.add(listing)
            db.session.commit()
            flash('Listed units successfully.', 'success')
            return redirect(url_for('seller_dashboard'))
        else:
            flash('Not enough available units!', 'error')

    active_listings = Listing.query.filter_by(seller_id=current_user.id, status='active').all()
    return render_template("seller_page.html", sell_orders=active_listings, form=form)


@app.route("/cancel_sell_order", methods=["GET", "POST"])
@require_auth
@require_role(['seller'])
def cancel_sell_order():
    order_id = request.args.get("order_id")
    if order_id:
        listing = Listing.query.filter_by(id=order_id, seller_id=current_user.id).first()
        if listing and listing.status == 'active':
            user = User.query.get(current_user.id)
            user.available_units += listing.units_listed  # Refund
            listing.status = 'cancelled'
            db.session.commit()
            flash("Listing cancelled. Units refunded.", "success")
    return redirect(url_for('seller_dashboard'))


# ==========================================
# SHARED/UNIVERSAL
# ==========================================

@app.route('/transactions')
@require_auth
@require_role(['buyer', 'seller', 'admin'])
def transactions():
    user_id = current_user.id
    if current_user.role == 'admin':
        history = Transaction.query.order_by(Transaction.created_at.desc()).all()
    else:
        history = Transaction.query.filter(or_(
            Transaction.buyer_id == user_id,
            Transaction.seller_id == user_id
        )).order_by(Transaction.created_at.desc()).all()
        
    return render_template("transaction.html", history=history)


# ==========================================
# ADVANCED API ENDPOINTS
# ==========================================

@app.route('/api/prediction')
@require_auth
def get_prediction():
    data = PredictionService.predict_next_day_price()
    
    # Handle the case where predict_next_day_price returns a tuple (fallback mechanism from old code if not updated everywhere)
    if isinstance(data, tuple):
        return {
            "predictedPrice": data[0],
            "changePercent": data[1],
            "trend": data[2],
            "realDemand": 0,
            "realSupply": 0
        }
        
    return {
        "predictedPrice": data["predicted_price"],
        "changePercent": data["change_pct"],
        "trend": data["trend"],
        "realDemand": data["real_demand"],
        "realSupply": data["real_supply"]
    }

@app.route('/api/map-data')
@require_auth
def get_map_data():
    sellers = User.query.filter_by(role='seller', seller_status='approved').all()
    map_items = []
    for s in sellers:
        if s.latitude and s.longitude:
            active_listing = Listing.query.filter_by(seller_id=s.id, status='active').first()
            if active_listing:
                energy = active_listing.units_listed
                price = active_listing.price_per_unit
            else:
                energy = 0
                price = 'N/A'
                
            map_items.append({
                "id": s.id,
                "lat": s.latitude,
                "lng": s.longitude,
                "energy": energy,
                "price": price,
                "type": s.energy_type or 'General'
            })
    return {"sellers": map_items}

@app.route('/api/seller/update-location', methods=['POST'])
@require_auth
@require_role(['seller'])
def update_seller_location():
    data = request.json
    lat = data.get('lat')
    lng = data.get('lng')
    
    if lat and lng:
        current_user.latitude = lat
        current_user.longitude = lng
        db.session.commit()
        return jsonify({"status": "success", "message": "Location updated"}), 200
    
    return jsonify({"status": "error", "message": "Invalid coordinates"}), 400

@app.route('/api/leaderboard')
@require_auth
def get_leaderboard():
    board = GamificationService.get_leaderboard()
    return {
        "leaderboard": [
            {"email": b.user.email, "points": b.points, "badges": b.badges} 
            for b in board
        ]
    }

@app.route('/api/admin/analytics')
@require_auth
@require_role(['admin'])
def admin_analytics():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get range for last 7 days
    end_date = datetime.utcnow()
    start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Energy Trading Trends (kWh per day)
    trading_data = db.session.query(
        func.cast(Transaction.created_at, db.Date).label('date'),
        func.sum(Transaction.units).label('total_units')
    ).filter(Transaction.created_at >= start_date)\
     .group_by(func.cast(Transaction.created_at, db.Date))\
     .all()
    
    # Carbon Offset Impact (kg per day)
    carbon_data = db.session.query(
        func.cast(CarbonLog.created_at, db.Date).label('date'),
        func.sum(CarbonLog.co2_saved).label('total_co2')
    ).filter(CarbonLog.created_at >= start_date)\
     .group_by(func.cast(CarbonLog.created_at, db.Date))\
     .all()

    # Map results to dates to handle missing days
    day_map_energy = {str(d.date): d.total_units for d in trading_data}
    day_map_carbon = {str(d.date): d.total_co2 for d in carbon_data}
    
    labels = []
    energy_points = []
    carbon_points = []
    
    for i in range(7):
        current_date = (start_date + timedelta(days=i)).date()
        labels.append(current_date.strftime('%a'))
        energy_points.append(float(day_map_energy.get(str(current_date), 0)))
        carbon_points.append(float(day_map_carbon.get(str(current_date), 0)))
        
    return {
        "labels": labels,
        "energyData": energy_points,
        "carbonData": carbon_points
    }

