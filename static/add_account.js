const symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;':\"<>,./?"
    $("#generate").click(function () {
        var password = ""

        for (let i = 0; i < 16; i++) {
            password += symbols.charAt(Math.floor(Math.random() * symbols.length));
        }

        $("#password").val(password)
    });

    $("#visible").click(function () {
        if ($("#password").attr("type") == "password") {
            $("#password").attr("type", "text")
        } else {
            $("#password").attr("type", "password")
        }
    });