# Migración de `l10n_ar_stock_adhoc`: V17 → V19

## Resumen

Este documento describe los cambios realizados para migrar el módulo
`l10n_ar_stock_adhoc` de **Odoo 17.0** a **Odoo 19.0**, siguiendo las guías
oficiales de OCA:

- [Migration to version 18.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0)
- [Migration to version 19.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0)

---

## Cambios realizados

### 1. Bump de versión (`__manifest__.py`)

La versión del módulo se actualizó de `17.0.2.0.0` a `19.0.1.0.0`, de acuerdo
con el esquema `<odoo_version>.1.0.0` requerido por OCA para módulos migrados.

### 2. Eliminación de la carpeta `migrations/17.0.2.0.0/`

Según las guías de OCA, al migrar a una nueva versión principal se deben
eliminar todos los scripts de migración de versiones anteriores. Se eliminó la
carpeta `migrations/17.0.2.0.0/` que contenía los scripts `pre-rename.py` y
`post-rename.py`. El `pre_init_hook` definido en `hooks.py` sigue siendo válido
para instalaciones nuevas sobre bases con el módulo `l10n_ar_stock` (módulo
predecesor renombrado).

### 3. Reemplazo de `<tree>` por `<list>` en vistas XML (cambio V18)

En Odoo 18, el elemento `<tree>` en los arches de vistas fue renombrado a
`<list>`. Se actualizó `views/uom_uom_views.xml` en la vista
`product_uom_tree_view` (herencia de `uom.product_uom_tree_view`): el elemento
raíz del arch pasó de `<tree>` a `<list>`.

**Archivo:** `views/uom_uom_views.xml`

```xml
<!-- Antes (V17) -->
<tree>
    <field name="adhoc_arba_code" optional="show"/>
    <button name="action_arba_codes" .../>
</tree>

<!-- Después (V19) -->
<list>
    <field name="adhoc_arba_code" optional="show"/>
    <button name="action_arba_codes" .../>
</list>
```

> **Nota:** Los XML-IDs que contienen la palabra `tree`
> (p. ej. `product_uom_tree_view`, `view_production_lot_tree`) se conservan sin
> cambios, en línea con la recomendación de OCA de no renombrarlos para evitar
> romper dependencias en otros módulos.

### 4. Corrección de nombres de campos en `data/product_uom_data.xml`

El archivo de datos iniciales de unidades de medida referenciaba el campo con
el nombre anterior (`arba_code`) en lugar del nombre correcto del campo
definido en el modelo (`adhoc_arba_code`). Esto causaría un error al instalar
el módulo desde cero. Se corrigieron los cuatro registros afectados.

**Archivo:** `data/product_uom_data.xml`

| Campo anterior | Campo corregido    |
|----------------|--------------------|
| `arba_code`    | `adhoc_arba_code`  |

### 5. Actualización de la firma de `_load` en `account_chart_template.py` (V19)

En Odoo 19, el método `account.chart.template._load` incorpora el parámetro
adicional `force_create=True`. El override del módulo sólo aceptaba tres
parámetros posicionales y no propagaba el nuevo parámetro a `super()`, lo que
causaría un `TypeError` en tiempo de ejecución al instalar el plan contable.

**Archivo:** `models/account_chart_template.py`

```python
# Antes (V17)
def _load(self, template_code, company, install_demo):
    ...
    return super(AccountChartTemplate, self)._load(template_code, company, install_demo)

# Después (V19)
def _load(self, template_code, company, install_demo, force_create=True):
    ...
    return super(AccountChartTemplate, self)._load(
        template_code, company, install_demo, force_create
    )
```

### 6. Eliminación de la herencia `product_uom_categ_form_view` (V19)

En Odoo 19, el módulo `uom` ya no incluye la vista
`uom.product_uom_categ_form_view` (el fichero `uom_category_views.xml` fue
eliminado). Además, la herencia original era incorrecta: intentaba insertar el
campo `adhoc_arba_code` (perteneciente a `uom.uom`) en un formulario de
`uom.category`. Se eliminó por completo el record correspondiente de
`views/uom_uom_views.xml`.

### 7. Corrección del anchor xpath en la vista de formulario `uom.uom` (V19)

En Odoo 19, el campo `rounding` desapareció de la vista `product_uom_form_view`
(pasó a ser un campo computed sin representación en el formulario). El inherit
que usaba `<field name="rounding" position="after">` como anchor fallaba al no
encontrar ese nodo. Se actualizó para usar `<group name="uom_details" position="inside">`.

**Archivo:** `views/uom_uom_views.xml`

```xml
<!-- Antes (V17) -->
<field name="rounding" position="after">
    <label for="adhoc_arba_code"/>
    ...
</field>

<!-- Después (V19) -->
<group name="uom_details" position="inside">
    <label for="adhoc_arba_code"/>
    ...
</group>
```

---

## Consideraciones especiales

### Compatibilidad con el módulo predecesor `l10n_ar_stock`

El `pre_init_hook` en `hooks.py` maneja el escenario en que la base de datos
tiene instalado el módulo `l10n_ar_stock` (predecesor de `l10n_ar_stock_adhoc`).
El hook renombra columnas de base de datos, actualiza `ir_model_data` e
`ir_model_fields` y marca el módulo anterior como desinstalado. Este mecanismo
**sigue siendo necesario y válido en V19** para bases migradas desde V14/V15/V16.

### Cambios V18 relevantes revisados y no aplicables a este módulo

Los siguientes cambios indicados por la guía OCA V18 fueron revisados y
**no requieren modificación** en este módulo:

- `user_has_groups` → `self.env.user.has_group`: no se usa en el módulo.
- `check_access_rights` / `check_access_rule` → `check_access`: no se usan.
- `_name_search` → `_search_display_name`: no se sobreescribe.
- `group_operator` → `aggregator` en campos: no se usa el atributo.
- `<div class="oe_chatter">` → `<chatter />`: no hay vistas con chatter en el módulo.
- `tree_view_ref` → `list_view_ref` en contextos: no se usa en ningún contexto.
- `/** @odoo-module **/` en archivos JS: el módulo no tiene assets JS propios.

### Cambios V19 relevantes revisados y no aplicables a este módulo

- `groups_id` → `group_ids` en records de vistas/menús/acciones: el módulo
  usa el atributo `groups="..."` en XML (válido), no el campo `groups_id`.
- `self._cr` / `self._uid` / `self._context`: no se usan.
- `odoo.osv.expression` → `odoo.fields.Domain`: no se importa ni se usa.
- `_sql_constraints` → `models.Constraint` / `models.UniqueIndex`: no se
  definen constraints SQL en el módulo.
- `read_group` → `_read_group` / `formatted_read_group`: no se usa.
- `type="json"` → `type="jsonrpc"` en controladores: el módulo no tiene
  controladores HTTP.
- `args` → `domain` en `name_search`: no se sobreescribe `name_search`.
- `toggle_active` → `action_archive` / `action_unarchive`: no se usa.

### Dependencia `pyafipws`

El módulo depende de la librería externa `pyafipws` (importada con guard
`try/except`). Verificar que la versión de `pyafipws` instalada en el entorno
V19 sea compatible con Python 3.12+ (versión de Python usada por Odoo 19).

---

## Checklist de migración OCA

| Tarea                                                                 | Estado     |
|-----------------------------------------------------------------------|------------|
| Bump de versión a `19.0.1.0.0`                                        | ✅ Hecho   |
| Eliminar `migrations/` de versión anterior                            | ✅ Hecho   |
| Reemplazar `<tree>` por `<list>` en arches de vistas                  | ✅ Hecho   |
| Verificar `user_has_groups` → `self.env.user.has_group`               | ✅ N/A     |
| Verificar `groups_id` → `group_ids` en records V19                    | ✅ N/A     |
| Verificar `self._cr` / `self._uid` / `self._context`                  | ✅ N/A     |
| Verificar `odoo.osv.expression` → `odoo.fields.Domain`                | ✅ N/A     |
| Verificar `_sql_constraints` → `models.Constraint`                    | ✅ N/A     |
| Verificar `read_group` → `_read_group`                                | ✅ N/A     |
| Corregir nombres de campos en archivos de datos                       | ✅ Hecho   |
| Actualizar firma `_load` en `account_chart_template.py` (V19)         | ✅ Hecho   |
| Eliminar herencia `product_uom_categ_form_view` inexistente en V19     | ✅ Hecho   |
| Corregir anchor xpath `rounding` → `group uom_details` en V19         | ✅ Hecho   |
