# Copyright 2026
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fix_legacy_account_debitnote_journal_xpath(env):
    """Normalize account_debitnote journal form arch to Odoo 18-safe xpath.

    Some migrated databases keep stale inherited arches (including rewritten
    ones) that target fields not present in the current parent view.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view v
           SET arch_db = jsonb_build_object('en_US', $xml$
                <data>
                    <xpath expr="///field[@name='code']" position="after">
                        <label for="sequence_number_next"/>
                        <div>
                            <field name="sequence_number_next" style="padding-right: 1.0em"/>
                        </div>
                        <field name="refund_sequence" invisible="type in ('sale', 'purchase')" string="Dedicated Credit Note Sequence"/>
                        <label for="refund_sequence_number_next" invisible=" not refund_sequence"/>
                        <field name="refund_sequence_number_next" style="padding-right: 1.0em"/>
                        <field name="debitnote_sequence" invisible="type not in ('sale', 'purchase')"/>
                        <label for="debitnote_sequence_number_next" invisible="type not in ('sale', 'purchase') or debitnote_sequence"/>
                        <div invisible="type not in ('sale', 'purchase') or debitnote_sequence">
                            <field name="debitnote_sequence_number_next" style="padding-right: 1.0em"/>
                            <field name="debitnote_sequence_id" required="0" readonly="True"/>
                        </div>
                    </xpath>
                </data>
            $xml$)
          FROM ir_model_data imd
         WHERE imd.model = 'ir.ui.view'
           AND imd.module = 'account_debitnote'
           AND imd.name = 'view_account_journal_form'
           AND imd.res_id = v.id
           AND (
                v.arch_db::text LIKE '%%journal_entries%%'
                OR v.arch_db::text LIKE '%%///field[@name=''sequence_id'']%%'
                OR v.arch_db::text LIKE '%%///field[@name=''refund_sequence'']%%'
               )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fix_legacy_account_debitnote_journal_xpath(env)
