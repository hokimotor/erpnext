# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class EksporSPTPPN(Document):
	def validate(self):
		self.naming_series = "PPN-" + self.tanggal_awal.rsplit('-', 1)[0] + "-"

@frappe.whitelist()
def get_data(start_date, end_date):
	ret = {"Sales Invoices": [], "Purchase Invoices": []}

	ret["Sales Invoices"] = frappe.db.sql("""
		SELECT "AR Invoice Entry" as doctype, h.name, faktur_pajak, customer, tanggal_faktur_pajak,
		tipe_pajak, kode_dokumen, h.net_total as base_net_total,
		SUM(d.tax_amount) as base_total_taxes_and_charges
		FROM `tabAR Invoice Entry` h
		JOIN `tabSales Taxes and Charges` d ON h.name = d.parent AND d.parenttype = "AR Invoice Entry" AND export_on_efaktur = 1
		WHERE kode_dokumen = 'Faktur Pajak' AND faktur_pajak like '%-%'
		AND total_taxes_and_charges IS NOT NULL AND total_taxes_and_charges != 0
		AND tanggal_faktur_pajak BETWEEN '""" + start_date + """' AND '""" + end_date + """'
		AND h.docstatus != 0
		GROUP BY h.name
	""", as_dict=True)

	ret["Sales Invoices"] += frappe.db.sql("""
		SELECT "AR Official Receipt" as doctype, h.name, faktur_pajak, customer, tanggal_faktur_pajak,
		tipe_pajak, kode_dokumen, SUM(d.allocated)/0.1 as base_net_total,
		SUM(d.allocated) as base_total_taxes_and_charges
		FROM `tabAR Official Receipt` h
		JOIN `tabAR Payment Charges` d ON h.name = d.parent AND d.parenttype = "AR Official Receipt"
			AND export_on_efaktur = 1 AND allocated IS NOT NULL AND allocated != 0
		WHERE kode_dokumen = 'Faktur Pajak' AND faktur_pajak like '%-%'
		AND tanggal_faktur_pajak BETWEEN '""" + start_date + """' AND '""" + end_date + """'
		AND h.docstatus != 0
		GROUP BY h.name
	""", as_dict=True)

	# ret["Purchase Invoices"] = frappe.db.sql("""
	# 	SELECT name, faktur_pajak, supplier, tanggal_faktur_pajak,
	# 	tipe_pajak, kode_dokumen, base_net_total, base_total_taxes_and_charges
	# 	FROM `tabPurchase Invoice`
	# 	WHERE kode_dokumen = 'Faktur Pajak'
	# 	AND faktur_pajak IS NOT NULL AND faktur_pajak != ''
	# 	AND total_taxes_and_charges IS NOT NULL AND total_taxes_and_charges != 0
	# 	AND tanggal_faktur_pajak BETWEEN '""" + start_date + """' AND '""" + end_date + """'
	# 	AND docstatus != 0
	# """, as_dict=True)

	return ret

def ifnull(d, key, replace="-"):
	return d[key] if d[key] is not None and d[key] != "" else replace

def to_fixed(d):
	return str(int(float(d)))

@frappe.whitelist()
def download_csv(name, download_type):
	doc = frappe.get_doc("Ekspor SPT PPN", name)

	if download_type == "Pajak Keluaran":
		return export_data_pajak_keluaran(doc)
	if download_type == "Retur Pajak Keluaran":
		return export_data_retur_pajak_keluaran(doc)
	if download_type == "Pajak Masukan":
		return export_data_pajak_masukan(doc)
	if download_type == "Retur Pajak Masukan":
		return export_data_retur_pajak_masukan(doc)
	if download_type == "All":
		return {
			"Pajak Keluaran": export_data_pajak_keluaran(doc),
			"Retur Pajak Keluaran": export_data_retur_pajak_keluaran(doc),
			# "Pajak Masukan": export_data_pajak_masukan(doc),
			# "Retur Pajak Masukan": export_data_retur_pajak_masukan(doc),
		}

def export_data_pajak_keluaran(doc):
	sinv_data = frappe.db.sql("""
		SELECT si.`name`, faktur_pajak, CONVERT(tanggal_faktur_pajak, char) as tanggal_faktur_pajak, npwp,
		customer, nama_wajib_pajak, alamat_pajak as address_display,
		si.net_total as base_net_total,
		SUM(d.tax_amount) as base_total_taxes_and_charges,
		no_ktp, addr.address_line1, addr.city, addr.state, addr.pincode, addr.phone
		FROM `tabAR Invoice Entry` si
		JOIN `tabSales Taxes and Charges` d ON si.name = d.parent AND d.parenttype = "AR Invoice Entry" AND export_on_efaktur = 1
		LEFT JOIN `tabAddress` addr ON addr.name = si.alamat_pajak_name
		WHERE si.is_return != 1
		AND si.name in (
			SELECT voucher_no
			FROM `tabEkspor SPT PPN Faktur`
			WHERE parentfield = "faktur_pajak_keluaran"
			AND voucher_type = "AR Invoice Entry" AND
			parent = '""" + doc.name + """'
		)
		GROUP BY si.name

		UNION

		SELECT si.`name`, faktur_pajak, CONVERT(tanggal_faktur_pajak, char) as tanggal_faktur_pajak, npwp,
		customer, nama_wajib_pajak, alamat_pajak as address_display,
		SUM(d.allocated)/0.1 as base_net_total,
		SUM(d.allocated) as base_total_taxes_and_charges,
		NULL as no_ktp, addr.address_line1, addr.city, addr.state, addr.pincode, addr.phone
		FROM `tabAR Official Receipt` si
		JOIN `tabAR Payment Charges` d ON si.name = d.parent AND d.parenttype = "AR Official Receipt"
			AND export_on_efaktur = 1 AND allocated IS NOT NULL AND allocated != 0
		LEFT JOIN `tabAddress` addr ON addr.name = si.alamat_pajak_name
		WHERE si.name in (
			SELECT voucher_no
			FROM `tabEkspor SPT PPN Faktur`
			WHERE parentfield = "faktur_pajak_keluaran"
			AND voucher_type = "AR Official Receipt" AND
			parent = '""" + doc.name + """'
		)
		GROUP BY si.name
	""", as_dict=True)

	# Buat header
	data = [
		[ # Header 1 => FK
			"FK", "KD_JNS_TRANSAKSI", "FG_PENGGANTI", "NOMOR_FAKTUR", "MASA_PAJAK", "TAHUN_PAJAK",
			"TANGGAL_FAKTUR", "NPWP", "NAMA", "ALAMAT_LENGKAP", "JUMLAH_DPP", "JUMLAH_PPN", 
			"JUMLAH_PPNBM", "ID_KETERANGAN_TAMBAHAN", "FG_UANG_MUKA", "UANG_MUKA_DPP", "UANG_MUKA_PPN",
			"UANG_MUKA_PPNBM", "REFERENSI"
		],
		[ # Header 2 => LT
			"LT", "NPWP", "NAMA", "JALAN", "BLOK", "NOMOR", "RT", "RW", "KECAMATAN",
			"KELURAHAN", "KABUPATEN", "PROVINSI", "KODE_POS", "NOMOR_TELEPON"
		],
		[ # Header 3 => OF
			"OF", "KODE_OBJEK", "NAMA", "HARGA_SATUAN", "JUMLAH_BARANG", "HARGA_TOTAL",
			"DISKON", "DPP", "PPN", "TARIF_PPNBM", "PPNBM"
		],
	]

	for inv in sinv_data:
		# items = json.loads(inv["items_json"])
		npwp_provided = ifnull(inv, "npwp", "-") != "-"

		# # Re-map item taxes
		# item_taxes = {}
		# for tax in json.loads(inv["item_tax_json"]):
		# 	for item in tax["item_wise_tax_detail"]:
		# 		if item not in item_taxes:
		# 			item_taxes[item] = {"dpp": 0, "ppn": 0}

		# 		item_taxes[item]["ppn"] += tax["item_wise_tax_detail"][item][1]
		# 		if tax["included_in_print_rate"] == 1:
		# 			item_taxes[item]["dpp"] += tax["item_wise_tax_detail"][item][1]

		# Append data invoice, Header 1
		data.append([
			"FK",
			inv.faktur_pajak[0:2], # KD_JENIS_TRANSAKSI
			inv.faktur_pajak[2], # FG_PENGGANTI
			inv.faktur_pajak[4:].replace("-", "").replace(".", ""), # NOMOR_FAKTUR
			inv.tanggal_faktur_pajak[5:7].replace("0", ""), # MASA_PAJAK
			inv.tanggal_faktur_pajak[:4], # TAHUN_PAJAK
			inv.tanggal_faktur_pajak[-2:] + "/" + inv.tanggal_faktur_pajak[5:7] + "/" + inv.tanggal_faktur_pajak[:4], # TANGGAL_FAKTUR
			ifnull(inv, "npwp", "000000000000000").replace("-", "").replace(".", ""), # NPWP
			((ifnull(inv, "no_ktp", "") + "#NIK#NAMA#") if not npwp_provided else "") + inv.customer, # NAMA
			ifnull(inv, "address_display", "").replace("<br>", " "), # ALAMAT_LENGKAP
			inv.base_net_total, # JUMLAH_DPP
			inv.base_total_taxes_and_charges, # JUMLAH_PPN
			"0", # JUMLAH_PPNBM
			"", # ID_KETERANGAN_TAMBAHAN
			"0", # FG_UANG_MUKA
			"0", # UANG_MUKA_DPP
			"0", # UANG_MUKA_PPN
			"0", # UANG_MUKA_PPNBM
			"# " + inv.name # REFERENSI
		])

		# Append data PKP jika terdapat NPWP, Header 2
		if npwp_provided:
			data.append([
				"LT",
				inv.npwp.replace("-", "").replace(".", ""), # NPWP
				ifnull(inv, "nama_wajib_pajak", inv.customer), # NAMA
				ifnull(inv, "address_line1", "-"), # JALAN
				"-", # BLOK
				"-", # NOMOR
				"0", # RT
				"0", # RW
				"-", # KECAMATAN
				"-", # KELURAHAN
				ifnull(inv, "city", "-"), # KABUPATEN
				ifnull(inv, "state", "-"), # PROVINSI
				ifnull(inv, "pincode", "-"), # KODE_POS
				ifnull(inv, "phone", "-"), # NOMOR_TELEPON
			])

		# Append data item, Header 3
		data.append([
			"OF",
			"01", # KODE_OBJEK
			"Item Harsaya", # NAMA
			inv.base_net_total, # HARGA_SATUAN
			"1", # JUMLAH_BARANG
			inv.base_net_total, # HARGA_TOTAL
			"0", # DISKON
			inv.base_net_total, # DPP
			inv.base_total_taxes_and_charges, # PPN
			"0", # TARIF_PPNBM
			"0", # PPNBM
		])
		# for item in items:
		# 	data.append([
		# 		"OF",
		# 		ifnull(item, "barcode", item["item_code"]), # KODE_OBJEK
		# 		item["item_name"], # NAMA
		# 		to_fixed(item["rate"]), # HARGA_SATUAN
		# 		to_fixed(item["qty"]), # JUMLAH_BARANG
		# 		to_fixed(item["amount"]), # HARGA_TOTAL
		# 		to_fixed(ifnull(item, "discount_amount", "0")), # DISKON
		# 		to_fixed(float(item["amount"]) - item_taxes[item["item_code"]]["dpp"]), # DPP
		# 		to_fixed(item_taxes[item["item_code"]]["ppn"]), # PPN
		# 		"0", # TARIF_PPNBM
		# 		"0", # PPNBM
		# 	])

	return data

def export_data_retur_pajak_keluaran(doc):
	sinv_data = frappe.db.sql("""
		SELECT si.`name`, faktur_pajak, CONVERT(tanggal_faktur_pajak, char) as tanggal_faktur_pajak, npwp,
		customer, nama_wajib_pajak, si.net_total as base_net_total,
		SUM(d.tax_amount) as base_total_taxes_and_charges, no_ktp, CONVERT(posting_date, char) as posting_date

		FROM `tabAR Invoice Entry` si
		JOIN `tabSales Taxes and Charges` d ON si.name = d.parent AND d.parenttype = "AR Invoice Entry" AND export_on_efaktur = 1
		WHERE si.is_return = 1
		AND si.name in (
			SELECT voucher_no
			FROM `tabEkspor SPT PPN Faktur`
			WHERE parentfield = "faktur_pajak_keluaran"
			AND voucher_type = "AR Invoice Entry" AND
			parent = '""" + doc.name + """'
		)
		GROUP BY si.name
	""", as_dict=True)

	# Buat header
	data = [
		[
			"RK", "NPWP", "NAMA", "KD_JENIS_TRANSAKSI", "FG_PENGGANTI", "NOMOR_FAKTUR",
			"TANGGAL_FAKTUR", "NOMOR_DOKUMEN_RETUR", "TANGGAL_RETUR", "MASA_PAJAK_RETUR",
			"TAHUN_PAJAK_RETUR", "NILAI_RETUR_DPP", "JUMLAH_PPN", "NILAI_RETUR_PPNBM"	
		],
	]

	for inv in sinv_data:
		npwp_provided = ifnull(inv, "npwp", "-") != "-"

		# Append data invoice
		data.append([
			"RK",
			ifnull(inv, "npwp", "000000000000000").replace("-", "").replace(".", ""), # NPWP
			((ifnull(inv, "no_ktp", "") + "#NIK#NAMA#") if not npwp_provided else "") + inv.customer, # NAMA
			inv.faktur_pajak[0:2], # KD_JENIS_TRANSAKSI
			inv.faktur_pajak[2], # FG_PENGGANTI
			inv.faktur_pajak[4:].replace("-", "").replace(".", ""), # NOMOR_FAKTUR
			inv.tanggal_faktur_pajak[-2:] + "/" + inv.tanggal_faktur_pajak[5:7] + "/" + inv.tanggal_faktur_pajak[:4], # TANGGAL_FAKTUR
			inv.name, # NOMOR DOKUMEN RETUR
			inv.posting_date[-2:] + "/" + inv.posting_date[5:7] + "/" + inv.posting_date[:4], # TANGGAL_RETUR
			inv.posting_date[5:7].replace("0", ""), # MASA_PAJAK_RETUR
			inv.posting_date[:4], # TAHUN_PAJAK_RETUR
			inv.base_net_total * -1, # NILAI_RETUR DPP
			inv.base_total_taxes_and_charges * -1, # JUMLAH_PPN
			"0", # JUMLAH_PPNBM
		])

	return data

def export_data_pajak_masukan(doc):
	sinv_data = frappe.db.sql("""
		SELECT pi.`name`, faktur_pajak, CONVERT(tanggal_faktur_pajak, char) as tanggal_faktur_pajak, npwp, is_paid, address_display,
		supplier, base_net_total, base_total_taxes_and_charges, no_ktp, CONVERT(posting_date, char) as posting_date

		FROM `tabPurchase Invoice` pi
		WHERE pi.is_return != 1
		AND pi.name in (
			SELECT voucher_no
			FROM `tabEkspor SPT PPN Faktur`
			WHERE parentfield = "faktur_pajak_masukan" AND
			parent = '""" + doc.name + """'
		)
		GROUP BY pi.name
	""", as_dict=True)

	# Buat header
	data = [
		[
			"FM", "KD_JENIS_TRANSAKSI", "FG_PENGGANTI", "NOMOR_FAKTUR", "MASA_PAJAK", "TAHUN_PAJAK",
			"TANGGAL_FAKTUR", "NPWP", "NAMA", "ALAMAT_LENGKAP", "JUMLAH_DPP", "JUMLAH_PPN", "JUMLAH_PPNBM", "IS_CREDITABLE"	
		],
	]

	for inv in sinv_data:
		npwp_provided = ifnull(inv, "npwp", "-") != "-"

		# Append data invoice
		data.append([
			"FM",
			inv.faktur_pajak[0:2], # KD_JENIS_TRANSAKSI
			inv.faktur_pajak[2], # FG_PENGGANTI
			inv.faktur_pajak[4:].replace("-", "").replace(".", ""), # NOMOR_FAKTUR
			inv.tanggal_faktur_pajak[5:7].replace("0", ""), # MASA_PAJAK
			inv.tanggal_faktur_pajak[:4], # TAHUN_PAJAK
			inv.tanggal_faktur_pajak[-2:] + "/" + inv.tanggal_faktur_pajak[5:7] + "/" + inv.tanggal_faktur_pajak[:4], # TANGGAL_FAKTUR
			ifnull(inv, "npwp", "000000000000000").replace("-", "").replace(".", ""), # NPWP
			inv.supplier, # NAMA
			ifnull(inv, "address_display", "").replace("<br>", " "), # ALAMAT_LENGKAP
			inv.base_net_total, # JUMLAH_DPP
			inv.base_total_taxes_and_charges, # JUMLAH_PPN
			"0", # JUMLAH_PPNBM
			("0" if inv.is_paid == 1 else "1"), # IS_CREDITABLE
		])

	return data

def export_data_retur_pajak_masukan(doc):
	sinv_data = frappe.db.sql("""
		SELECT pi.`name`, faktur_pajak, CONVERT(tanggal_faktur_pajak, char) as tanggal_faktur_pajak, npwp, is_paid, address_display,
		supplier, base_net_total, base_total_taxes_and_charges, no_ktp, CONVERT(posting_date, char) as posting_date

		FROM `tabPurchase Invoice` pi
		WHERE pi.is_return = 1
		AND pi.name in (
			SELECT voucher_no
			FROM `tabEkspor SPT PPN Faktur`
			WHERE parentfield = "faktur_pajak_masukan" AND
			parent = '""" + doc.name + """'
		)
		GROUP BY pi.name
	""", as_dict=True)

	# Buat header
	data = [
		[
			"RM", "NPWP", "NAMA", "KD_JENIS_TRANSAKSI", "FG_PENGGANTI", "NOMOR_FAKTUR", "TANGGAL_FAKTUR", "IS_CREDITABLE", 
			"NOMOR_DOKUMEN_RETUR", "TANGGAL_RETUR", "MASA_PAJAK", "TAHUN_PAJAK", "NILAI_RETUR_DPP", "NILAI_RETUR_PPN", "NILAI_RETUR_PPNBM", 
		],
	]

	for inv in sinv_data:
		npwp_provided = ifnull(inv, "npwp", "-") != "-"

		# Append data invoice
		data.append([
			"RM",
			ifnull(inv, "npwp", "000000000000000").replace("-", "").replace(".", ""), # NPWP
			inv.supplier, # NAMA
			inv.faktur_pajak[0:2], # KD_JENIS_TRANSAKSI
			inv.faktur_pajak[2], # FG_PENGGANTI
			inv.faktur_pajak[4:].replace("-", "").replace(".", ""), # NOMOR_FAKTUR
			inv.tanggal_faktur_pajak[-2:] + "/" + inv.tanggal_faktur_pajak[5:7] + "/" + inv.tanggal_faktur_pajak[:4], # TANGGAL_FAKTUR
			("0" if inv.is_paid == 1 else "1"), # IS_CREDITABLE
			inv.name, # NOMOR DOKUMEN RETUR
			inv.posting_date[-2:] + "/" + inv.posting_date[5:7] + "/" + inv.posting_date[:4], # TANGGAL_RETUR
			inv.posting_date[5:7].replace("0", ""), # MASA_PAJAK_RETUR
			inv.posting_date[:4], # TAHUN_PAJAK_RETUR
			inv.base_net_total * -1, # NILAI_RETUR DPP
			inv.base_total_taxes_and_charges * -1, # JUMLAH_PPN
			"0", # JUMLAH_PPNBM
		])

	return data