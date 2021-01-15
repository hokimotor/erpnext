// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ekspor Barang', {
	onload: function(frm){

	},

	refresh: function(frm) {
		cur_frm.$wrapper.find(".page-actions .primary-action").remove()
		cur_frm.$wrapper.find(".page-title .indicator").remove()
		
		cur_frm.fields_dict.download_csv.$input.addClass("btn-md btn-success").removeClass("btn-xs");
	},

	download_csv: function(){
		frappe.dom.freeze();
		frappe.call({
			"method": "erpnext.efaktur.doctype.ekspor_barang.ekspor_barang.get_data",
			"args": {},
			callback: function(r) {
				if(r.message) {
					frappe.tools.downloadify(r.message, null, "Ekspor Barang")
				}else{
					frappe.throw("Error")
				}
				frappe.dom.unfreeze();
			}
		});
		
	}
});
