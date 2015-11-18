var controller = function($scope, $http, $log){
    $http.get("/userinfo").then(function(res){
        $scope.display_name = res.data.display_name
        $scope.email = res.data.email
    },
    function(res){
    })

    // get the user todo list.
    $http.get("/todolist").then(function(res){
        $scope.todo_list = res.data.todo_list
    }, function(res){})

    $scope.done_click = function(id){
        var req = {
            url: "/completed",
            method: "put",
            headers: {
                "Content-type": "application/json"
            },

            data: {"item_id": id}
        }

        $http(req).then(function(res){
            $scope.todo_list = res.data.todo_list
        }, function(res){})
    }

}

app = angular.module("app", [])
app.controller("controller", controller)
