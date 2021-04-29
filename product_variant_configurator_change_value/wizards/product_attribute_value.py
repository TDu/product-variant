# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductAttributeValueWizard(models.TransientModel):
    _name = "product.attribute.value.wizard"
    _description = "aslkdfj"

    # _inherits = {
    #     'product.attribute.value': 'attribute_value_id',
    # }

    product_attribute_value_id = fields.Many2one("product.attribute.value")
    attribute_action = fields.Selection([("delete", "Delete"), ("replace", "Replace"), ("do_nothing", "Do Nothing")], default="do_nothing")
    replaced_by = fields.Many2one("product.attribute.value")
