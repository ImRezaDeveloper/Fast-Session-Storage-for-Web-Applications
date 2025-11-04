# redis-cart
import redis
from django.conf import settings
import json

redis_client = settings.REDIS_CLIENT

CART_TTL = 60 * 30

def _refresh_cart_ttl(session_id):
    redis_client.expire(_qty_key(session_id), CART_TTL)
    redis_client.expire(_details_key(session_id), CART_TTL)
    redis_client.expire(f"{_cart_key}:promo_code", CART_TTL)
    
def _cart_key(session_id):
    return f'cart:{session_id}'

def _qty_key(session_id):
    return f'{_cart_key(session_id)}:qty'

def _details_key(session_id):
    return f'{_cart_key(session_id)}:details'

def add_to_cart(session_id, product_id, name, price, quantity):
    # cart_key = _cart_key(session_id)
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)
    
    redis_client.hincrby(qty_key, product_id, quantity)
    
    if not redis_client.hexists(details_key, product_id):
        product_data = {
            "product_id": product_id,
            "name": name,
            "price": float(price)
        }
        redis_client.hset(details_key, product_id, json.dumps(product_data))
    
    _refresh_cart_ttl(session_id)
    
# get_carts
def get_cart(session_id):
    qty = redis_client.hgetall(_qty_key(session_id))
    details = redis_client.hgetall(_details_key(session_id))
    
    cart_items = []
    
    for pid, qty, in qty.items():
        detail_json = details.get(pid)
        if not detail_json:
            continue
        
        data = json.loads(detail_json)
        data["quantity"] = int(qty)
        cart_items.append(data)
        
    return cart_items

# remove cart
def remove_cart(session_id, product_id):
    redis_client.hdel(_qty_key(session_id), product_id)
    redis_client.hdel(_details_key(session_id), product_id)
    
    if redis_client.hlen(session_id) == 0:
        redis_client.delete(f"{_cart_key(session_id)}:promo_code")
    
    _refresh_cart_ttl(session_id)
    
# remove all items in cart
def remove_all_items(session_id):
    redis_client.delete(_qty_key(session_id))
    redis_client.delete(_details_key(session_id))
    redis_client.delete(f"{_cart_key(session_id)}:promo_code")
    
# increment quantity
def increment_quantity(session_id, product_id, step=1):
    redis_client.hincrby(_qty_key(session_id), product_id, step)
    _refresh_cart_ttl(session_id)
    
    return True

# decrement quantity
def decrement_quantity(session_id, product_id, step=1):
    qty_key = _qty_key(session_id)
    new_qty = redis_client.hincryby(qty_key, product_id, -step)
    
    if new_qty < 1:
        redis_client.hdel(qty_key, product_id)
        redis_client.hdel(_details_key(session_id), product_id)
        
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
    details = {
        "product_id": product_id,
        "name": name,
        "price": float(product_id),
    }
    
    redis_client.hset(_details_key(session_id), product_id, json.dumps(details))
    redis_client.hset(_qty_key(session_id), product_id, quantity)
    _refresh_cart_ttl(session_id)