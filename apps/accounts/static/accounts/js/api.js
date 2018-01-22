
/* Define API endpoints once globally */
$.fn.api.settings.api = {
  'set final submission' : '/accounts/panel/set_final_submission/{id}'
};

$('.submission')
  .api({
    action: 'set final submission',
    on: 'click',
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
      $('.submission').prop('checked', false);
      $('#submission_' + response.submission_id).prop('checked', true);
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
  });

$('#id_team').change(function () {
    window.location.href='/accounts/panel/' + this.value;
});