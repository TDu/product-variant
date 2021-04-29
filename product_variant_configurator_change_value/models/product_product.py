# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    # def action_change_variant_attributes(self):
    #     action = self.env.ref(
    #         "product_variant_configurator_change_value.action_variant_change_value"
    #     ).read()[0]
    #     action["context"] = {"product_ids": self.ids}
    #     return action
