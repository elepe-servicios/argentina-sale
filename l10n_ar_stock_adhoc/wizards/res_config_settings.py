from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    adhoc_group_arba_cot_enabled = fields.Boolean(
        "Usar COT de ARBA?",
        help='Permite generar el COT de arba una vez que se han asignado '
        'números de remitos en las entregas',
        implied_group='l10n_ar_stock_adhoc.arba_cot_enabled',
    )
    adhoc_arba_cot = fields.Char(
        related='company_id.adhoc_arba_cot',
        readonly=False,
    )
