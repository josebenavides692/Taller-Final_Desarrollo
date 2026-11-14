
from database.connection import db_instance

class TransactionManager:
    def __init__(self, db=None):
        self.db = db if db is not None else db_instance

    async def begin_transaction(
        self,
        product_id: str,
        quantity: int
    ) -> bool:
        if quantity <= 0:
            return False

        return await self.db.process_stock_transaction(
            product_id,
            quantity
        )

    async def rollback_transaction(
        self,
        product_id: str,
        quantity: int
    ) -> None:
        if quantity <= 0:
            return

        async with self.db._lock:
            current_stock = self.db._inventory.get(product_id, 0)

            self.db._inventory[product_id] = (
                current_stock + quantity
            )
