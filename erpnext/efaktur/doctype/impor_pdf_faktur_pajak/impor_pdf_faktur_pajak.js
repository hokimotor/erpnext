// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Impor PDF Faktur Pajak', {
	refresh: function() {
		cur_frm.disable_save();
		var me = this;
		
		var $wrapper = $(cur_frm.fields_dict.upload_html.wrapper).empty();
		

		// upload
		frappe.upload.make({
			parent: $wrapper,
			args: {
				method: 'erpnext.efaktur.doctype.impor_pdf_faktur_pajak.impor_pdf_faktur_pajak.upload'
			},
			no_socketio: true,
			sample_url: "e.g. http://example.com/somefile.csv",
			callback: function(res) {
				console.log("RES", res);
				var $log_wrapper = $(cur_frm.fields_dict.import_log.wrapper).find(".log-row-container");

				if(res.error){
					$log_wrapper.append(`
						<tr>
							<td>${res.error.filename}</td>
							<td><span class="indicator red">Gagal, ${res.error.message}</span></td>
						</tr>
					`)
				}

				if(res.message){
					$log_wrapper.append(`
						<tr>
							<td>${res.message.filename}</td>
							<td><span class="indicator green">Sukses, ${res.message.message}</span></td>
						</tr>
					`)
				}

			}
		});

		setTimeout(() => {
			$wrapper.find(".private-file").next().hide();
			$wrapper.find(".web-link-wrapper").hide();
			$wrapper.find(".attach-btn").addClass("btn-primary").css("margin-top", "0");
			$wrapper.find(".input-upload button").addClass("btn-default").removeClass("btn-primary");
			$wrapper.find(".attach-btn").html("Upload & Import")

			$wrapper.find(".attach-btn").on("click", ()=>{
				cur_frm.set_df_property("log_section", "hidden", 0)
				$(cur_frm.fields_dict.import_log.wrapper).html(`
					<table class="table table-bordered">
						<thead>
							<tr>
								<td style="width: 35%">Filename</td>
								<td style="width: 65%">Message</td>
							</tr>
						</thead>
						<tbody class="log-row-container">
						</tbody>
					</table>
				`);
			})
		}, 250);
	},
});
