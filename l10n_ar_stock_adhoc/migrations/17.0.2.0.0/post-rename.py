##############################################################################
# Post-migration script: l10n_ar_stock -> l10n_ar_stock_adhoc
#
# Runs after the module and its dependencies are fully loaded.
#
# Odoo automatically re-reads and updates standard (noupdate=True) view arches
# from XML files during the module upgrade, so those are already correct.
#
# This script patches any user-customised view arches stored in ir_ui_view
# that may still contain old field names or old module XML IDs.
##############################################################################
import logging

_logger = logging.getLogger(__name__)

# Pairs of (old_substring, new_substring) applied to view arch text
_ARCH_REPLACEMENTS = [
    # module XML ID prefix used in groups="…" attributes and action refs
    ('l10n_ar_stock.arba_cot_enabled',   'l10n_ar_stock_adhoc.arba_cot_enabled'),
    # stock.picking fields
    ('"dispatch_number"',                 '"adhoc_dispatch_number"'),
    ('"cot_numero_unico"',                '"adhoc_cot_numero_unico"'),
    ('"cot_numero_comprobante"',          '"adhoc_cot_numero_comprobante"'),
    ('name="cot"',                        'name="adhoc_cot"'),
    ('for="cot"',                         'for="adhoc_cot"'),
    ('"l10n_ar_afip_barcode"',            '"adhoc_l10n_ar_afip_barcode"'),
    ('name="document_type_id"',           'name="adhoc_document_type_id"'),
    # stock.book fields
    ('name="l10n_ar_cai"',               'name="adhoc_l10n_ar_cai"'),
    ('for="l10n_ar_cai"',                'for="adhoc_l10n_ar_cai"'),
    ('name="l10n_ar_cai_due"',           'name="adhoc_l10n_ar_cai_due"'),
    ('for="l10n_ar_cai_due"',            'for="adhoc_l10n_ar_cai_due"'),
    ('name="report_partner_id"',          'name="adhoc_report_partner_id"'),
    ('for="report_partner_id"',           'for="adhoc_report_partner_id"'),
    ('name="report_signature_section"',   'name="adhoc_report_signature_section"'),
    ('for="report_signature_section"',    'for="adhoc_report_signature_section"'),
    # product.template / uom.uom fields
    ('name="arba_code"',                  'name="adhoc_arba_code"'),
    ('for="arba_code"',                   'for="adhoc_arba_code"'),
    # res.company / res.config.settings fields
    ('name="arba_cot"',                   'name="adhoc_arba_cot"'),
    ('for="arba_cot"',                    'for="adhoc_arba_cot"'),
    ('name="group_arba_cot_enabled"',     'name="adhoc_group_arba_cot_enabled"'),
    ('for="group_arba_cot_enabled"',      'for="adhoc_group_arba_cot_enabled"'),
    # stock.lot field
    ('name="dispatch_number"',            'name="adhoc_dispatch_number"'),
    # QWeb template expressions
    ('o.cot',                             'o.adhoc_cot'),
    ('o.l10n_ar_afip_barcode',            'o.adhoc_l10n_ar_afip_barcode'),
    ('lot_id.dispatch_number',            'lot_id.adhoc_dispatch_number'),
    ("'dispatch_number'",                 "'adhoc_dispatch_number'"),
    ('book_id.l10n_ar_cai',              'book_id.adhoc_l10n_ar_cai'),
    ('book_id.l10n_ar_cai_due',          'book_id.adhoc_l10n_ar_cai_due'),
    ('book_id.report_partner_id',         'book_id.adhoc_report_partner_id'),
    ('book_id.report_signature_section',  'book_id.adhoc_report_signature_section'),
    ('book_id.document_type_id',          'book_id.adhoc_document_type_id'),
]


def migrate(cr, version):
    _logger.info("l10n_ar_stock_adhoc post-migration: patching view arches.")

    # Retrieve IDs of views that belong to this module (after module rename)
    cr.execute(
        """
        SELECT v.id
          FROM ir_ui_view v
          JOIN ir_model_data d
            ON d.model = 'ir.ui.view'
           AND d.res_id = v.id
           AND d.module = 'l10n_ar_stock_adhoc'
        """
    )
    view_ids = [row[0] for row in cr.fetchall()]

    if not view_ids:
        _logger.info(
            "No views found for l10n_ar_stock_adhoc – skipping arch patch."
        )
        return

    patched = 0
    for view_id in view_ids:
        cr.execute(
            "SELECT arch_db FROM ir_ui_view WHERE id = %s", (view_id,)
        )
        row = cr.fetchone()
        if not row or not row[0]:
            continue

        arch = row[0]
        new_arch = arch
        for old, new in _ARCH_REPLACEMENTS:
            new_arch = new_arch.replace(old, new)

        if new_arch != arch:
            cr.execute(
                "UPDATE ir_ui_view SET arch_db = %s WHERE id = %s",
                (new_arch, view_id)
            )
            patched += 1
            _logger.info("Patched arch for ir.ui.view id=%s", view_id)

    _logger.info(
        "l10n_ar_stock_adhoc post-migration: patched %d view arch(es).",
        patched,
    )
