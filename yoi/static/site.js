var formatAmount = function(amt) {
    // FIXME -- should wrap in .red/.green
    return amt >= 0 ? '+ ' + amt.toFixed(2) : '− ' + (-amt).toFixed(2);
};
$.fn.yoi_entry_editor = function() {
    var self = this;
    if(self.length == 0)
        return;

    console.log(this);

    var update_share_descriptions = function() {
        if(self.find('input[name=manual_entry]').attr('checked'))
            update_share_descriptions_manual();
        else
            update_share_descriptions_automatic();
    };

    var update_share_descriptions_manual = function() {
        self.find('.preview').hide();

        var amount_total = 0;
        self.find('.victim input[name=shares]').each(function(i, e) {
            amount_total += Yoi.parse_amount(e.value);
        });

        self.find('input[name=amount]').val(amount_total);
    };

    var update_share_descriptions_automatic = function() {
        var payer = self.find(':input[name=payer]').val();

        var shares_total = 0;
        self.find('input[name=shares]').each(function(i, e) {
            shares_total += Yoi.parse_amount(e.value);
        });

        var amount_total = Yoi.parse_amount(self.find('input[name=amount]').val());

        self.find('.victim').each(function(i, e) {
            var e = $(e);
            var victim = e.find('input[name=victim]').val();
            var shares = e.find('input[name=shares]').val();
            var percentage = 100 / shares_total * shares;
            var amount = - amount_total / shares_total * shares;

            if(victim == payer)
                amount += amount_total;
            if(amount.toString() == 'NaN')
                amount = 0;

            var text = '(' + shares + ' shares ~ '
                           + percentage.toFixed(0) + '% ~ '
                           + formatAmount(amount) + ' DKK)';
            text = text.replace('(1 shares', '(1 share');

            e.find('.preview').text(text).show();
        });
    };

    self.find('input').on('change', function(ev) {
        update_share_descriptions();
    });

    $('#select-payer').on('click activate', '.select-person', function(ev) {
        ev.preventDefault();

        $('#select-payer').dialog('close');

        $('#payer-avatar .avatar')
            .replaceWith($(this).find('.avatar').clone());
        $('input[name=payer]')
            .val($(this).data('person'));

        update_share_descriptions();
    });

    self.on('change', 'input[name=manual_entry]', function(ev) {
        var amount_readonly = this.checked,
            shares_type = this.checked ? 'number' : 'range',
            shares_max = this.checked ? undefined : 10;

        self.find('input[name=amount]')
            .attr('readonly', amount_readonly);
        self.find('input[name=shares]')
            /* Because IE is sucky jQuery refuses to touch the type attribute,
             * but we don't give a rat's ass about IE. */
            .each(function(i, e) {
                e.type = shares_type;
                e.max = shares_max;
            });

        update_share_descriptions();
    });

    self.on('click activate', '.toggle-victim', function(ev) {
        ev.preventDefault();
        var victim = $(this).data('person');
        self.find('.victim').each(function(i, e) {
            var e = $(e);
            if(e.data('person') != victim)
                return;
            if(e.filter(':visible').length > 0)
                e.find('input[name=shares]').val(0);
            else if(! self.find('input[name=manual_entry]').attr('checked'))
                e.find('input[name=shares]').val(1);
            e.toggle();
        });

        update_share_descriptions();
    });

    var payer = $('input[name=payer]').val()

    update_share_descriptions();
};
$(document).ready(function() {
    $('.entry-editor').yoi_entry_editor();
});

/* Magic for "Add People" dialog */
$(document).ready(function() {
    $('ol.input-auto-repeat').on('keyup', 'input', function() {
        /* Add a new empty input, if this is the last input, and it not
         * empty. */
        var this_is_last = ($(this)
                                .closest('li')
                                .filter(':last-child')
                                .length > 0);

        if(this.value != '' && this_is_last) {
            var ol = $(this).closest('ol.input-auto-repeat');
            var li = ol.find('li:first-child').clone();
            li.find('input').val('');
            ol.append(li);
        }
    });

    $('ol.input-auto-repeat').on('blur focus', 'input', function() {
        /* Remove all empty inputs, except the last one. */
        $(this)
            .closest('ol.input-auto-repeat')
            .find('li:not(:last-child):has(input[value=])')
            .remove();
    });
});

/* Generic dialogs */
$(document).ready(function() {
    var dialogs = {};
    $('.dialog').each(function(i, e) {
        var self = $(this);
        var title = self.find('h1').remove().text();

        var buttons = {};
        self.find('button').remove().each(function() {
            var btn = $(this);
            var event = btn.data('event');
            buttons[btn.text()] = function() {
                self.trigger(event);
                self.dialog('close');
            };
        });

        var dialog_opts = {
            title: title,
            autoOpen: false,
            width: '50%',
            modal: true,
            buttons: buttons
        };
        dialogs[this.id] = self.dialog(dialog_opts);
    });

    $(document).on('click activate', '.for-dialog', function(ev) {
        ev.preventDefault();
        dialogs[$(this).data('dialog')].dialog('open');
    });

    console.log(document.location.hash);
    if(document.location.hash.length > 0) {
        var name = document.location.hash.substring(1);
        $('.for-dialog[data-dialog=' + name + ']').click();
    }
});

var Yoi = {};

Yoi.parse_amount = function(amt) {
    return parseFloat(amt.replace(',', '.'));
};

Yoi.ajax = function(opts) {
    var defaults = {
        error: Yoi.ajax_error_handler,
        traditional: true
    };
    var opts = $.extend({}, defaults, opts);
    if(opts.type == 'POST')
        opts.data = $.extend({}, opts.data, {csrf_token: csrf_token});
    return $.ajax(opts);
};
Yoi.post = function(url, data, success) {
    return Yoi.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: success
    });
};
Yoi.ajax_error_handler = function() {
    alert('Ajax request failed. I do not know what to do <_<');
};

/* Magic for "Join Event" dialog */
$(document).ready(function() {
    function ajax_join(person_id) {
        Yoi.post('join',
                 {person: person_id || ''},
                 function() { document.location.reload() });
    }

    $('.for-dialog[data-dialog=join]').on('click activate', function(ev) {
        ev.preventDefault();
        if($('#join').find('li').length == 0) {
            ev.stopPropagation();
            ajax_join();
        }
    });
    $('#join').on('dialogclose', function(ev) {
        document.location.replace(document.location.pathname);
    });

    $('#join').dialog('option', 'buttons', {
        'I am someone else!': function() {
            ajax_join();
        }
    });

    $('#join').on('click activate', 'a', function(ev) {
        ev.preventDefault();
        ajax_join($(this).find('.avatar').data('person'));
    });
});

/* Magic for "Add People" dialog */
$(document).ready(function() {
    $('#add-people').on('dialogopen', function() {
        /* Reset dialog when opening */
        $(this)
            .find('li:not(:first-child)').remove().end()
            .find('li input').val('').focus().end();
    });

    $('#add-people').on('keyup', 'input', function(ev) {
        if(ev.keyCode == 13)
            $('.ui-dialog:has(#add-people)').find('button').click();
    });

    $('#add-people').on('dialog-ok', function() {
        var people = $.map($('#add-people').find('input[value!=]'),
                           function(e) { return e.value });
        Yoi.post('add-people', {people: people},
                 function() { document.location.reload() });
    });
});
