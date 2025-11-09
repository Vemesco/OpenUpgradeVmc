
from openupgradelib import openupgrade


model_renames = [
    ("alfa.amb_risk_classes", "vmc.risk.classes"),
]

table_renames = [
    ("alfa_amb_risk_classes", "vmc_risk_classes"),
]

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
