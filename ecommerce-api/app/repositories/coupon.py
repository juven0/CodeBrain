
"""
Repository pour Coupon
Gestion de l'accès aux données des coupons
"""

from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.coupon import Coupon, DiscountType
from app.repositories.base import BaseRepository


class CouponRepository(BaseRepository[Coupon]):
    """Repository pour gérer les coupons"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Coupon, db)
    
    async def get_by_code(self, code: str) -> Optional[Coupon]:
        """
        Récupère un coupon par son code
        
        Args:
            code: Code promo
        
        Returns:
            Coupon ou None
        """
        query = select(Coupon).where(Coupon.code == code.upper())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un code promo existe déjà
        
        Args:
            code: Code à vérifier
            exclude_id: ID à exclure
        
        Returns:
            True si existe, False sinon
        """
        query = select(Coupon.id).where(Coupon.code == code.upper())
        
        if exclude_id:
            query = query.where(Coupon.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def get_active_coupons(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Coupon]:
        """
        Récupère les coupons actifs
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de coupons actifs
        """
        query = (
            select(Coupon)
            .where(Coupon.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Coupon.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_valid_coupons(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Coupon]:
        """
        Récupère les coupons valides (actifs et non expirés)
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de coupons valides
        """
        now = datetime.utcnow()
        
        query = (
            select(Coupon)
            .where(
                and_(
                    Coupon.is_active == True,
                    or_(
                        Coupon.expires_at.is_(None),
                        Coupon.expires_at > now
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Coupon.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_discount_type(
        self,
        discount_type: DiscountType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Coupon]:
        """
        Récupère les coupons par type de réduction
        
        Args:
            discount_type: Type de réduction
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de coupons
        """
        query = (
            select(Coupon)
            .where(Coupon.discount_type == discount_type)
            .offset(skip)
            .limit(limit)
            .order_by(Coupon.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_expired_coupons(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Coupon]:
        """
        Récupère les coupons expirés
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste de coupons expirés
        """
        now = datetime.utcnow()
        
        query = (
            select(Coupon)
            .where(
                and_(
                    Coupon.expires_at.is_not(None),
                    Coupon.expires_at < now
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Coupon.expires_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def is_valid(self, coupon_id: int) -> bool:
        """
        Vérifie si un coupon est valide
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            True si valide (actif et non expiré)
        """
        coupon = await self.get_by_id(coupon_id)
        if not coupon:
            return False
        
        if not coupon.is_active:
            return False
        
        if coupon.expires_at and coupon.expires_at < datetime.utcnow():
            return False
        
        return True
    
    async def validate_code(self, code: str) -> tuple[bool, Optional[Coupon], Optional[str]]:
        """
        Valide un code promo complet
        
        Args:
            code: Code à valider
        
        Returns:
            (is_valid, coupon, error_message)
        """
        coupon = await self.get_by_code(code)
        
        if not coupon:
            return False, None, "Code promo invalide"
        
        if not coupon.is_active:
            return False, coupon, "Ce code promo n'est plus actif"
        
        if coupon.expires_at and coupon.expires_at < datetime.utcnow():
            return False, coupon, "Ce code promo a expiré"
        
        return True, coupon, None
    
    async def activate(self, coupon_id: int) -> Optional[Coupon]:
        """
        Active un coupon
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Coupon activé
        """
        return await self.update(coupon_id, {"is_active": True})
    
    async def deactivate(self, coupon_id: int) -> Optional[Coupon]:
        """
        Désactive un coupon
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Coupon désactivé
        """
        return await self.update(coupon_id, {"is_active": False})
    
    async def count_active(self) -> int:
        """
        Compte les coupons actifs
        
        Returns:
            Nombre de coupons actifs
        """
        return await self.count(is_active=True)
    
    async def count_valid(self) -> int:
        """
        Compte les coupons valides (actifs et non expirés)
        
        Returns:
            Nombre de coupons valides
        """
        now = datetime.utcnow()
        
        query = select(func.count(Coupon.id)).where(
            and_(
                Coupon.is_active == True,
                or_(
                    Coupon.expires_at.is_(None),
                    Coupon.expires_at > now
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def get_usage_count(self, coupon_id: int) -> int:
        """
        Compte le nombre de fois qu'un coupon a été utilisé
        
        Args:
            coupon_id: ID du coupon
        
        Returns:
            Nombre d'utilisations
        """
        coupon = await self.get_by_id(coupon_id)
        if not coupon:
            return 0
        
        return len(coupon.orders) if coupon.orders else 0


# Import nécessaire pour les conditions OR
from sqlalchemy import or_