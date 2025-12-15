"""
Service d'authentification
Gestion de l'inscription, connexion, tokens JWT
"""

from typing import Optional, Tuple
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_email_verification_token,
    create_password_reset_token
)
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import LoginResponse, UserInfo, RefreshTokenResponse
from app.schemas.user import UserCreate


class AuthService:
    """Service d'authentification"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, user_data: UserCreate) -> User:
        """
        Inscription d'un nouvel utilisateur
        
        Args:
            user_data: Données d'inscription
        
        Returns:
            Utilisateur créé
        
        Raises:
            HTTPException: Si email déjà utilisé
        """
        # Vérifier si l'email existe déjà
        if await self.user_repo.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        
        # Hasher le mot de passe
        password_hash = hash_password(user_data.password)
        
        # Créer l'utilisateur
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password_hash"] = password_hash
        user_dict["role"] = UserRole.CUSTOMER  # Par défaut client
        
        user = await self.user_repo.create(user_dict)
        
        return user
    
    async def login(self, email: str, password: str) -> LoginResponse:
        """
        Connexion utilisateur
        
        Args:
            email: Email
            password: Mot de passe
        
        Returns:
            Tokens JWT et infos utilisateur
        
        Raises:
            HTTPException: Si identifiants invalides
        """
        # Récupérer l'utilisateur
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier le mot de passe
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier si le compte est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé. Contactez l'administrateur"
            )
        
        # Générer les tokens
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role}
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user.id}
        )
        
        # Préparer les infos utilisateur
        user_info = UserInfo(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info
        )
    
    async def refresh_access_token(self, refresh_token: str) -> RefreshTokenResponse:
        """
        Rafraîchit le token d'accès
        
        Args:
            refresh_token: Token de rafraîchissement
        
        Returns:
            Nouveau token d'accès
        
        Raises:
            HTTPException: Si token invalide
        """
        try:
            payload = decode_token(refresh_token)
            
            # Vérifier le type de token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Type de token invalide"
                )
            
            user_id = payload.get("sub")
            
            # Vérifier que l'utilisateur existe toujours
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Utilisateur invalide"
                )
            
            # Générer un nouveau token d'accès
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email, "role": user.role}
            )
            
            return RefreshTokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de rafraîchissement invalide"
            )
    
    async def verify_email(self, token: str) -> User:
        """
        Vérifie l'email d'un utilisateur
        
        Args:
            token: Token de vérification
        
        Returns:
            Utilisateur vérifié
        
        Raises:
            HTTPException: Si token invalide
        """
        try:
            payload = decode_token(token)
            
            if payload.get("type") != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Type de token invalide"
                )
            
            email = payload.get("sub")
            user = await self.user_repo.get_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé"
                )
            
            if user.is_email_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email déjà vérifié"
                )
            
            # Vérifier l'email
            verified_user = await self.user_repo.verify_email(user.id)
            
            return verified_user
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de vérification invalide ou expiré"
            )
    
    async def request_password_reset(self, email: str) -> str:
        """
        Demande de réinitialisation de mot de passe
        
        Args:
            email: Email de l'utilisateur
        
        Returns:
            Token de réinitialisation
        
        Raises:
            HTTPException: Si utilisateur non trouvé
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            # Ne pas révéler si l'email existe ou non (sécurité)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Si cet email existe, un lien de réinitialisation a été envoyé"
            )
        
        # Générer le token
        reset_token = create_password_reset_token(email)
        
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> User:
        """
        Réinitialise le mot de passe
        
        Args:
            token: Token de réinitialisation
            new_password: Nouveau mot de passe
        
        Returns:
            Utilisateur mis à jour
        
        Raises:
            HTTPException: Si token invalide
        """
        try:
            payload = decode_token(token)
            
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Type de token invalide"
                )
            
            email = payload.get("sub")
            user = await self.user_repo.get_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Utilisateur non trouvé"
                )
            
            # Hasher le nouveau mot de passe
            new_password_hash = hash_password(new_password)
            
            # Mettre à jour
            updated_user = await self.user_repo.update_password(
                user.id,
                new_password_hash
            )
            
            return updated_user
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide ou expiré"
            )
    
    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> User:
        """
        Change le mot de passe d'un utilisateur connecté
        
        Args:
            user_id: ID de l'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
        
        Returns:
            Utilisateur mis à jour
        
        Raises:
            HTTPException: Si mot de passe actuel incorrect
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Vérifier le mot de passe actuel
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe actuel incorrect"
            )
        
        # Hasher le nouveau mot de passe
        new_password_hash = hash_password(new_password)
        
        # Mettre à jour
        updated_user = await self.user_repo.update_password(
            user.id,
            new_password_hash
        )
        
        return updated_user
