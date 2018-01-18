"""
Create geolocations and etablissements_backoffice importer tables.

Revision ID: 0592646101eb
Revises: 240900fabe59
Create Date: 2017-11-13 13:52:23.414532
"""
from alembic import op
from sqlalchemy.dialects import mysql
import sqlalchemy as sa

# works - even if there is a pylint warning which says it does not.
from labonneboite.common.env import get_current_env, ENV_LBBDEV

migration_should_run_in_this_environment = get_current_env() != ENV_LBBDEV

# Revision identifiers, used by Alembic.
revision = '0592646101eb'
down_revision = '240900fabe59'
branch_labels = None
depends_on = None


def upgrade():
    if migration_should_run_in_this_environment:
        # ### commands auto generated by Alembic - please adjust! ###
        op.create_table('geolocations',
        sa.Column('full_address', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=False),
        sa.Column('coordinates_x', mysql.FLOAT(), nullable=True),
        sa.Column('coordinates_y', mysql.FLOAT(), nullable=True),
        sa.PrimaryKeyConstraint('full_address'),
        mysql_collate=u'utf8mb4_unicode_ci',
        mysql_default_charset=u'utf8mb4',
        mysql_engine=u'InnoDB'
        )
        op.create_table('etablissements_backoffice',
        sa.Column('siret', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=False),
        sa.Column('raisonsociale', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('enseigne', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('codenaf', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('trancheeffectif', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('numerorue', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('libellerue', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('codepostal', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=11), nullable=True),
        sa.Column('tel', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('email', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('website', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('flag_alternance', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column('flag_junior', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column('flag_senior', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column('flag_handicap', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column('has_multi_geolocations', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
        sa.Column('codecommune', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=191), nullable=True),
        sa.Column('coordinates_x', mysql.FLOAT(), nullable=True),
        sa.Column('coordinates_y', mysql.FLOAT(), nullable=True),
        sa.Column('departement', mysql.VARCHAR(collation=u'utf8mb4_unicode_ci', length=11), nullable=True),
        sa.Column('score', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
        sa.Column('semester-1', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('semester-2', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('semester-3', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('semester-4', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('semester-5', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('semester-6', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('semester-7', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('effectif', mysql.DOUBLE(asdecimal=True), nullable=True),
        sa.Column('score_regr', mysql.FLOAT(), nullable=True),
        sa.PrimaryKeyConstraint('siret'),
        mysql_collate=u'utf8mb4_unicode_ci',
        mysql_default_charset=u'utf8mb4',
        mysql_engine=u'InnoDB'
        )
        # ### end Alembic commands ###


def downgrade():
    if migration_should_run_in_this_environment:
        # ### commands auto generated by Alembic - please adjust! ###
        op.drop_table('geolocations')
        op.drop_table('etablissements_backoffice')
        # ### end Alembic commands ###


