// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ekspor SPT PPN', {
	onload: function(frm) {
		if(!cur_frm.doc.tanggal_awal && !cur_frm.doc.tanggal_akhir){
			cur_frm.set_value("tanggal_awal", frappe.datetime.month_start());
			cur_frm.set_value("tanggal_akhir", frappe.datetime.month_end());
		}
	},

	refresh: function(){
		cur_frm.fields_dict.faktur_pajak_keluaran.$wrapper.find(".grid-footer .grid-add-row").remove();
		cur_frm.fields_dict.faktur_pajak_masukan.$wrapper.find(".grid-footer .grid-add-row").remove();
		
		// Munculkan jumlah child table pada section break
		$(cur_frm.fields_dict.pajak_keluaran_section.wrapper).find(".section-head .h6").html("PAJAK KELUARAN (" + cur_frm.doc.faktur_pajak_keluaran.length +")")
		$(cur_frm.fields_dict.pajak_masukan_section.wrapper).find(".section-head .h6").html("PAJAK MASUKAN (" + cur_frm.doc.faktur_pajak_masukan.length +")")

		cur_frm.clear_custom_buttons()
		cur_frm.add_custom_button("Pajak Keluaran", ()=>{ cur_frm.events.download_csv("Pajak Keluaran") }, "Download CSV");
		cur_frm.add_custom_button("Retur Pajak Keluaran", ()=>{ cur_frm.events.download_csv("Retur Pajak Keluaran") }, "Download CSV");
		// cur_frm.add_custom_button("Pajak Masukan", ()=>{ cur_frm.events.download_csv("Pajak Masukan") }, "Download CSV");
		// cur_frm.add_custom_button("Retur Pajak Masukan", ()=>{ cur_frm.events.download_csv("Retur Pajak Masukan") }, "Download CSV");
		cur_frm.add_custom_button("Download Semua", ()=>{ cur_frm.events.download_all_csv() }, "Download CSV");
		$(cur_frm.page.inner_toolbar).find("ul.dropdown-menu li:last-child").css("border-top", "1px solid #d4d4d5")
	},

	validate: function(){
		if(cur_frm.doc.processed != 1){
			frappe.validated = false;
			frappe.throw("Harap proses transaksi terlebih dahulu");
		}

		if(!cur_frm.doc.naming_series)
			cur_frm.doc.naming_series = "PPN-" + cur_frm.doc.tanggal_awal.substr(0, 7) + "-"
	},

	proses_transaksi: function(){
		if(!cur_frm.doc.tanggal_awal || !cur_frm.doc.tanggal_akhir){
			frappe.throw("Tanggal awal & akhir harus diisi terlebih dahulu");
			return;
		}

		frappe.dom.freeze();
		frappe.call({
			"method": "erpnext.efaktur.doctype.ekspor_spt_ppn.ekspor_spt_ppn.get_data",
			"args": {
				start_date: cur_frm.doc.tanggal_awal,
				end_date: cur_frm.doc.tanggal_akhir,
			},
			callback: function(r) {
				if(r.message) {
					console.log(r.message)
					load_to_childtable(r.message)
				}else{
					frappe.throw("Error")
				}
				frappe.dom.unfreeze();
			}
		});

		function load_to_childtable(data){
			frappe.model.clear_table(cur_frm.doc, "faktur_pajak_masukan");
			frappe.model.clear_table(cur_frm.doc, "faktur_pajak_keluaran");

			["Sales Invoice", "Purchase Invoice"].forEach(type => {
				var inv_data = data[type + "s"];
				inv_data.forEach(invoice => {
					var row = frappe.model.add_child(
						cur_frm.doc, "Ekspor SPT PPN Faktur",
						(type == "Sales Invoice" ? "faktur_pajak_keluaran" : "faktur_pajak_masukan")
					);

					row.no_pajak = invoice.faktur_pajak;
					row.voucher_type = invoice.doctype;
					row.voucher_no = invoice.name;
					row[(type=="Sales Invoice" ? "customer" : "supplier")] = invoice[(type=="Sales Invoice" ? "customer" : "supplier")];
					row.tanggal_faktur_pajak = invoice.tanggal_faktur_pajak;
					row.tipe_pajak = invoice.tipe_pajak;
					row.kode_dokumen = invoice.kode_dokumen;
					row.dpp = invoice.base_net_total;
					row.ppn = invoice.base_total_taxes_and_charges;
				});
			})

			cur_frm.trigger("refresh");
			
			cur_frm.set_value("processed", 1);
			cur_frm.refresh_fields();
		}
	},

	download_csv: function(type){
		frappe.dom.freeze();
		frappe.call({
			"method": "erpnext.efaktur.doctype.ekspor_spt_ppn.ekspor_spt_ppn.download_csv",
			"args": {
				download_type: type,
				name: cur_frm.doc.name
			},
			callback: function(r) {
				if(r.message) {
					frappe.tools.downloadify(r.message, null, type + " " + cur_frm.doc.tanggal_awal.substr(0, 7))
				}else{
					frappe.throw("Error")
				}
				frappe.dom.unfreeze();
			}
		});
	},

	download_all_csv: function(){
		frappe.dom.freeze();
		$.getScript("https://cdnjs.cloudflare.com/ajax/libs/jszip/3.2.2/jszip.min.js", ()=>{
			var zip = new JSZip();
			var suffix = " " + cur_frm.doc.tanggal_awal.substr(0, 7);
			var filename =  "SPT PPN" + suffix
			var folder = zip.folder(filename);

			frappe.call({
				"method": "erpnext.efaktur.doctype.ekspor_spt_ppn.ekspor_spt_ppn.download_csv",
				"args": {
					download_type: "All",
					name: cur_frm.doc.name
				},
				callback: function(r) {
					if(r.message) {
						Object.keys(r.message).forEach(type => {
							folder.file(type + suffix + ".csv", frappe.tools.to_csv(r.message[type]));
						});

						zip.generateAsync({type:"blob"}).then(function(content) {
							var a = document.createElement('a');
							if ("download" in a) {
								// Used Blob object, because it can handle large files
								a.href = URL.createObjectURL(content);
								a.download = filename + ".zip";
							} else {
								// use old method
								a.href = 'data:attachment/zip,' + encodeURIComponent(content);
								a.download = filename + ".zip";
								a.target = "_blank";
							}
			
							document.body.appendChild(a);
							a.click();
							document.body.removeChild(a);
							frappe.dom.unfreeze();
						});
					}else{
						frappe.throw("Error")
						frappe.dom.unfreeze();
					}
				}
			});
		})
	}
});

frappe.ui.form.on("Ekspor SPT PPN Faktur", {
	faktur_pajak_masukan_remove: function(){ cur_frm.trigger("refresh") },
	faktur_pajak_keluaran_remove: function(){ cur_frm.trigger("refresh") }
})