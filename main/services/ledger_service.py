import hashlib
import json
from main.models import Transaction
from main import db

class LedgerService:
    @staticmethod
    def generate_hash(transaction_data):
        payload = json.dumps(transaction_data, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def seal_transaction(transaction):
        """Creates the SHA-256 hash and links to the previous transaction."""
        prev_tx = Transaction.query.filter(Transaction.id != transaction.id).order_by(Transaction.created_at.desc()).first()
        prev_hash = prev_tx.transaction_hash if prev_tx else "0" * 64
        
        tx_data = {
            "id": transaction.id,
            "buyer_id": transaction.buyer_id,
            "seller_id": transaction.seller_id,
            "units": transaction.units,
            "total_price": transaction.total_price,
            "timestamp": transaction.created_at.isoformat(),
            "prev_hash": prev_hash
        }
        
        transaction.previous_hash = prev_hash
        transaction.transaction_hash = LedgerService.generate_hash(tx_data)
        db.session.commit()

    @staticmethod
    def verify_chain():
        """Validate the immutability of the ledger."""
        transactions = Transaction.query.order_by(Transaction.created_at.asc()).all()
        for i in range(1, len(transactions)):
            if transactions[i].previous_hash != transactions[i-1].transaction_hash:
                return False, transactions[i].id # Tampering detected
        return True, None
