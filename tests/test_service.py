"""Ověření skladu, přesunu a faktury proti testovací databázi."""

from __future__ import annotations

import unittest
from datetime import date, timedelta
from decimal import Decimal

from config import DB_CONFIG
from domain.database import Database
from domain.documents import InvoiceDocument
from domain.entities import Company, InvoiceHeader, InvoiceLineInput, PartyInput
from domain.errors import StockError, ValidationError
from domain.inventory_service import InventoryService
from domain.money import VatBreakdown
from domain.validation import Ico


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = dict(DB_CONFIG)
        config["database"] = "skladova_karta_test"
        cls.database = Database(config)
        cls.database.initialize()
        cls.database.initialize()
        cls.service = InventoryService(cls.database)

    def setUp(self) -> None:
        self.database.reset_data()

    def test_ico_checksum(self) -> None:
        self.assertTrue(Ico("27082440").is_valid())
        self.assertFalse(Ico("27082441").is_valid())

    def test_vat_rounding(self) -> None:
        breakdown = VatBreakdown.from_line(Decimal("1"), Decimal("10.10"), Decimal("21"))
        self.assertEqual(breakdown.net.amount, Decimal("10.10"))
        self.assertEqual(breakdown.vat.amount, Decimal("2.12"))
        self.assertEqual(breakdown.gross.amount, Decimal("12.22"))

    def test_warehouse_product_and_duplicate(self) -> None:
        self.service.add_warehouse("hlavni", "Hlavní sklad", "Dlouhá 1, Praha")
        self.service.add_product("sroub-8", "Šroub M8", "ks", Decimal("12.50"), Decimal("21"))
        warehouses = self.service.list_warehouses()
        products = self.service.list_products()
        self.assertEqual(warehouses[0].code, "HLAVNI")
        self.assertEqual(products[0].sku, "SROUB-8")
        self.assertEqual(products[0].name, "Šroub M8")
        with self.assertRaises(ValidationError):
            self.service.add_warehouse("HLAVNI", "Jiný", "")

    def test_receive_transfer_and_stock_guard(self) -> None:
        self.service.add_warehouse("A", "Sklad A", "")
        self.service.add_warehouse("B", "Sklad B", "")
        self.service.add_product("KABEL", "Kabel", "m", Decimal("20"), Decimal("21"))
        product = self.service.list_products()[0].id
        warehouses = {row.code: row.id for row in self.service.list_warehouses()}
        self.service.receive(product, warehouses["A"], Decimal("10"), "dodací list 1")
        self.service.transfer(product, warehouses["A"], warehouses["B"], Decimal("4"), "")
        stock = {(row.warehouse_code, row.quantity) for row in self.service.list_stock()}
        self.assertIn(("A", Decimal("6.000")), stock)
        self.assertIn(("B", Decimal("4.000")), stock)
        with self.assertRaises(StockError):
            self.service.transfer(product, warehouses["A"], warehouses["B"], Decimal("7"), "")
        again = {row.warehouse_code: row.quantity for row in self.service.list_stock()}
        self.assertEqual(again["A"], Decimal("6.000"))
        with self.assertRaises(ValidationError):
            self.service.transfer(product, warehouses["A"], warehouses["A"], Decimal("1"), "")

    def test_invoice_for_person_and_company(self) -> None:
        self._supplier()
        self.service.add_warehouse("EXP", "Expedice", "Výdejní 5")
        self.service.add_product("DESKA", "Dubová deska", "ks", Decimal("100"), Decimal("21"))
        product = self.service.list_products()[0]
        warehouse = self.service.list_warehouses()[0]
        self.service.receive(product.id, warehouse.id, Decimal("5"), "")
        today = date.today()
        detail = self.service.issue_invoice(
            PartyInput(
                kind="fyzicka",
                first_name="Jan",
                last_name="Novák",
                street="Polní 12",
                city="Brno",
                zip_code="60200",
                email="jan@example.com",
            ),
            InvoiceHeader(today, today, today + timedelta(days=14), "bankovní převod", "", "Děkujeme."),
            [InvoiceLineInput(product.id, warehouse.id, Decimal("2"), Decimal("100"))],
        )
        self.assertEqual(detail.invoice_number, f"FA-{today.year}-0001")
        self.assertEqual(detail.total_gross, Decimal("242.00"))
        self.assertEqual(detail.buyer.zip_code, "602 00")
        rendered = InvoiceDocument(detail).render()
        self.assertIn("Jan Novák", rendered)
        self.assertIn("Fyzická osoba", rendered)
        left = {row.warehouse_code: row.quantity for row in self.service.list_stock()}
        self.assertEqual(left["EXP"], Decimal("3.000"))

        legal = self.service.issue_invoice(
            PartyInput(
                kind="pravnicka",
                company_name="Alza.cz a.s.",
                ico="27082440",
                dic="CZ27082440",
                first_name="Eva",
                last_name="Malá",
                street="Jankovcova 1522/53",
                city="Praha",
                zip_code="170 00",
            ),
            InvoiceHeader(today, today, today, "hotovost", "123456", ""),
            [InvoiceLineInput(product.id, warehouse.id, Decimal("1"), Decimal("100"))],
        )
        self.assertEqual(legal.invoice_number, f"FA-{today.year}-0002")
        self.assertEqual(legal.variable_symbol, "123456")
        legal_text = InvoiceDocument(legal).render()
        self.assertIn("Právnická osoba", legal_text)
        self.assertIn("Kontaktní osoba: Eva Malá", legal_text)
        self.assertEqual(len(self.service.list_invoices()), 2)

    def test_invoice_rejects_bad_buyer_and_empty_stock(self) -> None:
        self._supplier()
        self.service.add_warehouse("EXP", "Expedice", "")
        self.service.add_product("DESKA", "Deska", "ks", Decimal("10"), Decimal("21"))
        product = self.service.list_products()[0].id
        warehouse = self.service.list_warehouses()[0].id
        self.service.receive(product, warehouse, Decimal("1"), "")
        today = date.today()
        header = InvoiceHeader(today, today, today, "bankovní převod", "", "")
        with self.assertRaises(ValidationError):
            self.service.issue_invoice(
                PartyInput(kind="pravnicka", company_name="Špatná", ico="27082441", street="A", city="B", zip_code="11000"),
                header,
                [InvoiceLineInput(product, warehouse, Decimal("1"), Decimal("10"))],
            )
        with self.assertRaises(StockError):
            self.service.issue_invoice(
                PartyInput(kind="fyzicka", first_name="A", last_name="B", street="A", city="B", zip_code="11000"),
                header,
                [InvoiceLineInput(product, warehouse, Decimal("2"), Decimal("10"))],
            )
        left = self.service.list_stock()[0].quantity
        self.assertEqual(left, Decimal("1.000"))

    def _supplier(self) -> None:
        self.service.save_company(
            Company(
                company_name="Pila Řeřicha s.r.o.",
                ico="27082440",
                dic="CZ27082440",
                street="Skladová 9",
                city="Praha",
                zip_code="11000",
                country="Česká republika",
                email="faktury@rericcha.cz",
                phone="777111222",
                bank_account="123456789",
                bank_code="0100",
                iban="CZ6501000000001234567899",
            )
        )


if __name__ == "__main__":
    unittest.main()
