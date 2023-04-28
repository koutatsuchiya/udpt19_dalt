import uvicorn
from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel

app = FastAPI()  # gọi constructor và gán vào var app

redis = get_redis_connection(
    host='redis-18501.c1.ap-southeast-1-1.ec2.cloud.redislabs.com',
    port=18501,
    password='E6r6fkC2tA4MFZfYbBrKAXAEBNtNRLdc',
    decode_responses=True
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get('/products')  # giống flask, khai báo phương thức get và url
# async def root(): # do dùng ASGI nên ở đây thêm async, nếu bên thứ 3 không hỗ trợ thì bỏ async đi
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    p = Product.get(pk)
    return {
        'id': p.pk,
        'name': p.name,
        'price': p.price,
        'quantity': p.quantity
    }


@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.post('/products')
def create(product: Product):
    return product.save()


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
