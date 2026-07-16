/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillDestroy } from "@odoo/owl";

class CotizacionAutoSave extends Component {
    static template = "cotizaciones_express.CotizacionAutoSave";
    static props = { "*": true };

    setup() {
        let lastInputTime = Date.now();
        let interval = null;

        const onInput = () => {
            lastInputTime = Date.now();
        };

        const forceSave = () => {
            const isMac = /Mac|iPad|iPhone|iPod/.test(navigator.platform);
            const event = new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                key: 's',
                code: 'KeyS',
                keyCode: 83,
                which: 83,
                ctrlKey: !isMac,
                metaKey: isMac
            });
            document.dispatchEvent(event);
        };

        onMounted(() => {
            document.addEventListener('input', onInput, true);
            document.addEventListener('click', onInput, true);

            interval = setInterval(() => {
                const formEl = document.querySelector('.o_form_view');
                const isDirty = formEl && formEl.classList.contains('o_form_dirty');
                
                // Si el formulario tiene cambios sin guardar y el usuario está inactivo por 2.5s,
                // enviamos el comando Ctrl+S de manera invisible.
                if (isDirty && (Date.now() - lastInputTime > 2500)) {
                    lastInputTime = Date.now(); // resetea timer
                    forceSave();
                }
            }, 1000);
        });

        onWillDestroy(() => {
            document.removeEventListener('input', onInput, true);
            document.removeEventListener('click', onInput, true);
            if (interval) clearInterval(interval);
        });
    }
}

registry.category("fields").add("cotizacion_auto_save", {
    component: CotizacionAutoSave,
    supportedTypes: ["char"],
});
