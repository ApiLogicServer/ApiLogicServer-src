from pathlib import Path

from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .models import Base, engine, get_db, Customer, Product, Order, Item
from .orders import place_order, OrderRejected

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Entry")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------- JSON API ----------

class LineItemIn(BaseModel):
    product_id: int
    quantity: int


class OrderIn(BaseModel):
    customer_id: int
    notes: str = ""
    items: list[LineItemIn]


@app.get("/api/customers")
def api_list_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "balance": c.balance,
            "credit_limit": c.credit_limit,
        }
        for c in customers
    ]


@app.get("/api/products")
def api_list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [{"id": p.id, "name": p.name, "unit_price": p.unit_price} for p in products]


@app.get("/api/orders")
def api_list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return [
        {
            "id": o.id,
            "customer_id": o.customer_id,
            "customer_name": o.customer.name,
            "notes": o.notes,
            "amount_total": o.amount_total,
            "created_on": o.CreatedOn,
        }
        for o in orders
    ]


@app.post("/api/orders")
def api_create_order(order_in: OrderIn, db: Session = Depends(get_db)):
    try:
        order = place_order(
            db,
            customer_id=order_in.customer_id,
            notes=order_in.notes,
            line_items=[li.model_dump() for li in order_in.items],
        )
    except OrderRejected as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "amount_total": order.amount_total,
        "items": [
            {
                "product_id": i.product_id,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
                "amount": i.amount,
            }
            for i in order.items
        ],
    }


# ---------- Web UI ----------

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return templates.TemplateResponse(
        request, "orders_list.html", {"orders": orders}
    )


@app.get("/orders/new")
def new_order_form(request: Request, error: str | None = None, db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.name).all()
    products = db.query(Product).order_by(Product.name).all()
    return templates.TemplateResponse(
        request,
        "order_form.html",
        {"customers": customers, "products": products, "error": error},
    )


@app.post("/orders/new")
async def create_order_from_form(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    customer_id = int(form["customer_id"])
    notes = form.get("notes", "")

    product_ids = form.getlist("product_id")
    quantities = form.getlist("quantity")

    line_items = []
    for pid, qty in zip(product_ids, quantities):
        if pid and qty and int(qty) > 0:
            line_items.append({"product_id": int(pid), "quantity": int(qty)})

    try:
        order = place_order(db, customer_id=customer_id, notes=notes, line_items=line_items)
    except OrderRejected as e:
        from urllib.parse import quote
        return RedirectResponse(url=f"/orders/new?error={quote(str(e))}", status_code=303)

    return RedirectResponse(url=f"/orders/{order.id}", status_code=303)


@app.get("/orders/{order_id}")
def order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return templates.TemplateResponse(
        request, "order_detail.html", {"order": order}
    )
