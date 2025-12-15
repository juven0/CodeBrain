"""
Module repositories - Tous les repositories
Importations centralisées pour faciliter l'usage
"""

from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.product import ProductRepository
from app.repositories.category import CategoryRepository
from app.repositories.cart import CartRepository, CartItemRepository
from app.repositories.order import OrderRepository, OrderItemRepository
from app.repositories.payment import PaymentRepository
from app.repositories.review import ReviewRepository
from app.repositories.coupon import CouponRepository


__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProductRepository",
    "CategoryRepository",
    "CartRepository",
    "CartItemRepository",
    "OrderRepository",
    "OrderItemRepository",
    "PaymentRepository",
    "ReviewRepository",
    "CouponRepository",
]