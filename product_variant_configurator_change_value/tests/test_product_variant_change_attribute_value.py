# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestProductVariantChangeAttributeValue(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.legs = cls.env.ref("product.product_attribute_1")
        cls.steel = cls.env.ref("product.product_attribute_value_1")
        cls.aluminium = cls.env.ref("product.product_attribute_value_2")

        cls.color = cls.env.ref("product.product_attribute_2")
        cls.white = cls.env.ref("product.product_attribute_value_3")
        cls.black = cls.env.ref("product.product_attribute_value_4")
        cls.pink = cls.env["product.attribute.value"].create({
            "name": "Pink",
            "attribute_id": cls.color.id
        })

        cls.variant_1 = cls.env.ref("product.product_product_4")
        cls.variant_2 = cls.env.ref("product.product_product_4b")
        cls.variant_3 = cls.env.ref("product.product_product_4c")
        cls.variant_4 = cls.env.ref("product.product_product_4d")
        cls.variants = [cls.variant_1.id, cls.variant_2.id, cls.variant_3.id, cls.variant_4.id]

        cls.wizard = cls.env["product.variant.update.attribute.wizard"]

    def change_action(self, value, action, replace_by=False):
        "Set an action to do on an attribute value."
        actions = self.wizard_1.attributes_action_ids
        action_id = actions.filtered(lambda r: r.product_attribute_value_id == value)
        action_id.attribute_action = action
        action_id.replaced_by = replace_by

    def check_template_attribute_value(self, product, attr_value):
        """Check if attribute value is assigned to the template."""
        template = product.product_tmpl_id
        attr = attr_value.attribute_id
        tpl_attr_line = template.attribute_line_ids.filtered(
            lambda l: l.attribute_id == attr
        )
        if not tpl_attr_line:
            return False
        tpl_attr_value = self.env["product.template.attribute.value"].search(
            [
                ("attribute_line_id", "=", tpl_attr_line.id),
                ("product_attribute_value_id", "=", attr_value.id),
            ]
        )
        if not tpl_attr_value:
            return False
        return True

    def test_remove_attribure_value(self):
        """ """
        self.wizard_1 = self.wizard.with_context(
            default_res_ids=self.variants
        ).create({})
        self.change_action(self.steel, "delete")
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertTrue(self.steel in vals)
        self.wizard_1.action_change_attributes()
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertFalse(self.steel in vals)
        # Fix me
        # self.assertFalse(self.check_template_attribute_value(self.variant_1, self.steel))

    def test_change_attribure_value(self):
        self.wizard_1 = self.wizard.with_context(
            default_res_ids=self.variants
        ).create({})
        self.change_action(self.steel, "replace", self.aluminium)
        # self.change_action(self.white, "replace", self.pink)
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertTrue(self.steel in vals)
        self.assertFalse(self.aluminium in vals)
        self.wizard_1.action_change_attributes()
        vals = self.variant_1.product_template_attribute_value_ids.mapped("product_attribute_value_id")
        self.assertFalse(self.steel in vals)
        self.assertTrue(self.aluminium in vals)
        # Fix me
        # self.assertFalse(self.check_template_attribute_value(self.variant_1, self.steel))
