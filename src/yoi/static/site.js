var formatAmount = function(amt) {
    return (amt >= 0 ? '+' : '') + amt.toFixed(2);
};
$.fn.yoi_entry_editor = function() {
    var self = this;

    var update_share_descriptions = function() {
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

            e.find('.preview').text(text);
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

    this.on('click activate', '.toggle-victim', function(ev) {
        ev.preventDefault();
        var victim = $(this).data('user');
        self.find('.victim').each(function(i, e) {
            var e = $(e);
            if(e.data('user') != victim)
                return;
            if(e.filter(':visible').length > 0)
                e.find('input[name=shares]').val(0);
            else
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
