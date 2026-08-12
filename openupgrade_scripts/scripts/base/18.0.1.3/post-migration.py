# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


def _reset_unavailable_modules(env, module_names):
    modules = env["ir.module.module"].search(
        [
            ("name", "in", module_names),
            ("state", "in", ["to install", "to upgrade"]),
        ]
    )
    if modules:
        modules.write({"state": "uninstalled"})


def _remove_obsolete_fiscalyear_closing(env):
    obsolete_models = [
        "account.fiscalyear.closing.abstract",
        "account.fiscalyear.closing.config.abstract",
        "account.fiscalyear.closing.mapping.abstract",
        "account.fiscalyear.closing.type.abstract",
        "account.fiscalyear.closing",
        "account.fiscalyear.closing.config",
        "account.fiscalyear.closing.mapping",
        "account.fiscalyear.closing.template",
        "account.fiscalyear.closing.config.template",
        "account.fiscalyear.closing.mapping.template",
        "account.fiscalyear.closing.type",
        "account.fiscalyear.closing.type.template",
        "account.fiscalyear.closing.unbalanced.move",
        "account.fiscalyear.closing.unbalanced.move.line",
    ]
    env.cr.execute(
        "SELECT id FROM ir_model WHERE model = ANY(%s)", (obsolete_models,)
    )
    model_ids = [row[0] for row in env.cr.fetchall()]
    env.cr.execute(
        "SELECT id FROM ir_act_window WHERE res_model = ANY(%s)",
        (obsolete_models,),
    )
    action_ids = [row[0] for row in env.cr.fetchall()]
    menu_actions = [f"ir.actions.act_window,{action_id}" for action_id in action_ids]
    menu_ids = []
    if menu_actions:
        env.cr.execute(
            "SELECT id FROM ir_ui_menu WHERE action = ANY(%s)", (menu_actions,)
        )
        menu_ids = [row[0] for row in env.cr.fetchall()]

    if model_ids:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE model = 'ir.model' AND res_id = ANY(%s)",
            (model_ids,),
        )
        env.cr.execute(
            "DELETE FROM ir_rule WHERE model_id = ANY(%s)",
            (model_ids,),
        )
        env.cr.execute(
            "DELETE FROM ir_model_access WHERE model_id = ANY(%s)",
            (model_ids,),
        )
        env.cr.execute(
            "DELETE FROM ir_model_fields WHERE model_id = ANY(%s)",
            (model_ids,),
        )
        env.cr.execute(
            "DELETE FROM ir_model WHERE id = ANY(%s)",
            (model_ids,),
        )

    if action_ids:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE model = 'ir.actions.act_window' AND res_id = ANY(%s)",
            (action_ids,),
        )
        env.cr.execute(
            "DELETE FROM ir_act_window WHERE id = ANY(%s)",
            (action_ids,),
        )

    if menu_ids:
        env.cr.execute(
            "DELETE FROM ir_model_data WHERE model = 'ir.ui.menu' AND res_id = ANY(%s)",
            (menu_ids,),
        )
        env.cr.execute(
            "DELETE FROM ir_ui_menu WHERE id = ANY(%s)",
            (menu_ids,),
        )


def _clear_invalid_user_home_actions(env):
        env.cr.execute(
                """
                UPDATE res_users u
                SET action_id = NULL
                WHERE action_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1
                        FROM ir_actions a
                        WHERE a.id = u.action_id
                    )
                """
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "base", "18.0.1.3/noupdate_changes.xml")
    openupgrade_180.convert_company_dependent(env, "res.partner", "barcode")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["base.module_sale_ebay", "base.module_website_twitter_wall"]
    )
    _reset_unavailable_modules(
        env,
        [
            "spreadsheet_dashboard_purchase_oca",
            "spreadsheet_dashboard_purchase_stock_oca",
        ],
    )
    _clear_invalid_user_home_actions(env)
    _remove_obsolete_fiscalyear_closing(env)
    enterprise_old = env.ref("base.module_account_accountant", raise_if_not_found=False)
    env["ir.model.data"].search(
        [("module", "=", "base"), ("name", "=", "module_account_accountant")]
    ).unlink()
    enterprise_new = env.ref("base.module_accountant", raise_if_not_found=False)
    if (
        enterprise_old
        and enterprise_new
        and enterprise_old.state in ("to install", "to upgrade")
    ):
        enterprise_new.state = "to install"
