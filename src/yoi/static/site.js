var formatAmount = function(amt) {
    return (amt >= 0 ? '+' : '') + amt.toFixed(2);
};
$.fn.yoi_entry_editor = function() {
    var self = this;

    var update_share_descriptions = function() {
        if(self.find('input[name=manual-entry]').attr('checked'))
            update_share_descriptions_manual();
        else
            update_share_descriptions_automatic();
    };

    var update_share_descriptions_manual = function() {
        self.find('.preview').hide();

        var amount_total = 0;
        self.find('.victim input[name=shares]').each(function(i, e) {
            amount_total += parseFloat(e.value);
        });

        self.find('input[name=amount]').val(amount_total);
    };

    var update_share_descriptions_automatic = function() {
        var payer = self.find(':input[name=payer]').val();

        var shares_total = 0;
        self.find('input[name=shares]').each(function(i, e) {
            shares_total += parseFloat(e.value);
        });

        var amount_total = parseFloat(self.find('input[name=amount]').val());

        self.find('.victim').each(function(i, e) {
            var e = $(e);
            var victim = e.find('input[name=victim]').val();
            var shares = e.find('input[name=shares]').val();
            var percentage = 100 / shares_total * shares;
            var amount = - amount_total / shares_total * shares;

            if(victim == payer)
                amount += amount_total;

            var text = '(' + shares + ' shares ~ '
                           + percentage.toFixed(0) + '% ~ '
                           + formatAmount(amount) + ' DKK)';
            text = text.replace('(1 shares', '(1 share');

            e.find('.preview').text(text).show();
        });
    };

    this.find('input').on('change', function(ev) {
        update_share_descriptions();
    });

    this.on('click activate', '#select-payer', function(ev) {
        ev.preventDefault();

        var offset = $(this).offset();
        $('#user-selector')
            .css({top: ev.pageY, left: ev.pageX - offset.left})
            .show();

        update_share_descriptions();
    });
    this.on('click activate', '.select-user', function(ev) {
        ev.preventDefault();

        $('#user-selector')
            .hide();
        $('#select-payer .avatar')
            .replaceWith($(this).find('.avatar').clone());
        $('input[name=payer]')
            .val($(this).data('user'));

        update_share_descriptions();
    });

    self.on('change', 'input[name=manual-entry]', function(ev) {
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

    this.on('click activate', '.toggle-victim', function(ev) {
        ev.preventDefault();
        var victim = $(this).data('user');
        self.find('.victim').each(function(i, e) {
            var e = $(e);
            if(e.data('user') != victim)
                return;
            if(e.filter(':visible').length > 0)
                e.find('input[name=shares]').val(0);
            else if(! self.find('input[name=manual-entry]').attr('checked'))
                e.find('input[name=shares]').val(1);
            e.toggle();
        });

        update_share_descriptions();
    });

    var payer = $('input[name=payer]').val()
    $('.toggle-victim[data-user=' + payer + ']').click();

    update_share_descriptions();
};

$(document).ready(function() {
    $('.entry-editor').yoi_entry_editor();

    if(document.location.pathname == '/journal'
       && document.location.search != '')
        $('#new-entry-notice').toggle();
});
