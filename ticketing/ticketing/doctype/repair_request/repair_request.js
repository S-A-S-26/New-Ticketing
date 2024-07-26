// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Repair Request', {
	refresh: function(frm) {
		show_notes(frm)
	}
});

function show_notes(frm) {
    const crm_notes = new erpnext.utils.CRMNotes({
        frm: frm,
        notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
    });
    crm_notes.refresh();

    frm.dirty();
}
