/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onMounted, useEffect } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class CotizacionPreview extends Component {
    static template = "cotizaciones_express.CotizacionPreview";
    static props = { ...standardFieldProps };

    setup() {
        this.iframeRef = useRef("previewIframe");
        this.state = useState({
            iframeSrc: this._buildUrl(),
            isLoading: true,
        });
        this._refreshTimeout = null;

        onMounted(() => {
            this._setupIframeListener();
            // Carga inicial: si ya hay un registro guardado, carga la preview
            if (this.resId > 0) {
                this._doRefresh();
            } else {
                this.state.isLoading = false;
            }
        });

        // useEffect observa el valor de preview_trigger.
        // Solo dispara cuando el campo cambia (después de guardar),
        // NO en cada re-render — evita el bucle infinito de onPatched.
        useEffect(
            (value) => {
                if (value) {
                    this._scheduleRefresh();
                }
            },
            () => [this.props.value]
        );
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
            this._doRefresh();
        }, 800);
    }

    _doRefresh() {
        this.state.isLoading = true;
        this.state.iframeSrc = this._buildUrl();
    }

    onClickRefresh() {
        this._doRefresh();
    }

    onClickDownloadPdf() {
        const id = this.resId;
        if (id > 0) {
            window.open(
                `/report/pdf/cotizaciones_express.cotizacion_preview_template/${id}`,
                "_blank"
            );
        }
    }
}

export const cotizacionPreviewField = {
    component: CotizacionPreview,
    supportedTypes: ["char"],
};

registry.category("fields").add("cotizacion_preview", cotizacionPreviewField);
