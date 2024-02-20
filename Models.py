from flask_login import UserMixin
from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class User(UserMixin, Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

    # ONE-MANY RELATIONSHIP
    products = relationship('Product', back_populates='user_product')


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    product_url: Mapped[str] = mapped_column(String(3000), nullable=False)
    product_price: Mapped[str] = mapped_column(String(500), nullable=False)
    current_price: Mapped[str] = mapped_column(String(500), nullable=False)
    site_name: Mapped[str] = mapped_column(String(500), nullable=False)
    target_price: Mapped[str] = mapped_column(String(250), nullable=False)
    track_status: Mapped[bool] = mapped_column(Boolean(), default=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    user_product = relationship("User", back_populates="products")
