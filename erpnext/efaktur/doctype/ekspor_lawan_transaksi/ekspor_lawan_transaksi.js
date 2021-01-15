// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ekspor Lawan Transaksi', {
	onload: function(frm){
		cur_frm.set_value("supplier", 1);
		cur_frm.set_value("customer", 1);
	},

	refresh: function(frm) {
		cur_frm.$wrapper.find(".page-actions .primary-action").remove()
		cur_frm.$wrapper.find(".page-title .indicator").remove()
		
		cur_frm.fields_dict.download_csv.$input.addClass("btn-md btn-success").removeClass("btn-xs");
	},

	download_csv: function(){
		frappe.dom.freeze();
		frappe.call({
			"method": "erpnext.efaktur.doctype.ekspor_lawan_transaksi.ekspor_lawan_transaksi.get_data",
			"args": {
				"customer": cur_frm.doc.customer || 0,
				"supplier": cur_frm.doc.supplier || 0,
			},
			callback: function(r) {
				if(r.message) {
					frappe.tools.downloadify(r.message, null, "Ekspor Lawan Transaksi")
				}else{
					frappe.throw("Error")
				}
				frappe.dom.unfreeze();
			}
		});
		
	}
});
