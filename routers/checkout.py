
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from database.session_manager import TransactionManager
from services.payment_service import StripePaymentGateway
from services.document_service import InvoiceGenerator
from services.notification_core import NotificationDispatcher

router = APIRouter()

class CheckoutRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    payment_token: str
    user_email: str
    notify_via: list[str]

def get_transaction_manager():
    return TransactionManager()

def get_payment_gateway():
    return StripePaymentGateway()

def get_invoice_generator():
    return InvoiceGenerator()

def get_notification_dispatcher():
    return NotificationDispatcher()

@router.post("/process")
async def process_checkout(
    payload: CheckoutRequest,
    tx_manager: TransactionManager = Depends(get_transaction_manager),
    payment_gateway: StripePaymentGateway = Depends(get_payment_gateway),
    invoice_service: InvoiceGenerator = Depends(get_invoice_generator),
    notifier: NotificationDispatcher = Depends(get_notification_dispatcher)
):
    transaction_completed = False

    try:
        if not await tx_manager.begin_transaction(
            payload.product_id,
            payload.quantity
        ):
            raise HTTPException(
                status_code=400,
                detail="Stock insuficiente o error de base de datos"
            )

        transaction_completed = True

        total_amount = payload.quantity * 99.99

        payment_success = await payment_gateway.execute_charge(
            payload.payment_token,
            total_amount
        )

        if not payment_success:
            await tx_manager.rollback_transaction(
                payload.product_id,
                payload.quantity
            )
            transaction_completed = False

            raise HTTPException(
                status_code=402,
                detail="Pago rechazado por la pasarela"
            )

        order_id = f"TX-{payload.product_id}-12345"

        await invoice_service.generate_pdf_manifest(
            order_id,
            total_amount
        )

        await notifier.send_alerts(
            payload.notify_via,
            payload.user_email,
            "Su orden ha sido procesada"
        )

        return {
            "status": "success",
            "order_id": order_id
        }

    except HTTPException:
        raise

    except Exception as error:
        if transaction_completed:
            await tx_manager.rollback_transaction(
                payload.product_id,
                payload.quantity
            )

        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar la compra"
        ) from error
