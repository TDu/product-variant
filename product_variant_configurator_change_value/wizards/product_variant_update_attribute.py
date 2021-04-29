# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductVariantUpdateAttributeWizard(models.TransientModel):
    _name = "product.variant.update.attribute.wizard"
    _description = "Wizard to attriubtes on product variants"

    # def _default_product_tmpl_id(self):
    #     return self.env["product.template"].browse(self._context.get("product_tmpl_id"))

    # def _default_product_pricelist_item_id(self):
    #     if self._context.get("active_model") != "product.pricelist.item":
    #         return False
    #     return self.env["product.pricelist.item"].browse(self._context.get("active_id"))

    # def _default_product_supplierinfo_id(self):
    #     if self._context.get("active_model") != "product.supplierinfo":
    #         return False
    #     return self.env["product.supplierinfo"].browse(self._context.get("active_id"))

    def _default_product_id(self):
        return self.env["product.product"].browse(self._context.get("default_res_ids"))

    def _default_attributes_action_ids(self):
        p = self.env["product.product"].browse(self._context.get("default_res_ids"))
        links = p.product_template_attribute_value_ids
        attribute_ids = links.product_attribute_value_id
        return [(0, 0, {"product_attribute_value_id": x.id, "attribute_action": "do_nothing"}) for x in attribute_ids]
    # product_tmpl_id = fields.Many2one(
    #     "product.template", default=lambda self: self._default_product_tmpl_id()
    # )
    product_ids = fields.Many2many(
        "product.product", default=lambda self: self._default_product_id()
    )
    product_attribute_value_ids = fields.Many2many("product.attribute.value", compute="_compute_product_attribute_value_ids", readonly=False)
    #     "product.pricelist.item",
    #     default=lambda self: self._default_product_pricelist_item_id(),
    # )

    # attributes_action_ids = fields.Many2many("product.attribute.value.wizard", compute="_compute_attributes_action_ids", readonly=False)
    attributes_action_ids = fields.Many2many("product.attribute.value.wizard", relation="rrhha_rel", default=lambda self: self._default_attributes_action_ids())

    # product_supplierinfo_id = fields.Many2one(
    #     "product.supplierinfo",
    #     default=lambda self: self._default_product_supplierinfo_id(),
    # )
    # product_variant_ids = fields.One2many(
    #     "product.product",
    #     "product_tmpl_id",
    #     related="product_tmpl_id.product_variant_ids",
    # )
    # selected_packaging_id = fields.Many2one(
    #     "product.packaging", domain="[('product_id', 'in', product_variant_ids)]",
    # )
    # packaging_price = fields.Float("Package Price", default=0.0, digits="Product Price")
    # unit_price = fields.Float(
    #     "Unit Price",
    #     compute="_compute_unit_price",
    #     readonly=True,
    #     digits="Product Price",
    # )
    # current_unit_price = fields.Float(
    #     compute="_compute_current_unit_price", digits="Product Price"
    # )
    # packaging_ids = fields.One2many(
    #     "product.packaging",
    #     string="Product Packages",
    #     compute="_compute_packaging_ids",
    # )
    warning_message = fields.Char(readonly=True, default=" ")

    @api.depends("product_ids")
    def _compute_product_attribute_value_ids(self):
        links = self.product_ids.product_template_attribute_value_ids
        attribute_ids = links.product_attribute_value_id
        self.product_attribute_value_ids = attribute_ids # self.env["product.attribute.value"].browse(attribute_ids)

    @api.depends("product_ids.product_attribute_value_ids.product_attribute_value_id")
    def _compute_attributes_action_ids(self):
        # It is called multiple times ?
        # It is called after the click on save button ?!
        links = self.product_ids.product_template_attribute_value_ids
        attribute_ids = links.product_attribute_value_id
        self.attributes_action_ids = [(0, 0, {"product_attribute_value_id": x.id, "attribute_action": "delete"}) for x in attribute_ids]

        # self.product_attribute_value_ids = attribute_ids # self.env["product.attribute.value"].browse(attribute_ids)
    # @api.depends(
    #     "product_pricelist_item_id", "product_supplierinfo_id", "product_tmpl_id"
    # )
    # def _compute_current_unit_price(self):
    #     """Compute the original unit price, the one  that the calculator will change."""
    #     if self.product_pricelist_item_id:
    #         self.current_unit_price = self.product_pricelist_item_id.fixed_price
    #     elif self.product_supplierinfo_id:
    #         self.current_unit_price = self.product_supplierinfo_id.price
    #     elif self.product_id:
    #         self.current_unit_price = self.product_id.lst_price
    #     else:
    #         self.current_unit_price = self.product_tmpl_id.list_price

    # @api.depends("unit_price")
    # def _compute_package_prices(self):
    #     for pack in self.packaging_ids:
    #         pack.packaging_wizard_price = self.unit_price * pack.qty

    # @api.depends("product_tmpl_id")
    # def _compute_packaging_ids(self):
    #     self.packaging_ids = self.product_tmpl_id.mapped(
    #         "product_variant_ids.packaging_ids"
    #     )

    def action_change_attributes(self):
        for value in self.attributes_action_ids:
            print("{}, {} ".format(value.attribute_action, value.product_attribute_value_id.name))
            # if value.attribute_action == "delete":
            self.remove_attribute_value_on_variant(value)

    def remove_attribute_value_on_variant(self, value):
        # Lets deal with one product ideally all variant of a template
        if not self.product_ids:
            return
        pav = value.product_attribute_value_id
        action = value.attribute_action
        # replacing with
        attr_value = value.replaced_by
        if action == "do_nothing":
            return
        product_id = self.product_ids[0]

        TplAttrLine = self.env["product.template.attribute.line"]
        TplAttrValue = self.env["product.template.attribute.value"]
        template = product_id.product_tmpl_id

        if attr_value:
            # Find the corresponding attribute line on the template
            # or create it if none is found
            attr = attr_value.attribute_id
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
