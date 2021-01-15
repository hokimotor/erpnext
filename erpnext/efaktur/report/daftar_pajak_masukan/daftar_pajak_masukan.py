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
			"width": 200
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
			"fieldname": "total_taxes_and_charges",
			"label": _("Nilai Pajak"),
			"fieldtype": "Currency",
			"width": 150
		},
	]

def prepare_data(filters):
	invoice_list = frappe.db.sql("""
		SELECT name, tanggal_faktur_pajak, posting_date, total_taxes_and_charges,
		IF(kode_dokumen="Faktur Pajak", faktur_pajak, "") as faktur_pajak
		FROM `tabPurchase Invoice`
		WHERE docstatus = 1
		AND total_taxes_and_charges IS NOT NULL AND total_taxes_and_charges != 0 
		%s
	""" % get_conditions(filters), filters, as_dict=True)

	return invoice_list

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " AND company=%(company)s"
	if filters.get("supplier"): conditions += " AND supplier = %(supplier)s"

	if filters.get("from_date"): conditions += " and tanggal_faktur_pajak >= %(from_date)s"
	if filters.get("to_date"): conditions += " and tanggal_faktur_pajak <= %(to_date)s"

	return conditions


