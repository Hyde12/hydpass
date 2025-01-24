$("#email-modal-submit").click(function() {
    var emailEditEmail = ($("#email-edit-email").val()).trim();
    var emailEditPassword = ($("#email-edit-password").val()).trim();

    if (emailEditEmail == "" || emailEditPassword == "") {
        if ($("body").find(".empty-fields").length <= 0) {
            $("body").prepend(
                '<div class="alert alert-warning mt-5 empty-fields">One or more important fields are empty!</div>'
            );
            $("#title").attr("class", "mt-1")
        }

        $("#email-modal").modal("hide")
    } else {
        $.ajax ({
            method: "POST",
            url: "/edit-account",
            data: {
                "email": emailEditEmail,
                "password": emailEditPassword,
                "action": "editEmail",
            },
            success:function(res) {
                if (res == "wrongPass") {
                    if ($("body").find(".wrong-password").length <= 0) {
                        $("body").prepend(
                            '<div class="alert alert-warning mt-5 wrong-password">Password does not match!</div>'
                        );
                        $("#title").attr("class", "mt-1")
                    }
                    $("#email-modal").modal("hide")
                } else if (res == "invalidEmail") {
                    if ($("body").find(".invalid-email").length <= 0) {
                        $("body").prepend(
                            '<div class="alert alert-warning mt-5 invalid-email">Invalid Email</div>'
                        );
                        $("#title").attr("class", "mt-1")
                    }
                    $("#email-modal").modal("hide")
                } else if (res == "inUse") {
                    if ($("body").find(".in-use").length <= 0) {
                        $("body").prepend(
                            '<div class="alert alert-warning mt-5 in-use">Email already in use!</div>'
                        );
                        $("#title").attr("class", "mt-1")
                    }
                    $("#email-modal").modal("hide")
                } else {
                    $("body").html(res)
                }
            }
        });
    }
});

$("#username-modal-submit").click(function() {
    var usernameEditUsername = ($("#username-edit-username").val()).trim()
    var passwordEditUsername = ($("#username-edit-password").val()).trim()

    if (usernameEditUsername == "" || passwordEditUsername == "") {
        if ($("body").find(".empty-fields").length <= 0) {
            $("body").prepend(
                '<div class="alert alert-warning mt-5 empty-fields">One or more important fields are empty!</div>'
            );
            $("#title").attr("class", "mt-1")
        }

        $("#username-modal").modal("hide")
    } else {
        $.ajax ({
            method: "POST",
            url: "/edit-account",
            data: {
                "username": usernameEditUsername,
                "password": passwordEditUsername,
                "action": "editUsername",
            },
            success:function(res) {
                if (res) {
                    window.location = "/manager"
                } else {
                    if ($("body").find(".wrong-pass").length <= 0) {
                        $("body").prepend(
                            '<div class="alert alert-warning mt-5 wrong-pass">Password does not match!</div>'
                        );
                        $("#title").attr("class", "mt-1")
                    }
                }
            }
        });
    }
});

$("#password-modal-submit").click(function() {
    var password = $("#password-edit-password").val()
    var confirm = $("#confirm-edit-password").val()

    if (password == "" || confirm == "") {
        if ($("body").find(".empty-fields").length <= 0) {
            $("body").prepend(
                '<div class="alert alert-warning mt-5 empty-fields">One or more important fields are empty!</div>'
            );
            $("#title").attr("class", "mt-1")
        }

        $("#password-modal").modal("hide")
    } else if (password != confirm) {
        if ($("body").find(".wrong-pass").length <= 0) {
            $("body").prepend(
                '<div class="alert alert-warning mt-5 wrong-pass">Password does not match!</div>'
            );
            $("#title").attr("class", "mt-1")
        }
        $("#password-modal").modal("hide")
    } else {
        $.ajax ({
            method: "POST",
            url: "/edit-account",
            data: {
                "password": password,
                "action": "editPassword",
            },
            success:function(res) {
                $("body").html(res)
            }
        });
    }
});