# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.file_manager import get_uploaded_content, save_file
import re

class ImporPDFFakturPajak(Document):
	pass

@frappe.whitelist()
def upload():
	fname, fcontent = get_uploaded_content()
	err = {}

	regex_pattern = r"^\d{15}-\d{16}-\d{15}-\d{14}\.pdf$"
	regex_test = re.compile(regex_pattern)

	# Validasi file
	if fname[-4:] != ".pdf": # Bukan PDF
		err["message"] = "Format dokumen harus PDF"
	elif regex_test.match(fname) is None: # Pattern tidak sesuai
		err["message"] = "Format nama file tidak sesuai"
	else:
		no_faktur = fname.split("-")[1]

		# Validasi no faktur
 		invoice_name = frappe.db.sql("""
			SELECT name
			FROM `tabSales Invoice`
			WHERE docstatus = 1 AND workflow_state = "Submitted"
			AND kode_dokumen = "Faktur Pajak"
			AND REPLACE(REPLACE(faktur_pajak , "-", ""), ".", "") = '""" + no_faktur + """'
		""", as_dict=True)

		if len(invoice_name) == 0:
			err["message"] = "Invoice dengan nomor faktur " + no_faktur + " tidak ditemukan"
		else:
			invoice_name = invoice_name[0]["name"]

	
	if "message" not in err:
		file_doc = save_file(fname, fcontent, "Sales Invoice", invoice_name, is_private=1)

		# sales_doc = frappe.get_doc("Sales Invoice", invoice_name)
		# sales_doc.file_faktur_pajak = file_doc.file_url
		# sales_doc.save()

		frappe.db.sql("""
			UPDATE `tabSales Invoice`
			SET file_faktur_pajak = '""" + file_doc.file_url + """'
			WHERE name = '""" + invoice_name + """'
		""")
		frappe.db.commit()

		return {"message": {
			"filename": fname,
			"message": "Berhasil attach ke dokumen Sales Invoice <a href='#Form/Sales%20Invoice/" + invoice_name + "'>" + invoice_name + "</a>"
		}}
	else:
		err["filename"] = fname
		return {"error": err}
	
	# frappe.errprint("Fname : " + str(fname))
