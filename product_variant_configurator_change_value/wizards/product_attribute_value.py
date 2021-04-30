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
