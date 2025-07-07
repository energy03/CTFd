CTFd.plugin.run((_CTFd) => {
    const ezQuery = _CTFd.ui.ezq.ezQuery;
    const ezProgressBar = _CTFd.ui.ezq.ezProgressBar;
    const htmlEntities = _CTFd.utils.html.htmlEntities;
    const $ = _CTFd.lib.$;
    const CTFdFetch = _CTFd.fetch;
    const ezToast = _CTFd.ui.ezq.ezToast;

    $(() => {
        $(".start-challenge").click(function (_e) {
          ezQuery({
            title: "Start Challenge",
            body: `Are you sure you want to start docker instance for challenge <strong>${htmlEntities(
              window.CHALLENGE_NAME,
            )}</strong>`,
            success: function () {
              pg = ezProgressBar({
                width: 50,
                title: "Starting Docker Instance",
              });
              CTFdFetch("/api/v1/dockerized_challenges/instances/start", {
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
                    pg = ezProgressBar({
                      target: pg,
                      width: 100,
                    });
                    pg.modal("hide");
                    ezToast({
                      title: "Success",
                      body: "Docker instance started successfully.",
                      icon: "success",
                    });
                    setTimeout(() => {
                      window.location.reload();
                    }, 1000);
                  } else {
                    pg = ezProgressBar({
                      target: pg,
                      width: 0,
                    });
                    pg.modal("hide");
                    ezToast({
                      title: "Error",
                      body: "An error occurred while starting the challenge.",
                      icon: "error",
                    });
                  }
                })
                .catch(function (error) {
                  pg = ezProgressBar({
                    target: pg,
                    width: 0,
                  });
                  pg.modal("hide");
                  ezToast({
                    title: "Error",
                    body: "An error occurred while starting the challenge.",
                    icon: "error",
                  });
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
              pg = ezProgressBar({
                width: 50,
                title: "Restarting Docker Instance",
              });
              CTFdFetch("/api/v1/dockerized_challenges/instances/restart", {
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
                    pg = ezProgressBar({
                      target: pg,
                      width: 100,
                    });
                    pg.modal("hide");
                    ezToast({
                      title: "Success",
                      body: "Docker instance restarted successfully.",
                      icon: "success",
                    });
                    setTimeout(() => {
                      window.location.reload();
                    }, 1000);
                  } else {
                    pg = ezProgressBar({
                      target: pg,
                      width: 0,
                    });
                    pg.modal("hide");
                    ezToast({
                      title: "Error",
                      body: "An error occurred while restarting the challenge.",
                      icon: "error",
                    });
                  }
                })
                .catch(function (error) {
                  pg = ezProgressBar({
                    target: pg,
                    width: 0,
                  });
                  pg.modal("hide");
                  ezToast({
                    title: "Error",
                    body: "An error occurred while restarting the challenge.",
                    icon: "error",
                  });
                });
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
              pg = ezProgressBar({
                width: 50,
                title: "Stopping Docker Instance",
              });
              CTFdFetch("/api/v1/dockerized_challenges/instances/stop", {
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
                    pg = ezProgressBar({
                      target: pg,
                      width: 100,
                    });
                    pg.modal("hide");
                    ezToast({
                      title: "Success",
                      body: "Docker instance stopped successfully.",
                      icon: "success",
                    });
                    setTimeout(() => {
                      window.location.reload();
                    }, 1000);
                  } else {
                    pg = ezProgressBar({
                      target: pg,
                      width: 0,
                    });
                    pg.modal("hide");
                    ezToast({
                      title: "Error",
                      body: "An error occurred while stopping the challenge.",
                      icon: "error",
                    });
                  }
                })
                .catch(function (error) {
                  pg = ezProgressBar({
                    target: pg,
                    width: 0,
                  });
                  pg.modal("hide");
                  ezToast({
                    title: "Error",
                    body: "An error occurred while stopping the challenge.",
                    icon: "error",
                  });
                });
            },
          });
        });
      
      
      });
})