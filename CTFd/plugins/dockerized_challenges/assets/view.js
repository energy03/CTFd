CTFd._internal.challenge.data = undefined;

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.renderer = null;

CTFd._internal.challenge.preRender = function() {};

// TODO: Remove in CTFd v4.0
CTFd._internal.challenge.render = null;

CTFd._internal.challenge.postRender = function() {};

CTFd._internal.challenge.submit = function(preview) {
  var challenge_id = parseInt(CTFd.lib.$("#challenge-id").val());
  var submission = CTFd.lib.$("#challenge-input").val();

  var body = {
    challenge_id: challenge_id,
    submission: submission
  };
  var params = {};
  if (preview) {
    params["preview"] = true;
  }

  return CTFd.api.post_challenge_attempt(params, body).then(function(response) {
    if (response.status === 429) {
      // User was ratelimited but process response
      return response;
    }
    if (response.status === 403) {
      // User is not logged in or CTF is paused.
      return response;
    }
    return response;
  });
};

console.log(document.body)


    const ezQuery = CTFd.ui.ezq.ezQuery;
    const ezProgressBar = CTFd.ui.ezq.ezProgressBar;
    const htmlEntities = CTFd.utils.html.htmlEntities;
    const $ = CTFd.lib.$;
    const CTFdFetch = CTFd.fetch;
    const ezToast = CTFd.ui.ezq.ezToast;
    $(() => {
        // TODO: It does not work because the element with this ID is not detected
        $("#challenge-join-button").click(function (_e) {
          alert(1)
          ezQuery({
            title: "Join Challenge",
            body: `Are you sure you want to join challenge <strong>${htmlEntities(
              window.CHALLENGE_NAME,
            )}</strong>`,
            success: function () {
              pg = ezProgressBar({
                width: 50,
                title: "Joining Challenge",
              });
              CTFdFetch("/api/v1/dockerized_challenges/instances/join", {
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
                      body: "Challenge joined successfully.",
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
                      body: "An error occurred while joining the challenge.",
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
                    body: "An error occurred while joining the challenge.",
                    icon: "error",
                  });
                });
            },
          });
        });
        
      });