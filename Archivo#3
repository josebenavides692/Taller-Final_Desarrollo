
import asyncio
from typing import Optional


class InMemoryDatabase:
    def __init__(self):
        self._inventory = {
            "PROD-A99": 10,
            "PROD-B88": 2
        }
        self._orders = {}
        self._lock = asyncio.Lock()

    async def get_stock(self, product_id: str) -> int:
        async with self._lock:
            return self._inventory.get(product_id, 0)

    async def update_stock(self, product_id: str, quantity: int) -> None:
        async with self._lock:
            self._inventory[product_id] = quantity

    async def save_order(self, order_id: str, data: dict) -> None:
        async with self._lock:
            self._orders[order_id] = data

    async def process_stock_transaction(
        self,
        product_id: str,
        quantity: int
    ) -> bool:
        async with self._lock:
            current_stock = self._inventory.get(product_id, 0)

            if current_stock < quantity:
                return False

            self._inventory[product_id] = current_stock - quantity
            return True


db_instance = InMemoryDatabase()
