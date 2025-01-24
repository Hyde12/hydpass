let textCopy1 = document.getElementById("pass-1");

function copyText1() {
    textCopy1.select();
    textCopy1.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(textCopy1.placeholder);
    $("#icon").attr("class", "fa fa-check")
}
