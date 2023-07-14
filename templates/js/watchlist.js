$(document).ready(function () {
    getWatchlist();

    $("#watchlistform").submit(function (event) {

        const loader = document.querySelector("popup-loading");

        // Stop form from submitting normally.
        event.preventDefault();

        // Extract the URL path for the action.
        let $form = $(this);
        path = $form.attr('action');

        // Extract the ticker symbol.
        let $ticker = $('#watchlist-ticker').val();
        if ($ticker.length === 0) {
            return;
        }

        // Start loading
        loader.show();

        // Post the data to the path.
        let posting = $.post(path, {ticker: $ticker});

        posting.fail(function (response) {
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
        posting.done(function (data) {
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
            addTickerHtml($ticker)
            $.snackbar({
                content: "Ticker added to watchlist",
                style: 'toast',
                timeout: 3500
            });
        });
    });
});

function getWatchlist() {
    let getWatchlist = $.get("/watchlist");
    getWatchlist.fail(function (response) {
        $.snackbar({
            content: `Could not get watchlist. Code ${response.status}`,
            style: 'toast',
            timeout: 3500
        });
        return;
    });

    getWatchlist.done(function (data) {
        if (data['error']) {
            $.snackbar({
                content: data['error'],
                style: 'toast',
                timeout: 3500
            });
            return;
        }

        addWatchlistHtml(data.data)
        addWatchlistTickerEvents()
    });
}

function addWatchlistHtml(tickers) {
    $("#ticker-list").html("");

    tickers.split(",").forEach((ticker) => {
        addTickerHtml(ticker)
    })
}

function addTickerHtml(ticker) {
    let list = $("#ticker-list");
    list.append(`<a href="#" class="list-group-item watchlist-ticker">${ticker}</a>`);
}

function addWatchlistTickerEvents() {
    $('.watchlist-ticker').click((e) => {
        e.preventDefault();

        $('#ticker').val(e.target.text);
        $('#searchboxform').submit();
    })
}