# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestProductVariantChangeAttributeValue(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.attribute_steel = cls.env.ref("product.product_attribute_value_1")
        cls.attribute_aluminium = cls.env.ref("product.product_attribute_value_2")
        cls.variant_1 = cls.env.ref("product.product_product_4")
        cls.wizard = cls.env["product.variant.update.attribute.wizard"]

    def test_remove_attribure_value(self):
        self.wizard_1 = self.wizard.with_context(
            default_res_ids=self.variant_1.ids
        ).create({})
        changes = self.wizard_1.attributes_action_ids
        changes[0].attribute_action = "delete"
        ptav = changes[0].product_attribute_value_id
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertTrue(ptav in vals)
        self.wizard_1.action_change_attributes()
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertFalse(ptav in vals)

    def test_change_attribure_value(self):
        self.wizard_1 = self.wizard.with_context(
            default_res_ids=self.variant_1.ids
        ).create({})
        changes = self.wizard_1.attributes_action_ids
        changes[0].attribute_action = "replace"
        changes[0].replaced_by = self.attribute_aluminium
        ptav = changes[0].product_attribute_value_id
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertTrue(ptav in vals)
        self.assertFalse(self.attribute_aluminium in vals)
        self.wizard_1.action_change_attributes()
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertFalse(ptav in vals)
        self.assertTrue(self.attribute_aluminium in vals)
