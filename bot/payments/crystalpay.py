from bot.payments.crystalpay_sdk import CrystalPAY, InvoiceType
from bot.config import TOKENS_DATA
crystalpayAPI = CrystalPAY(TOKENS_DATA["crystal_login"], TOKENS_DATA["crystal_secret_1"], TOKENS_DATA["crystal_secret_2"])

async def create_invoice(amount: int, lifetime: int = 30, description: str = None):
    """
    Create an invoice using CrystalPAY API.
    
    :param amount: Amount in kopecks
    :param description: Description of the payment
    :param order_id: Unique identifier for the order
    :return: Invoice URL
    """
    try:
        invoice = crystalpayAPI.Invoice.create(
            amount = amount,
            type_ = InvoiceType.purchase,
            lifetime = lifetime,
            description = description
        )
        return invoice
    except Exception as e:
        print(f"Error creating invoice: {e}")
        return None
    
async def check_invoice_status(invoice_id: str):
    """
    Check the status of an invoice using CrystalPAY API.
    
    :param invoice_id: Unique identifier for the invoice
    :return: Status of the invoice
    """
    try:
        status = crystalpayAPI.Invoice.getinfo(invoice_id)
        return status
    except Exception as e:
        print(f"Error checking invoice status: {e}")
        return None
    



