# redis-cart
import redis
from django.conf import settings
import json

redis_client = settings.REDIS_CLIENT

CART_TTL = 60 * 30

def _refresh_cart_ttl(session_id):
    cart_key = _cart_key(session_id)
    promo_code = f"{cart_key}:promo_code"

    redis_client.expire(cart_key, CART_TTL)
    redis_client.expire(promo_code, CART_TTL)
    
def _cart_key(session_id):
    return f'cart:{session_id}'

def add_to_cart(session_id, product_id, name, price, quantity):
    cart_key = _cart_key(session_id)
    
    product_data = {
        "product_id": product_id,
        "name": name,
        "price": float(price),
        "quantity": quantity
    }
    
    # Set the product data in the cart
    # cart:item:session_id
    redis_client.hset(cart_key, product_id, json.dumps(product_data))
    _refresh_cart_ttl(session_id)
    
# get_carts
def get_cart(session_id):
    key = _cart_key(session_id)
    raw_cart = redis_client.hgetall(key)
    return [json.loads(item) for item in raw_cart.values()]

# remove cart
def remove_cart(session_id, product_id):
    key = _cart_key(session_id)
    redis_client.hdel(key, product_id)
    
    if redis_client.hlen(key) == 0:
        promo_key = f"cart:{session_id}:promo_code"
        redis_client.delete(promo_key)
    
    _refresh_cart_ttl(session_id)
    
# remove all items in cart
def remove_all_items(session_id):
    key = _cart_key(session_id)
    redis_client.delete(key)
    
# increment quantity
def increment_quantity(session_id, product_id, step=1):
    key = _cart_key(session_id)
    existing = redis_client.hget(key, product_id)
    
    if not existing:
        return False
    
    data = json.loads(existing)
    data['quantity'] += step
    redis_client.hset(key, product_id, json.dumps(data))
    
    _refresh_cart_ttl(session_id)
    
    return True

# decrement quantity
def decrement_quantity(session_id, product_id, step=1):
    key = _cart_key(session_id)
    existing = redis_client.hget(key, product_id)
    
    if not existing:
        return False
    
    data = json.loads(existing)
    data['quantity'] += max(data['quantity'] - step, 1)
    redis_client.hset(key, product_id, json.dumps(data))
    
    _refresh_cart_ttl(session_id)
    
    return True

# set explicity
def set_quantity(session_id, product_id, quantity):
    key = _cart_key(session_id)
    existing = redis_client.hget(key, product_id)
    
    if not existing:
        return False
    
    data = json.loads(existing)
    data['quantity'] = quantity
    redis_client.hset(key, product_id, json.dumps(data))
    
    _refresh_cart_ttl(session_id)
    
    return True

def set_cart_promo_code(session_id, promo_code):
    key = f"cart:{session_id}:promo_code"
    redis_client.set(key, promo_code)
    _refresh_cart_ttl(session_id)

def get_cart_promo_code(session_id):
    key = f"cart:{session_id}:promo_code"
    return redis_client.get(key)

def update_cart_item(session_id, product_id, name, price, quantity):
    key = _cart_key(session_id)
    
    product_data = {
        "product_id": product_id,
        "name": name,
        "price": price,
        "quantity": quantity
    }
    
    redis_client.hset(key, product_id, json.dumps(product_data))
    _refresh_cart_ttl(session_id)