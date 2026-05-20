$(function () {
    $('#closeAll').click(function () {
        console.log('All tabs are closed');
        $.addtabs.closeAll('#tabs1');
    })
})

//weather window app
WIDGET = {
    "CONFIG": {
        "layout": "1",
        "width": "400",
        "height": "115",
        "background": "1",
        "dataColor": "FFFFFF",
        "language": "en",
        "borderRadius": "5",
        "key": "05e77f36b08f469182105bac72f04098"
    }
}

//remind the user of cookies policies
window.addEventListener("load", function () {
    // if no messages, show cookie policies
    bootoast({
        message: "Attention! this website uses cookies!",
        type: 'danger',
        position: 'top-center',
        icon: 'glyphicon glyphicon-info-sign',
        timeout: 5,
        dismissable: true,
        animationDuration: 1000,
    });
});
