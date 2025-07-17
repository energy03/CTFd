
CTFd.plugin.run((_CTFd) => {
  const ezq = _CTFd.ui.ezq;
  const htmlEntities = _CTFd.utils.html.htmlEntities;
  const $ = _CTFd.lib.$;
  const ezToast = _CTFd.ui.ezq.ezToast;

  const upload = (form, extra_data, cb) => {
    const CTFd = window.CTFd;
    let formData = new FormData(form);
    formData.append("nonce", CTFd.config.csrfNonce);
    for (let [key, value] of Object.entries(extra_data)) {
      formData.append(key, value);
    }
    let pg = ezq.ezProgressBar({
      title: "Building Docker Image",
      width: 0,
    });
    $.ajax({
      url: CTFd.config.urlRoot + "/api/v1/dockerized_challenges/instances/build",
      data: formData,
      type: "POST",
      cache: false,
      contentType: false,
      processData: false,
      xhr: function () {
        let xhr = $.ajaxSettings.xhr();
        xhr.upload.onprogress = function (e) {
          if (e.lengthComputable) {
            let width = (e.loaded / e.total) * 100;
            pg = ezq.ezProgressBar({
              target: pg,
              width: width,
            });
          }
        };
        return xhr;
      },
      success: function (data) {
        form.reset();
        pg = ezq.ezProgressBar({
          target: pg,
          width: 100,
        });
        setTimeout(function () {
          pg.modal("hide");
        }, 500);

        if (cb) {
          cb(data);
        }
      },
      error: function (_xhr, _status, _error) {
        form.reset();
        pg = ezq.ezProgressBar({
          target: pg,
          width: 0,
        });
        pg.modal("hide");
        ezToast({
          title: "Error",
          body: "An error occurred while building the Docker image.",
          icon: "error",
        });
      },
    });
  }

  $(() => {
    $("#build-image-form").submit(function (_e) {
      _e.preventDefault();
      ezq.ezQuery({
        title: "Build Docker Image",
        body: `Are you sure you want to build the Docker image for challenge <strong>${htmlEntities(
          window.CHALLENGE_NAME,
        )}</strong>?`,
        success: () => {
          upload(this, {
            challenge_id: window.CHALLENGE_ID,
          }, (response) => {
            if (response.success) {
              ezToast({
                title: "Success",
                body: "Docker image build started successfully.",
                icon: "success",
              });
            } else {
              ezToast({
                title: "Error",
                body: "An error occurred while building the Docker image.",
                icon: "error",
              });
            }
          });
        },
      });

    })
  })
})