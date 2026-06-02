/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";

/**
 * BookFormController — extends the standard FormController to inject
 * extra reactive state (availability colour, badge label) used by the
 * custom template rendered by OWL.
 */
class BookFormController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");

        // Reactive state kept in sync with the record
        this.bookState = useState({
            isAvailable: true,
            badgeClass: "badge-success",
            badgeLabel: "Available",
            availabilityPct: 100,
        });

        // Re-derive computed display values whenever the record changes
        this._syncBookState();
    }

    // ------------------------------------------------------------------ //
    //  Helpers
    // ------------------------------------------------------------------ //

    /** Pull values from the live record and update reactive bookState. */
    _syncBookState() {
        const record = this.model?.root;
        if (!record) return;

        const total = record.data?.total_copies ?? 0;
        const available = record.data?.available_copies ?? 0;
        const state = record.data?.state ?? "available";

        const isAvail = state === "available";
        this.bookState.isAvailable = isAvail;
        this.bookState.badgeClass = isAvail ? "bg-success" : "bg-danger";
        this.bookState.badgeLabel = isAvail ? "Available" : "All Borrowed";
        this.bookState.availabilityPct =
            total > 0 ? Math.round((available / total) * 100) : 0;
    }

    // ------------------------------------------------------------------ //
    //  Public helpers called from the template
    // ------------------------------------------------------------------ //

    get availabilityPercent() {
        this._syncBookState();
        return this.bookState.availabilityPct;
    }

    get progressBarClass() {
        this._syncBookState();
        return this.bookState.badgeClass;
    }

    get statusLabel() {
        this._syncBookState();
        return this.bookState.badgeLabel;
    }
}

// Register the custom form view for library.book model
registry.category("views").add("library_book_form", {
    ...formView,
    Controller: BookFormController,
});
