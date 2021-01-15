// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Schedule', {
	refresh: function(frm) {
		cur_frm.disable_save();
		Object.keys(cur_frm.fields_dict).forEach(field => {
			cur_frm.toggle_enable(field, 0);
		});

		cur_frm.add_custom_button(__('Invoice'), ()=>{
			// return frappe.confirm(
			// 	'This action will create submitted invoice, continue?',
			// 	function(){
					frappe.call({
						method: "erpnext.accounts.doctype.payment_schedule.payment_schedule.make_invoice",
						args: {
							"dt": cur_frm.doc.doctype,
							"dn": cur_frm.doc.name
						},
						callback: function(r) {
							var doclist = frappe.model.sync(r.message);
							frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
							setTimeout(() => {
								cur_frm.events.trigger_from_reservation();
							}, 2000);
						}
					});
			// 	},
			// 	function(){}
			// )
			
		}, __("Make"));
		cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
	}
});
