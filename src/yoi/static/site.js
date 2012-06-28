var formatAmount = function(amt) {
    return (amt >= 0 ? '+' : '') + amt.toFixed(2);
};
$.fn.yoi_entry_editor = function() {
    var self = this;

    var update_share_descriptions = function() {
        var payer = self.find('input[name=payer]').val();

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
    update_share_descriptions();
};

$(document).ready(function() {
    $('.entry-editor').yoi_entry_editor();
});
