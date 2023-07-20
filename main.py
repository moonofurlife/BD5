import configparser
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import json
import sqlalchemy as sq

Base = declarative_base()

class Publisher(Base):
    __tablename__ = 'publisher'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=50), unique=True)
    book = relationship('Book', back_populates='publisher')
    def __str__(self):
        return f'name:{self.name}'
class Stock(Base):
    __tablename__ = 'stock'
    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('book.id'), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shop.id'), nullable=False)
    count = sq.Column(sq.Integer)

    book = relationship('Book', back_populates = 'stock')
    shop = relationship('Shop', back_populates='stock')
    def __str__(self):
        return f'count:{self.count}'
class Shop(Base):
    __tablename__ = 'shop'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=50), unique=True)
    stock = relationship('Stock', back_populates = 'shop')
    def __str__(self):
        return f'name:{self.name}, stock:{self.stock}'
class Book(Base):
    __tablename__ = 'book'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=50), unique=True)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publisher.id'), nullable=False)

    publisher = relationship('Publisher', back_populates = 'book')
    stock = relationship('Stock', back_populates = 'book')
    def __str__(self):
        return f'title:{self.title}'

class Sale(Base):
    __tablename__ = 'sale'
    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.String(length=50), nullable=False)
    date_sale = sq.Column(sq.Date, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey('stock.id'), nullable=False)
    count = sq.Column(sq.Integer)
    stock = relationship('Stock', backref='stock')
    def __str__(self):
        return f'count:{self.count}, stock:{self.stock}, date_sale:{self.date_sale}, price:{self.price}'

def create_tables(engine):
    Base.metadata.create_all(engine)
def drop_tables(engine):
    Base.metadata.drop_all(engine)
def complete_base(session):
    with open('data.json', 'r') as fd:
        data = json.load(fd)

    for record in data:
        model = {
            'publisher': Publisher,
            'shop': Shop,
            'book': Book,
            'stock': Stock,
            'sale': Sale,
        }[record.get('model')]
        session.add(model(id=record.get('pk'), **record.get('fields')))
def query_publisher(request):
    qu = session.query(Book, Shop, Sale, Publisher) \
        .join(Book) \
        .join(Stock) \
        .join(Sale) \
        .join(Shop)

    if request.isnumeric():
        res = qu.filter(Publisher.id == request).all()
    if request.isnumeric() == False:
        res = qu.filter(Publisher.name == request).all()
    for i in res:
        print(f' {i.Book.title} | {i.Shop.name}| {i.Sale.price} | {i.Sale.date_sale}')


if __name__ == '__main__':

    conf = configparser.ConfigParser()
    conf.read('config.ini')
    DSN = f"postgresql://{conf['pg_x']['user']}:{conf['pg_x']['password']}@localhost:5432/{conf['pg_x']['database']}"
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()

    request = input('Введите имя или идентификатор издателя: ')
    query_publisher(request)

    session.commit()
    session.close()
