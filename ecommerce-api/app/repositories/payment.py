
"""
Repository pour Payment
Gestion de l'accès aux données des paiements
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository pour gérer les paiements"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)
    
    async def get_by_order_id(self, order_id: int) -> List[Payment]:
        """
        Récupère tous les paiements d'une commande
        
        Args:
            order_id: ID de la commande
        
        Returns:
            Liste de paiements
        """
        query = (
            select(Payment)
            .where(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_transaction_reference(
        self,
        transaction_reference: str
    ) -> Optional[Payment]:
        """
        Récupère un paiement par sa référence de transaction
        
        Args:
            transaction_reference: Référence de transaction (ex: Stripe payment_intent_id)
        
        Returns:
            Paiement ou None
        """
        query = select(Payment).where(
            Payment.transaction_reference == transaction_reference
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_status(
        self,
        status: PaymentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Récupère les paiements par statut
        
        Args:
            status: Statut recherché
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de paiements
        """
        query = (
            select(Payment)
            .where(Payment.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Payment.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_method(
        self,
        method: PaymentMethod,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Récupère les paiements par méthode
        
        Args:
            method: Méthode de paiement
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de paiements
        """
        query = (
            select(Payment)
            .where(Payment.method == method)
            .offset(skip)
            .limit(limit)
            .order_by(Payment.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_successful_payments(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Récupère les paiements réussis
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de paiements réussis
        """
        return await self.get_by_status(PaymentStatus.SUCCESS, skip, limit)
    
    async def get_pending_payments(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Récupère les paiements en attente
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de paiements en attente
        """
        return await self.get_by_status(PaymentStatus.PENDING, skip, limit)
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Récupère les paiements dans une période
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de paiements
        """
        query = (
            select(Payment)
            .where(
                and_(
                    Payment.created_at >= start_date,
                    Payment.created_at <= end_date
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Payment.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_status(
        self,
        payment_id: int,
        status: PaymentStatus,
        paid_at: Optional[datetime] = None
    ) -> Optional[Payment]:
        """
        Met à jour le statut d'un paiement
        
        Args:
            payment_id: ID du paiement
            status: Nouveau statut
            paid_at: Date de paiement (optionnel)
        
        Returns:
            Paiement mis à jour
        """
        update_data = {"status": status}
        
        if paid_at:
            update_data["paid_at"] = paid_at
        elif status == PaymentStatus.SUCCESS and not paid_at:
            update_data["paid_at"] = datetime.utcnow()
        
        return await self.update(payment_id, update_data)
    
    async def mark_as_success(
        self,
        payment_id: int,
        transaction_reference: Optional[str] = None
    ) -> Optional[Payment]:
        """
        Marque un paiement comme réussi
        
        Args:
            payment_id: ID du paiement
            transaction_reference: Référence de transaction (optionnel)
        
        Returns:
            Paiement mis à jour
        """
        update_data = {
            "status": PaymentStatus.SUCCESS,
            "paid_at": datetime.utcnow()
        }
        
        if transaction_reference:
            update_data["transaction_reference"] = transaction_reference
        
        return await self.update(payment_id, update_data)
    
    async def mark_as_failed(self, payment_id: int) -> Optional[Payment]:
        """
        Marque un paiement comme échoué
        
        Args:
            payment_id: ID du paiement
        
        Returns:
            Paiement mis à jour
        """
        return await self.update_status(payment_id, PaymentStatus.FAILED)
    
    async def mark_as_refunded(self, payment_id: int) -> Optional[Payment]:
        """
        Marque un paiement comme remboursé
        
        Args:
            payment_id: ID du paiement
        
        Returns:
            Paiement mis à jour
        """
        return await self.update_status(payment_id, PaymentStatus.REFUNDED)
    
    async def count_by_status(self, status: PaymentStatus) -> int:
        """
        Compte les paiements par statut
        
        Args:
            status: Statut à compter
        
        Returns:
            Nombre de paiements
        """
        return await self.count(status=status)
    
    async def count_by_method(self, method: PaymentMethod) -> int:
        """
        Compte les paiements par méthode
        
        Args:
            method: Méthode de paiement
        
        Returns:
            Nombre de paiements
        """
        return await self.count(method=method)
    
    async def get_total_amount_by_status(self, status: PaymentStatus) -> float:
        """
        Calcule le montant total des paiements par statut
        
        Args:
            status: Statut des paiements
        
        Returns:
            Montant total
        """
        payments = await self.get_by_status(status, skip=0, limit=10000)
        return sum(float(p.amount) for p in payments)