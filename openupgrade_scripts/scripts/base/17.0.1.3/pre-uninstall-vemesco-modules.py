from odoo.addons.openupgrade_scripts.scripts.base.module_to_uninstall import MODULES_TO_UNINSTALL
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    # Collect target module names
    target_names = [name for name, _backup in MODULES_TO_UNINSTALL]

    # Log what will be uninstalled
    openupgrade.message(
        env.cr,
        "base",
        "ir_module_module",
        "state",
        "Uninstalling modules (and their downstream dependencies, if any): %s",
        ", ".join(target_names),
    )

    try:
        env.cr.execute("""UPDATE ir_module_module SET state='to remove' WHERE name IN %s""", [tuple(target_names)])
        openupgrade.message(
            env.cr,
            "base",
            "ir_module_module",
            "state",
            "Uninstalled modules: %s",
            ", ".join(target_names),
        )
    except Exception as e:  # noqa: BLE001 - We want to keep migration running and report details
        openupgrade.message(
            env.cr,
            "base",
            "ir_module_module",
            "state",
            "Error while uninstalling modules: %s",
            str(e),
        )
