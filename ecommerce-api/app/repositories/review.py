
"""
Repository pour Review
Gestion de l'accès aux données des avis clients
"""

from typing import Optional, List, Dict
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Repository pour gérer les avis clients"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Review, db)
    
    async def get_by_product_id(
        self,
        product_id: int,
        approved_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Récupère les avis d'un produit
        
        Args:
            product_id: ID du produit
            approved_only: Avis approuvés uniquement
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'avis
        """
        query = (
            select(Review)
            .where(Review.product_id == product_id)
            .options(selectinload(Review.user))
        )
        
        if approved_only:
            query = query.where(Review.is_approved == True)
        
        query = query.offset(skip).limit(limit).order_by(Review.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Récupère les avis d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'avis
        """
        query = (
            select(Review)
            .where(Review.user_id == user_id)
            .options(selectinload(Review.product))
            .offset(skip)
            .limit(limit)
            .order_by(Review.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int
    ) -> Optional[Review]:
        """
        Récupère l'avis d'un utilisateur pour un produit spécifique
        
        Args:
            user_id: ID de l'utilisateur
            product_id: ID du produit
        
        Returns:
            Avis ou None
        """
        query = select(Review).where(
            and_(
                Review.user_id == user_id,
                Review.product_id == product_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def user_has_reviewed_product(
        self,
        user_id: int,
        product_id: int
    ) -> bool:
        """
        Vérifie si un utilisateur a déjà donné un avis sur un produit
        
        Args:
            user_id: ID de l'utilisateur
            product_id: ID du produit
        
        Returns:
            True si avis existe
        """
        review = await self.get_by_user_and_product(user_id, product_id)
        return review is not None
    
    async def get_by_rating(
        self,
        rating: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Récupère les avis par note
        
        Args:
            rating: Note (1-5)
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'avis
        """
        query = (
            select(Review)
            .where(
                and_(
                    Review.rating == rating,
                    Review.is_approved == True
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Review.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_pending_reviews(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Récupère les avis en attente de modération
        
        Args:
            skip: Offset
            limit: Limite
        
        Returns:
            Liste d'avis non approuvés
        """
        query = (
            select(Review)
            .where(Review.is_approved == False)
            .options(
                selectinload(Review.user),
                selectinload(Review.product)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Review.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def approve(self, review_id: int) -> Optional[Review]:
        """
        Approuve un avis
        
        Args:
            review_id: ID de l'avis
        
        Returns:
            Avis approuvé
        """
        return await self.update(review_id, {"is_approved": True})
    
    async def reject(self, review_id: int) -> Optional[Review]:
        """
        Rejette un avis
        
        Args:
            review_id: ID de l'avis
        
        Returns:
            Avis rejeté
        """
        return await self.update(review_id, {"is_approved": False})
    
    async def get_average_rating(self, product_id: int) -> Optional[float]:
        """
        Calcule la note moyenne d'un produit
        
        Args:
            product_id: ID du produit
        
        Returns:
            Note moyenne ou None
        """
        query = (
            select(func.avg(Review.rating))
            .where(
                and_(
                    Review.product_id == product_id,
                    Review.is_approved == True
                )
            )
        )
        result = await self.db.execute(query)
        average = result.scalar_one_or_none()
        
        return round(float(average), 2) if average else None
    
    async def count_by_product(self, product_id: int, approved_only: bool = True) -> int:
        """
        Compte les avis d'un produit
        
        Args:
            product_id: ID du produit
            approved_only: Compter uniquement les avis approuvés
        
        Returns:
            Nombre d'avis
        """
        if approved_only:
            return await self.count(product_id=product_id, is_approved=True)
        return await self.count(product_id=product_id)
    
    async def count_by_user(self, user_id: int) -> int:
        """
        Compte les avis d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Nombre d'avis
        """
        return await self.count(user_id=user_id)
    
    async def get_rating_distribution(self, product_id: int) -> Dict[int, int]:
        """
        Calcule la distribution des notes pour un produit
        
        Args:
            product_id: ID du produit
        
        Returns:
            Dict avec {note: nombre_avis}
        """
        query = (
            select(Review.rating, func.count(Review.id))
            .where(
                and_(
                    Review.product_id == product_id,
                    Review.is_approved == True
                )
            )
            .group_by(Review.rating)
        )
        result = await self.db.execute(query)
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating, count in result.all():
            distribution[rating] = count
        
        return distribution
    
    async def count_pending(self) -> int:
        """
        Compte les avis en attente de modération
        
        Returns:
            Nombre d'avis non approuvés
        """
        return await self.count(is_approved=False)