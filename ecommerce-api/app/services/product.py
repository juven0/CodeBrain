
"""
Service de gestion des produits
CRUD et opérations sur les produits
"""

from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.repositories.category import CategoryRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductFilterParams


class ProductService:
    """Service de gestion des produits"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)
    
    async def get_product_by_id(self, product_id: int) -> Product:
        """
        Récupère un produit par son ID
        
        Args:
            product_id: ID du produit
        
        Returns:
            Produit
        
        Raises:
            HTTPException: Si produit non trouvé
        """
        product = await self.product_repo.get_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )
        
        return product
    
    async def get_product_by_slug(self, slug: str) -> Product:
        """
        Récupère un produit par son slug
        
        Args:
            slug: Slug du produit
        
        Returns:
            Produit avec détails
        
        Raises:
            HTTPException: Si produit non trouvé
        """
        product = await self.product_repo.get_by_slug(slug)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produit non trouvé"
            )
        
        return product
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Crée un nouveau produit
        
        Args:
            product_data: Données du produit
        
        Returns:
            Produit créé
        
        Raises:
            HTTPException: Si slug ou SKU existe déjà
        """
        # Vérifier le slug
        if await self.product_repo.slug_exists(product_data.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce slug est déjà utilisé"
            )
        
        # Vérifier le SKU si fourni
        if product_data.sku and await self.product_repo.sku_exists(product_data.sku):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce SKU est déjà utilisé"
            )
        
        # Créer le produit
        product_dict = product_data.model_dump(exclude={"category_ids"})
        product = await self.product_repo.create(product_dict)
        
        # Ajouter aux catégories
        if product_data.category_ids:
            for category_id in product_data.category_ids:
                await self.product_repo.add_to_category(product.id, category_id)
        
        # Recharger le produit avec les relations
        return await self.product_repo.get_by_slug(product.slug)
    
    async def update_product(
        self,
        product_id: int,
        product_update: ProductUpdate
    ) -> Product:
        """
        Met à jour un produit
        
        Args:
            product_id: ID du produit
            product_update: Données à mettre à jour
        
        Returns:
            Produit mis à jour
        
        Raises:
            HTTPException: Si produit non trouvé ou slug/SKU existe déjà
        """
        # Vérifier que le produit existe
        product = await self.get_product_by_id(product_id)
        
        # Vérifier le slug si changé
        if product_update.slug and product_update.slug != product.slug:
            if await self.product_repo.slug_exists(product_update.slug, exclude_id=product_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce slug est déjà utilisé"
                )
        
        # Vérifier le SKU si changé
        if product_update.sku and product_update.sku != product.sku:
            if await self.product_repo.sku_exists(product_update.sku, exclude_id=product_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce SKU est déjà utilisé"
                )
        
        # Mettre à jour les catégories si fournies
        if product_update.category_ids is not None:
            # Retirer de toutes les catégories actuelles
            for category in product.categories:
                await self.product_repo.remove_from_category(product_id, category.id)
            
            # Ajouter aux nouvelles catégories
            for category_id in product_update.category_ids:
                await self.product_repo.add_to_category(product_id, category_id)
        
        # Mettre à jour le produit
        update_data = product_update.model_dump(exclude_unset=True, exclude={"category_ids"})
        updated_product = await self.product_repo.update(product_id, update_data)
        
        # Recharger avec les relations
        return await self.product_repo.get_by_slug(updated_product.slug)
    
    async def delete_product(self, product_id: int) -> bool:
        """
        Supprime un produit
        
        Args:
            product_id: ID du produit
        
        Returns:
            True si supprimé
        
        Raises:
            HTTPException: Si produit non trouvé
        """
        await self.get_product_by_id(product_id)
        
        deleted = await self.product_repo.delete(product_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression"
            )
        
        return True
    
    async def get_products(
        self,
        filters: ProductFilterParams,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Product], int]:
        """
        Récupère les produits avec filtres et pagination
        
        Args:
            filters: Paramètres de filtrage
            skip: Offset
            limit: Limite
        
        Returns:
            (Liste de produits, Total)
        """
        # Recherche textuelle
        if filters.search:
            products = await self.product_repo.search(filters.search, skip, limit)
            all_results = await self.product_repo.search(filters.search, 0, 10000)
            return products, len(all_results)
        
        # Filtrer par catégorie
        if filters.category_id:
            products = await self.product_repo.get_by_category(
                filters.category_id, skip, limit
            )
            all_results = await self.product_repo.get_by_category(
                filters.category_id, 0, 10000
            )
            return products, len(all_results)
        
        # Filtrer par fourchette de prix
        if filters.min_price is not None and filters.max_price is not None:
            products = await self.product_repo.get_by_price_range(
                filters.min_price, filters.max_price, skip, limit
            )
            all_results = await self.product_repo.get_by_price_range(
                filters.min_price, filters.max_price, 0, 10000
            )
            return products, len(all_results)
        
        # Produits en stock
        if filters.in_stock:
            products = await self.product_repo.get_in_stock(skip, limit)
            all_results = await self.product_repo.get_in_stock(0, 10000)
            return products, len(all_results)
        
        # Produits en promotion
        if filters.on_sale:
            products = await self.product_repo.get_on_sale(skip, limit)
            all_results = await self.product_repo.get_on_sale(0, 10000)
            return products, len(all_results)
        
        # Tous les produits actifs
        products = await self.product_repo.get_active(skip, limit)
        total = await self.product_repo.count(is_active=True)
        
        return products, total
    
    async def update_stock(
        self,
        product_id: int,
        quantity: int
    ) -> Product:
        """
        Met à jour le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Nouvelle quantité
        
        Returns:
            Produit mis à jour
        
        Raises:
            HTTPException: Si produit non trouvé
        """
        await self.get_product_by_id(product_id)
        
        updated_product = await self.product_repo.update_stock(product_id, quantity)
        
        return updated_product
    
    async def decrease_stock(
        self,
        product_id: int,
        quantity: int
    ) -> Product:
        """
        Diminue le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité à retirer
        
        Returns:
            Produit mis à jour
        
        Raises:
            HTTPException: Si stock insuffisant
        """
        product = await self.get_product_by_id(product_id)
        
        if product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuffisant. Disponible: {product.stock}"
            )
        
        updated_product = await self.product_repo.decrease_stock(product_id, quantity)
        
        return updated_product
    
    async def increase_stock(
        self,
        product_id: int,
        quantity: int
    ) -> Product:
        """
        Augmente le stock d'un produit
        
        Args:
            product_id: ID du produit
            quantity: Quantité à ajouter
        
        Returns:
            Produit mis à jour
        """
        await self.get_product_by_id(product_id)
        
        updated_product = await self.product_repo.increase_stock(product_id, quantity)
        
        return updated_product