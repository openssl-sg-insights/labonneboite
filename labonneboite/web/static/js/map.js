/* jshint esversion: 6 */
function createMap(element) {
  L.mapbox.accessToken = 'pk.eyJ1IjoibGFib25uZWJvaXRlIiwiYSI6ImNpaDNoN3A0cDAwcmdybGx5aXF1Z21lOGIifQ.znyUeU7KoIY9Ns_AQPquAg';
  var mapEl = L.mapbox.map(element, 'mapbox.streets', {
      attributionControl: false
  });
  mapEl.scrollWheelZoom.disable();
  return mapEl;
}

(function($) {
  var center = null;
  var zoom = null;
  var autoRefreshActivated = false;

  function initResultsMap() {
    "use strict";
    var $map = $('#lbb-result-map');
    var $latitude = $("#lat");
    var $longitude = $("#lon");
    if (!$map.length) {
      return;
    }

    var map = createMap($map[0]);
    var minLat = 90, maxLat = -90, minLng = 180, maxLng = -180;
    var companyCount = 0;

    $(".lbb-result").each(function() {
      var companyName = $(this).find('input[name="company-name"]').val();
      var lat = $(this).find('input[name="company-latitude"]').val();
      var lng = $(this).find('input[name="company-longitude"]').val();
      var siret = $(this).find('input[name="company-siret"]').val();
      var description = $(this).find('.company-naf-text').html();

      var coords = [lat, lng];
      var link = "<a class='map-marker' href='#company-" + siret + "'>" + companyName + "</a><br>" + description;
      L.marker(coords).addTo(map).bindPopup(link);

      companyCount += 1;
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
    });

    $map.on("click", "a.map-marker", function(e) {
        var href = this.attributes.href.value;
        ga('send', 'event', 'Carte', 'click entreprise', href);
        // Toggle company details on click on link
        $(href).find(".js-result-toggle-details").click();
    });

    // Focus either on the companies or the requested coordinates
    if (center !== null && zoom !== null) {
      // Reset to the same position if we just moved the map
      map.setView(center, zoom);
    } else if (companyCount == 1) {
      map.setView([minLat, minLng], 13);
    } else if (companyCount > 0) {
      map.fitBounds([
        [minLat, minLng],
        [maxLat, maxLng]
      ]);
    } else {
      map.setView([$latitude.val(), $longitude.val()], 13);
    }

    // Add auto-refresh check
    $map.append("<div id='map-auto-refresh'><div id='map-auto-refresh-checkbox'><input type='checkbox'></input><span>Rechercher quand je déplace la carte<span></div></div>");
    $("#map-auto-refresh input").prop('checked', autoRefreshActivated);
    $("#map-auto-refresh input").change(function() {
        autoRefreshActivated = $(this).is(':checked');
        ga('send', 'event', 'Carte', 'toggle autorefresh', autoRefreshActivated ? 1 : 0);
    });


    var onMapMove = function() {
      if(autoRefreshActivated) {
        updateMap();
      }
      else {
          $("#map-auto-refresh").html("<a class='btn btn-small btn-info' href='#''>Relancer la recherche ici</a>").addClass();
          $("#map-auto-refresh a").click(function(e) {
              ga('send', 'event', 'Carte', 'refresh');
              e.preventDefault();
              updateMap();
          });
      }
    };
    var onMapDrag = function() {
      ga('send', 'event', 'Carte', 'drag');
      onMapMove();
    };
    var onMapZoom = function() {
        ga('send', 'event', 'Carte', 'zoom');
        onMapMove();
    };

    var updateMap = function() {
      ga('send', 'event', 'Carte', 'update');
      center = map.getCenter();
      zoom = map.getZoom();

      $latitude.val(center.lat);
      $longitude.val(center.lng);

      // Adjust search radius
      var distances = [5, 10, 30, 50, 100, 3000];
      var earthPerimeterKm = 2 * 3.14159 * 6371;
      var earthPerimeterAtCompanyLocationKm = earthPerimeterKm * Math.cos(center.lat);
      // See leaflet.js zoom definition https://wiki.openstreetmap.org/wiki/Zoom_levels
      var pixelSizeKm = earthPerimeterAtCompanyLocationKm / (256 * Math.pow(2, zoom));
      var mapHeightPixels = map.getSize().y;
      var windowHeightKm = pixelSizeKm * mapHeightPixels * 2;// 2 is an arbitrary scaling factor to include results just ouside the bounding box
      var newDistance = distances[distances.length - 1];
      for(var d=0; d < distances.length; d++) {
          if(windowHeightKm < distances[d]) {
              newDistance = distances[d];
              break;
          }
      }
      $("input[name='d']").val(newDistance);

      $('.js-search-form').trigger('submit', {async: true});
    };
    map.on('dragend', onMapDrag);
    map.on('zoom', onMapZoom);
  }

  $(document).on('lbbready', function () {
      initResultsMap();
  });

})(jQuery);