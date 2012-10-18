function delete_element() {
    var delete_button = $('a.delete-element');

    if (delete_button[0] !== undefined) {

        $(".delete-item-accept").live("click", function() {
            var href_del_url = $(this).attr("data-url");
            var trId = "#" + $(this).attr("data-uid");
            var row_item = $(trId).parents("tr");
            $.ajax({
               'url': href_del_url,
                'success': function(data) {
                        $("a.delete-element", $(trId)).popover('hide');
                        row_item.fadeOut('slow', function() {
                        row_item.remove();
                    });
                }
            }); 
        });
        
        $(".delete-item-cancel").live("click", function() {
            var trId = "#" + $(this).attr("data-uid");
            $("a.delete-element", $(trId)).popover('hide');
        });
        
        delete_button.each(function() {
            var elem = $(this);
            var row_item = elem.parents('td');
            var data = $(".delete-item", row_item);
            elem.popover(
                {
                    title: $(".delete-item-title", data).text(),
                    content: $(".delete-item-buttons", data).html() ,
                    trigger: 'manual'
                });
        });
        
        delete_button.click(function(e) {
            e.preventDefault();
            var $this = $(this);
            var href_del_url = $this.attr('href');
            var row_item = $this.parents('tr');
            var that = this;
            delete_button.each(function() {
                if (that != this) {
                    var elem = $(this);
                    elem.popover('hide');
                }        
            });
            $this.popover('toggle');
        });
    }
}

function sortContent() {
    $(".contents-sort").click(function() {
        var data = $(this).attr("data-sort");
        
        var direction = undefined
        if($(this).hasClass("up")) {
            direction = "down"
            $(this).removeClass("up");
        } else if ($(this).hasClass("down")) {
            direction = "up"
            $(this).removeClass("down");
        } else {
            direction = "up"
        }
        $(this).addClass(direction);
        $("#order").val(data);
        $("#order-direction").val(direction);
        $('#contents-filter-form').submit();
    });
}

function filterOnFly() {
    $(".contents-view-field select").change(function() {
        $('#contents-filter-form').submit();
    });
}

$(document).ready(function() {
    delete_element();
    sortContent();
    filterOnFly();
});