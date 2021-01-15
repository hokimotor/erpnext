# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	columns = get_columns()
	data = prepare_data(filters)

	return columns, data

def get_columns():
	return [
		{
			"fieldname": "name",
			"label": _("Invoice"),
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 250
		},
		{
			"fieldname": "posting_date",
			"label": _("Tanggal"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "faktur_pajak",
			"label": _("Faktur Pajak"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "tanggal_faktur_pajak",
			"label": _("Tanggal Pajak"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 200
		},
		{
			"fieldname": "total_taxes_and_charges",
			"label": _("Nilai Pajak"),
			"fieldtype": "Currency",
			"width": 150
		},
	]

def prepare_data(filters):
	invoice_list = frappe.db.sql("""
		SELECT name, tanggal_faktur_pajak, posting_date, total_taxes_and_charges, supplier,
		kode_dokumen, tipe_pajak,
		IF(kode_dokumen="Faktur Pajak", faktur_pajak, "") as faktur_pajak
		FROM `tabPurchase Invoice`
		WHERE docstatus = 1
		AND total_taxes_and_charges IS NOT NULL AND total_taxes_and_charges != 0 
		%s
	""" % get_conditions(filters), filters, as_dict=True)

	# Group berdasarkan tipe pajak, kode dokumen
	grouped_invoice = {}
	for invoice in invoice_list:
		if invoice.kode_dokumen not in grouped_invoice:
			grouped_invoice[invoice.kode_dokumen] = {}
		if invoice.tipe_pajak not in grouped_invoice[invoice.kode_dokumen]:
			grouped_invoice[invoice.kode_dokumen][invoice.tipe_pajak] = []

		grouped_invoice[invoice.kode_dokumen][invoice.tipe_pajak].append(invoice)
	
	ret = []
	for kode_dokumen in grouped_invoice:
		kode_dokumen_header = {
			"name": "<b>" + kode_dokumen + "</b>",
			"parent": "",
			"indent": 0
		}
		ret.append(kode_dokumen_header)

		total_kode_dokumen = 0
		for tipe_pajak in grouped_invoice[kode_dokumen]:
			tipe_dokumen_header = {
				"name": "<b>" + tipe_pajak + "</b>",
				"parent": kode_dokumen,
				"indent": 1
			}
			ret.append(tipe_dokumen_header)

			total_tipe_pajak = 0
			for invoice in grouped_invoice[kode_dokumen][tipe_pajak]:
				invoice["indent"] = 2
				invoice["parent"] = tipe_pajak
				total_tipe_pajak += invoice["total_taxes_and_charges"]
				ret.append(invoice)

			total_kode_dokumen += total_tipe_pajak
			tipe_dokumen_header["total_taxes_and_charges"] = total_tipe_pajak
			ret.append({
				"parent": tipe_pajak,
				"indent": 2,
				"supplier": "<b>Total " + tipe_pajak + "</b>",
				"total_taxes_and_charges": total_tipe_pajak
			})
		
		kode_dokumen_header["total_taxes_and_charges"] = total_kode_dokumen
		ret.append({
			"supplier": "<b>Total " + kode_dokumen + "</b>",
			"parent": "",
			"indent": 0,
			"total_taxes_and_charges": total_kode_dokumen
		})
		ret.append({ "parent": "", "indent": 0 })
	return ret

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " AND company=%(company)s"
	if filters.get("supplier"): conditions += " AND supplier = %(supplier)s"

	if filters.get("from_date"): conditions += " and tanggal_faktur_pajak >= %(from_date)s"
	if filters.get("to_date"): conditions += " and tanggal_faktur_pajak <= %(to_date)s"

	return conditions