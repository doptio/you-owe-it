from flaskext import wtf
from flaskext.wtf import Form, Field, IntegerField, BooleanField, \
                         DateField, DecimalField, FileField
from flaskext.wtf import Required, Optional, Length, NumberRange, Email, \
                         Regexp, AnyOf

class DecimalField(wtf.DecimalField):
    'A decial field that treats "," and "." alike.'

    def process_formdata(self, formdata):
        formdata = [fd.replace(',', '.') for fd in formdata]
        super(DecimalField, self).process_formdata(formdata)

class TextField(wtf.TextField):
    'A non-retarded text field.'

    def process_formdata(self, formdata):
        super(TextField, self).process_formdata(formdata)
        if self.data:
            self.data = self.data.strip()

class ListOf(Field):
    'I am a pseudo-field that can only parse incoming form data.'

    def __init__(self, unbound_field, **kwargs):
        super(ListOf, self).__init__(**kwargs)
        self.subfield = unbound_field.bind(form=None, name='')

    def process(self, formdata):
        self.data = []
        for data in formdata.getlist(self.name):
            self.subfield.process_formdata([data])
            self.data.append(self.subfield.data)
