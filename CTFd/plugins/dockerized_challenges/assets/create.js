CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()

    function onStandardChallenge() {
        $(".dockerize-hiddable-dynamic").prop("hidden", true);
        $(".dockerize-hiddable-standard").prop("hidden", false);
        // $(".dockerize-hiddable-standard-required-field").prop("required", true);
        // $(".dockerize-hiddable-dynamic-required-field").prop("required", false);
        $(".dockerize-hiddable-standard-required-field").prop("disabled", false);
        $(".dockerize-hiddable-dynamic-required-field").prop("disabled", true);
    }

    function onDynamicChallenge() {
        $(".dockerize-hiddable-dynamic").prop("hidden", false);
        $(".dockerize-hiddable-standard").prop("hidden", true);
        // $(".dockerize-hiddable-standard-required-field").prop("required", false);
        // $(".dockerize-hiddable-dynamic-required-field").prop("required", true);
        $(".dockerize-hiddable-standard-required-field").prop("disabled", true);
        $(".dockerize-hiddable-dynamic-required-field").prop("disabled", false);
    }

    $(() => {
        onStandardChallenge(); // Default to standard challenge

        $("#dockerize-challenge-dynamic-check-input").on("change", function() {
            if ($(this).is(":checked")) {
                onDynamicChallenge();
            } else {
                onStandardChallenge();
            }
        });

    })
})