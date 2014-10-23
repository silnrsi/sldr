'use strict';

angular.module('sa.projects', [
    'sa.services'
  ])
  .controller('ProjectsCtrl', [ '$scope', function($scope) {

  }])
  .controller('PublicPieCtrl', [ '$scope', 'PublicProjectService', function($scope, PublicProjectService) {
    var projects = PublicProjectService.query(function() {
      var temp = {};
      projects.forEach(function(d) {
//        console.log(d);
        if (temp[d.type] == undefined) {
          temp[d.type] = 1;
        } else {
          temp[d.type]++;
        }
      });
      var data = [];
      for (var key in temp) {
        data.push({type: key, value: temp[key]});
      }

//      console.log(data);

      nv.addGraph(function() {
        var chart = nv.models.pieChart().x(function(d) {
          return d.type;
        }).y(function(d) {
          return d.value
        }).showLabels(true);

        d3.select(".chartPublicPie").datum(data).transition().duration(1200).call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
      });

    });

  }])
  .controller('PublicProjectsCtrl', [ '$scope', 'PublicProjectService', function($scope, PublicProjectService) {
    var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S%Z").parse;

    var data = PublicProjectService.query(function() {
      var sum = 0;
      data.forEach(function(d) {
        d.created_on = parseDate(d.created_on);
        d.total = sum++;
      });
      var graphData = [
        {
          key: 'Public Projects Created',
          values: data
        }
      ];

      nv.addGraph(function() {
        var chart = nv.models.lineChart();
          chart.x(function(d) {
            return d.created_on;
          });
          chart.y(function(d) {
            return d.total;
        });

        chart.xAxis.tickFormat(function(d) { return d3.time.format('%m/%Y')(new Date(d)) });

        chart.yAxis.tickFormat(d3.format(',f'));

        chart.xScale(d3.time.scale());

      // chart.y2Axis
      // .tickFormat(d3.format(',f'));

        d3.select('.chartPublic')
          .datum(graphData)
          .transition().duration(500)
          .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
      });

    });

  }])
  .controller('PrivatePieCtrl', [ '$scope', 'PrivateProjectService', function($scope, PrivateProjectService) {
    var projects = PrivateProjectService.query(function() {
      var temp = {};
      projects.forEach(function(d) {
//        console.log(d);
        if (temp[d.type] == undefined) {
          temp[d.type] = 1;
        } else {
          temp[d.type]++;
        }
      });
      var data = [];
      for (var key in temp) {
        data.push({type: key, value: temp[key]});
      }

//      console.log(data);

      nv.addGraph(function() {
        var chart = nv.models.pieChart().x(function(d) {
          return d.type;
        }).y(function(d) {
          return d.value
        }).showLabels(true);

        d3.select(".chartPrivatePie").datum(data).transition().duration(1200).call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
      });

    });

  }])
  .controller('PrivateProjectsCtrl', [ '$scope', 'PrivateProjectService', function($scope, PrivateProjectService) {
    var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S%Z").parse;

    var data = PrivateProjectService.query(function() {
      var sum = 0;
      data.forEach(function(d) {
        d.created_on = parseDate(d.created_on);
        d.total = sum++;
      });
      var graphData = [
        {
          key: 'Private Projects Created',
          values: data
        }
      ];

      nv.addGraph(function() {
        var chart = nv.models.lineChart();
          chart.x(function(d) {
            return d.created_on;
          });
          chart.y(function(d) {
            return d.total;
        });

        chart.xAxis.tickFormat(function(d) { return d3.time.format('%m/%Y')(new Date(d)) });

        chart.yAxis.tickFormat(d3.format(',f'));

        chart.xScale(d3.time.scale());

      // chart.y2Axis
      // .tickFormat(d3.format(',f'));

        d3.select('.chartPrivate')
          .datum(graphData)
          .transition().duration(500)
          .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
      });

    });

  }])
  ;
