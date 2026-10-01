"""Načte všechny tabulky, aby se zaregistrovaly do ORM mapování."""

from models.data.base import Entity, Record
from models.data.company_profile import CompanyProfile
from models.data.invoice import Invoice
from models.data.invoice_line import InvoiceLine
from models.data.party import LegalEntity, NaturalPerson, Party
from models.data.product import Product
from models.data.stock_item import StockItem
from models.data.stock_movement import InvoiceIssue, Receipt, StockMovement, TransferIn, TransferOut
from models.data.warehouse import Warehouse

__all__ = [
    "CompanyProfile",
    "Entity",
    "Invoice",
    "InvoiceIssue",
    "InvoiceLine",
    "LegalEntity",
    "NaturalPerson",
    "Party",
    "Product",
    "Receipt",
    "Record",
    "StockItem",
    "StockMovement",
    "TransferIn",
    "TransferOut",
    "Warehouse",
]
