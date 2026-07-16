/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillUpdateProps, useState } from "@odoo/owl";

class CotizacionPreview extends Component {
    static template = "cotizaciones_express.PreviewIframe";

    setup() {
        this.state = useState({ src: this._getSrc(this.props) });
        onWillUpdateProps((nextProps) => {
            this.state.src = this._getSrc(nextProps);
        });
    }

    _getSrc(props) {
        const resId = props.record?.resId;
        if (resId) {
            return "/cotizacion/preview_html/" + resId;
        }
        return "";
    }
}

registry.category("widgets").add("cotizacion_preview_iframe", CotizacionPreview);
