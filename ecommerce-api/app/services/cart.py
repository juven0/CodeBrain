
"""
Service de gestion du panier
Opérations sur le panier d'achat
"""

from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.repositories.cart import CartRepository, CartItemRepository
from app.repositories.product import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate


class CartService:
    """Service de gestion du panier"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cart_repo = CartRepository(db)
        self.cart_item_repo = CartItemRepository(db)
        self.product_repo = ProductRepository(db)
    
    async def get_or_create_cart(self, user_id: int) -> Cart:
        """
        Récupère ou crée le panier d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Panier
        """
        cart = await self.cart_repo.get_or_create(user_id)
        return cart
    
    async def get_cart(self, user_id: int) -> Cart:
        """
        Récupère le panier d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Panier
        
        Raises:
            HTTPException: Si panier non trouvé
        """
        cart = await self.cart_repo.get_by_user_id(user_id)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Panier non trouvé"
            )
        
        return cart
    
    async def add_to_cart(
        self,
        user_id: int,
        item_data: CartItemCreate
    ) -> CartItem:
        """
        Ajoute un produit au panier
        
        Args:
            user_id: ID de l'utilisateur
            item_data: Données de l'article
        
        Returns:
            Article ajouté
        
        Raises:
            HTTPException: Si produit non disponible
        """
        # Vérifier que le produit existe et est disponible
        product = await self.product_repo.get_by_id(item_data.product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )
        
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce produit n'est plus disponible"
            )
        
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuffisant. Disponible: {product.stock}"
            )
        
        # Récupérer ou créer le panier
        cart = await self.get_or_create_cart(user_id)
        
        # Ajouter l'article (ou mettre à jour si déjà présent)
        cart_item = await self.cart_item_repo.add_item(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.current_price
        )
        
        return cart_item
    
    async def update_cart_item(
        self,
        user_id: int,
        item_id: int,
        item_update: CartItemUpdate
    ) -> CartItem:
        """
        Met à jour la quantité d'un article du panier
        
        Args:
            user_id: ID de l'utilisateur
            item_id: ID de l'article
            item_update: Données de mise à jour
        
        Returns:
            Article mis à jour
        
        Raises:
            HTTPException: Si article non trouvé ou stock insuffisant
        """
        # Vérifier que l'article existe et appartient à l'utilisateur
        cart_item = await self.cart_item_repo.get_by_id(item_id)
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article non trouvé dans le panier"
            )
        
        # Vérifier que l'article appartient au panier de l'utilisateur
        cart = await self.cart_repo.get_by_user_id(user_id)
        if not cart or cart_item.cart_id != cart.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cet article ne vous appartient pas"
            )
        
        # Vérifier le stock
        product = await self.product_repo.get_by_id(cart_item.product_id)
        if product.stock < item_update.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuffisant. Disponible: {product.stock}"
            )
        
        # Mettre à jour
        updated_item = await self.cart_item_repo.update_quantity(
            item_id,
            item_update.quantity
        )
        
        return updated_item
    
    async def remove_from_cart(
        self,
        user_id: int,
        item_id: int
    ) -> bool:
        """
        Retire un article du panier
        
        Args:
            user_id: ID de l'utilisateur
            item_id: ID de l'article
        
        Returns:
            True si supprimé
        
        Raises:
            HTTPException: Si article non trouvé
        """
        # Vérifier que l'article existe et appartient à l'utilisateur
        cart_item = await self.cart_item_repo.get_by_id(item_id)
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article non trouvé dans le panier"
            )
        
        # Vérifier l'appartenance
        cart = await self.cart_repo.get_by_user_id(user_id)
        if not cart or cart_item.cart_id != cart.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cet article ne vous appartient pas"
            )
        
        # Supprimer
        deleted = await self.cart_item_repo.remove_item(item_id)
        
        return deleted
    
    async def clear_cart(self, user_id: int) -> bool:
        """
        Vide le panier d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            True si vidé
        
        Raises:
            HTTPException: Si panier non trouvé
        """
        cart = await self.get_cart(user_id)
        
        cleared = await self.cart_repo.clear(cart.id)
        
        return cleared
    
    async def get_cart_total(self, user_id: int) -> dict:
        """
        Calcule le total du panier
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Dictionnaire avec les totaux
        """
        cart = await self.get_or_create_cart(user_id)
        
        return {
            "subtotal": cart.subtotal,
            "total_items": cart.total_items,
            "items_count": len(cart.items) if cart.items else 0
        }
    
    async def validate_cart(self, user_id: int) -> tuple[bool, list[str]]:
        """
        Valide le panier avant commande
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            (is_valid, errors)
        """
        cart = await self.get_cart(user_id)
        errors = []
        
        if cart.is_empty:
            errors.append("Le panier est vide")
            return False, errors
        
        # Vérifier chaque article
        for item in cart.items:
            product = await self.product_repo.get_by_id(item.product_id)
            
            if not product:
                errors.append(f"Produit {item.product_id} non trouvé")
                continue
            
            if not product.is_active:
                errors.append(f"{product.name} n'est plus disponible")
            
            if product.stock < item.quantity:
                errors.append(
                    f"Stock insuffisant pour {product.name}. "
                    f"Disponible: {product.stock}, Demandé: {item.quantity}"
                )
        
        is_valid = len(errors) == 0
        
        return is_valid, errors