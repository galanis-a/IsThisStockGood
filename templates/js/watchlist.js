$(document).ready(function() {
  $("#watchlistform").submit(function(event) {

    const loader = document.querySelector("popup-loading");

    // Stop form from submitting normally.
    event.preventDefault();

    // Extract the URL path for the action.
    let $form = $(this);
    path = $form.attr('action');

    // Extract the ticker symbol.
    let $ticker = $('#watchlist-ticker').val();
    if ($ticker.length == 0) {
      return;
    }

    // Start loading
    loader.show();

    // Post the data to the path.
    let posting = $.post(path, { ticker: $ticker } );

    posting.fail(function(response) {
    $.snackbar({
          content: `There was an error. Code ${response.status}`,
          style: 'toast',
          timeout: 3500
        });
        // Hide loading
        loader.hide();
        return;
    })
    // Update the HTML with the results.
    posting.done(function(data) {
      if (data['error']) {
        $.snackbar({
          content: data['error'],
          style: 'toast',
          timeout: 3500
        });
        // Hide loading
        loader.hide();
        return;
      }

      // Hide loading
      loader.hide();
    });
  });
});