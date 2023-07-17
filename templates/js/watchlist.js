$(document).ready(function () {
    getWatchlist();

    $("#watchlistform").submit(function (event) {

        const loader = document.querySelector("popup-loading");

        // Stop form from submitting normally.
        event.preventDefault();

        // Extract the URL path for the action.
        let $form = $(this);
        const path = $form.attr('action');

        // Extract the ticker symbol.
        let $ticker = $('#watchlist-ticker').val();
        if ($ticker.length === 0) {
            return;
        }

        // Start loading
        loader.show();

        $.ajax({
            url: path,
            type: 'POST',
            dataType: 'json',
            data: {ticker: $ticker},
            headers: {
                "X-CSRFToken": getCSRFToken()
            },
            success: (response) => {
                if (response['error']) {
                    $.snackbar({
                        content: response['error'],
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
            },
            error: (response) => {
                $.snackbar({
                    content: `There was an error. Code ${response.status}`,
                    style: 'toast',
                    timeout: 3500
                });
                // Hide loading
                loader.hide();
            }
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
    $("#ticker-list").empty();

    tickers.split(",").forEach((ticker) => {
        addTickerHtml(ticker)
    })
}

function addTickerHtml(ticker) {
    let list = $("#ticker-list");
    list.append(`<div class="list-group-item">
        <a href="#" class="watchlist-ticker">${ticker}</a>
        <button type="button" class="btn btn-danger watchlist-delete" data-symbol="${ticker}"><span class="material-icons">delete</span></button>
    </div>`);
}

function removeTickerHtml(ticker) {
    $(`button[data-symbol=${ticker}]`).parent().remove();
}

function addWatchlistTickerEvents() {
    $('.watchlist-ticker').click((e) => {
        e.preventDefault();

        $('#ticker').val(e.target.text);
        $('#searchboxform').submit();
    })

    $('.watchlist-delete').click((e) => {
        e.preventDefault();
        let ticker = $(e.currentTarget).data("symbol");

        $.ajax({
            url: '/watchlist',
            type: 'DELETE',
            dataType: 'json',
            data: {ticker: ticker},
            headers: {
                "X-CSRFToken": getCSRFToken()
            },
            success: (response) => {
                if (response['error']) {
                    $.snackbar({
                        content: response['error'],
                        style: 'toast',
                        timeout: 3500
                    });
                    return;
                }
                removeTickerHtml(ticker);
            },
            error: (response) => {
                $.snackbar({
                    content: `There was an error deleting the symbol from watchlist. Code ${response.status}`,
                    style: 'toast',
                    timeout: 3500
                });
            }
        });
    })
}