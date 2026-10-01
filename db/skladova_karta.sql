-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Počítač: localhost:8889
-- Vytvořeno: Čtv 01. říj 2026, 06:24
-- Verze serveru: 8.0.44
-- Verze PHP: 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Databáze: `skladova_karta`
--

-- --------------------------------------------------------

--
-- Struktura tabulky `company_settings`
--

CREATE TABLE `company_settings` (
  `id` int NOT NULL,
  `company_name` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `ico` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `dic` varchar(20) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `street` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `city` varchar(128) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `zip_code` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `country` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `email` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `phone` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `bank_account` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `bank_code` varchar(8) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `iban` varchar(42) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

--
-- Vypisuji data pro tabulku `company_settings`
--

INSERT INTO `company_settings` (`id`, `company_name`, `ico`, `dic`, `street`, `city`, `zip_code`, `country`, `email`, `phone`, `bank_account`, `bank_code`, `iban`) VALUES
(1, '', '', '', '', '', '', 'Česká republika', '', '', '', '', '');

-- --------------------------------------------------------

--
-- Struktura tabulky `invoices`
--

CREATE TABLE `invoices` (
  `id` int NOT NULL,
  `invoice_number` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL,
  `issued_on` date NOT NULL,
  `taxable_on` date NOT NULL,
  `due_on` date NOT NULL,
  `payment_method` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL,
  `variable_symbol` varchar(10) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `note` varchar(2000) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `party_id` int NOT NULL,
  `total_net` decimal(14,2) NOT NULL,
  `total_vat` decimal(14,2) NOT NULL,
  `total_gross` decimal(14,2) NOT NULL,
  `supplier_name` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL,
  `supplier_ico` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_dic` varchar(20) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_street` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_city` varchar(128) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_zip` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_country` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_email` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_phone` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_account` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_bank` varchar(8) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `supplier_iban` varchar(42) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- --------------------------------------------------------

--
-- Struktura tabulky `invoice_lines`
--

CREATE TABLE `invoice_lines` (
  `id` int NOT NULL,
  `invoice_id` int NOT NULL,
  `product_id` int NOT NULL,
  `warehouse_id` int NOT NULL,
  `item_name` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL,
  `sku` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL,
  `unit` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL,
  `warehouse_code` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL,
  `quantity` decimal(12,3) NOT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `vat_rate` decimal(5,2) NOT NULL,
  `line_net` decimal(14,2) NOT NULL,
  `line_vat` decimal(14,2) NOT NULL,
  `line_gross` decimal(14,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- --------------------------------------------------------

--
-- Struktura tabulky `movements`
--

CREATE TABLE `movements` (
  `id` int NOT NULL,
  `kind` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL,
  `product_id` int NOT NULL,
  `warehouse_id` int NOT NULL,
  `quantity` decimal(12,3) NOT NULL,
  `related_warehouse_id` int DEFAULT NULL,
  `invoice_id` int DEFAULT NULL,
  `note` varchar(512) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- --------------------------------------------------------

--
-- Struktura tabulky `parties`
--

CREATE TABLE `parties` (
  `id` int NOT NULL,
  `kind` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL,
  `first_name` varchar(128) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `last_name` varchar(128) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `company_name` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `ico` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `dic` varchar(20) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `street` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `city` varchar(128) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `zip_code` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `country` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `email` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `phone` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- --------------------------------------------------------

--
-- Struktura tabulky `products`
--

CREATE TABLE `products` (
  `id` int NOT NULL,
  `sku` varchar(64) COLLATE utf8mb4_czech_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL,
  `unit` varchar(16) COLLATE utf8mb4_czech_ci NOT NULL,
  `unit_price` decimal(12,2) NOT NULL,
  `vat_rate` decimal(5,2) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

-- --------------------------------------------------------

--
-- Struktura tabulky `stock`
--

CREATE TABLE `stock` (
  `id` int NOT NULL,
  `product_id` int NOT NULL,
  `warehouse_id` int NOT NULL,
  `quantity` decimal(12,3) NOT NULL DEFAULT '0.000'
) ;

-- --------------------------------------------------------

--
-- Struktura tabulky `warehouses`
--

CREATE TABLE `warehouses` (
  `id` int NOT NULL,
  `code` varchar(32) COLLATE utf8mb4_czech_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_czech_ci NOT NULL,
  `address` varchar(512) COLLATE utf8mb4_czech_ci NOT NULL DEFAULT '',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_czech_ci;

--
-- Indexy pro exportované tabulky
--

--
-- Indexy pro tabulku `company_settings`
--
ALTER TABLE `company_settings`
  ADD PRIMARY KEY (`id`);

--
-- Indexy pro tabulku `invoices`
--
ALTER TABLE `invoices`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_invoices_number` (`invoice_number`),
  ADD KEY `fk_invoices_party` (`party_id`);

--
-- Indexy pro tabulku `invoice_lines`
--
ALTER TABLE `invoice_lines`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_lines_invoice` (`invoice_id`),
  ADD KEY `fk_lines_product` (`product_id`),
  ADD KEY `fk_lines_warehouse` (`warehouse_id`);

--
-- Indexy pro tabulku `movements`
--
ALTER TABLE `movements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_mov_product` (`product_id`),
  ADD KEY `fk_mov_warehouse` (`warehouse_id`),
  ADD KEY `fk_mov_related` (`related_warehouse_id`),
  ADD KEY `fk_mov_invoice` (`invoice_id`);

--
-- Indexy pro tabulku `parties`
--
ALTER TABLE `parties`
  ADD PRIMARY KEY (`id`);

--
-- Indexy pro tabulku `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_products_sku` (`sku`);

--
-- Indexy pro tabulku `stock`
--
ALTER TABLE `stock`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_stock_item` (`product_id`,`warehouse_id`),
  ADD KEY `fk_stock_warehouse` (`warehouse_id`);

--
-- Indexy pro tabulku `warehouses`
--
ALTER TABLE `warehouses`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_warehouses_code` (`code`);

--
-- AUTO_INCREMENT pro tabulky
--

--
-- AUTO_INCREMENT pro tabulku `invoices`
--
ALTER TABLE `invoices`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pro tabulku `invoice_lines`
--
ALTER TABLE `invoice_lines`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pro tabulku `movements`
--
ALTER TABLE `movements`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pro tabulku `parties`
--
ALTER TABLE `parties`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pro tabulku `products`
--
ALTER TABLE `products`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pro tabulku `stock`
--
ALTER TABLE `stock`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pro tabulku `warehouses`
--
ALTER TABLE `warehouses`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Omezení pro exportované tabulky
--

--
-- Omezení pro tabulku `invoices`
--
ALTER TABLE `invoices`
  ADD CONSTRAINT `fk_invoices_party` FOREIGN KEY (`party_id`) REFERENCES `parties` (`id`);

--
-- Omezení pro tabulku `invoice_lines`
--
ALTER TABLE `invoice_lines`
  ADD CONSTRAINT `fk_lines_invoice` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  ADD CONSTRAINT `fk_lines_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `fk_lines_warehouse` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`);

--
-- Omezení pro tabulku `movements`
--
ALTER TABLE `movements`
  ADD CONSTRAINT `fk_mov_invoice` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  ADD CONSTRAINT `fk_mov_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `fk_mov_related` FOREIGN KEY (`related_warehouse_id`) REFERENCES `warehouses` (`id`),
  ADD CONSTRAINT `fk_mov_warehouse` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`);

--
-- Omezení pro tabulku `stock`
--
ALTER TABLE `stock`
  ADD CONSTRAINT `fk_stock_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `fk_stock_warehouse` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
