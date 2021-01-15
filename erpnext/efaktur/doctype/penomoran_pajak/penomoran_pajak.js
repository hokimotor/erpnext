// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Penomoran Pajak', {
	setup: function(frm){
		$.getScript("https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js", function(){
			cur_frm.fields_dict.dari_nomor.$input.mask("###-##.########");
			cur_frm.fields_dict.sampai_nomor.$input.mask("###-##.########");
		})
	},
	refresh: function(frm) {
		setTimeout(() => {
			cur_frm.fields_dict.dari_nomor.$input.mask("###-##.########");
			cur_frm.fields_dict.sampai_nomor.$input.mask("###-##.########");
		}, 200);
		
	},
	validate: function(frm){
		let is_numeric = function(value) {
			return /^-{0,1}\d+$/.test(value);
		}

		let validate_series_format = function(field){
			let valid = true

			// Format valid: ###-##.########
			let val = cur_frm.doc[field];

			let split1 = val.split(".");
			if(split1.length != 2) return false;
			if(split1[1].length != 8 || split1[0].length != 6) return false;

			let split2 = split1[0].split("-");
			if(split2.length != 2) return false;
			if(split2[1].length != 2 || split2[0].length != 3) return false;

			if(!is_numeric(split2[0]) || !is_numeric(split2[1]) || !is_numeric(split1[1])){
				return false;
			}

			return true
		}

		if(!validate_series_format("dari_nomor") || !validate_series_format("sampai_nomor")){
			frappe.validated = false
			frappe.throw("Nomor seri faktur pajak tidak sesuai format")
		}

		let from = parseInt(cur_frm.doc.dari_nomor.split(".")[1]);
		let to = parseInt(cur_frm.doc.sampai_nomor.split(".")[1]);
		if(to - from < 0){
			frappe.validated = false
			frappe.throw("Jumlah nomor seri yang diinputkan minimal 1")
		}

	},

	seri_faktur_pajak_on_form_rendered: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		console.log("Oke")
		var button_wrapper = cur_frm.cur_grid.get_field("lihat_faktur_pdf").wrapper;
		$(button_wrapper).hide();

		if(d.voucher_type && d.voucher_no){
			frappe.db.get_value(d.voucher_type, {name: d.voucher_no}, ["file_faktur_pajak"], (res)=>{
				if(res && res.file_faktur_pajak && res.file_faktur_pajak != null){
					$(button_wrapper).show();
					window.cur_pdf_link = res.file_faktur_pajak
				}
			})
		}
	},

});

frappe.ui.form.on('Seri Faktur Pajak', {
	unlink: function(frm, cdt, cdn){
		frappe.call({
			"method": "erpnext.efaktur.doctype.seri_faktur_pajak.seri_faktur_pajak.unlink",
			"args": {
				"name": cdn
			},
			callback: function(r) {
				var idx = -1;
				for (let i = 0; i < cur_frm.doc.seri_faktur_pajak.length; i++) {
					const sfp = cur_frm.doc.seri_faktur_pajak[i];
					if(sfp.name == cdn) idx = i;
				}

				cur_frm.doc.seri_faktur_pajak[idx].voucher_type = ""
				cur_frm.doc.seri_faktur_pajak[idx].voucher_no = ""
				cur_frm.doc.seri_faktur_pajak[idx].terpakai = 0
				cur_frm.refresh_field("seri_faktur_pajak")
			}
		});
	},

	seri_faktur_pajak_on_form_rendered: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		console.log("Oke")
		var button_wrapper = cur_frm.fields_dict[d.parentfield].grid.grid_rows_by_docname[cdn].grid_form.fields_dict["lihat_faktur_pdf"].wrapper;
		$(button_wrapper).hide();

		if(d.voucher_type && d.voucher_no){
			frappe.db.get_value(d.voucher_type, {name: d.voucher_no}, ["file_faktur_pajak"], (res)=>{
				if(res && res.file_faktur_pajak && res.file_faktur_pajak != null){
					$(button_wrapper).show();
					window.cur_pdf_link = res.file_faktur_pajak
				}
			})
		}
	},

	lihat_faktur_pdf: function(){
		if(!window.cur_pdf_link) return;
		var base_url = window.location.origin;

		var win = window.open(base_url + "/" + window.cur_pdf_link, '_blank');
  		win.focus();
	}
});
