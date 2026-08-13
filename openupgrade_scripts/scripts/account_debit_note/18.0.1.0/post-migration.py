# Copyright 2026
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fix_legacy_account_debitnote_journal_xpath(env):
    """Fix stale account_debitnote xpaths targeting removed journal_entries page.

    Some migrated databases keep an old view architecture for
    `account_debitnote.view_account_journal_form` that references
    `/form/sheet/notebook//page[@name='journal_entries']`, which no longer exists
    in Odoo 18.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view v
           SET arch_db = replace(
                        replace(
                        replace(
                        replace(v.arch_db::text,
                            '/form/sheet/notebook//page[@name=''''journal_entries'''']/group//group[1]/field[@name=''''refund_sequence'''']',
                            '///field[@name=''''refund_sequence'''']'
                        ),
                            '/form/sheet/notebook//page[@name=''''journal_entries'''']/group//group[1]/field[@name=''''sequence_id'''']',
                            '///field[@name=''''sequence_id'''']'
                        ),
                            '/form/sheet/notebook//page[@name=''''journal_entries'''']/group//group[1]/field[@name=''''refund_sequence_id'''']',
                            '///field[@name=''''refund_sequence_id'''']'
                        ),
                            '/form/sheet/notebook//page[@name=''''journal_entries'''']/group//group[1]/field[@name=''''code'''']',
                            '///field[@name=''''code'''']'
                        )::jsonb
          FROM ir_model_data imd
         WHERE imd.model = 'ir.ui.view'
           AND imd.module = 'account_debitnote'
           AND imd.name = 'view_account_journal_form'
           AND imd.res_id = v.id
           AND v.arch_db::text LIKE '%%journal_entries%%'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fix_legacy_account_debitnote_journal_xpath(env)
