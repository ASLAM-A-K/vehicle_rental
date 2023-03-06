odoo.define('vehicle_rental.rental_request', function (require) {
'use strict';
var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');
publicWidget.registry.VehicleRental = publicWidget.Widget.extend({
    selector: '.available_vehicle',
    events: {
        'click #vehicle': '_onClick',
    },
    _onClick: function () {
    var vehicle_id = document.getElementById("vehicle").value;
           rpc.query({
           route: '/get_period',
           params: {
               vehicle_id: vehicle_id
           }
        })
          .then(function(result){
          var names = result;
          $("#rental_period").empty()
          $.each(Object.keys(names),function(index, name){
               $("#rental_period").append($('<option></option>').attr("value",name).text(names[name]));
                })
           })
    },
});
});