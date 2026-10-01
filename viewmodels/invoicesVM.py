"""Seznam faktur. Patří k views/invoices.kv."""

from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.properties import ListProperty

from domain.documents import InvoiceDocument


class InvoicesVM(EventDispatcher):
    rows = ListProperty([])

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell

    def open_invoice(self, invoice_id: int) -> None:
        def action() -> None:
            detail = self.shell.service.get_invoice(invoice_id)
            self.shell.show_document(InvoiceDocument(detail).render())

        self.shell.guard(action)
