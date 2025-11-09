
from openupgradelib import openupgrade


_column_renames = {
    "account_asset_asset": [("invoice_id", "account_asset_management_legacy_8_invoice_id")],
}

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
