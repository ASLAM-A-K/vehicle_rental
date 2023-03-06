odoo.define('vehicle_rental.dynamic', function (require) {
'use strict';
   var PublicWidget = require('web.public.widget');
   var rpc = require('web.rpc');
PublicWidget.registry.TopVehicles = PublicWidget.Widget.extend({
       selector: '.dynamic_snippet_vehicle',
       start: function () {
           rpc.query({
               route: '/TopFourVehicles',
               params: {},
           }).then(function (result) {
               var vehicle_id = result;
               var core = require('web.core');
               var QWeb = core.qweb;
               console.log(vehicle_id)
                $('.qweb_vehicle').append(QWeb.render('vehicle_rental.vehicle_template', {vehicle_id}));
           })

       },
   });
});