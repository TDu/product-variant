# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ProductAttributeValueWizard(models.TransientModel):
    _name = "product.attribute.value.wizard"
    _description = "wizard action on product attribute value"

    product_attribute_value_id = fields.Many2one("product.attribute.value")
    attribute_action = fields.Selection(
        [
            ("delete", "Delete"),
            ("replace", "Replace"),
            ("do_nothing", "Do Nothing")
        ],
        default="do_nothing",
        required=True,
    )
    replaced_by = fields.Many2one(
        "product.attribute.value",
        string="Replace by"
    )
    # replaced_by = fields.Many2one("product.attribute.value", compute="_compute_replaced_by", readonly=False)

    # @api.depends("attribute_action")
    # def _compute_replaced_by(self):
    #     for rec in self:
    #         if rec.attribute_action != "replace":
    #             rec.replaced_by = False
    #         else:
    #             rec.replaced_by = rec.replaced_by
