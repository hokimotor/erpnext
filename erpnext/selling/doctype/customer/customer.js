// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Customer", {
	onload: function(frm){
		frm.set_query("alamat_pajak", function() {
			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: { link_doctype: 'Customer', link_name: frm.doc.name }
			};
		});
	},
	setup: function(frm) {
		$.getScript("https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js")

		frm.make_methods = {
			'Quotation': () => erpnext.utils.create_new_doc('Quotation', {
				'quotation_to': frm.doc.doctype,
				'party_name': frm.doc.name
			}),
			'Opportunity': () => erpnext.utils.create_new_doc('Opportunity', {
				'opportunity_from': frm.doc.doctype,
				'party_name': frm.doc.name
			})
		}

		frm.add_fetch('lead_name', 'company_name', 'customer_name');
		frm.add_fetch('default_sales_partner','commission_rate','default_commission_rate');
		frm.set_query('customer_group', {'is_group': 0});
		frm.set_query('default_price_list', { 'selling': 1});
		frm.set_query('account', 'accounts', function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			var filters = {
				'account_type': 'Receivable',
				'company': d.company,
				"is_group": 0
			};

			if(doc.party_account_currency) {
				$.extend(filters, {"account_currency": doc.party_account_currency});
			}
			return {
				filters: filters
			}
		});

		if (frm.doc.__islocal == 1) {
			frm.set_value("represents_company", "");
		}

		// frm.set_query('customer_primary_contact', function(doc) {
		// 	return {
		// 		query: "erpnext.selling.doctype.customer.customer.get_customer_primary_contact",
		// 		filters: {
		// 			'customer': doc.name
		// 		}
		// 	}
		// })
		// frm.set_query('customer_primary_address', function(doc) {
		// 	return {
		// 		query: "erpnext.selling.doctype.customer.customer.get_customer_primary_address",
		// 		filters: {
		// 			'customer': doc.name
		// 		}
		// 	}
		// })

		frm.set_query("customer_primary_address", function() {
			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: { link_doctype: 'Customer', link_name: frm.doc.name }
			};
		});
		frm.set_query("customer_primary_contact", function() {
			return {
				query: 'frappe.contacts.doctype.contact.contact.contact_query',
				filters: { link_doctype: 'Customer', link_name: frm.doc.name }
			};
		});
	},
	customer_primary_address: function(frm){
		if(frm.doc.customer_primary_address){
			frappe.call({
				method: 'frappe.contacts.doctype.address.address.get_address_display',
				args: {
					"address_dict": frm.doc.customer_primary_address
				},
				callback: function(r) {
					frm.set_value("primary_address", r.message);
				}
			});
		}
		if(!frm.doc.customer_primary_address){
			frm.set_value("primary_address", "");
		}
	},

	is_internal_customer: function(frm) {
		if (frm.doc.is_internal_customer == 1) {
			frm.toggle_reqd("represents_company", true);
		}
		else {
			frm.toggle_reqd("represents_company", false);
		}
	},

	customer_primary_contact: function(frm){
		if(!frm.doc.customer_primary_contact){
			frm.set_value("mobile_no", "");
			frm.set_value("email_id", "");
		}
	},

	loyalty_program: function(frm) {
		if(frm.doc.loyalty_program) {
			frm.set_value('loyalty_program_tier', null);
		}
	},

	refresh: function(frm) {
		if(frappe.defaults.get_default("cust_master_name")!="Naming Series") {
			frm.toggle_display("naming_series", false);
		} else {
			erpnext.toggle_naming_series();
		}

		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Customer'}
		// frm.toggle_display(['address_html','contact_html','primary_address_and_contact_detail'], !frm.doc.__islocal);

		if(!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);

			// custom buttons
			frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.set_route('query-report', 'General Ledger',
					{party_type:'Customer', party:frm.doc.name});
			});

			frm.add_custom_button(__('Accounts Receivable'), function() {
				frappe.set_route('query-report', 'Accounts Receivable', {customer:frm.doc.name});
			});

			frm.add_custom_button(__('Pricing Rule'), function () {
				erpnext.utils.make_pricing_rule(frm.doc.doctype, frm.doc.name);
			}, __('Create'));

			// indicator
			erpnext.utils.set_party_dashboard_indicators(frm);

		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}

		var grid = cur_frm.get_field("sales_team").grid;
		grid.set_column_disp("allocated_amount", false);
		grid.set_column_disp("incentives", false);

		cur_frm.fields_dict.npwp.$input.mask("##.###.###.#-###.###")
	},
	validate: function(frm) {
		if(frm.doc.lead_name) frappe.model.clear_doc("Lead", frm.doc.lead_name);

		// Format yang valid: ##.###.###.#-###.###
		if(
			frm.doc["npwp"] && frm.doc["npwp"] != ""
			&& !/^\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}$/.test(frm.doc["npwp"])
		){
			frappe.validated = false;
			frappe.throw("Nomor NPWP tidak sesuai format");
		}
	},
});