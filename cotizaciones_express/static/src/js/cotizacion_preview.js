/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef, onMounted, useEffect } from "@odoo/owl";

// LOG DE DIAGNÓSTICO: si ves este mensaje en la consola del navegador,
// el archivo JS se está cargando correctamente.
console.log("[CotizacionesExpress] cotizacion_preview.js cargado ✓");

class CotizacionPreview extends Component {
    static template = "cotizaciones_express.CotizacionPreview";
    // "*": true acepta cualquier prop sin validación — más compatible con v19
    static props = { "*": true };

    setup() {
        this.iframeRef = useRef("previewIframe");
        this.state = useState({
            iframeSrc: "",
            isLoading: false,
        });
        this._timeout = null;

        onMounted(() => {
            console.log("[CotizacionesExpress] CotizacionPreview montado, resId=", this._getResId());
            const el = this.iframeRef.el;
            if (el) {
                el.addEventListener("load", () => {
                    this.state.isLoading = false;
                });
            }
            // Carga inicial si el registro ya está guardado
            if (this._getResId() > 0) {
                this._refresh();
            }
        });

        // useEffect: el callback NO recibe parámetros en OWL 2.
        // Se ejecuta cuando el array de dependencias cambia.
        // Al guardar, Odoo recalcula preview_trigger → this.props.value cambia → se refresca.
        useEffect(
            () => {
                // Leer el valor por closure, NO como parámetro
                const trigger = this.props.value;
                if (trigger && this._getResId() > 0) {
                    if (this._timeout) clearTimeout(this._timeout);
                    this._timeout = setTimeout(() => this._refresh(), 800);
                }
            },
            () => [this.props.value]
        );
    }

    _getResId() {
        try {
            return this.props.record.resId || 0;
        } catch (e) {
            return 0;
        }
    }

    _refresh() {
        const id = this._getResId();
        if (id > 0) {
            this.state.isLoading = true;
            this.state.iframeSrc = `/cotizacion/preview_html/${id}?t=${Date.now()}`;
        }
    }

    onClickRefresh() {
        this._refresh();
    }

    onClickDownload() {
        const id = this._getResId();
        if (id > 0) {
            window.open(
                `/report/pdf/cotizaciones_express.cotizacion_preview_template/${id}`,
                "_blank"
            );
        }
    }
}

console.log("[CotizacionesExpress] Registrando widget 'cotizacion_preview'...");
registry.category("fields").add("cotizacion_preview", {
    component: CotizacionPreview,
    supportedTypes: ["char"],
});
console.log("[CotizacionesExpress] Widget registrado ✓");
