odoo.define('clickup_connector.kanban_interactions', ['web.ajax'], function (require) {
    "use strict";

    const ajax = require('web.ajax');

    // Inline editable description
    $(document).on('blur', '.o_kanban_editable_description', function () {
        const $el = $(this);
        const newValue = $el.text().trim();
        const model = $el.data('model');
        const field = $el.data('field');
        const id = $el.data('id');

        if (!model || !field || !id) return;

        ajax.jsonRpc('/web/dataset/call_kw', 'call', {
            model: model,
            method: 'write',
            args: [[id], { [field]: newValue }],
            kwargs: {}
        });
    });

    // State dropdown change
    $(document).on('click', '.kanban-state-change', function (e) {
        e.preventDefault();

        const $el = $(this);
        const newState = $el.data('state');
        const id = parseInt($el.data('id'));

        ajax.jsonRpc('/web/dataset/call_kw', 'call', {
            model: 'project.task',
            method: 'write',
            args: [[id], { 'state': newState }],
            kwargs: {}
        }).then(function () {
            location.reload(); // reload after update
        });
    });
});
