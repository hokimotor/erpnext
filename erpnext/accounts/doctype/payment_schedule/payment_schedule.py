# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from hansaya.hansaya.party import get_party_details
import frappe


class PaymentSchedule(Document):
	def before_insert(self):
		pass


@frappe.whitelist()
def make_invoice(dt, dn):
	doc = frappe.get_doc(dt, dn)
	reservation_doc = frappe.get_doc(doc.parenttype, doc.parent)
	company = frappe.get_doc("Company", reservation_doc.company)
	trx_type = frappe.get_doc("Transaction Type", doc.transaction_type)

	deferred_revenue_account = company.default_deferred_revenue_account
	if trx_type.get("accounts") and len(trx_type.accounts):
		for d in trx_type.accounts:
			if d.get("is_credit") == 1:
				deferred_revenue_account = d.account

	if reservation_doc.docstatus != 1:
		frappe.throw("Document <b>" + doc.parenttype + " " + doc.parent + "</b> is not yet submitted")


	inv = frappe.new_doc("AR Invoice Entry")
	inv.transaction_type = doc.transaction_type
	inv.company = reservation_doc.company
	inv.posting_date = frappe.utils.today()
	inv.base_reservation_doc = reservation_doc.base_reservation_doc
	
	inv.customer = reservation_doc.customer
	inv.due_date = doc.due_date
	inv.debit_to = company.default_receivable_account
	inv.payment_schedule = doc.name

	# inv.nama_wajib_pajak = party_detail.get("nama_wajib_pajak")
	# inv.npwp = party_detail.get("npwp")
	# inv.no_ktp = party_detail.get("no_ktp")

	inv.append("accounts", {
		'account': deferred_revenue_account,
		'amount': doc.net_payment_amount
	})

	inv.taxes_and_charges = doc.get("tax_template")
	inv.ref_no = reservation_doc.name
	inv.bill_no = doc.name

	inv.reservation_payment_term = doc.payment_term
	inv.remarks = doc.payment_term #+ "\n\nGenerated from Reservation Entry " + reservation_doc.name + " Payment Schedule " + doc.name

	# inv.save()
	# inv.submit()
	# frappe.db.commit()
	
	return inv
