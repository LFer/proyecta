# -*- coding: utf-8 -*-
# from odoo import http


# class SaleCustomer(http.Controller):
#     @http.route('/sale_customer/sale_customer', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_customer/sale_customer/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_customer.listing', {
#             'root': '/sale_customer/sale_customer',
#             'objects': http.request.env['sale_customer.sale_customer'].search([]),
#         })

#     @http.route('/sale_customer/sale_customer/objects/<model("sale_customer.sale_customer"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_customer.object', {
#             'object': obj
#         })
