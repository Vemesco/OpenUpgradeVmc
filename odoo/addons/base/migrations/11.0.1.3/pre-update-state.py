# -*- coding: utf-8 -*-

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Dara from res.country.state is founded in l10n_co_cities. Pending to be removed (l10n_co_cities).
    env.cr.execute(
        """
        UPDATE ir_model_data
        SET module='base'
        WHERE id IN (SELECT ir_model_data.id AS data_id
                     FROM ir_model_data
                              JOIN public.res_country_state cs ON cs.id = ir_model_data.res_id
                     WHERE model = 'res.country.state'
                       AND cs.country_id = 50
                     ORDER BY ir_model_data.name)
        """)
