import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login

from datetime import datetime
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    city: so.Mapped[str] = so.mapped_column(sa.String(32))
    profession: so.Mapped[str] = so.mapped_column(sa.String(128))

    surnames: so.WriteOnlyMapped["Surnames"] = so.relationship(back_populates='author')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Surnames(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    surname_beginning: so.Mapped[str] = so.mapped_column(sa.String(140))
    surnames_generated: so.Mapped[str] = so.mapped_column(sa.String(300))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='surnames')

    def __repr__(self):
        return '<Surnames {}>'.format(self.surnames_generated)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
