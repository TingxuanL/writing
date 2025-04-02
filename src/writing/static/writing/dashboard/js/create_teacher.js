jQuery(function ($) {

    $.fn.ready(function() {
        var $extract_features_form = $('#FormCreateStudent');
        if ($extract_features_form.length > 0) {
            $extract_features_form.submit(on_extract_features_form_submit);
        }
    });

    function on_extract_features_form_submit(event) {
        event.preventDefault();
        extract_features(event.target);
        return false;
    }
    
    function extract_features(form) {
        if (form.preview_busy) {
            return false;
        }

        form.preview_busy = true;
        var $form = $(form);
        var data = $form.serialize();
        var ajaxurl = $form.data('ajax-action');

        var $indicator = $('#badgeCreateStudent');
        $indicator.text("创建中...");

        $.ajax({
            type: 'POST',
            url: ajaxurl,
            data: data,
            dataType: 'json',
            success: function(data) {
                form.preview_busy = false;
                // remove_errors($form);
                
                if (data['success']) {
                    extract_features_success($form, data);
                } else{
                    extract_features_failure(data);
                }
            },
            error: function(xhr) {
                form.preview_busy = false;

                var response = xhr.responseText;
                if(response && window.console && response.indexOf('DJANGO_SETTINGS_MODULE') != -1) {
                    console.error(response);
                }

                alert("Internal CMS error: failed to create teachers!");    // can't yet rely on $.ajaxError

                // Submit as non-ajax instead
                //$form.unbind('submit').submit();
            }
        });
    }

    function extract_features_success($form, data) {
        reset_extract_features_form($form);
        var $indicator = $('#badgeCreateStudent');
        $indicator.text("成功创建" + data["cnt_created"] + "个教师");
        // $("#btn-extract").addClass("invisible");
        // $("#btn-download").removeClass("invisible");
    }

    function extract_features_failure(data) {
        var $indicator = $('#badgeCreateStudent');
        $indicator.text("创建失败" + data["errors"]["message"]);
        // var form = $('#extract-features-form')[0];

        // Show mew errors
        // for (var field_name in data['errors']) {
        //     if(field_name) {
        //         var $field = $(form.elements[field_name]);

        //         // Twitter bootstrap style
        //         var $closet_form_group = $field.closest('.form-group');
        //         $closet_form_group.append(
        //             '<div class="help-block">' + data['errors'][field_name] + '</div>'
        //         );
        //         $closet_form_group.addClass('has-error');
        //     }
        // }
    }

    function reset_extract_features_form($form) {
        $($form[0].elements['TextareaStudentIDs']).val('');
    }

});