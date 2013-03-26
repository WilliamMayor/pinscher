function hide_results() {
    $("body table").hide();
}
function clear_results() {
    $("body table tbody tr").remove();
}
function show_results(results) {
    var tbody = $("body table tbody");
    if (results.length === 0) {
        tbody.append($('<tr class="no_results"><td colspan="4">--no results--</td></tr>'));
    } else {
        $("body table").removeClass("no_results");
    }
    $.each(results, function(index, value) {
        var td_database = $("<td>");
        td_database.text(value['keyfile']);
        var td_domain = $("<td>");
        td_domain.text(value['domain']);
        var td_username = $("<td>");
        td_username.text(value['username']);
        var tr = $("<tr>");
        tr.append(td_database);
        tr.append(td_domain);
        tr.append(td_username);
        tr.append($("<td>********</td>"));
        tbody.append(tr);
    });
    $("body table").show();
}
function combine_results(list_a, list_b) {
    $.each(list_b, function(index_b, value_b) {
        var keep = true;
        $.each(list_a, function(index_a, value_a) {
            keep = keep && !(value_b['keyfile'] === value_a['keyfile'] && value_b['domain'] === value_a['domain'] && value_b['username'] === value_a['username']);
        });
        if (keep === true) {
            list_a.push(value_b);
        }
    });
    return list_a;
}
$(document).ready(function() {
    hide_results();
    $("#search_box").keyup(function() {
        var q = $(this).val().trim();
        if (q === "") {
            clear_results();
            hide_results();
        } else {
            var promises = [];
            $.each(q.split(" "), function(index, value) {
                promises.push($.getJSON('/api/search/?domain=' + value));
                promises.push($.getJSON('/api/search/?username=' + value));
            });
            $.when.apply($, promises).done(function() {
                var results = [];
                $.each(arguments, function(index, value) {
                    results = combine_results(results, value[0]['results']);
                });
                clear_results();
                show_results(results);
            });
        }
    });
});