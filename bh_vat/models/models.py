# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re

class VatConfigure(models.Model):
    _name = 'vat.configuration'
    _description = 'Vat Automation'

    name = fields.Char(string="VAT Code")
    code_name = fields.Char(string='VAT Name')
    tax_id = fields.Many2one('account.tax', string="Tax")
    tax_scope = fields.Selection(string="Scope", related='tax_id.type_tax_use')
    description = fields.Text(string="Description")


class VatFileReturn(models.Model):
    _name = 'vat.return'
    _description = 'VAT File Return'

    name = fields.Char(string="Label")
    date = fields.Date(string="Date")
    reference = fields.Many2one('account.invoice', string="Sales Reference")
    purchase_reference = fields.Many2one('purchase.order', string="Purchases Reference")
    partner_id = fields.Many2one('res.partner', string="Partner")
    account_id = fields.Many2one('account.account', string="Account")
    tax_id = fields.Many2one('account.tax', string="Tax")
    base_amount = fields.Float(string="Base Amount")
    tax_amount = fields.Float(string="Tax Amount")
    vat_code_ref = fields.Many2one('vat.configuration', string='VAT Code')
    category = fields.Char(string='Category')
    eligibility = fields.Selection([('true', 'Eligible'),('false', 'Ineligible')], string="Eligibility")
    product_type = fields.Char(string="Product Type")
    move_id = fields.Many2one('account.move', string="Journal")


class IvoicesLine(models.Model):
    _inherit = 'account.invoice.line'
    _description = 'VAT line'

    vat_code_id = fields.Many2one('vat.configuration', string='VAT Code')
    x_eligibility = fields.Selection([('true', 'Eligible'),
                                      ('false', 'Ineligible')], string="VAT Eligibility")
    @api.onchange('vat_code_id')
    def get_tax_from_code(self):
        for record in self:
            list_line = []
            data = {}
            tax_id = 1
            for tax in record.vat_code_id:
                tax_id = tax.tax_id.id

            line = (6, 0, [tax_id])
            list_line.append(line)
            data['invoice_line_tax_ids'] = list_line
            record.update(data)

    @api.onchange('product_id')
    def get_automated_vat(self):
        for record in self:
            for product in record.invoice_id:
                if product.partner_id.x_tax_type == 'notgcc':
                    record.update({
                        'vat_code_id': 235
                    })
                if product.partner_id.x_tax_type == 'register':
                    record.update({
                        'vat_code_id': 234
                    })
                if product.partner_id.x_tax_type == 'not_register':
                    record.update({
                        'vat_code_id': 234
                    })
                if product.partner_id.x_tax_type == 'gccnot_register':
                    record.update({
                        'vat_code_id': 236
                    })
                if product.partner_id.x_tax_type == 'gcc_register':
                    record.update({
                        'vat_code_id': 236
                    })





class Invoices(models.Model):
    _inherit = 'account.invoice'
    _description = 'VAT Move'

    # def action_invoice_open(self):
    #     record = super(Invoices, self).action_invoice_open()

    @api.onchange('state')
    def get_invoice_moved(self):
        for record in self:
            vat = self.env['vat.return']
            for move in record.invoice_line_ids:
                data = {
                    'name': move.vat_code_id.name,
                    'partner_id': record.partner_id.id,
                    'tax_id': move.invoice_line_tax_ids.id,
                    'base_amount': move.price_subtotal,
                    'tax_amount': move.price_tax,
                    'vat_code_ref': move.vat_code_id.id,
                    'reference': record.id,
                    'date': record.date_invoice,
                    'category': 'Sale',
                    'product_type': move.product_id.type,
                    'account_id': move.account_id.id,
                    'move_id': record.move_id.id
                }
                print(move.product_id.type)
                vat.create(data)
                print('get out')



class PurchasesLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Code'

    vat_code_id = fields.Many2one('vat.configuration', string='VAT Code')
    x_eligibility = fields.Selection([('true', 'Eligible'),
        ('false', 'Ineligible')], string="VAT Eligibility")

    @api.onchange('vat_code_id')
    def get_tax_from_code(self):
        for record in self:
            list_line = []
            data = {}
            tax_id = 1
            for tax in record.vat_code_id:
                tax_id = tax.tax_id.id

            line = (6, 0, [tax_id])
            list_line.append(line)
            data['taxes_id'] = list_line
            record.update(data)


    @api.onchange('product_id')
    def get_automated_vat(self):
        for record in self:
            for product in record.order_id:
                if product.partner_id.x_tax_type == 'notgcc':
                    record.update({
                        'vat_code_id': 235
                    })
                if product.partner_id.x_tax_type == 'register':
                    record.update({
                        'vat_code_id': 234
                    })
                if product.partner_id.x_tax_type == 'not_register':
                    record.update({
                        'vat_code_id': 234
                    })
                if product.partner_id.x_tax_type == 'gccnot_register':
                    record.update({
                        'vat_code_id': 236
                    })
                if product.partner_id.x_tax_type == 'gcc_register':
                    record.update({
                        'vat_code_id': 236
                    })


class Purchases(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Move'


    def get_purchase_moved(self):
        for record in self:
            vat = self.env['vat.return']
            for move in record.order_line:
                data = {
                    'name': move.vat_code_id.name,
                    'partner_id': record.partner_id.id,
                    'tax_id': move.taxes_id.id,
                    'base_amount': move.price_subtotal,
                    'tax_amount': move.price_tax,
                    'vat_code_ref': move.vat_code_id.id,
                    'purchase_reference': record.id,
                    'date': record.date_order,
                    'category': 'Purchase',
                    'eligibility': move.x_eligibility,
                    'product_type': move.product_id.type
                }
                vat.create(data)
                print('get out')


class Partners(models.Model):
    _inherit = 'res.partner'
    _description = 'Custom Partner'

    x_tax_type = fields.Selection([
        ('register', 'VAT Registered'),
        ('not_register', 'Non VAT Registered'),
        ('gcc_register', 'GCC VAT Registered'),
        ('gccnot_register', 'GCC Non VAT Registered'),
        ('notgcc', 'Non GCC')], string="Tax Type")

    x_supply_place = fields.Char(string="Place Of Supply")

class Products(models.Model):
    _inherit = 'product.template'
    _description = 'Product Custom'

    x_is_zero = fields.Boolean(string="Is zero%")
    x_is_exmpted = fields.Boolean(string="Is exmpted%")



class AccountMove(models.Model):
    _inherit = 'account.move.line'
    _description = 'Move Test'

    x_vat_code = fields.Many2one('vat.configuration', string='VAT Code')



