/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onMounted, onWillDestroy, useState } from "@odoo/owl";

class CotizacionPreview extends Component {
    static template = "cotizaciones_express.PreviewIframe";

    setup() {
        this.state = useState({ src: this._getSrc() });
        this._timer = null;
        onMounted(() => {
            this._timer = setInterval(() => this._refresh(), 2000);
            this._bindFormEvents();
        });
        onWillDestroy(() => {
            if (this._timer) clearInterval(this._timer);
            this._unbindFormEvents();
        });
    }

    _getSrc() {
        const resId = this.props.record?.resId;
        if (resId) {
            return "/cotizacion/preview_html/" + resId;
        }
        return "";
    }

    _refresh() {
        const baseSrc = this._getSrc();
        if (baseSrc) {
            this.state.src = baseSrc + "?t=" + Date.now();
        }
    }

    _bindFormEvents() {
        this._onFormChange = () => this._refresh();
        document.addEventListener("change", this._onFormChange, true);
        document.addEventListener("input", this._onFormChange, true);
    }

    _unbindFormEvents() {
        if (this._onFormChange) {
            document.removeEventListener("change", this._onFormChange, true);
            document.removeEventListener("input", this._onFormChange, true);
        }
    }
}

registry.category("widgets").add("cotizacion_preview_iframe", CotizacionPreview);
