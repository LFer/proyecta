# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc
import datetime
from odoo.exceptions import UserError
import calendar
from datetime import date, timedelta
from datetime import datetime, timedelta


class BracketLine(models.Model):
    _name = 'bracket.line'

    name = fields.Char(string='Bracket')
    cost = fields.Float(string='Cost x Order')
    qty_orders = fields.Integer(string='#Orders')
    currency_id = fields.Many2one(comodel_name='res.currency', default=2)
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    sale_customer_id = fields.Many2one(comodel_name='sale.customer')


class SaleCustomer(models.Model):
    _name = 'sale.customer'
    _description = 'Sale Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(readonly=1)
    num_orders = fields.Integer(string='#Total Orders')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    currency_id = fields.Many2one(comodel_name='res.currency', default=2)
    total_amount = fields.Monetary(string='Total amount', currency_field='currency_id')
    bracket_lines = fields.One2many(comodel_name='bracket.line', inverse_name='sale_customer_id')
    qty_test = fields.Integer()
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('orders_counted', 'Orders Counted'), ('sale', 'Sale Created')], default='draft')
    sale_id = fields.Many2one(comodel_name='sale.order', readonly=1)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('sale_customer_sequence') or '/'
        res = super(SaleCustomer, self).create(vals)
        return res

    def get_resource(self):
        username = 'lferreira@proyectasoft.com'
        password = '312d32a8ce8a2a953ec1df1027f7b5171697f08a'
        url = 'https://fraccion-backend.feposoft.com'
        database = 'fraccion'
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        common.version()
        try:
            uid = common.authenticate(database, username, password, {})
        except Exception as Error:
            raise UserError(Error)
        resource = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        return resource, database, uid, password

    def connect_with_customer(self):
        bracket_obj = self.env['bracket.line']
        FIELDS = ['id', 'name', 'date_order']
        resource, database, uid, password = self.get_resource()
        # Get the current year and month
        now = datetime.now()
        year = now.year
        month = now.month

        # Define search criteria for sales orders
        search_criteria = [
            ('state', '!=', 'cancel'),
            ('date_order', '>=', '{}-{}-01'.format(year, month)),
            ('date_order', '<=', '{}-{}-{}'.format(year, month, calendar.monthrange(year, month)[1])),
        ]

        sales_orders = resource.execute_kw(database, uid, password, 'sale.order', 'search_read', [search_criteria],
                                           {'fields': FIELDS})
        self.bracket_lines.unlink()
        # num_orders = len(sales_orders)
        num_orders = self.qty_test
        cost = 0
        if min(num_orders, 1000) > 0:
            cost = 0.50 * min(num_orders, 1000)
            bracket_values = {
                'name': '0 - 1.000',
                'cost': 0.50,
                'qty_orders': min(num_orders, 1000),
                'amount': cost,
                'sale_customer_id': self.id,

            }
            bracket = bracket_obj.create(bracket_values)
        if num_orders > 1000:
            bracket_cost = 0.65 * min(num_orders - 1000, 4000)
            cost += bracket_cost
            bracket_values = {
                'name': '1.001 - 5.000',
                'cost': 0.65,
                'qty_orders': min(num_orders - 1000, 4000),
                'amount': bracket_cost,
                'sale_customer_id': self.id,
            }
            bracket = bracket_obj.create(bracket_values)
        if num_orders > 5000:
            bracket_cost = 0.80 * min(num_orders - 5000, 5000)
            cost += bracket_cost
            bracket_values = {
                'name': '5.001 - 10.000',
                'cost': 0.65,
                'qty_orders': min(num_orders - 5000, 5000),
                'amount': bracket_cost,
                'sale_customer_id': self.id,
            }
            bracket = bracket_obj.create(bracket_values)

        if num_orders > 10000:
            bracket_cost = 0.95 * (num_orders - 10000)
            cost += bracket_cost
            bracket_values = {
                'name': '> 10.001',
                'cost': 0.95,
                'qty_orders': (num_orders - 10000),
                'amount': bracket_cost,
                'sale_customer_id': self.id,
            }
            bracket = bracket_obj.create(bracket_values)

        self.total_amount = cost
        self.num_orders = num_orders
        self.state = 'orders_counted'

    def create_sale_order(self):
        lines = []
        product_id = self.env['product.product'].browse(3)
        today = datetime.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=1, month=today.month + 1) - timedelta(days=1)
        note_name = f'Periodo de Facturacion {first_day.strftime("%d-%m-%Y")} - {last_day.strftime("%d-%m-%Y")} #Ordenes: {self.num_orders}'
        line_note_dict = {
            'display_type': 'line_note',
            'name': f'{note_name}'
        }
        lines.append((0, 0, line_note_dict))
        for bracket in self.bracket_lines:
            line_section_dict = {
                'display_type': 'line_section',
                'name': f'Tramo: {bracket.name}'
            }
            lines.append((0, 0, line_section_dict))

            line_dict = {
                'product_id': product_id.id,
                'name': f'{bracket.qty_orders} Ordenes',
                'product_uom_qty': bracket.qty_orders,
                'price_unit': bracket.cost,
                'product_uom': product_id.uom_id.id,
                'tax_id': [(6, 0, product_id.taxes_id.ids)]
            }
            lines.append((0, 0, line_dict))

        values = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'date_order': date.today().replace(day=1) + timedelta(days=32 - date.today().day),
            'order_line': lines,
        }
        order_obj = self.env['sale.order']
        order_id = order_obj.create(values)
        self.sale_id = order_id.id
        self.state = 'sale'

    def cancel_and_draft(self):
        self.sale_id.action_cancel()
        self.sale_id = False
        self.bracket_lines.unlink()
        self.state = 'draft'
        self.num_orders = 0
        self.total_amount = 0