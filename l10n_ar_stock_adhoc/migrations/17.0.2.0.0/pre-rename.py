##############################################################################
# Migration script: l10n_ar_stock -> l10n_ar_stock_adhoc
#
# This pre-migration script handles:
#   1. Renaming the module itself in ir_module_module / ir_model_data
#   2. Renaming all DB columns for fields that received the adhoc_ prefix
#   3. Renaming field metadata and all indirect references (filters, actions,
#      domains, related fields, …) via upgrade-utils' rename_field helper.
#
# HOW TO RUN
# ----------
# Option A – recommended (Odoo 16+):
#   Run with --pre-upgrade-scripts so the script executes before base loads:
#
#     odoo-bin --pre-upgrade-scripts=\
#       l10n_ar_stock_adhoc/migrations/17.0.2.0.0/pre-rename.py \
#       -u l10n_ar_stock_adhoc ...
#
# Option B – manual SQL before deploying new code:
#   Execute the equivalent SQL statements listed at the bottom of this file.
##############################################################################
import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # ------------------------------------------------------------------ #
    # 1. Rename module
    #    Updates: ir_module_module, ir_module_module_dependency,
    #             ir_model_data (xml_id prefix), ir_model (module column),
    #             ir_model_fields (module column) and more.
    # ------------------------------------------------------------------ #
    if util.module_installed(cr, 'l10n_ar_stock'):
        _logger.info("Renaming module l10n_ar_stock -> l10n_ar_stock_adhoc")
        util.rename_module(cr, 'l10n_ar_stock', 'l10n_ar_stock_adhoc')
    else:
        _logger.info(
            "Module l10n_ar_stock not found in DB – skipping module rename "
            "(fresh install of l10n_ar_stock_adhoc)."
        )
        return   # nothing else to do for a fresh install

    # ------------------------------------------------------------------ #
    # 2. Rename fields (DB columns + ir_model_fields + all references)
    # ------------------------------------------------------------------ #

    # --- stock.picking (table: stock_picking) ---
    # Stored char/many2one fields → DB column rename
    util.rename_field(cr, 'stock.picking', 'dispatch_number',
                      'adhoc_dispatch_number')
    util.rename_field(cr, 'stock.picking', 'cot_numero_unico',
                      'adhoc_cot_numero_unico')
    util.rename_field(cr, 'stock.picking', 'cot_numero_comprobante',
                      'adhoc_cot_numero_comprobante')
    util.rename_field(cr, 'stock.picking', 'cot',
                      'adhoc_cot')
    # Computed (no DB column) and related (no DB column) fields:
    # rename_field handles the metadata update gracefully even for non-stored
    util.rename_field(cr, 'stock.picking', 'l10n_ar_afip_barcode',
                      'adhoc_l10n_ar_afip_barcode')
    util.rename_field(cr, 'stock.picking', 'document_type_id',
                      'adhoc_document_type_id')

    # --- stock.book (table: stock_book) ---
    util.rename_field(cr, 'stock.book', 'document_type_id',
                      'adhoc_document_type_id')
    util.rename_field(cr, 'stock.book', 'l10n_ar_cai',
                      'adhoc_l10n_ar_cai')
    util.rename_field(cr, 'stock.book', 'l10n_ar_cai_due',
                      'adhoc_l10n_ar_cai_due')
    util.rename_field(cr, 'stock.book', 'report_partner_id',
                      'adhoc_report_partner_id')
    util.rename_field(cr, 'stock.book', 'report_signature_section',
                      'adhoc_report_signature_section')

    # --- product.template (table: product_template) ---
    util.rename_field(cr, 'product.template', 'arba_code',
                      'adhoc_arba_code')

    # --- res.company (table: res_company) ---
    util.rename_field(cr, 'res.company', 'arba_cot',
                      'adhoc_arba_cot')

    # --- uom.uom (table: uom_uom) ---
    util.rename_field(cr, 'uom.uom', 'arba_code',
                      'adhoc_arba_code')

    # --- stock.lot (table: stock_lot) ---
    util.rename_field(cr, 'stock.lot', 'dispatch_number',
                      'adhoc_dispatch_number')

    # --- res.config.settings (transient, table: res_config_settings) ---
    # group_arba_cot_enabled is stored; arba_cot is a related (not stored)
    util.rename_field(cr, 'res.config.settings', 'group_arba_cot_enabled',
                      'adhoc_group_arba_cot_enabled')
    util.rename_field(cr, 'res.config.settings', 'arba_cot',
                      'adhoc_arba_cot')

    _logger.info(
        "l10n_ar_stock -> l10n_ar_stock_adhoc: module and field renames done."
    )


# ==========================================================================
# Option B – manual SQL fallback (run BEFORE loading the new code)
# ==========================================================================
# -- 1. Rename module
# UPDATE ir_module_module
#    SET name = 'l10n_ar_stock_adhoc'
#  WHERE name = 'l10n_ar_stock';
#
# UPDATE ir_module_module_dependency
#    SET name = 'l10n_ar_stock_adhoc'
#  WHERE name = 'l10n_ar_stock';
#
# UPDATE ir_model_data
#    SET module = 'l10n_ar_stock_adhoc'
#  WHERE module = 'l10n_ar_stock';
#
# UPDATE ir_model
#    SET module = 'l10n_ar_stock_adhoc'
#  WHERE module = 'l10n_ar_stock';
#
# UPDATE ir_model_fields
#    SET module = 'l10n_ar_stock_adhoc'
#  WHERE module = 'l10n_ar_stock';
#
# -- 2. Rename DB columns
# ALTER TABLE stock_picking  RENAME COLUMN dispatch_number         TO adhoc_dispatch_number;
# ALTER TABLE stock_picking  RENAME COLUMN cot_numero_unico        TO adhoc_cot_numero_unico;
# ALTER TABLE stock_picking  RENAME COLUMN cot_numero_comprobante  TO adhoc_cot_numero_comprobante;
# ALTER TABLE stock_picking  RENAME COLUMN cot                     TO adhoc_cot;
# ALTER TABLE stock_book     RENAME COLUMN document_type_id        TO adhoc_document_type_id;
# ALTER TABLE stock_book     RENAME COLUMN l10n_ar_cai             TO adhoc_l10n_ar_cai;
# ALTER TABLE stock_book     RENAME COLUMN l10n_ar_cai_due         TO adhoc_l10n_ar_cai_due;
# ALTER TABLE stock_book     RENAME COLUMN report_partner_id       TO adhoc_report_partner_id;
# ALTER TABLE stock_book     RENAME COLUMN report_signature_section TO adhoc_report_signature_section;
# ALTER TABLE product_template RENAME COLUMN arba_code             TO adhoc_arba_code;
# ALTER TABLE res_company    RENAME COLUMN arba_cot                TO adhoc_arba_cot;
# ALTER TABLE uom_uom        RENAME COLUMN arba_code               TO adhoc_arba_code;
# ALTER TABLE stock_lot      RENAME COLUMN dispatch_number         TO adhoc_dispatch_number;
# -- res_config_settings is transient; rename only if column exists:
# ALTER TABLE res_config_settings RENAME COLUMN group_arba_cot_enabled TO adhoc_group_arba_cot_enabled;
#
# -- 3. Update ir_model_fields names
# UPDATE ir_model_fields SET name = 'adhoc_dispatch_number'
#  WHERE model = 'stock.picking'  AND name = 'dispatch_number';
# UPDATE ir_model_fields SET name = 'adhoc_cot_numero_unico'
#  WHERE model = 'stock.picking'  AND name = 'cot_numero_unico';
# UPDATE ir_model_fields SET name = 'adhoc_cot_numero_comprobante'
#  WHERE model = 'stock.picking'  AND name = 'cot_numero_comprobante';
# UPDATE ir_model_fields SET name = 'adhoc_cot'
#  WHERE model = 'stock.picking'  AND name = 'cot';
# UPDATE ir_model_fields SET name = 'adhoc_l10n_ar_afip_barcode'
#  WHERE model = 'stock.picking'  AND name = 'l10n_ar_afip_barcode';
# UPDATE ir_model_fields SET name = 'adhoc_document_type_id'
#  WHERE model = 'stock.picking'  AND name = 'document_type_id';
# UPDATE ir_model_fields SET name = 'adhoc_document_type_id'
#  WHERE model = 'stock.book'     AND name = 'document_type_id';
# UPDATE ir_model_fields SET name = 'adhoc_l10n_ar_cai'
#  WHERE model = 'stock.book'     AND name = 'l10n_ar_cai';
# UPDATE ir_model_fields SET name = 'adhoc_l10n_ar_cai_due'
#  WHERE model = 'stock.book'     AND name = 'l10n_ar_cai_due';
# UPDATE ir_model_fields SET name = 'adhoc_report_partner_id'
#  WHERE model = 'stock.book'     AND name = 'report_partner_id';
# UPDATE ir_model_fields SET name = 'adhoc_report_signature_section'
#  WHERE model = 'stock.book'     AND name = 'report_signature_section';
# UPDATE ir_model_fields SET name = 'adhoc_arba_code'
#  WHERE model = 'product.template' AND name = 'arba_code';
# UPDATE ir_model_fields SET name = 'adhoc_arba_cot'
#  WHERE model = 'res.company'    AND name = 'arba_cot';
# UPDATE ir_model_fields SET name = 'adhoc_arba_code'
#  WHERE model = 'uom.uom'        AND name = 'arba_code';
# UPDATE ir_model_fields SET name = 'adhoc_dispatch_number'
#  WHERE model = 'stock.lot'      AND name = 'dispatch_number';
# UPDATE ir_model_fields SET name = 'adhoc_group_arba_cot_enabled'
#  WHERE model = 'res.config.settings' AND name = 'group_arba_cot_enabled';
# UPDATE ir_model_fields SET name = 'adhoc_arba_cot'
#  WHERE model = 'res.config.settings' AND name = 'arba_cot';
