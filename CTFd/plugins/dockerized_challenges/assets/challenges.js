CTFd.plugin.run((_CTFd) => {
    const ezQuery = _CTFd.ui.ezq.ezQuery;
    const htmlEntities = _CTFd.utils.html.htmlEntities;
    const $ = _CTFd.lib.$;
    const CTFdFetch = _CTFd.fetch;
    const ezAlert = _CTFd.ui.ezq.ezAlert;
    const ezToast = _CTFd.ui.ezq.ezToast;

    function startChallenge(_event) {
      // Get id from the button
      var id = $(this).data("challenge-id");
      var challenge_name = window.CHALLENGES[id];

      ezQuery({
        title: "Start Challenge",
        body: `Are you sure you want to start docker instance for <strong>${htmlEntities(
          challenge_name,
        )}</strong>`,
        success: function () {
          CTFdFetch("/api/v1/challenge/start", {
            method: "POST",
            body: JSON.stringify({
              challenge_id: id,
            }),
          })
            .then(function (response) {
              return response.json();
            })
            .then(function (response) {
              if (response.success) {
                window.location.reload();
                ezToast({
                    title: "Success",
                    body: `Docker instance for <strong>${htmlEntities(
                        challenge_name,
                    )}</strong> started successfully.`,
                    icon: "success",
                    });
              } else {
                ezToast({
                  title: "Error",
                  body: "An error occurred while starting the challenge.",
                  icon: "error",
                });
              }
            })
            .catch(function (error) {
              console.error("Error:", error);
              ezToast({
                title: "Error",
                body: "An error occurred while starting the challenge.",
                icon: "error",
              });
            });
        },
      });
    }

    function restartChallenge(_event) {
        // Get id from the button
        var id = $(this).data("challenge-id");
        var challenge_name = window.CHALLENGES[id];

        ezQuery({
          title: "Restart Challenge",
          body: `Are you sure you want to restart docker instance for <strong>${htmlEntities(
            challenge_name,
          )}</strong>`,
          success: function () {
            CTFdFetch("/api/v1/challenge/restart", {
              method: "POST",
              body: JSON.stringify({
                challenge_id: id,
              }),
            })
              .then(function (response) {
                return response.json();
              })
              .then(function (response) {
                if (response.success) {
                  window.location.reload();
                  ezToast({
                    title: "Success",
                    body: `Docker instance for <strong>${htmlEntities(
                        challenge_name,
                    )}</strong> restarted successfully.`,
                    icon: "success",
                    });
                } else {
                    ezToast({
                        title: "Error",
                        body: "An error occurred while restarting the challenge.",
                        icon: "error",
                    });
                }
              })
              .catch(function (error) {
                console.error("Error:", error);
                ezToast({
                  title: "Error",
                  body: "An error occurred while restarting the challenge.",
                  icon: "error",
                });
              });
          },
        });
      }
    
    function stopChallenge(_event) {
        // Get id from the button
        var id = $(this).data("challenge-id");
        var challenge_name = window.CHALLENGES[id];
    
        ezQuery({
            title: "Stop Challenge",
            body: `Are you sure you want to stop docker instance for <strong>${htmlEntities(
            challenge_name,
            )}</strong>`,
            success: function () {
            CTFdFetch("/api/v1/challenge/stop", {
                method: "POST",
                body: JSON.stringify({
                challenge_id: id,
                }),
            })
                .then(function (response) {
                return response.json();
                })
                .then(function (response) {
                if (response.success) {
                    window.location.reload();
                    ezToast({
                        title: "Success",
                        body: `Docker instance for <strong>${htmlEntities(
                            challenge_name,
                        )}</strong> stopped successfully.`,
                        icon: "success",
                    });
                } else {
                    ezToast({
                        title: "Error",
                        body: "An error occurred while stopping the challenge.",
                        icon: "error",
                    });
                }
                })
                .catch(function (error) {
                  console.error("Error:", error);
                    ezToast({
                        title: "Error",
                        body: "An error occurred while stopping the challenge.",
                        icon: "error",
                    });
                });

            },
        });
        }

    function deleteChallenge(_event) {
      var id = $(this).data("challenge-id");
      var challenge_name = window.CHALLENGES[id];
      ezQuery({
        title: "Delete Challenge",
        body: `Are you sure you want to delete challenge <strong>${htmlEntities(challenge_name)}</strong> ?`,
        success: function () {
          CTFdFetch(`/api/v1/challenges/${id}`, {
            method: "DELETE",
          }).then(function (response) {
            if (response.status === 200) {
              window.location.reload();
                ezToast({
                    title: "Success",
                    body: `Challenge <strong>${htmlEntities(challenge_name)}</strong> deleted successfully.`,
                    icon: "success",
                });
            } else {
              ezToast({
                title: "Error",
                body: `An error occurred while deleting the challenge.`,
                icon: "error",
              });
            }
          })
          .catch(function (error) {
            console.error("Error:", error);
            ezToast({
              title: "Error",
              body: `An error occurred while deleting the challenge.`,
              icon: "error",
            });
          }
        );
        },
      });
    }

    $(() => {
        $(".challenge-start-button").click(startChallenge);
        $(".challenge-restart-button").click(restartChallenge);
        $(".challenge-stop-button").click(stopChallenge);
        $(".challenge-delete-button").click(deleteChallenge);
    }
    );
    
})