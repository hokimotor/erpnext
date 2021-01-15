# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SeriFakturPajak(Document):
	pass

@frappe.whitelist()
def unlink(name):
	sfp = frappe.get_doc("Seri Faktur Pajak", name)

	# Cek, status dokumen tidak boleh submitted
	ref_doc = frappe.get_doc(sfp.voucher_type, sfp.voucher_no)
	if ref_doc.docstatus == 1:
		frappe.throw("Can't unlink from submitted document. Please cancel first")

	frappe.db.sql("""
		UPDATE `tab""" + sfp.voucher_type + """`
		SET kode_dokumen = NULL
		WHERE name = '""" + sfp.voucher_no + """'
	""")

	sfp.voucher_type = ""
	sfp.voucher_no = ""
	sfp.terpakai = 0
	sfp.save()
