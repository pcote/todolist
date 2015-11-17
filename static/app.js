var controller = function($scope, $http, $log){
    $http.get("/userinfo").then(function(res){
        $scope.display_name = res.data.display_name
        $scope.email = res.data.email
    },
    function(res){
    })
}

app = angular.module("app", [])
app.controller("controller", controller)
