//JavaScript
function init_ckeditor() {
    var notetext = document.getElementById('notetext');
    var noteid = document.getElementById('noteid');
    if (notetext != null)
    {
        editor = CKEDITOR.replace( 'notetext', {
        extraPlugins: 'imageresize',
        filebrowserImageUploadUrl: '/uploadimage/' + noteid.value + "/",
        uploadUrl: '/uploadimage_json/' + noteid.value + "/",
        allowedContent: true
        });

        editor.on( 'fileUploadResponse', function( evt ) {
            var fileLoader = evt.data.fileLoader,
                xhr = fileLoader.xhr,
                data = evt.data;
            try {
                var response = JSON.parse( xhr.responseText );

                // Error message does not need to mean that upload finished unsuccessfully.
                // It could mean that ex. file name was changes during upload due to naming collision.
                if ( response.error && response.error.message ) {
                    data.message = response.error.message;
                }

                // But !uploaded means error.
                if ( !response.uploaded ) {
                    evt.cancel();
                } else {
                    data.fileName = response.fileName;
                    data.url = response.url;
                    data.width = response.width;
                    data.height = response.height;

                    // Do not call the default listener.
                    evt.stop();
                }
            } catch ( err ) {
                // Response parsing error.
                data.message = fileLoader.lang.filetools.responseError;
                window.console && window.console.log( xhr.responseText );

                evt.cancel();
            }
        });

        editor.on( 'instanceReady', function() {
            editor.widgets.registered.uploadimage.onUploaded = function( upload ) {
                var response = JSON.parse( upload.xhr.responseText );
                this.replaceWith( '<img src="' + upload.url + '" ' +
                    'width="' + response.width + '" ' +
                    'height="' + response.height + '">' );
            }
        });
    }

}

init_ckeditor();

//Angular JS
var main_app = angular.module('main_app', []);
main_app.controller('main_ctrl', function($scope) {

$scope.showNote = function(idnote) {
    window.location.assign("/get_note/" + idnote);
}

})

main_app.controller('tag_ctrl', function($scope, $http, $window) {

    function update_note_tags() {
        try {
            var filters = getCheckedBoxes("t");
            document.getElementsByName("note_tags")[0].value = filters == null ? "" : filters;;
        }
        catch(err) {
            //just skip. not all pages has tis element.
        }
    }

    $scope.tag_onclick = function() {
        update_note_tags();
    };

    update_note_tags();

    $scope.default_taggroup = function(){
        var tg = document.getElementsByName('tg')[0].value;
        var edit_tg = {};
        edit_tg["tg"] = tg;
        var json_filter = JSON.stringify(edit_tg)
        $http.get("/default_group", {params: {"p": json_filter}}  )
        .success(function (response) {
           alert("Default topic set.");
           $window.location.reload();
        });
    };

    $scope.manage_taggroup = function() {
        var tg = document.getElementsByName('tg')[0].value;
        var edit_tg = {};
        edit_tg["tg"] = tg;
        var json_filter = JSON.stringify(edit_tg)
        $http.get("/manage_group2", {params: {"p": json_filter}}  )
        .success(function (response) {
           alert("Topic added to favourites.");
           $window.location.reload();
        })
        .error(function (response) {
           alert("Failed to add topic to favourites.");
        });
    };

    $scope.gotoPage = function(page) {
       holder = document.getElementsByName('tagpagetable')[0]
       tags = document.getElementsByName('tagpage'+page)[0]
       holder.scrollTop = tags.offsetTop;
    };
})

main_app.controller('taggroup_ctrl', function($scope, $http, $window) {

    //Edit taggroup dialog
    $scope.taggroup_edit_ok_btn = function(edit_idtaggroup, edit_taggroupname){
        var edit_data = {};
        edit_data["edit_idtaggroup"] = edit_idtaggroup;
        edit_data["edit_taggroupname"] = edit_taggroupname;
        var json_filter = JSON.stringify(edit_data);
        $http.get("/edit_group", {params: {"p": json_filter}}  )
        .success(function (response) {
            $window.location.reload();
        });
    };

    $scope.edit_taggroup_onclick = function(edit_idtaggroup, edit_taggroupname){
        $scope.edit_idtaggroup = edit_idtaggroup;
        $scope.edit_taggroupname = edit_taggroupname;
    }
    //End edit taggroup dialog

    //Edit tag dialog
    $scope.tag_edit_ok_btn = function(edit_idtag, edit_tagname, edit_tagpage){
        var edit_data = {};
        edit_data["edit_idtag"] = edit_idtag;
        edit_data["edit_tagname"] = edit_tagname;
        edit_data["edit_tagpage"] = edit_tagpage;
        var json_filter = JSON.stringify(edit_data);
        $http.get("/edit_tag", {params: {"p": json_filter}}  )
        .success(function (response) {
            $window.location.reload();
        });
    };

    $scope.edit_tag_onclick = function(edit_idtag, edit_tagname, edit_tagpage){
        $scope.edit_idtag = edit_idtag;
        $scope.edit_tagname = edit_tagname;
        $scope.edit_tagpage = edit_tagpage;
    }
    //End edit tag dialog
 })

// Pass the checkbox name to the function
function getCheckedBoxes(chkboxName) {
  var checkboxes = document.getElementsByName(chkboxName);
  var checkboxesChecked = [];
  // loop over them all
  for (var i=0; i<checkboxes.length; i++) {
     // And stick the checked ones onto an array...
     if (checkboxes[i].checked) {
        checkboxesChecked.push(checkboxes[i].id);
     }
  }
  // Return the array if it is non-empty, or null
  return checkboxesChecked.length > 0 ? checkboxesChecked : null;
}