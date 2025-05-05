CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()

    $("#dockerize-challenge-dynamic-check-input").on("change", function() {
        if ($(this).is(":checked")) {
            $(".dockerize-hiddable-dynamic").prop("hidden", false);
            $(".dockerize-hiddable-standard").prop("hidden", true);
            $(".dockerize-hiddable-standard-required-field").prop("required", false);
            $(".dockerize-hiddable-dynamic-required-field").prop("required", true);
            // Retirer la propriété name de l'input
            $(".dockerize-hiddable-standard-required-field").removeAttr("name");
        } else {
            $(".dockerize-hiddable-dynamic").prop("hidden", true);
            $(".dockerize-hiddable-standard").prop("hidden", false);
            $(".dockerize-hiddable-standard-required-field").prop("required", true);
            $(".dockerize-hiddable-dynamic-required-field").prop("required", false);
        }
    }
    );
})

