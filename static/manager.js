$(document).ready(function() {
    $('#search').keyup(function() {
    var searchTerm = $(this).val().toLowerCase();
    $('.table-body tr').each(function() {
        var website = $(this).find('th:first').text().toLowerCase();

        if (website.indexOf(searchTerm) == 0) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
    });

    $('.delete').click(function() {

        $("#delete-modal").modal("show");

        var buttonId = $(this).attr("id");
        var row = $("#row-" + buttonId);

        website = row.find(".website").text();
        email = row.find(".email").text();
        username = row.find(".username").text();
        password = row.find(".password").val();
    });

    $("#delete-account").click(function() {
        passwordConfirm = $("#delete-password-confirmation").val()

        $.ajax ({
            method: "POST",
            url: "/manager",
            data: {
                "action": "delete",
                "website": website,
                "email": email,
                "username": username,
                "password": password,
                "passwordConfirm": passwordConfirm,
            },
            success:function(res) {
                $("#delete-password-confirmation").val("")
                if (res == false) {
                    if ($("body").find(".wrong-password").length <= 0) {
                        $("body").prepend(
                            '<div class="alert alert-warning mt-5 wrong-password">Wrong password!</div>'
                        );
                        $("#title").attr("class", "mt-1")
                    }
                    $("#delete-modal").modal("hide")
                } else {
                    location.reload();
                }
            }
            })
        });

        $(".toggle-visibility").click(function () {
            id = $(this).attr("id")
            password = $("#password-" + id)

            if (password.attr("type") == "password") {
                $("#confirmation-modal").modal("show");
            } else {
                password.attr("type", "password")
            }
        });

        $("#confirm-modal").click(function () {
            password = $("#confirm-password-confirmation").val()

            $.ajax ({
                method: "POST",
                url: "/",
                data: {"password": password},
                success:function(res) {
                    $("#confirm-password-confirmation").val("")
                    if (res == false) {
                        if ($("body").find(".wrong-password").length <= 0) {
                            $("body").prepend(
                                '<div class="alert alert-warning mt-5 wrong-password">Wrong password!</div>'
                            );
                            $("#title").attr("class", "mt-1")
                        }
                        $("#confirmation-modal").modal('hide')
                    } else {
                        var password = $("#password-" + id)
                        password.attr("type", "text")
                        $("#confirmation-modal").modal('hide')
                    }
                }
            })
        });

        $(".edit").click(function () {
            $("#edit-modal").modal("show")
            var editId = $("#row-" + $(this).attr("id"))

            editWebsite = editId.find("th:nth-of-type(1)").text()
            editEmail = editId.find("th:nth-of-type(2)").text()
            editUsername = editId.find("th:nth-of-type(3)").text()
            editPassword = editId.find("th:nth-of-type(4)").find("input").attr("value")

            $("#edit-website").val(editWebsite)
            $("#edit-email").val(editEmail)
            $("#edit-username").val(editUsername)
            $("#edit-password").val(editPassword)
        });

        $("#edit-done").click(function () {
            editWebsite2 = $("#edit-website").val()
            editEmail2 = $("#edit-email").val()
            editUsername2 = $("#edit-username").val()
            editPassword2 = $("#edit-password").val()
            verifyEditPassword = $("#edit-master-password").val()

            if (editWebsite == editWebsite2 && editEmail == editEmail2 && editUsername == editUsername2 && editPassword == editPassword2) {
                location.reload()
            } else if (verifyEditPassword == "" || editWebsite2 == "" || editPassword2 == "") {
                if ($("body").find(".master-password-blank").length <= 0) {
                    $("body").prepend(
                        '<div class="alert alert-warning mt-5 master-password-blank">You have left some important fields blank!</div>'
                    );
                    $("#title").attr("class", "mt-1")
                }
                $("#edit-modal").modal('hide')
            } else {
                $.ajax ({
                    method: "POST",
                    url: "/manager",
                    data: {
                        "action": "edit",
                        "passwordConfirm": verifyEditPassword,

                        "editWebsite": editWebsite2,
                        "editEmail": editEmail2,
                        "editUsername": editUsername2,
                        "editPassword": editPassword2,

                        "orgWebsite": editWebsite,
                        "orgEmail": editEmail,
                        "orgUsername": editUsername,
                        "orgPassword": editPassword,
                    },
                    success:function(res) {
                        if (res == false) {
                            if ($("body").find(".wrong-password").length <= 0) {
                                $("body").prepend(
                                    '<div class="alert alert-warning mt-5 wrong-password">Wrong password!</div>'
                                );
                                $("#title").attr("class", "mt-1")
                            }
                            $("#edit-modal").modal('hide')
                        } else {
                            $("#edit-modal").modal('hide')
                            location.reload()
                        }
                    }
                })
            }
        })
    })