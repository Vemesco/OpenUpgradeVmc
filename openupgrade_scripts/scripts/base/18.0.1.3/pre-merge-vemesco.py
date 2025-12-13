from openupgradelib import openupgrade

from odoo.addons.openupgrade_scripts.scripts.base.merged_modules  import MODULES_TO_MERGE



@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.update_module_names(cr, MODULES_TO_MERGE.items(), merge_modules=True)

    for new_module in MODULES_TO_MERGE.keys():
        openupgrade.logged_query(
            cr,"""UPDATE ir_module_module SET state = 'to upgrade' WHERE name = %s""", (new_module,)
        )


    openupgrade.logged_query( cr, """DELETE FROM ir_ui_view WHERE id=2576;""")
    openupgrade.logged_query(cr, """DELETE FROM ir_ui_view WHERE id=2517;""")
