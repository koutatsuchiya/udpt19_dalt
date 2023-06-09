from main import redis, Product
import time

key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists')


while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        # decrease quantity in product db
        if results is not []:
            for r in results:
                obj = r[1][0][1]
                try:
                    p = Product.get(obj['p_id'])
                    p.quantity = p.quantity - int(obj['quantity'])
                    p.save()
                except:
                    redis.xadd('refund_order', obj, '*')
    except Exception as e:
        print(str(e))
    time.sleep(2)
