# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EksporBarang(Document):
	pass

@frappe.whitelist()
def get_data():
	price_list = frappe.get_doc("Selling Settings", "Selling Settings").selling_price_list

	data = [[
		"OB", "KODE_OBJEK", "NAMA", "HARGA_SATUAN"
	]]

	def ifnull(d, key, replace="-"):
		return d[key] if d[key] is not None else replace

	sql = frappe.db.sql("""
		SELECT barcode, i.name, i.item_name, price_list_rate
		FROM `tabItem` i
		JOIN `tabItem Price` p ON i.name = p.item_code AND price_list='""" + price_list + """'
		GROUP BY i.name
	""", as_dict=True)

	for d in sql:
		data.append([
			"OB", ifnull(d, "barcode", d["name"]), d["item_name"], d["price_list_rate"],
		])

	return data
