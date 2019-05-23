# coding: utf8
from flask import request

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, RadioField, SelectMultipleField, StringField, TextAreaField
from wtforms import validators
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import DataRequired, Email, Optional, Regexp, URL, Length
from wtforms.widgets import ListWidget, CheckboxInput

from labonneboite.common.load_data import ROME_CODES
from labonneboite.conf import settings


CONTACT_MODES = (
    ('mail', 'Par courrier'),
    ('email', 'Par email'),
    ('phone', 'Par téléphone'),
    ('office', 'Sur place'),
    ('website', 'Via votre site internet'),
)
CONTACT_MODES_LABELS = dict(CONTACT_MODES)
PHONE_REGEX = "^(0|\+33)[1-9]([-. ]?[0-9]{2}){4}$"


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    https://wtforms.readthedocs.io/en/stable/specific_problems.html#specialty-field-tricks
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class OfficeIdentificationForm(FlaskForm):
    siret = StringField(
        'N° de Siret *',
        validators=[
            DataRequired(),
            Regexp('[0-9]{14}', message=("Le siret de l'établissement est invalide (14 chiffres)"))
        ],
        description="14 chiffres, sans espace. Exemple: 36252187900034",
    )

    last_name = StringField('Nom *', validators=[DataRequired()])
    first_name = StringField('Prénom *', validators=[DataRequired()])
    phone = TelField(
        'Téléphone *',
        validators=[DataRequired(), Regexp(PHONE_REGEX)],
        render_kw={"placeholder": "01 77 86 39 49, +331 77 86 39 49"}
    )
    email = EmailField(
        'Adresse email *',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "exemple@domaine.com"}
    )


class OfficeHiddenIdentificationForm(FlaskForm):
    siret = HiddenField('Siret *', validators=[DataRequired()])
    last_name = HiddenField('Nom *', validators=[DataRequired()])
    first_name = HiddenField('Prénom *', validators=[DataRequired()])
    phone = HiddenField(
        'Téléphone *',
        validators=[DataRequired(), Regexp(PHONE_REGEX)],
        render_kw={"placeholder": "01 77 86 39 49, +331 77 86 39 49"}
    )
    email = HiddenField(
        'Adresse email *',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "exemple@domaine.com"}
    )

    def validate_identification(self):
        success = True
        for field in ['siret', 'last_name', 'first_name', 'phone', 'email']:
            if not self._fields[field].validate(self):
                success = False
        return success


class OfficeOtherRequestForm(OfficeHiddenIdentificationForm):
    comment = TextAreaField(
        'Votre message*',
        validators=[DataRequired(), validators.length(max=15000)],
        description="15000 caractères maximum"
    )


class OfficeUpdateJobsForm(OfficeHiddenIdentificationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.office = kwargs.pop('office')
        self.romes_choices = [(rome.code, rome.name) for rome in self.office.romes]

        # Construct choices properties dynamically, depending on ROME codes
        # associated with the current office.
        self.romes_to_keep.choices = self.romes_choices
        self.romes_alternance_to_keep.choices = self.romes_choices

    romes_to_keep = MultiCheckboxField("Intéressé par des candidatures")
    romes_alternance_to_keep = MultiCheckboxField("Métier ouvert à l'alternance")

    def zipped_romes_fields(self):
        return zip(self.romes_to_keep, self.romes_alternance_to_keep)

    def validate(self):
        is_valid = super().validate()
        if not is_valid:
            return False

        # Checked ROME codes.
        romes_to_add = set(self.romes_to_keep.data)
        romes_alternance_to_add = set(self.romes_alternance_to_keep.data)

        # Unchecked ROME codes.
        romes_to_remove = self.office.romes_codes - romes_to_add
        romes_alternance_to_remove = self.office.romes_codes - romes_alternance_to_add

        # ROME codes not present in the default NAF/ROME mapping that a company wants to use.
        # `extra_romes_to_add` and `extra_romes_alternance_to_add` are pupulated via JavaScript.
        # Those fields are defined outside of the form class so we use `request.form` to get them.
        extra_romes_to_add = set([
            rome for rome in request.form.getlist('extra_romes_to_add')
            if rome in settings.ROME_DESCRIPTIONS
        ])
        extra_romes_alternance_to_add = set([
            rome for rome in request.form.getlist('extra_romes_alternance_to_add')
            if rome in settings.ROME_DESCRIPTIONS
        ])

        setattr(self, 'romes_to_add', romes_to_add.union(extra_romes_to_add))
        setattr(self, 'romes_alternance_to_add', romes_alternance_to_add.union(extra_romes_alternance_to_add))
        setattr(self, 'romes_to_remove', romes_to_remove)
        setattr(self, 'romes_alternance_to_remove', romes_alternance_to_remove)

        return True


class OfficeUpdateCoordinatesForm(OfficeHiddenIdentificationForm):
    # Note : we add new_ to avoid conflict with request.args
    new_contact_mode = RadioField('Mode de contact à privilégier', choices=CONTACT_MODES, default='email')
    new_website = StringField(
        'Site Internet',
        validators=[URL(), Optional()], render_kw={"placeholder": "http://exemple.com"}
    )
    new_email = EmailField(
        'Email recruteur',
        validators=[Email(), Optional()], render_kw={"placeholder": "exemple@domaine.com"}
    )
    new_phone = StringField(
        'Téléphone',
        validators=[Optional(), Regexp(PHONE_REGEX)],
        render_kw={"placeholder": "01 77 86 39 49, +331 77 86 39 49"}
    )
    social_network = StringField('Réseau social', validators=[URL(), Optional()])
    new_email_alternance = EmailField(
        'Email recruteur spécialisé alternance',
        validators=[validators.optional(), Email()],
        render_kw={"placeholder": "exemple-alternance@domaine.com"}
    )
    new_phone_alternance = StringField(
        'Téléphone du recruteur spécialisé alternance',
        validators=[validators.optional(), Regexp(PHONE_REGEX)],
        render_kw={"placeholder": "01 77 86 39 49, +331 77 86 39 49"}
    )
    rgpd_consent = BooleanField(
        'En cochant cette case, vous consentez à diffuser des données à caractère personnel sur les services numériques de Pôle emploi.',
        [validators.required()]
    )


class OfficeRemoveForm(OfficeHiddenIdentificationForm):
    remove_lbb = BooleanField(
        'Supprimer mon entreprise du service La Bonne Boite puisque je ne suis pas intéressé-e pour recevoir des candidatures spontanées via ce site',
        [validators.optional()]
    )
    remove_lba = BooleanField(
        'Supprimer mon entreprise du service La Bonne Alternance puisque je ne suis pas intéressé-e pour recevoir des candidatures spontanées via ce site',
        [validators.optional()]
    )
