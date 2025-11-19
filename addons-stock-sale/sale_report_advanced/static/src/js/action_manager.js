odoo.define('sale_report_advanced.action_manager', function (require) {
"use strict";
var ActionManager = require('web.ActionManager');
var framework = require('web.framework');
var session = require('web.session');
ActionManager.include({
    _executexlsxReportDownloadAction: function (action) {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/xlsx_reports',
            data: action.data,
            success: def.resolve.bind(def),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: framework.unblockUI,
        });
        return def;
    },
    _isSaleAdvancedXlsx: function (action) {
        const data = action.data || {};
        return (
            action.report_type === 'xlsx' &&
            data.model &&
            data.options &&
            data.output_format &&
            data.report_name
        );
    },
    _handleAction: function (action, options) {
        // if (action.report_type === 'xlsx') {
        if (this._isSaleAdvancedXlsx(action)) {
            return this._executexlsxReportDownloadAction(action, options);
        }
        return this._super.apply(this, arguments);
    },
});
});