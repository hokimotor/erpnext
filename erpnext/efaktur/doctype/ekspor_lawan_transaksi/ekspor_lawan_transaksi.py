# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from frappe.model.document import Document

class EksporLawanTransaksi(Document):
	pass

@frappe.whitelist()
def get_data(customer, supplier):
	data = [[
		"LT", "NPWP", "NAMA", "JALAN", "BLOK", "NOMOR",
		"RT", "RW", "KECAMATAN", "KELURUHAN", "KABUPATEN",
		"PROVINSI", "KODE_POS", "NOMOR_TELEPON"
	]]

	def ifnull(d, key, replace="-"):
		return d[key] if d[key] is not None else replace

	if customer == "1":
		sql = frappe.db.sql("""
			SELECT npwp, customer_name, address_line1,
				city, state, pincode, phone
			FROM `tabCustomer` c
			LEFT JOIN `tabAddress` a ON c.alamat_pajak = a.name
			WHERE npwp IS NOT NULL AND npwp != ""
		""", as_dict=True)

		for d in sql:
			data.append([
				"LT", ifnull(d, "npwp", "000000000000000").replace(".", "").replace("-", "")
				, d["customer_name"], ifnull(d, "address_line1"),
				"-", "-", "-", "-", "-", "-",
				ifnull(d, "city"), ifnull(d, "state"), ifnull(d, "pincode"), ifnull(d, "phone")
			])

	if supplier == "1":
		
		sql = frappe.db.sql("""
			SELECT npwp, supplier_name, address_line1,
				city, state, pincode, phone
			FROM `tabSupplier` c
			LEFT JOIN `tabAddress` a ON c.alamat_pajak = a.name
			WHERE npwp IS NOT NULL AND npwp != ""
		""", as_dict=True)
		
		for d in sql:
			data.append([
				"LT", ifnull(d, "npwp", "000000000000000").replace(".", "").replace("-", "")
				, d["supplier_name"], ifnull(d, "address_line1"),
				"-", "-", "-", "-", "-", "-",
				ifnull(d, "city"), ifnull(d, "state"), ifnull(d, "pincode"), ifnull(d, "phone")
			])

	return data
