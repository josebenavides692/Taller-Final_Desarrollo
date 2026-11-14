
import math
import asyncio
from concurrent.futures import ProcessPoolExecutor


def calculate_manifest_hash(iterations: int) -> float:
    result = 0.0

    for i in range(iterations):
        result += math.sqrt(i) * math.sin(i)

    return result


class InvoiceGenerator:
    def __init__(self, max_workers: int = 2):
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    async def generate_pdf_manifest(self, order_id: str, amount: float) -> bytes:
        iterations = 5_000_000
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(self.executor, calculate_manifest_hash, iterations)

        manifest_data = (f"ORDER:{order_id}|TOTAL:{amount}|HASH:{result}")

        return manifest_data.encode("utf-8")

    def shutdown(self):
        self.executor.shutdown(wait=True)
