$(function () {
    $('#closeAll').click(function () {
        $.addtabs.closeAll('#tabs1');
        bootoast({
            message: "All tabs were closed.",
            type: 'info',
            position: 'top-center',
            icon: 'glyphicon glyphicon-ok-circle',
            timeout: 2,
            dismissable: true,
            animationDuration: 500,
        });
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
    var cookieNoticeKey = "workout_cookie_notice_at";
    var now = Date.now();
    var lastShown = Number(localStorage.getItem(cookieNoticeKey) || "0");
    var oneWeek = 7 * 24 * 60 * 60 * 1000;

    if (now - lastShown > oneWeek) {
        bootoast({
            message: "This site uses cookies to keep your session and preferences stable.",
            type: 'warning',
            position: 'top-center',
            icon: 'glyphicon glyphicon-info-sign',
            timeout: 6,
            dismissable: true,
            animationDuration: 700,
        });
        localStorage.setItem(cookieNoticeKey, String(now));
    }
});
