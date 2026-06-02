/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";

// ── Book Form Controller ─────────────────────────────────────────────────────
class BookFormController extends FormController {
    setup() {
        super.setup();
    }
}

// ── Member Form Controller ───────────────────────────────────────────────────
class MemberFormController extends FormController {
    setup() {
        super.setup();
    }
}

// ── Borrow Form Controller ───────────────────────────────────────────────────
class BorrowFormController extends FormController {
    setup() {
        super.setup();
    }
}

// ── Register all three views ─────────────────────────────────────────────────
registry.category("views").add("library_book_form", {
    ...formView,
    Controller: BookFormController,
});

registry.category("views").add("library_member_form", {
    ...formView,
    Controller: MemberFormController,
});

registry.category("views").add("library_borrow_form", {
    ...formView,
    Controller: BorrowFormController,
});
