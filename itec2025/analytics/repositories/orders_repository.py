"""
aisla el acceso a la db, y devuelve una estructura lista para pandas, y no hay business logic
"""

import pandas as pd

from products.models import Order, OrderDetail, Product, Category

def fetch_orders_dataframe() -> pd.DataFrame:
    """
    carga ordenes con sus detalles a un dataframe
    returns:
        dataframe con columnas: order_id, date, product, category,
        price, quantity, total
    """

    qs= (OrderDetail.objects.select_related
         ('order', 'product', 'product__category')
         .values(
            "order_id",
            "order__date",
            "product__name",
            "product__price",
            "product__category__name",
            "quantity"
            )
         )
    
    rows = list(qs)

    if not rows:
        return pd.DataFrame(
            columns=[
                "order_id",
                "date",
                "product",
                "category",
                "price",
                "quantity",
                "total"   
            ]
        )
    
    df = pd.DataFrame(rows)#genera el dataframe a partir de una lista de objetos
    df = df.rename(
        #renombra columnas
        columns={
            "order__date":"date",
            "product__name":"product",
            "product__price":"price",
            "product__category__name":"category"
        }
    )

    df["total"] = df["price"] * df["quantity"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return(df)