import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()  # gọi constructor và gán vào var app

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)  # giống flask, khai báo phương thức get và url
async def root(request: Request):  # do dùng ASGI nên ở đây thêm async, nếu bên thứ 3 không hỗ trợ thì bỏ async đi
    req = requests.get('http://localhost:8001/products')
    products = req.json()
    return templates.TemplateResponse("pList.html", {"products": products, "request": request})


@app.get('/addProduct', response_class=HTMLResponse)
async def addProductPage(request: Request):
    return templates.TemplateResponse("pAdd.html", {"request": request})


@app.post('/pCreate', response_class=RedirectResponse, status_code=302)
async def createProduct(p_name: str = Form(...), p_price: float = Form(...), p_quan: int = Form(...)):
    requests.post('http://localhost:8001/products', json={'name': p_name, 'price': p_price, 'quantity': p_quan})
    return '/'


@app.post('/deleteProduct', response_class=RedirectResponse, status_code=302)
async def deleteProduct(p_id: str = Form(...)):
    requests.delete('http://localhost:8001/products/%s' % p_id)
    return '/'


@app.get('/Orders', response_class=HTMLResponse)
async def loadOrders(request: Request):
    req = requests.get('http://localhost:8002/orders')
    orders = req.json()
    return templates.TemplateResponse("orderList.html", {"orders": orders, "request": request})


@app.get('/makeOrder', response_class=HTMLResponse)
async def makeOrderPage(request: Request):
    req = requests.get('http://localhost:8001/products')
    products = req.json()
    selected_product = products.pop()
    return templates.TemplateResponse("makeOrder.html", {"products": products, "selected_product": selected_product,
                                                         "request": request})


@app.post('/oCreate', response_class=RedirectResponse, status_code=302)
async def createOrder(p_sel: str = Form(...), p_quan: int = Form(...)):
    requests.post('http://localhost:8002/orders', json={'id': p_sel, 'quantity': p_quan})
    return '/Orders'


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
