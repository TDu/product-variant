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
        return [(0, 0, {"product_attribute_value_id": x.id, "attribute_action": "delete"}) for x in attribute_ids]
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
        print("change attributes")
        for value in self.attributes_action_ids:
            # if value.attribute_action == "delete":
            print("{}, {} ".format(value.attribute_action, value.product_attribute_value_id.name))
