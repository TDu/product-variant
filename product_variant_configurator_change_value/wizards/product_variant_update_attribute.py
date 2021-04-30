# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models


class ProductVariantUpdateAttributeWizard(models.TransientModel):
    _name = "product.variant.update.attribute.wizard"
    _description = "Wizard to attriubtes on product variants"

    def _default_product_id(self):
        return self.env["product.product"].browse(self._context.get("default_res_ids"))

    def _default_attributes_action_ids(self):
        p = self.env["product.product"].browse(self._context.get("default_res_ids"))
        links = p.product_template_attribute_value_ids
        attribute_ids = links.product_attribute_value_id
        return [(0, 0, {"product_attribute_value_id": x.id, "attribute_action": "do_nothing"}) for x in attribute_ids]

    product_ids = fields.Many2many(
        "product.product", default=lambda self: self._default_product_id()
    )

    attributes_action_ids = fields.Many2many(
        "product.attribute.value.wizard",
        relation="rrhha_rel",
        default=lambda self: self._default_attributes_action_ids()
    )

    def action_change_attributes(self):
        for product in self.product_ids:
            self.update_variant_value(product)

    def is_attribute_value_being_used(self, variant_id, attribute_value):
        """Check if attribute value is still in used on any variant of a template."""
        existing_variants = self.env["product.product"].search(
            [
                ("id", "!=", variant_id.id),
                ("product_tmpl_id", "=", variant_id.product_tmpl_id.id),
            ],
        )
        existing_attributes = existing_variants.mapped(
            "product_template_attribute_value_ids.product_attribute_value_id"
        )
        return attribute_value in existing_attributes

    def update_variant_value(self, product):
        for value in self.attributes_action_ids:
            action = value.attribute_action
            if action == "do_nothing":
                continue
            pav = value.product_attribute_value_id
            # replacing with
            attr_value = value.replaced_by
            if action == "replace" and not attr_value:
                continue
            product_id = product

            TplAttrLine = self.env["product.template.attribute.line"]
            TplAttrValue = self.env["product.template.attribute.value"]
            template = product_id.product_tmpl_id
            print("{} -> {} by {}".format(action, pav, attr_value))
            attr = attr_value.attribute_id
            if attr_value:
                # Find the corresponding attribute line on the template
                # or create it if none is found
                tpl_attr_line = template.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == attr
                )
                if not tpl_attr_line:
                    tpl_attr_line = TplAttrLine.create(
                        {
                            "product_tmpl_id": template.id,
                            "attribute_id": attr.id,
                            "value_ids": [(6, False, [attr_value.id])],
                        }
                    )
                # Ensure that the value exists in this attribute line.
                # The context key 'update_product_template_attribute_values' avoids
                # to create/unlink variants when values are updated on the template
                # attribute line.
                tpl_attr_line.with_context(
                    update_product_template_attribute_values=False
                ).write({"value_ids": [(4, attr_value.id)]})
                # Get (and create if needed) the 'product.template.attribute.value'
                tpl_attr_value = TplAttrValue.search(
                    [
                        ("attribute_line_id", "=", tpl_attr_line.id),
                        ("product_attribute_value_id", "=", attr_value.id),
                    ]
                )
                if not tpl_attr_value:
                    tpl_attr_value = TplAttrValue.create(
                        {
                            "attribute_line_id": tpl_attr_line.id,
                            "product_attribute_value_id": attr_value.id,
                        }
                    )
            # atpv_set = product_id.product_template_attribute_value_ids.product_attribute_value_id
            # Remove the value to change or delete
            # Todo update attribute line
            ptavs = product_id.product_template_attribute_value_ids.filtered(lambda r: r.product_attribute_value_id != pav)
            if action == "replace":
                ptavs |= tpl_attr_value
            product_id.product_template_attribute_value_ids = ptavs

            if not self.is_attribute_value_being_used(product_id, pav):
                tpl_attr_line = template.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == pav.attribute_id
                )
                print("REMOVE VALUE FROM TEMPLATE")

                tpl_attr_line.with_context(
                    update_product_template_attribute_values=False
                ).write({"value_ids": [(3, pav.id)]})
                tpl_attr_value = TplAttrValue.search(
                    [
                        ("attribute_line_id", "=", tpl_attr_line.id),
                        ("product_attribute_value_id", "=", pav.id),
                    ]
                )
                if tpl_attr_value:
                    tpl_attr_value.unlink()
