# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_renamed_xmlids = [
    (
        "base.lang_sr_RS",
        "base.lang_sr@Cyrl",
    ),
    (
        "spreadsheet_dashboard.dashboard_management",
        "base.module_category_productivity_dashboard",
    ),
]

_non_installable_modules = [
    "account_statement_import_file",
    "spreadsheet_dashboard_purchase_oca",
    "spreadsheet_dashboard_purchase_stock_oca",
    "website_project_issue_sheet",
]

_force_uninstall_modules = [
    "account_fiscal_year_closing",
]

_obsolete_modules = [
    "account_debitnote",
]


def _fix_list_view_type(cr):
    """
    Former tree views have view type list now.

    It's not strictly necessary to change this, but squelches a lot of warnings
    in the log
    """
    openupgrade.logged_query(cr, "UPDATE ir_ui_view SET type='list' WHERE type='tree'")


def _fix_list_view_mode(cr):
    """
    Previous actions had a default value of tree,form, but now the default is list,form.
    If any records do not define this field explicitly,
    the default value from the previous version is kept, which causes an error.
    """
    openupgrade.logged_query(
        cr,
        r"""UPDATE ir_act_window
            SET view_mode = REGEXP_REPLACE(view_mode, '(^|,)tree(,|$)', '\1list\2', 'g')
        WHERE view_mode ~ '(^|,)tree(,|$)'
        """,
    )


def _fix_serbian_res_lang_record(cr):
    """
    ISO code of Serbian (Cyrillic) has been changed
    """
    openupgrade.logged_query(
        cr, "UPDATE res_lang SET code='sr@Cyrl', iso_code='sr@Cyrl' WHERE code='sr_RS'"
    )


def _fix_company_layout_background(cr):
    """
    res.company#layout_background has lost the geometric option
    """
    openupgrade.logged_query(
        cr,
        "UPDATE res_company SET layout_background='Blank' "
        "WHERE layout_background='Geometric'",
    )


def _clear_non_installable_module_states(cr):
    """Avoid module graph warnings for missing/non-installable modules."""
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_module_module
           SET state = 'uninstalled'
         WHERE name = ANY(%s)
           AND state IN ('to install', 'to upgrade', 'to remove', 'installed')
        """,
        (_non_installable_modules,),
    )
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
         WHERE model = 'ir.module.module'
           AND module = 'base'
           AND name = ANY(%s)
        """,
        (tuple(f"module_{name}" for name in _non_installable_modules),),
    )
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_module_module
         WHERE name = ANY(%s)
        """,
        (_non_installable_modules,),
    )


def _force_uninstall_conflicting_modules(cr):
    """Neutralize conflicting modules that can break module graph resolution."""
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_module_module
           SET state = 'uninstalled'
         WHERE name = ANY(%s)
           AND state IN ('to install', 'to upgrade', 'to remove', 'installed')
        """,
        (_force_uninstall_modules,),
    )


def _remove_obsolete_modules(cr):
    """Remove stale module rows that should not exist in v18."""
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_module_module
           SET state = 'uninstalled'
         WHERE name = ANY(%s)
        """,
        (_obsolete_modules,),
    )
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
         WHERE model = 'ir.module.module'
           AND module = 'base'
           AND name = ANY(%s)
        """,
        (tuple(f"module_{name}" for name in _obsolete_modules),),
    )
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_module_module
         WHERE name = ANY(%s)
        """,
        (_obsolete_modules,),
    )


def _bind_vmc_risk_classes_decimal_precision_xmlid(cr):
    """Avoid duplicate decimal precision creation for reruns.

    If the decimal precision Risk Classes already exists from a prior run,
    create its expected XML-ID so subsequent loads update instead of insert.
    """
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
        SELECT 'vmc_l10n_co_hr_payroll_rules',
               'vmc_decimal_risk_clases',
               'decimal.precision',
               dp.id,
               TRUE
          FROM decimal_precision dp
         WHERE dp.name = 'Risk Classes'
           AND NOT EXISTS (
                SELECT 1
                  FROM ir_model_data imd
                 WHERE imd.module = 'vmc_l10n_co_hr_payroll_rules'
                   AND imd.name = 'vmc_decimal_risk_clases'
           )
        """,
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    _clear_non_installable_module_states(cr)
    _force_uninstall_conflicting_modules(cr)
    _remove_obsolete_modules(cr)
    openupgrade.logged_query(
        cr,
        f"""
        CREATE TABLE {openupgrade.get_legacy_name("ir_module_module")
            } AS (SELECT name, state FROM ir_module_module);
        """,
    )
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    openupgrade.clean_transient_models(cr)
    openupgrade.rename_xmlids(cr, _renamed_xmlids)
    _fix_list_view_type(cr)
    _fix_list_view_mode(cr)
    _fix_serbian_res_lang_record(cr)
    _fix_company_layout_background(cr)
    _bind_vmc_risk_classes_decimal_precision_xmlid(cr)
