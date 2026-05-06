# Copyright 2025 ADHOC SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Migration hook for l10n_ar_stock_adhoc.

This is the PRIMARY migration mechanism when the module was previously
installed as ``l10n_ar_stock``.  It runs as ``pre_init_hook`` **before**
the ORM loads any model class, so all renames happen at the raw-SQL level.

SUPPORTED SCENARIOS
-------------------
1. **Old module installed** (``l10n_ar_stock`` present in ``ir_module_module``):
   Renames DB columns, updates ``ir_model_data`` / ``ir_model_fields``
   metadata, updates module-dependency rows, and marks the old module
   as uninstalled.  This is the Odoo.sh path: Odoo sees
   ``l10n_ar_stock_adhoc`` as a *new* module and calls this hook before
   trying to create any table or column.

2. **Fresh installation**:
   No existing data — hook exits immediately without touching anything.
"""

import logging

_logger = logging.getLogger(__name__)

_OLD_MODULE = "l10n_ar_stock"
_NEW_MODULE = "l10n_ar_stock_adhoc"

# Stored DB columns that must be renamed.
# Format: (table_name, old_column, new_column)
_COLUMN_RENAMES = [
    # stock.picking
    ("stock_picking", "dispatch_number", "adhoc_dispatch_number"),
    ("stock_picking", "cot_numero_unico", "adhoc_cot_numero_unico"),
    ("stock_picking", "cot_numero_comprobante", "adhoc_cot_numero_comprobante"),
    ("stock_picking", "cot", "adhoc_cot"),
    # stock.book
    ("stock_book", "document_type_id", "adhoc_document_type_id"),
    ("stock_book", "l10n_ar_cai", "adhoc_l10n_ar_cai"),
    ("stock_book", "l10n_ar_cai_due", "adhoc_l10n_ar_cai_due"),
    ("stock_book", "report_partner_id", "adhoc_report_partner_id"),
    ("stock_book", "report_signature_section", "adhoc_report_signature_section"),
    # product.template
    ("product_template", "arba_code", "adhoc_arba_code"),
    # res.company
    ("res_company", "arba_cot", "adhoc_arba_cot"),
    # uom.uom
    ("uom_uom", "arba_code", "adhoc_arba_code"),
    # stock.lot
    ("stock_lot", "dispatch_number", "adhoc_dispatch_number"),
]

# ORM field metadata renames: (model, old_field, new_field)
# Includes both stored and non-stored fields so ir_model_fields stays in sync.
_FIELD_RENAMES = [
    ("stock.picking", "dispatch_number", "adhoc_dispatch_number"),
    ("stock.picking", "document_type_id", "adhoc_document_type_id"),
    ("stock.picking", "cot_numero_unico", "adhoc_cot_numero_unico"),
    ("stock.picking", "cot_numero_comprobante", "adhoc_cot_numero_comprobante"),
    ("stock.picking", "cot", "adhoc_cot"),
    ("stock.picking", "l10n_ar_afip_barcode", "adhoc_l10n_ar_afip_barcode"),
    ("stock.book", "document_type_id", "adhoc_document_type_id"),
    ("stock.book", "l10n_ar_cai", "adhoc_l10n_ar_cai"),
    ("stock.book", "l10n_ar_cai_due", "adhoc_l10n_ar_cai_due"),
    ("stock.book", "report_partner_id", "adhoc_report_partner_id"),
    ("stock.book", "report_signature_section", "adhoc_report_signature_section"),
    ("product.template", "arba_code", "adhoc_arba_code"),
    ("res.company", "arba_cot", "adhoc_arba_cot"),
    ("uom.uom", "arba_code", "adhoc_arba_code"),
    ("stock.lot", "dispatch_number", "adhoc_dispatch_number"),
    ("res.config.settings", "group_arba_cot_enabled", "adhoc_group_arba_cot_enabled"),
    ("res.config.settings", "arba_cot", "adhoc_arba_cot"),
]


def pre_init_hook(env):
    """Prepare the database for l10n_ar_stock_adhoc installation.

    Called by Odoo BEFORE the module's models and data are loaded.
    When ``l10n_ar_stock`` is detected in the database it performs all
    necessary renames so the ORM finds existing data under the new names.
    """
    cr = env.cr
    _logger.info("=" * 60)
    _logger.info("l10n_ar_stock_adhoc: pre_init_hook starting")
    _logger.info("=" * 60)

    if not _module_installed(cr, _OLD_MODULE):
        _logger.info(
            "Module '%s' not found or not installed — fresh install, "
            "nothing to migrate.",
            _OLD_MODULE,
        )
        _logger.info("l10n_ar_stock_adhoc: pre_init_hook finished (no-op)")
        return

    _logger.info(
        "Module '%s' detected — migrating to '%s'", _OLD_MODULE, _NEW_MODULE
    )

    # 1. Rename DB columns
    for table, old_col, new_col in _COLUMN_RENAMES:
        _rename_column(cr, table, old_col, new_col)

    # 2. Move all external IDs to the new module
    cr.execute(
        "UPDATE ir_model_data SET module = %s WHERE module = %s",
        (_NEW_MODULE, _OLD_MODULE),
    )
    _logger.info(
        "Moved %d external IDs: %s -> %s", cr.rowcount, _OLD_MODULE, _NEW_MODULE
    )

    # 3. Rename field entries in ir_model_fields (and their own xmlids)
    for model, old_field, new_field in _FIELD_RENAMES:
        _rename_field_metadata(cr, model, old_field, new_field)

    # 4. Redirect module dependencies that pointed to the old module name
    cr.execute(
        """
        UPDATE ir_module_module_dependency
           SET name = %s
         WHERE name = %s
           AND module_id NOT IN (
               SELECT id FROM ir_module_module WHERE name = %s
           )
        """,
        (_NEW_MODULE, _OLD_MODULE, _OLD_MODULE),
    )
    _logger.info("Updated %d module dependency rows", cr.rowcount)

    # 5. Mark the old module as uninstalled so Odoo does not try to manage it
    _cleanup_old_module(cr, _OLD_MODULE)

    _logger.info("=" * 60)
    _logger.info("l10n_ar_stock_adhoc: pre_init_hook finished")
    _logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _module_installed(cr, module):
    """Return True if *module* is installed or scheduled for upgrade."""
    cr.execute(
        "SELECT 1 FROM ir_module_module "
        "WHERE name = %s AND state IN ('installed', 'to upgrade')",
        (module,),
    )
    return bool(cr.fetchone())


def _column_exists(cr, table, column):
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = %s AND column_name = %s",
        (table, column),
    )
    return bool(cr.fetchone())


def _rename_column(cr, table, old_col, new_col):
    """Rename a column only when the old name exists and the new name does not."""
    if not _column_exists(cr, table, old_col):
        _logger.debug("Column %s.%s not found, skipping rename", table, old_col)
        return
    if _column_exists(cr, table, new_col):
        _logger.info(
            "Column %s.%s already exists — skipping rename from %s",
            table, new_col, old_col,
        )
        return
    cr.execute(
        'ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s"' % (table, old_col, new_col)
    )
    _logger.info("Renamed column %s: %s -> %s", table, old_col, new_col)


def _rename_field_metadata(cr, model, old_field, new_field):
    """Rename a field in ``ir_model_fields`` and update its xmlid."""
    cr.execute(
        "SELECT 1 FROM ir_model_fields WHERE model = %s AND name = %s",
        (model, old_field),
    )
    if not cr.fetchone():
        return
    cr.execute(
        "UPDATE ir_model_fields SET name = %s WHERE model = %s AND name = %s",
        (new_field, model, old_field),
    )
    _logger.info("Renamed field: %s.%s -> %s", model, old_field, new_field)
    # Update the corresponding xmlid (field_<model_u>__<field>)
    model_u = model.replace(".", "_")
    cr.execute(
        "UPDATE ir_model_data SET name = %s "
        "WHERE name = %s AND model = 'ir.model.fields'",
        (
            "field_%s__%s" % (model_u, new_field),
            "field_%s__%s" % (model_u, old_field),
        ),
    )


def _cleanup_old_module(cr, module_name):
    """Remove dependency rows and mark the old module as uninstalled."""
    cr.execute(
        "SELECT id FROM ir_module_module WHERE name = %s", (module_name,)
    )
    row = cr.fetchone()
    if not row:
        return
    module_id = row[0]
    cr.execute(
        "DELETE FROM ir_module_module_dependency WHERE module_id = %s",
        (module_id,),
    )
    cr.execute(
        "UPDATE ir_module_module SET state = 'uninstalled' WHERE id = %s",
        (module_id,),
    )
    _logger.info("Marked module '%s' (id=%d) as uninstalled", module_name, module_id)
