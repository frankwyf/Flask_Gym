$('.collapse').collapse({
    toggle: true, parent: '#accordion'
})
$('.panel-heading').on('click', function () {
    var self = this;
    $(self).nextAll().eq(0).collapse("show");
})