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

    posts: so.WriteOnlyMapped["Text"] = so.relationship(back_populates='author')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Text(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200))
    predictions: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
