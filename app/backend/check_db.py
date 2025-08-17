from app.backend.api.web.app import create_app
from models import db
from sqlalchemy import inspect

app, _, _ = create_app()
app.app_context().push()

inspector = inspect(db.engine)

print('Cart表结构:')
for column in inspector.get_columns('cart'):
    print(f'  {column["name"]}: {column["type"]}')

print('\nCart表索引:')
for index in inspector.get_indexes('cart'):
    print(f'  {index["name"]}: {index["column_names"]} - unique: {index["unique"]}')

print('\nCart表约束:')
for fk in inspector.get_foreign_keys('cart'):
    print(f'  外键: {fk["constrained_columns"]} -> {fk["referred_table"]}.{fk["referred_columns"]}')

print('\nCart表数据:')
from models import Cart
carts = Cart.query.all()
for cart in carts:
    print(f'  ID: {cart.id}, 用户ID: {cart.user_id}, 商品ID: {cart.product_id}, 规格组合ID: {cart.spec_combination_id}, 数量: {cart.quantity}') 