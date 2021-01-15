# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PenomoranPajak(Document):
	def validate(self):
		start = int(self.dari_nomor.split(".")[1])
		end = int(self.sampai_nomor.split(".")[1])
		if end - start < 0:
			frappe.throw("Jumlah nomor seri yang diinputkan minimal 1")

		self.total_jumlah = end - start + 1
		self.generate_serial()

	def generate_serial(self):
		if len(self.seri_faktur_pajak) != 0:
			return
		
		prefix = self.dari_nomor.split(".")[0]
		start = int(self.dari_nomor.split(".")[1])
		for i in range(self.total_jumlah):
			row = self.append('seri_faktur_pajak', {})
			row.nomor_seri = prefix + "." + str(start + i)

@frappe.whitelist()
def get_active_serial():
	return frappe.db.sql("""
		SELECT d.name
		FROM `tabSeri Faktur Pajak` d
		JOIN `tabPenomoran Pajak` h ON h.name = d.parent
		WHERE terpakai = 0 AND h.dinonaktifkan != 1
		ORDER BY d.creation ASC
	""", as_dict=True)

