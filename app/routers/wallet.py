from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import logging

from app.database import get_db
from app.models.wallet import UserWallet, WalletTransaction
from app.models.user import User
from app.models.admin import AdminUser
from app.schemas.wallet import (
    WalletResponse, WalletTransactionResponse, WithdrawalRequest, 
    WithdrawalResponse, RewardDistribution, WalletBalance, 
    TransactionType, TransactionStatus
)
from app.routers.auth import get_current_admin
# Pi Network integration handled by separate JS backend

router = APIRouter()

@router.get("/{user_id}/balance", response_model=WalletBalance)
async def get_wallet_balance(user_id: str, db: Session = Depends(get_db)):
    """Get user's wallet balance and transaction summary"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create wallet
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if not wallet:
        # Create wallet for new user
        wallet = UserWallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    # Calculate pending withdrawals
    pending_withdrawals = db.query(func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.user_id == user_id,
        WalletTransaction.transaction_type == TransactionType.WITHDRAWAL,
        WalletTransaction.status == TransactionStatus.PENDING
    ).scalar() or 0.0
    
    return WalletBalance(
        user_id=user_id,
        balance=wallet.balance,
        total_earned=wallet.total_earned,
        total_withdrawn=wallet.total_withdrawn,
        pending_withdrawals=pending_withdrawals
    )

@router.get("/{user_id}/transactions", response_model=List[WalletTransactionResponse])
async def get_wallet_transactions(
    user_id: str, 
    limit: int = 50, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get user's wallet transaction history"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get transactions
    transactions = db.query(WalletTransaction).filter(
        WalletTransaction.user_id == user_id
    ).order_by(WalletTransaction.created_at.desc()).offset(offset).limit(limit).all()
    
    return transactions

@router.post("/{user_id}/withdraw", response_model=WithdrawalResponse)
async def withdraw_funds(
    user_id: str,
    withdrawal: WithdrawalRequest,
    db: Session = Depends(get_db)
):
    """Request withdrawal - Pi backend will handle actual payment processing"""
    # Input validation
    if withdrawal.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")
    
    if withdrawal.amount < 0.01:
        raise HTTPException(status_code=400, detail="Minimum withdrawal amount is 0.01")
    
    if withdrawal.pi_user_id != user_id:
        raise HTTPException(status_code=400, detail="Pi user ID must match authenticated user")
    
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create wallet
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Check sufficient balance
    if wallet.balance < withdrawal.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    try:
        # Create withdrawal transaction (Pi backend will process)
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=withdrawal.amount,
            balance_before=wallet.balance,
            balance_after=wallet.balance - withdrawal.amount,
            status=TransactionStatus.PENDING,
            description=f"Withdrawal request to Pi Network",
            transaction_metadata={
                "pi_user_id": withdrawal.pi_user_id,
                "requested_at": datetime.now().isoformat(),
                "processed_by": "pi_backend"
            }
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Update wallet balance (will be confirmed by Pi backend webhook)
        wallet.balance -= withdrawal.amount
        wallet.total_withdrawn += withdrawal.amount
        db.commit()
        
        return WithdrawalResponse(
            transaction_id=transaction.transaction_id,
            amount=withdrawal.amount,
            status=TransactionStatus.PENDING,
            pi_transaction_id=None,  # Will be set by Pi backend
            message="Withdrawal request sent to Pi backend for processing"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Withdrawal request failed: {str(e)}")

@router.post("/distribute-quest-rewards")
async def distribute_quest_rewards(
    quest_id: str,
    rewards: List[RewardDistribution],
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Distribute quest rewards to user wallets (called when quest ends)"""
    try:
        total_distributed = 0.0
        
        for reward in rewards:
            # Get or create user wallet
            wallet = db.query(UserWallet).filter(UserWallet.user_id == reward.user_id).first()
            if not wallet:
                wallet = UserWallet(user_id=reward.user_id, balance=0.0)
                db.add(wallet)
                db.commit()
                db.refresh(wallet)
            
            # Create reward transaction
            transaction = WalletTransaction(
                wallet_id=wallet.wallet_id,
                user_id=reward.user_id,
                transaction_type=TransactionType.REWARD,
                amount=reward.amount,
                balance_before=wallet.balance,
                balance_after=wallet.balance + reward.amount,
                status=TransactionStatus.COMPLETED,
                quest_id=reward.quest_id,
                description=reward.description,
                transaction_metadata={
                    "quest_id": reward.quest_id,
                    "percentage": reward.percentage,
                    "distributed_at": datetime.now().isoformat(),
                    "source": "quest_completion"
                },
                processed_at=datetime.now()
            )
            
            db.add(transaction)
            
            # Update wallet balance
            wallet.balance += reward.amount
            wallet.total_earned += reward.amount
            total_distributed += reward.amount
        
        db.commit()
        
        return {
            "message": "Quest rewards distributed successfully",
            "quest_id": quest_id,
            "total_users": len(rewards),
            "total_amount": total_distributed,
            "distribution_details": [
                {
                    "user_id": r.user_id,
                    "amount": r.amount,
                    "percentage": r.percentage
                } for r in rewards
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Quest reward distribution failed: {str(e)}")

@router.get("/{user_id}/pending-withdrawals")
async def get_pending_withdrawals(user_id: str, db: Session = Depends(get_db)):
    """Get user's pending withdrawal transactions"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get pending withdrawals
    pending = db.query(WalletTransaction).filter(
        WalletTransaction.user_id == user_id,
        WalletTransaction.transaction_type == TransactionType.WITHDRAWAL,
        WalletTransaction.status == TransactionStatus.PENDING
    ).order_by(WalletTransaction.created_at.desc()).all()
    
    return {
        "user_id": user_id,
        "pending_withdrawals": len(pending),
        "total_pending_amount": sum(t.amount for t in pending),
        "transactions": pending
    }

@router.post("/pi-webhook")
async def pi_backend_webhook(
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """Receive transaction updates from Pi backend"""
    try:
        transaction_id = webhook_data.get("transaction_id")
        pi_transaction_id = webhook_data.get("pi_transaction_id")
        status = webhook_data.get("status")
        amount = webhook_data.get("amount")
        user_id = webhook_data.get("user_id")
        
        if not transaction_id:
            raise HTTPException(status_code=400, detail="Missing transaction_id")
        
        # Find the transaction
        transaction = db.query(WalletTransaction).filter(
            WalletTransaction.transaction_id == transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Update transaction with Pi backend data
        if pi_transaction_id:
            transaction.pi_transaction_id = pi_transaction_id
        
        # Update transaction status
        if status == "completed":
            transaction.status = TransactionStatus.COMPLETED
            transaction.processed_at = datetime.now()
        elif status == "cancelled":
            transaction.status = TransactionStatus.CANCELLED
            # Revert wallet balance
            wallet = db.query(UserWallet).filter(UserWallet.wallet_id == transaction.wallet_id).first()
            if wallet:
                wallet.balance += transaction.amount
                wallet.total_withdrawn -= transaction.amount
        elif status == "failed":
            transaction.status = TransactionStatus.FAILED
            # Revert wallet balance
            wallet = db.query(UserWallet).filter(UserWallet.wallet_id == transaction.wallet_id).first()
            if wallet:
                wallet.balance += transaction.amount
                wallet.total_withdrawn -= transaction.amount
        
        # Update transaction_metadata with Pi backend response
        transaction.transaction_metadata.update({
            "pi_backend_status": status,
            "pi_transaction_id": pi_transaction_id,
            "updated_at": datetime.now().isoformat(),
            "pi_backend_data": webhook_data
        })
        
        db.commit()
        
        return {"status": "success", "message": "Transaction updated from Pi backend"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Pi backend webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.post("/pi-payment-confirmation")
async def pi_payment_confirmation(
    payment_data: dict,
    db: Session = Depends(get_db)
):
    """Receive payment confirmations from Pi backend"""
    try:
        user_id = payment_data.get("user_id")
        amount = payment_data.get("amount")
        pi_transaction_id = payment_data.get("pi_transaction_id")
        status = payment_data.get("status")
        
        if not user_id or not amount:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get or create user wallet
        wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
        if not wallet:
            wallet = UserWallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.wallet_id,
            user_id=user_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            balance_before=wallet.balance,
            balance_after=wallet.balance + amount,
            status=TransactionStatus.COMPLETED if status == "completed" else TransactionStatus.PENDING,
            pi_transaction_id=pi_transaction_id,
            description="Pi Network payment deposit",
            transaction_metadata={
                "pi_payment_data": payment_data,
                "processed_by": "pi_backend",
                "received_at": datetime.now().isoformat()
            },
            processed_at=datetime.now() if status == "completed" else None
        )
        
        db.add(transaction)
        
        # Update wallet balance
        if status == "completed":
            wallet.balance += amount
            wallet.total_earned += amount
        
        db.commit()
        
        return {"status": "success", "message": "Payment recorded"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Pi payment confirmation error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment confirmation failed: {str(e)}")
