/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onWillStart, onMounted, onWillUpdateProps, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CotizacionPreview extends Component {
    static template = "cotizaciones_express.CotizacionPreview";
    static props = { ...standardFieldProps };

    setup() {
        this.iframeRef = useRef("previewIframe");
        this.orm = useService("orm");
        this.state = useState({
            iframeSrc: this._buildUrl(),
            isLoading: true,
        });
        this._refreshTimeout = null;

        onMounted(() => {
            this._setupIframeListener();
        });

        onPatched(() => {
            this._scheduleRefresh();
        });
    }

    get resId() {
        return this.props.record.resId || 0;
    }

    _buildUrl() {
        const id = this.resId;
        const ts = new Date().getTime();
        return `/cotizacion/preview_html/${id}?t=${ts}`;
    }

    _setupIframeListener() {
        const iframe = this.iframeRef.el;
        if (iframe) {
            iframe.addEventListener("load", () => {
                this.state.isLoading = false;
            });
        }
    }

    _scheduleRefresh() {
        if (this._refreshTimeout) {
            clearTimeout(this._refreshTimeout);
        }
        this._refreshTimeout = setTimeout(() => {
            this._refreshPreview();
        }, 1500);
    }

    _refreshPreview() {
        const newSrc = this._buildUrl();
        if (this.state.iframeSrc !== newSrc || this.resId > 0) {
            this.state.isLoading = true;
            this.state.iframeSrc = this._buildUrl();
        }
    }

    onClickRefresh() {
        this.state.isLoading = true;
        this.state.iframeSrc = this._buildUrl();
    }

    onClickDownloadPdf() {
        const id = this.resId;
        if (id > 0) {
            window.open(`/report/pdf/cotizaciones_express.cotizacion_preview_template/${id}`, '_blank');
        }
    }
}

export const cotizacionPreviewField = {
    component: CotizacionPreview,
    supportedTypes: ["char"],
};

registry.category("fields").add("cotizacion_preview", cotizacionPreviewField);
