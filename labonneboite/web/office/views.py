# coding: utf8

from datetime import date
import os
from urllib.parse import urlencode

from slugify import slugify
from sqlalchemy.orm.exc import NoResultFound

from flask import abort, redirect, render_template, flash, jsonify
from flask import Blueprint, current_app
from flask import make_response, send_file
from flask import request, session, url_for

from labonneboite.common import activity
from labonneboite.common import pdf as pdf_util
from labonneboite.common import util
from labonneboite.common.email_util import MandrillClient
from labonneboite.common.models import Office, OfficeAdminAdd, OfficeAdminUpdate, OfficeAdminRemove
from labonneboite.conf import settings
from labonneboite.common.contact_mode import CONTACT_MODE_STAGES
from labonneboite.web.utils import fix_csrf_session

from labonneboite.web.office.forms import OfficeRemovalForm


officeBlueprint = Blueprint('office', __name__)


@officeBlueprint.route('/<siret>/details')
def details(siret):
    """
    Display the details of an office.
    In case the context of a rome_code is given, display appropriate score value for this rome_code
    """
    fix_csrf_session()
    rome_code = request.args.get('rome_code', None)
    company = Office.query.filter_by(siret=siret).first()
    if not company:
        abort(404)

    # Check if company is hidden by SAVE
    if not company.score:
        abort(404)

    context = {
        'company': company,
        'rome_code': rome_code,
    }
    activity.log('details', siret=siret)
    return render_template('office/details.html', **context)


@officeBlueprint.route('/verification-informations-entreprise/<siret>')
def change_info_or_apply_for_job(siret):
    """
    Ask user if he wants to change company information or apply for a job,
    in order to avoid the change_info page to be spammed so much by
    people thinking they are actually applying for a job.
    """
    return render_template('office/change_info_or_apply_for_job.html', siret=siret)


@officeBlueprint.route('/postuler/<siret>')
def apply_for_job(siret):
    """
    If user arrives here, it means we successfully avoided having him spam the
    company modification form. Now we just have to explain him what is wrong.
    """
    return render_template('office/apply_for_job.html', siret=siret)

@officeBlueprint.route('/informations-entreprise', methods=['GET', 'POST'])
def change_info():
    """
    Let a user fill a form to request a removal or information change about an office.
    """
    fix_csrf_session()
    form = OfficeRemovalForm()
    if form.validate_on_submit():
        client = MandrillClient(current_app.extensions['mandrill'])
        client.send(
            """Un email a été envoyé par le formulaire de contact de la Bonne Boite :<br>
            - Action : %s<br>
            - Siret : %s,<br>
            - Prénom : %s,<br>
            - Nom : %s, <br>
            - E-mail : %s,<br>
            - Tél. : %s,<br>
            - Commentaire : %s<br>
            <hr>
            - Status SAVE : %s
            <hr>

            Cordialement,<br>
            La Bonne Boite""" % (
                form.action.data,
                form.siret.data,
                form.first_name.data,
                form.last_name.data,
                form.email.data,
                form.phone.data,
                form.comment.data,
                make_save_suggestion(form)
            )
        )
        msg = "Merci pour votre message, nous reviendrons vers vous dès que possible."
        flash(msg, 'success')

        return redirect(url_for('office.change_info'))
    return render_template('office/change_info.html', form=form)


def detail(siret):
    company = Office.query.filter(Office.siret == siret).one()

    if 'search_args' in session:
        search_url = util.get_search_url('/resultat', session['search_args'])
    else:
        search_url = None
    rome = request.args.get('r')
    if rome not in settings.ROME_DESCRIPTIONS:
        rome = None
        rome_description = None
    else:
        rome_description = settings.ROME_DESCRIPTIONS[rome]

    contact_mode = util.get_contact_mode_for_rome_and_office(rome, company)

    google_search = "%s+%s" % (company.name.replace(' ', '+'), company.city.replace(' ', '+'))
    google_url = "https://www.google.fr/search?q=%s" % google_search

    return {
        'company': company,
        'contact_mode': contact_mode,
        'rome': rome,
        'rome_description': rome_description,
        'google_url': google_url,
        'kompass_url': "http://fr.kompass.com/searchCompanies?text=%s" % company.siret,
        'search_url': search_url,
    }

def make_save_suggestion(form):
    # Save informations
    company = Office.query.filter_by(siret=form.siret.data).first()

    if not company:
        # OfficeAdminRemove already exits ?
        office_admin_remove = OfficeAdminRemove.query.filter_by(siret=form.siret.data).first()
        if office_admin_remove:
            url = url_for("officeadminremove.edit_view", id=office_admin_remove.id, _external=True)
            return "Entreprise retirée via Save : <a href='%s'>Voir la fiche de suppression</a>" % url
        return 'Aucune entreprise trouvée avec le siret %s' % form.siret.data

    # OfficeAdminAdd already exits ?
    office_admin_add = OfficeAdminAdd.query.filter_by(siret=form.siret.data).first()
    if office_admin_add:
        url = url_for("officeadminadd.edit_view", id=office_admin_add.id, _external=True)
        return "Entreprise créée via Save : <a href='%s'>Voir la fiche d'ajout</a>" % url

    # OfficeAdminUpdate already exits ?
    office_admin_update = OfficeAdminUpdate.query.filter(
        OfficeAdminUpdate.sirets.like("%{}%".format(form.siret.data))
    ).first()

    if office_admin_update:
        url = url_for("officeadminupdate.edit_view", id=office_admin_update.id, _external=True)
        return "Entreprise modifiée via Save : <a href='%s'>Voir la fiche de modification</a>" % url


    # No office AdminOffice found : suggest to create an OfficeAdminRemove and OfficeRemoveUpdate
    params = {
        'siret': form.siret.data,
        'name': company.company_name,
        'requested_by_email': form.email.data,
        'requested_by_first_name': form.first_name.data,
        'requested_by_last_name': form.last_name.data,
        'requested_by_phone': form.phone.data,
        'reason': form.comment.data,
    }
    params = {key: value.encode('utf8') for key, value in params.items()}
    if form.action.data == "enlever":
        url = url_for('officeadminremove.create_view', _external=True)
        status_save = " Une suppression a été demandée : <a href='%s'>Créer une fiche de suppression</a>"
    else:
        url = url_for('officeadminupdate.create_view', _external=True)
        status_save = "Entreprise non modifiée via Save : <a href='%s'>Créer une fiche de modification</a>"

    url = "%s?%s" % (url, urlencode(params))
    status_save = status_save % url
    return status_save


@officeBlueprint.route('/<siret>/download')
def download(siret):
    """
    Download the PDF of an office.
    """
    try:
        office = Office.query.filter(Office.siret == siret).one()
    except NoResultFound:
        abort(404)

    activity.log('telecharger-pdf', siret=siret)

    attachment_name = 'fiche_entreprise_%s.pdf' % slugify(office.name, separator='_')
    full_path = pdf_util.get_file_path(office)
    if os.path.exists(full_path):
        return send_file(full_path, mimetype='application/pdf', as_attachment=True, attachment_filename=attachment_name)

    dic = detail(siret)
    office = dic['company']

    contact_mode = dic['contact_mode']
    dic['stages'] = CONTACT_MODE_STAGES.get(contact_mode, [contact_mode])
    dic['date'] = date.today()

    # Render pdf file
    pdf_data = render_template('office/pdf_detail.html', **dic)
    pdf_target = pdf_util.convert_to_pdf(pdf_data)
    data_to_write = pdf_target.getvalue()
    pdf_util.write_file(office, data_to_write)

    # Return pdf
    response = make_response(data_to_write)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % attachment_name
    return response


@officeBlueprint.route('/events/toggle-details/<siret>', methods=['POST'])
def toggle_details_event(siret):
    try:
        Office.query.filter(Office.siret == siret).one()
    except NoResultFound:
        abort(404)

    activity.log('afficher-details', siret=siret)
    return jsonify({})
