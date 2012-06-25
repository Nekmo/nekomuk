$(document).ready(function(){      
    graph_conf = {
        series: {
            pie: { 
                show: true,
                combine: {
                    color: '#999',
                    threshold: 0.1
                }
            }
        },
        grid: {
            hoverable: true,
            clickable: true
        }
    }
    specials = new Array();
    
    $('#stats_total').append($('#stats_box_template .stats_box').clone());
    
    time_from_seconds = function(t) {
            var t = parseInt(t, 10);
            var y = Math.floor(t / (3600 * 24 * 365));
            t %= 3600 * 24 * 365;
            var m = Math.floor(t / (3600 * 24 * 30));
            t %= 3600 * 24 * 30;
            var d = Math.floor(t / (3600 * 24));
            t %= 3600 * 24
            var H = Math.floor(t / 3600);
            t %= 3600;
            var M = Math.floor(t / 60);
            t %= 60;
            var S = Math.floor(t % 60);
            return (y > 0 ? y + ' año' + ((y > 1) ? 's ' : ' ') : '') +
                    (m > 0 ? m + ' mes' + ((m > 1) ? 'es ' : ' ') : '') +
                    (d > 0 ? d + ' día' + ((d > 1) ? 's ' : ' ') : '') +
                    (H > 0 ? H + ' hora' + ((H > 1) ? 's' : ' ') : '');
    };

    function parseSize(size){
        var suffix = ["Bytes", "KiB", "MiB", "GiB", "TiB", "PiB"];
        tier = 0;
        while(size >= 1024) {
            size = size / 1024;
            tier++;
        }
        return Math.round(size * 10) / 10 + " " + suffix[tier];
    }
    
    function add_data_graphs(data){
        var arr = Array();
        $.each(data, function(name, val){
            arr[arr.length] = {label: name, data: val}
        });
        return arr
    }
    
    devices = {}
    $('#devices_index li').each(function(i, device){
        var device_url = $(device).attr('title');
        var device_name = $(device).text();
        $.getJSON('devices/' + $(device).attr('title'), function(data){
            devices[device_name] = data   
            // Estadísticas totales
            $('#stats_total .total_t').attr('title', parseInt($('#stats_total .total_t').attr('title')) + data['stats']['total_t']);
            $('#stats_total .total_size').attr('title', parseInt($('#stats_total .total_size').attr('title')) + parseInt(data['stats']['total_size']));
            
            $('#stats_total .total_size').text(parseSize($('#stats_total .total_size').attr('title')));
            $('#stats_total .total_t').text(time_from_seconds($('#stats_total .total_t').attr('title')));
            
            $('#stats_total .sdirs').text(parseInt($('#stats_total .sdirs').text()) + data['stats']['dirs']);
            $('#stats_total .sfiles').text(parseInt($('#stats_total .sfiles').text()) + data['stats']['files']);
            
            $.each(data['stats']['dirs_list'], function(i, value){
                var li = $('<li />');
                $(li).text(value);
                $('#stats_total .files_list').append(li)
            });
            containers_data = add_data_graphs(data['stats']['containers'])
            video_codecs_data = add_data_graphs(data['stats']['video_codecs'])
            $.plot($("#stats_total .containers"), containers_data, graph_conf);
            $.plot($("#stats_total .video_codecs"), video_codecs_data, graph_conf); 
            $.each(data['icons'], function(icon, subdata){
                if(specials.indexOf(subdata['about']['legend']) == -1){
                    var title = $('<h3 />');
                    $(title).text(subdata['about']['legend']);
                    $('#stats_special').append(title);
                    var box = $('#stats_box_template .stats_box').clone();
                    $('#stats_special').append(box);
                    specials[specials.length] = subdata['about']['legend']
                    $(box).attr('id', 'special_' + (specials.length - 1));
                } else {
                    var box = $('#special_' + specials.indexOf(subdata['about']['legend']))
                }
                $('.total_t', box).attr('title', parseInt($('.total_t', box).attr('title')) + subdata['total_t']);
                $('.total_size', box).attr('title', parseInt($('.total_size', box).attr('title')) + subdata['total_size']);
                $('.total_size', box).text(parseSize(parseInt($('.total_size', box).attr('title'))));
                $('.total_t', box).text(time_from_seconds($('.total_t', box).attr('title')));
                
                $('.sfiles', box).text(parseInt($('.sfiles', box).text()) + subdata['files']);
                $('.sdirs', box).text(parseInt($('.sdirs', box).text()) + subdata['dirs']);
                
                $.each(subdata['dirs_list'], function(i, value){
                    var li = $('<li />');
                    $(li).text(value);
                    $('.files_list', box).append(li);
                });
                containers_data = add_data_graphs(subdata['containers']);
                video_codecs_data = add_data_graphs(subdata['video_codecs']);
                $.plot($(box).find(".containers"), containers_data, graph_conf);
                $.plot($(box).find(".video_codecs"), video_codecs_data, graph_conf);
                if(!$(box).find(".oftotal").length){
                    $(box).find(".graphs:last").after($('<div class="graphs"><h4>Por directorio</h4><div class="oftotal"></div></div>'));
                }
                of_total = [
                    {label: 'Total', data: parseInt($('#stats_total .sdirs').text())},
                    {label: subdata['about']['legend'], data: parseInt($(box).find(".sdirs").text())}
                ]                    
                $.plot($(box).find(".oftotal")[0], of_total, graph_conf);
            });
            
        });
    });
    
    $('.toggle').live('click', function(){
        var elem = $(this).parent().children('.hide,.show');
        if($(elem).is('.hide')){
            $(elem).removeClass('hide');
            $(elem).addClass('show');
        } else {
            $(elem).removeClass('show');
            $(elem).addClass('hide');
        }
        var alt = $(this).attr('title');
        $(this).attr('title', $(this).text());
        $(this).text(alt);
    });
});