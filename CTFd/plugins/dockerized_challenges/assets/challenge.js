CTFd.plugin.run((_CTFd) => {
    const ezQuery = _CTFd.ui.ezq.ezQuery;
    const htmlEntities = _CTFd.utils.html.htmlEntities;
    const $ = _CTFd.lib.$;
    const CTFdFetch = _CTFd.fetch;

    $(() => {
        $(".start-challenge").click(function (_e) {
          ezQuery({
            title: "Start Challenge",
            body: `Are you sure you want to start docker instance for challenge <strong>${htmlEntities(
              window.CHALLENGE_NAME,
            )}</strong>`,
            success: function () {
              CTFdFetch("/api/v1/challenge/start", {
                method: "POST",
                body: JSON.stringify({
                  challenge_id: window.CHALLENGE_ID,
                }),
              })
                .then(function (response) {
                  return response.json();
                })
                .then(function (response) {
                  if (response.success) {
                    window.location.reload();
                  } else {
                    ezQuery({
                      title: "Error",
                      body: response.error,
                      button: "OK",
                    });
                  }
                });
            },
          });
        });
      
        $(".restart-challenge").click(function (_e) {
          ezQuery({
            title: "Restart Challenge",
            body: `Are you sure you want to restart docker instance for <strong>${htmlEntities(
              window.CHALLENGE_NAME,
            )}</strong>`,
            success: function () {
              CTFdFetch("/api/v1/challenge/restart", {
                method: "POST",
                body: JSON.stringify({
                  challenge_id: window.CHALLENGE_ID,
                }),
              })
                .then(function (response) {
                  return response.json();
                })
                .then(function (response) {
                  if (response.success) {
                    window.location.reload();
                  } else {
                    ezQuery({
                      title: "Error",
                      body: response.error,
                      button: "OK",
                    });
                  }
                })
            },
          });
        });
      
        $(".stop-challenge").click(function (_e) {
          ezQuery({
            title: "Stop Challenge",
            body: `Are you sure you want to stop docker instance for <strong>${htmlEntities(
              window.CHALLENGE_NAME,
            )}</strong>`,
            success: function () {
              CTFdFetch("/api/v1/challenge/stop", {
                method: "POST",
                body: JSON.stringify({
                  challenge_id: window.CHALLENGE_ID,
                }),
              })
                .then(function (response) {
                  return response.json();
                })
                .then(function (response) {
                  if (response.success) {
                    window.location.reload();
                  } else {
                    ezQuery({
                      title: "Error",
                      body: response.error,
                      button: "OK",
                    });
                  }
                });
            },
          });
        });
      
      
      });
})