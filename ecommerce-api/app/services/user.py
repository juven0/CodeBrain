
"""
Service de gestion des utilisateurs
CRUD et opérations sur les utilisateurs
"""

from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserUpdateRole


class UserService:
    """Service de gestion des utilisateurs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_user_by_id(self, user_id: int) -> User:
        """
        Récupère un utilisateur par son ID
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return user
    
    async def get_user_by_email(self, email: str) -> User:
        """
        Récupère un utilisateur par son email
        
        Args:
            email: Email de l'utilisateur
        
        Returns:
            Utilisateur
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return user
    
    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> Tuple[List[User], int]:
        """
        Récupère tous les utilisateurs avec pagination
        
        Args:
            skip: Offset
            limit: Limite
            active_only: Utilisateurs actifs uniquement
        
        Returns:
            (Liste d'utilisateurs, Total)
        """
        if active_only:
            users = await self.user_repo.get_all_active(skip, limit)
            total = await self.user_repo.count_active()
        else:
            users = await self.user_repo.get_all(skip, limit, order_by="created_at")
            total = await self.user_repo.count()
        
        return users, total
    
    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate
    ) -> User:
        """
        Met à jour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            user_update: Données à mettre à jour
        
        Returns:
            Utilisateur mis à jour
        
        Raises:
            HTTPException: Si utilisateur non trouvé ou email déjà utilisé
        """
        # Vérifier que l'utilisateur existe
        user = await self.get_user_by_id(user_id)
        
        # Vérifier si l'email est changé et s'il existe déjà
        if user_update.email and user_update.email != user.email:
            if await self.user_repo.email_exists(user_update.email, exclude_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )
        
        # Mettre à jour
        update_data = user_update.model_dump(exclude_unset=True)
        updated_user = await self.user_repo.update(user_id, update_data)
        
        return updated_user
    
    async def update_user_role(
        self,
        user_id: int,
        role: UserRole
    ) -> User:
        """
        Met à jour le rôle d'un utilisateur (admin uniquement)
        
        Args:
            user_id: ID de l'utilisateur
            role: Nouveau rôle
        
        Returns:
            Utilisateur mis à jour
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.get_user_by_id(user_id)
        
        updated_user = await self.user_repo.update_role(user_id, role)
        
        return updated_user
    
    async def activate_user(self, user_id: int) -> User:
        """
        Active un compte utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur activé
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.get_user_by_id(user_id)
        
        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le compte est déjà actif"
            )
        
        activated_user = await self.user_repo.activate(user_id)
        
        return activated_user
    
    async def deactivate_user(self, user_id: int) -> User:
        """
        Désactive un compte utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Utilisateur désactivé
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.get_user_by_id(user_id)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le compte est déjà désactivé"
            )
        
        deactivated_user = await self.user_repo.deactivate(user_id)
        
        return deactivated_user
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Supprime un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            True si supprimé
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.get_user_by_id(user_id)
        
        deleted = await self.user_repo.delete(user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression"
            )
        
        return True
    
    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[User], int]:
        """
        Recherche d'utilisateurs
        
        Args:
            search_term: Terme de recherche
            skip: Offset
            limit: Limite
        
        Returns:
            (Liste d'utilisateurs, Total)
        """
        users = await self.user_repo.search(search_term, skip, limit)
        
        # Pour le total, on refait une recherche sans pagination
        all_results = await self.user_repo.search(search_term, 0, 10000)
        total = len(all_results)
        
        return users, total
    
    async def get_users_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[User], int]:
        """
        Récupère les utilisateurs par rôle
        
        Args:
            role: Rôle recherché
            skip: Offset
            limit: Limite
        
        Returns:
            (Liste d'utilisateurs, Total)
        """
        users = await self.user_repo.get_by_role(role, skip, limit)
        total = await self.user_repo.count_by_role(role)
        
        return users, total
    
    async def get_user_statistics(self) -> dict:
        """
        Récupère les statistiques des utilisateurs
        
        Returns:
            Dictionnaire de statistiques
        """
        total = await self.user_repo.count()
        active = await self.user_repo.count_active()
        customers = await self.user_repo.count_by_role(UserRole.CUSTOMER)
        admins = await self.user_repo.count_by_role(UserRole.ADMIN)
        managers = await self.user_repo.count_by_role(UserRole.MANAGER)
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "customers": customers,
            "admins": admins,
            "managers": managers
        }