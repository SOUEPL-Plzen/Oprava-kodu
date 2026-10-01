"""Kořenový viewmodel okna. Patří k views/shell.kv."""

from __future__ import annotations

import traceback
from decimal import Decimal

from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty

from domain.errors import AppError
from viewmodels.base import ViewModel
from viewmodels.companyVM import CompanyVM
from viewmodels.issueVM import IssueVM
from viewmodels.invoicesVM import InvoicesVM
from viewmodels.productsVM import ProductsVM
from viewmodels.receiptVM import ReceiptVM
from viewmodels.transferVM import TransferVM
from viewmodels.warehousesVM import WarehousesVM


class ShellVM(ViewModel):
    screen = StringProperty("prehled")
    detail_text = StringProperty("")
    detail_token = NumericProperty(0)
    stock = ListProperty([])
    movements = ListProperty([])
    warehouse_choices = ListProperty([])
    product_choices = ListProperty([])
    warehouses_vm = ObjectProperty(None, allownone=True)
    products_vm = ObjectProperty(None, allownone=True)
    receipt_vm = ObjectProperty(None, allownone=True)
    transfer_vm = ObjectProperty(None, allownone=True)
    issue_vm = ObjectProperty(None, allownone=True)
    invoices_vm = ObjectProperty(None, allownone=True)
    company_vm = ObjectProperty(None, allownone=True)

    def __init__(self, service) -> None:
        super().__init__()
        self.service = service
        self.stock_index: dict = {}
        self.warehouses_vm = WarehousesVM(self)
        self.products_vm = ProductsVM(self)
        self.receipt_vm = ReceiptVM(self)
        self.transfer_vm = TransferVM(self)
        self.issue_vm = IssueVM(self)
        self.invoices_vm = InvoicesVM(self)
        self.company_vm = CompanyVM(self)
        self.warehouses_vm.bind(rows=self._sync_choices)
        self.products_vm.bind(rows=self._sync_choices)
        self.bind(stock=self._refresh_availability)
        self.transfer_vm.bind(tr_product=self._refresh_availability, tr_from=self._refresh_availability)
        self.issue_vm.bind(line_warehouse=self._refresh_availability)
        self.reload_lists()
        self.company_vm.load()

    def navigate(self, screen: str) -> None:
        try:
            self.reload_lists()
        except Exception as exc:
            traceback.print_exc()
            self.message_is_error = True
            self.message = f"Neočekávaná chyba: {exc}"
            return
        self.screen = screen
        self.message = ""

    def reload_lists(self) -> None:
        self.warehouses_vm.rows = [row.as_table() for row in self.service.list_warehouses()]
        self.products_vm.rows = [row.as_table() for row in self.service.list_products()]
        stock_rows = self.service.list_stock()
        self.stock_index = {(row.product_id, row.warehouse_id): row for row in stock_rows}
        self.stock = [row.as_table() for row in stock_rows if row.quantity != 0]
        self.invoices_vm.rows = [row.as_table() for row in self.service.list_invoices()]
        self.movements = [row.as_table() for row in self.service.list_movements()]

    def show_document(self, text: str) -> None:
        self.detail_text = text
        self.detail_token += 1

    def find_product(self, product_id: int) -> dict | None:
        for product in self.products_vm.rows:
            if product["id"] == product_id:
                return product
        return None

    def find_warehouse(self, warehouse_id: int) -> dict:
        for warehouse in self.warehouses_vm.rows:
            if warehouse["id"] == warehouse_id:
                return warehouse
        raise AppError("Vyberte sklad.")

    def available_qty(self, product_id: int, warehouse_id: int) -> Decimal:
        row = self.stock_index.get((product_id, warehouse_id))
        if row is None:
            return Decimal(0)
        return row.quantity

    def _sync_choices(self, *_args) -> None:
        self.product_choices = [f"#{row['id']}  {row['sku']} — {row['name']}" for row in self.products_vm.rows]
        self.warehouse_choices = [f"#{row['id']}  {row['code']} — {row['name']}" for row in self.warehouses_vm.rows]

    def _refresh_availability(self, *_args) -> None:
        self.transfer_vm.refresh_available()
        self.issue_vm.refresh_available()
