# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _replace_removed_social_googleplus_in_views(env):
    """Drop references to removed social_googleplus fields in website QWeb."""
    openupgrade.logged_query(
        env.cr,
        """
        WITH candidate AS (
            SELECT
                v.id,
                jsonb_object_agg(
                    kv.key,
                    replace(
                        replace(kv.value, 'website.social_googleplus', 'False'),
                        'company.social_googleplus',
                        'False'
                    )
                ) AS new_arch
            FROM ir_ui_view v
            CROSS JOIN LATERAL jsonb_each_text(v.arch_db) kv
            WHERE v.arch_db::text LIKE '%social_googleplus%'
            GROUP BY v.id
        )
        UPDATE ir_ui_view v
        SET arch_db = c.new_arch,
            write_uid = 1,
            write_date = NOW()
        FROM candidate c
        WHERE v.id = c.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _replace_removed_social_googleplus_in_views(env)