$(document).ready(function(){
    // En los inputs y textareas, mostrar el texto de
    // ayuda solo si el campo está vacio
    $('input, textarea').live('focusin', function(){
        if($(this).attr('title')==$(this).val()){
            $(this).val('');
        }
    }).live('focusout', function(){
        if($(this).val()==''){
            $(this).val($(this).attr('title'));
        }
    });
    
    // Función para mostrar el texto de ayuda en todos
    // los inputs y textareas del documento
    inputTitle = function(){
        $.each($('input, textarea'), function(key, val){
            if($(this).is('textarea')){
                $(this).val = $(this).text
            }
            if($(val).attr('title')){
                if($(val).val()==''){
                    $(val).val($(val).attr('title'));
                }
            }
        });
    }
    
    view_list_icons = function(){
        $('#content').removeClass('view_list_details');
        $('#content').addClass('view_list_icons');
    }
    
    view_list_details = function(){
        $('#content').removeClass('view_list_icons');
        $('#content').addClass('view_list_details');
    }
    
    $('#view .icons').click(function(){
        view_list_icons();
        $.cookie('view_list', 'icons');
    });
    $('#view .details').click(function(){
        view_list_details();
        $.cookie('view_list', 'details');
    });

    if($.cookie('view_list')){
        if($.cookie('view_list')=='icons'){
            view_list_icons()
        } else if($.cookie('view_list')=='details'){
            view_list_details()
        }
    }
    
    last_levels = window.location['pathname'].split('/').length

    function ajax_load(href){
        if(window.location.hash.startswith('#!')){ return }
        $.get(href, function(data) {
            data = data.replace(/<script/g, '<scr_ipt');
            data = data.replace(/<\/script>/g, '</scr_ipt>');
            var title = $('<div />').html(data).find('#title').text();
            var js = $('<div />').html(data).find('#script').text();
            if(js){
                eval(js);
            }
            var sub_root = $('<div />').html(data).find('#sub_root').text();
            $('#sub_root').text(sub_root)
            history.pushState({ path: href + window.location.hash}, title, href + window.location.hash);
            $('title').text(title);
            var files = $('<div />').html(data).find('#content .files').html();
            var levels = window.location['pathname'].split('/').length
            if(levels > last_levels){
                $('#content .files').css({'position': 'relative', 'left': '100%'});
                $('#content .files').stop().slideTo({ 
                    transition:500,
                    left: '0',
                    inside:'#content'
                });
            } else {
                $('#content .files').css({'position': 'relative', 'left': '-100%'});
                $('#content .files').stop().slideTo({ 
                    transition:500,
                    left: '0',
                    inside:'#content'
                });
            }
            last_levels = levels               
            $('#content .files').html(files);
            // PATCH - Soluciona el problema de deselección de inputs radio
            // tras Ajax
            $('.advance input').each(function(i, input){
                if($(input).attr('checked')){
                    $(input).attr('checked', true);
                }
            });
        });
    }

    function device_search(q_parts, results, device){
        $.each(q_parts, function(i, word){
            var terms_url = $('#sub_root').text()
            terms_url = terms_url + 's/' + device
            terms_url = terms_url + '/' + word.substr(0, 3) + '.json'
            $.ajax(terms_url, {
                cache: true,
                dataType: 'json',
                async: false,
                success: function(data) {
                    $.each(data, function(term, terms){
                        $.each(terms, function(j, val){
                            if(term.toLowerCase().startswith(word)){
                                // se contiene la palabra, se comprueba si el resto
                                // de términos concuerdan.
                                if(search_lock){
                                    results = new Array()
                                    return
                                }
                                var all_in_query = true; // Todas las palabras de las búsqueda pertenecen al término
                                $.each(q_parts, function(i, q_part){
                                    // Se mira si cada una de las palabras del término de búsqueda están en el término donde se busca.
                                    var is_in_term = false;
                                    $.each(val[0], function(i, in_term){
                                        if(in_term.startswith(q_part)){
                                            is_in_term = true;
                                        }
                                    });
                                    if(!is_in_term){
                                        all_in_query = false;
                                    }
                                });
                                if(all_in_query){
                                    // Término bueno
                                    val[1] = $('#sub_root').text() + 'devices/' + device + '/' + val[1]
                                    results.append(val);
                                }
                            }
                        });
                    });
                },
            });
        });
    }

    search_lock = false
    $('#search input').keydown(function(){
        setTimeout(function(){
            if($('[name="advance"]:checked').val() == '1'){
                // Búsqueda sólo aquí
                $('#content').show();
                $('#results').hide();
                var pattern = new RegExp($('#search input').val(), 'i')
                $.each($('#content .files > div'), function(){
                    if(pattern.exec($(this).find('.name').text())){
                        $(this).show();
                    } else {
                        $(this).hide();
                    }
                });
                return
            }
            $()
            // Búsqueda en dispositivos o en el dispositivo
            if($('#search input').val().length == 0){
                $('#results').hide();
                $('#content').show();
                $('#content .file, #content .dir').show();
            }
            if($('#search input').val().length < 3){
                return;
            }
            $('#content').hide();
            $('#results').show();
            search_lock = true
            sleep(50)
            search_lock = false
            var q = $('#search input').val().toLowerCase();
            var q_parts = q.split(' ')
            var results = new Array()
            
            if($('[name="advance"]:checked').val() == '2'){
                // Sólo en este dispositivo
                var devices = [encodeURIComponent($('#device').text())]
            } else {
                // En todos los dispositivos
                var devices = []
                var devices_url = $('#sub_root').text()
                devices_url = devices_url + 'index.html'
                $.ajax(devices_url, {
                    cache: true,
                    dataType: 'html',
                    async: false,
                    success: function(data){
                        data = data.replace(/<script/g, '<scr_ipt');
                        data = data.replace(/<\/script>/g, '</scr_ipt>');
                        data = $('<div />').html(data).find('#content li');
                        $.each(data, function(i, device){
                            devices[devices.length] = encodeURIComponent(encodeURIComponent($(device).text()));
                        });
                    }
                });
            }
            $.each(devices, function(i, device){
                device_search(q_parts, results, device)
            });
            $('#results * *').remove();
            $.each(results, function(i, file_data){
                if(file_data[3]=='dir'){
                    var pattern = $('#pattern .dir').clone();
                    $(pattern).find('.name').attr('href', file_data[1] + file_data[2]);
                    $(pattern).find('.name').text(file_data[2]);
                    $('#results .dirs').append(pattern);

                } else {
                    var pattern = $('#pattern .file').clone();
                    $(pattern).find('.name').text(file_data[2]);
                    $('#results .files').append(pattern);
                }
            });
        }, 50);
    });

    $('#content .files a').live('click', function() {
        if(window.location.hash.startswith('#!')){ return true }
        $('#panel .data').text('')
        $('#thumb').attr('style', '')
        ajax_load(this.href);
        return false 
    });
    
    $('#top .show_advance').click(function(){
        $('#top .show_advance').hide();
        $('#top .advance').show();
    });

    show_panel_info = function(obj){   
        $('#panel #thumb').css({'background-image': 'url("' + $(obj).find('.name').text() + '.jpg")'});
        $('#panel .video_codec').text($(obj).find('.video_codec').text());
        $('#panel .audio_codec').text($(obj).find('.audio_codec').text());
        $('#panel .resolution').text($(obj).find('.width').text() + 'x' + $(obj).find('.height').text());
        $('#panel .container').text($(obj).find('.container').text());
        $('#panel .length').text($(obj).find('.length').text());
        $('#panel .size').text($(obj).find('.size').text());
        $('#panel .aspect').text($(obj).find('.aspect').text());
        $('#panel .fps').text($(obj).find('.fps').text());
        $('#panel .container').text($(obj).find('.container').text());
        $('#panel .samplerate').text($(obj).find('.samplerate').text());
        $('#panel .audio_channels').text($(obj).find('.audio_channels').text());
    }
    
    HOVER_NOW = ''
    hover_info_wrapper = function(name, obj){
        if(HOVER_NOW==name){
            show_panel_info(obj);
        }
    }
    $('#content .file').live('mouseenter', function(){
        HOVER_NOW = $(this).find('.name').text();
        var this_ = this
        window.setTimeout(hover_info_wrapper, 300, HOVER_NOW, this_);
    });
    $('#content .file').live('mouseleave', function(){
        HOVER_NOW = ''
    });
    
    $('#locals div').each(function(i, pack){
        var to = $(pack).attr('title')
        $(pack).find('*').each(function(i, trans){
            $(to).find('.' + $(trans).attr('class')).text($(trans).text())
        });
    });
    
    merge = function(kwargs){
        var devices = kwargs['devices'].split(';')
        var path = kwargs['path'];
        $('#content').html('');
        $('#content').append($('<div class="files"></div>'));
        $.each(devices, function(i, device){
            $.ajax($('#sub_root').text() + 'devices/' + encodeURIComponent(encodeURIComponent(device)) + '/' + path, {
                cache: true,
                dataType: 'html',
                async: false,
                success: function(data){
                    data = data.replace(/<script/g, '<scr_ipt');
                    data = data.replace(/<\/script>/g, '</scr_ipt>');
                    data = $('<div />').html(data).find('#content .files > .filediv');
                    $(data).each(function(i, filediv){
                        var img_src = $(filediv).find('.icon').attr('src');
                        img_src = $('#sub_root').text() + img_src.replace(/\.\.\//g, '');
                        $(filediv).find('.icon').attr('src', img_src);
                        if($(filediv).find('a')){
                            var href = path.replace('/index.html', '') + '/' + $(filediv).find('a').attr('href');
                            href = '#!merge?devices=' + encodeURIComponent(kwargs['devices']) + '&path=' + encodeURIComponent(href);
                            $(filediv).find('a').attr('href', href);
                        }
                        $('#content .files').append(filediv);
                    });
                }
            });
        });
    }
    
    ajax_pages = {'merge': merge}
    
    $.History.bind(function(hash){
        if(hash[0] != '!'){
            return
        }
        hash = hash.substring(1, hash.length)
        var page = hash.split('?')[0]
        var kwargs = {}
        if(hash.split('?').length>1){
            var argv = hash.split('?')[1]
            $.each(argv.split('&'), function(i, key_val){
                kwargs[decodeURIComponent(key_val.split('=')[0])] = decodeURIComponent(key_val.split('=')[1])
            });
        };
        ajax_pages[page](kwargs)
    });
    
    $('.merge').click(function(){
        var devices = new Array()
        $('#devices input:checked').each(function(i, input){
            devices[devices.length] = $(input).attr('name');
        });
        devices = devices.join(';');
        path = '';
        window.location = '#!merge?devices=' + devices + '&path=' + path;
    });
    
    $('#legal .lic').live('click', function(ev){
        var this_ = this;
        ev.preventDefault();
        $.ajax($(this_).attr('href'), {
            cache: true,
            async: false,
            success: function(data){
                console.debug(data);
                $('#show_license').html(data);
            },
        });
    });
    
    inputTitle();
    $(window).bind('popstate', function() {
        ajax_load(location.pathname);
    })
    
    $('#logo_div').click(function(){
        window.location = $('#sub_root').text() + 'index.html'
    });
    
    String.prototype.startswith = function (str){
        return this.indexOf(str) == 0;
    };
    
    Array.prototype.append = function (val){
        this[this.length] = val;
    };

    function sleep(millisegundos) {
        var inicio = new Date().getTime();
        while ((new Date().getTime() - inicio) < millisegundos);
    }
});