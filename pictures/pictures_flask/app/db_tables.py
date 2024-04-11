from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    city: so.Mapped[str] = so.mapped_column(sa.String(32))
    company: so.Mapped[str] = so.mapped_column(sa.String(64))
    profession: so.Mapped[str] = so.mapped_column(sa.String(64))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    compared_files: so.WriteOnlyMapped['Pdfs'] = so.relationship(back_populates='file_compare_author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Пользователь {}>'.format(self.username)

class Pdfs(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    pdf_names: so.Mapped[str] = so.mapped_column(sa.String(256))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    file_compare_author: so.Mapped[User] = so.relationship(back_populates='compared_files')

    def __repr__(self):
        return '<pdf_names {}>'.format(self.pdf_names)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))