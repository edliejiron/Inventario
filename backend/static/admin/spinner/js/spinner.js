(function ($) {
    $(document).ready(function () {
        const openSpinner = function () {
            $('#grp-spinner').css('display', 'initial')
        };
        const closeSpinner = function () {
            $('#grp-spinner').css('display', 'none')
        };
        $(document).on('ajaxStart', openSpinner);
        $(document).on('ajaxStop', closeSpinner);
    })
})(grp.jQuery)