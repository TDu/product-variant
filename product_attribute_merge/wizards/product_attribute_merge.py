# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizardProductAttributeMerge(models.TransientModel):
    _name = "wizard.product.attribute.merge"
    _description = "Merge Product Attribute"

    product_attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Merge Attribute",
        readonly=True
    )
    into_product_attribute_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Into Attribute"
    )
    attribute_values_merge_action_ids = fields.Many2many(
        comodel_name="product.attribute.merge.value.action",
        relation="wizard_product_attribute_merge_action_rel"
    )

    @api.model
    def default_get(self, fields_list):
        """'default_get' method overloaded."""
        res = super().default_get(fields_list)
        # active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        if not active_ids:
            raise UserError(
                _("Please select at least one product attribute.")
            )
        res["product_attribute_id"] = active_ids[0]
        return res

    @api.onchange("into_product_attribute_id")
    def _onchange_merge_into_product_attribute_id(self):
        for record in self:
            actions = record._get_actions_for_values(
                record.product_attribute_id,
                record.into_product_attribute_id
            )
            record.attribute_values_merge_action_ids = [(6, 0, actions.ids)]

    @api.model
    def _get_action_for_value(self, value_to_merge, product_attribute):
        if not value_to_merge.pav_attribute_line_ids:
            return "delete"
        # should pass a dict of id values
        values = { value.name.casefold(): value.id for value in product_attribute.value_ids}
        iid = values.get(value_to_merge.name.casefold())
        if iid:
            return "merge"
        return "move"

    @api.model
    def _merge_attribute_value(self, value_to_merge, value_merge_into):

        pass

    @api.model
    def _move_attribute_value(self, value, attribute):
        Ptal = self.env["product.template.attribute.line"]
        Ptav = self.env["product.template.attribute.value"]
        # ptal_to_delete = Ptal.browse()
        ptal_to_move = value.pav_attribute_line_ids
        for line in ptal_to_move:
            # TODO handle archived line as well !
            line.with_context(
                update_product_template_attribute_values=False
            ).write({"value_ids": [(3, value.id)]})

        value.attribute_id = attribute

        for line in ptal_to_move:
            # Search for an existing line for attribute, if none create one
            template = line.product_tmpl_id
            ptav2move = line.product_template_value_ids.filtered(
                lambda ptav: ptav.product_attribute_value_id == value
            )
            tpl_attr_line = template.attribute_line_ids.filtered(
                lambda l: l.attribute_id == attribute
            )
            if not tpl_attr_line:
                tpl_attr_line = Ptal.with_context(
                    # Does not work at creation !
                    update_product_template_attribute_values=False
                ).create(
                    {
                        "product_tmpl_id": template.id,
                        "attribute_id": attribute.id,
                        "value_ids": [(6, False, [value.id])],
                    }
                )
                # The create will add the value on all variant, clean it up
                ptav_new = tpl_attr_line.product_template_value_ids.filtered(lambda ptav: ptav.product_attribute_value_id == value)
                product_to_update = ptav2move.ptav_product_variant_ids
                product_to_remove_value = ptav_new.ptav_product_variant_ids - product_to_update
                product_to_remove_value.product_template_attribute_value_ids = [(3, ptav_new.id, 0)]
            else:
                # Add the new value to an existing line
                product_to_update = ptav2move.ptav_product_variant_ids
                tpl_attr_line.with_context(
                    update_product_template_attribute_values=False
                ).write({"value_ids": [(4, value.id)]})
                ptav2move.write(
                    {
                        "attribute_line_id": tpl_attr_line.id
                    }
                )
            # TODO cleanup ptal_to_move that are empty !


    @api.model
    def _delete_attribute_value(self, value):
        if not value.pav_attribute_line_ids:
            value.unlink()
        else:
            raise UserError(_(f"Deleting the attribute value {value.name} is not possible, because it is being used."))

    @api.model
    def _get_actions_for_values(self, attribute_to_merge, attribute_merge_into):
        actions = self.env["product.attribute.merge.value.action"].browse()
        if not attribute_merge_into:
            return actions
        for value in attribute_to_merge.value_ids:
            action = self._get_action_for_value(value, attribute_merge_into)
            actions |= self.env["product.attribute.merge.value.action"].create(
                {
                    "attribute_value_id": value.id,
                    "attribute_value_action": action,
                    "merge_into_attribute_id": attribute_merge_into.id,
                    "merge_into_attribute_value_id": False,
                }
                # for value in attribute_to_merge.value_ids
            )
        return actions

    def action_merge(self):
        self.ensure_one()
        for action in self.attribute_values_merge_action_ids:
            if action.attribute_value_action == "merge":
                self._merge_attribute_value(action.attribute_value_id, action.merge_into_attribute_value_id)
            elif action.attribute_value_action == "move":
                self._move_attribute_value(action.attribute_value_id, action.merge_into_attribute_id)
                pass
            elif action.attribute_value_action == "delete":
                self._delete_attribute_value(action.attribute_value_id)
        return
