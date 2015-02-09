/* ajax.js
 *
 * Helper functions for asynchronous requests.
 *
 * Copyright 2014 Stark.
 */

$(function() {
    window.ts = window.ts || {};

    window.ts.ajax = function(input) {
        input = input || {};
        var url = input.url || '';
        var data = input.data || {};
        var csrf = input.csrf || '';
        var success = input.success || function() {};
        var error = input.error || function() {};

        var success_handler = function(data, textStatus, jqXHR) {
            if (textStatus !== 'success') {
                error('Request status: ' + textStatus);
            } else if (data.error) {
                error(data.error);
            } else {
                success(data);
            }
        };

        var error_handler = function(jqXHR, textStatus, error_data) {
            error(error_data);
        };

        data = data || {};
        data.csrfmiddlewaretoken = csrf;

        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: success_handler,
            error: error_handler,
            dataType: 'json'
        });
    };
});

