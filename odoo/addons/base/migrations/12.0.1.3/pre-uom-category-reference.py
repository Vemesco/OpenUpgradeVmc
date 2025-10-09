
from openupgradelib import openupgrade

_column_copies = {
    'uom_uom': [
        ('uom_type', 'uom_type_v12', None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)

    env.cr.execute(
        """
        UPDATE uom_uom
        SET uom_type = 'reference'
        WHERE id IN (SELECT res_id
                     FROM ir_model_data
                     WHERE name IN ('product_uom_hour', 'product_uom_day') AND model = 'uom.uom')
          AND uom_type != 'reference';
        """
    )
