odoo.define('cotizaciones_express.cotizacion_preview', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var core = require('web.core');
    var _t = core._t;

    FormController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            this._setPreviewSrc();
            this._setupPreviewRefresh();
        },

        _setPreviewSrc: function () {
            var iframe = document.getElementById('cotizacion_preview_iframe');
            if (!iframe) return;
            var resId = this.resId || (this.model && this.model.getResId && this.model.getResId());
            if (resId) {
                iframe.src = '/cotizacion/preview_html/' + resId;
            }
        },

        _setupPreviewRefresh: function () {
            var self = this;
            if (this.$el) {
                this.$el.on('change', 'input, select, textarea', function () {
                    self._refreshPreview();
                });
                this.$el.on('DOMSubtreeModified', '.o_field_widget', function () {
                    self._refreshPreviewDebounced();
                });
            }
        },

        _refreshPreview: function () {
            var iframe = document.getElementById('cotizacion_preview_iframe');
            if (iframe && iframe.src) {
                iframe.src = iframe.src;
            }
        },

        _refreshPreviewDebounced: function () {
            if (this._previewTimer) {
                clearTimeout(this._previewTimer);
            }
            var self = this;
            this._previewTimer = setTimeout(function () {
                self._refreshPreview();
            }, 1000);
        }
    });
