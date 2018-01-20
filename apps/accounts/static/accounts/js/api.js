var api = {
  'set final submission' : '/accounts/panel/set_final_submission/{id}'
};

function add_submission_api(submission_id) {
    $('.submission')
      .api({
        action: 'set final submission',
        on: 'click',
        urlData: {
          id: submission_id
        }
        onResponse: function(response) {
          // make some adjustments to response
          return response;
        },
        successTest: function(response) {
          // test whether a JSON response is valid
          return response.success || false;
        },
        onComplete: function(response) {
          // always called after XHR complete
        },
        onSuccess: function(response) {
          // valid response and response.success = true
          $('[name=submission_id]').setValue(response.data.submission_id);
        },
        onFailure: function(response) {
          // request failed, or valid response but response.success = false
        },
        onError: function(errorMessage) {
          // invalid response
        },
        onAbort: function(errorMessage) {
          // navigated to a new page, CORS issue, or user canceled request
        }
      })
    ;
}