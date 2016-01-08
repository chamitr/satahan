//JavaScript
function init_ckeditor() {
    var notetext = document.getElementById('notetext');
    var noteid = document.getElementById('noteid');
    if (notetext != null)
    {
        CKEDITOR.replace( 'notetext', {
        filebrowserImageUploadUrl: '/uploadimage/' + noteid.value + "/"
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
           alert("Default group set.");
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
           alert("Group added to favourites.");
           $window.location.reload();
        })
        .error(function (response) {
           alert("Failed to add group to favourites.");
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