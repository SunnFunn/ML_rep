import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.tables import User, Surnames

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Surnames=Surnames)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
