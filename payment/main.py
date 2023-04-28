import uvicorn
from fastapi import FastAPI, Request
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
import requests
import time

app = FastAPI()  # gọi constructor và gán vào var app

# nên dùng db khác, nhưng cho nhanh và gọn thì dùng lại
redis = get_redis_connection(
    host='redis-18501.c1.ap-southeast-1-1.ec2.cloud.redislabs.com',
    port=18501,
    password='E6r6fkC2tA4MFZfYbBrKAXAEBNtNRLdc',
    decode_responses=True
)


class Order(HashModel):
    p_id: str
    price: float
    quantity: int
    total: float
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get('/orders')
def all():
    return [format(pk) for pk in Order.all_pks()]


def format(pk: str):
    o = Order.get(pk)
    req = requests.get('http://localhost:8001/products/%s' % o.p_id)
    p = req.json()
    return {
        'id': pk,
        'p_name': p['name'],
        'price': o.price,
        'quantity': o.quantity,
        'total': o.total,
        'status': o.status
    }


@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, bg_tasks: BackgroundTasks):  # id, quantity
    body = await request.json()
    req = requests.get('http://localhost:8001/products/%s' % body['id'])
    p = req.json()
    order = Order(
        p_id=body['id'],
        price=p['price'],
        quantity=body['quantity'],
        total=body['quantity'] * p['price'],
        status='pending'
    )
    order.save()
    bg_tasks.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    time.sleep(5)  # xem như thời gian cần để hoàn tất đơn hàng
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')  # add an event to redis stream


@app.delete('/orders')
def delete():
    return [Order.delete(pk) for pk in Order.all_pks()]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
