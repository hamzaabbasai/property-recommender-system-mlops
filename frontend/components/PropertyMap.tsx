"use client";

import type { Map as MapboxMap, Marker as MapboxMarker } from "mapbox-gl";
import { useEffect, useRef } from "react";

type MapProperty = {
  id: string;
  title: string;
  neighborhood: string;
  price: number;
  latitude: number;
  longitude: number;
};

type PropertyMapProps = {
  properties: MapProperty[];
};

function priceLabel(price: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(price);
}

export default function PropertyMap({ properties }: PropertyMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

  useEffect(() => {
    if (!mapContainer.current || !accessToken) return;

    let map: MapboxMap | undefined;
    let markers: MapboxMarker[] = [];
    let stopped = false;

    async function createMap() {
      const mapboxgl = await import("mapbox-gl");
      if (!mapContainer.current || stopped) return;

      map = new mapboxgl.Map({
        accessToken,
        center: [13.405, 52.52],
        container: mapContainer.current,
        style: "mapbox://styles/mapbox/streets-v12",
        zoom: 10.6,
      });

      map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "top-right");

      const bounds = new mapboxgl.LngLatBounds();

      markers = properties.map((property, index) => {
        const markerButton = document.createElement("button");
        const markerNumber = document.createElement("span");
        markerButton.className = "property-map-marker";
        markerButton.type = "button";
        markerNumber.textContent = String(index + 1);
        markerButton.append(markerNumber);
        markerButton.setAttribute("aria-label", `View ${property.title}`);
        markerButton.addEventListener("click", () => {
          document.getElementById(`property-${property.id}`)?.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
        });

        const popupContent = document.createElement("div");
        const popupTitle = document.createElement("strong");
        const popupPrice = document.createElement("span");
        popupTitle.textContent = property.neighborhood;
        popupPrice.textContent = `${priceLabel(property.price)} / night`;
        popupContent.append(popupTitle, popupPrice);

        const popup = new mapboxgl.Popup({ closeButton: false, offset: 22 })
          .setDOMContent(popupContent);

        bounds.extend([property.longitude, property.latitude]);
        return new mapboxgl.Marker({ element: markerButton })
          .setLngLat([property.longitude, property.latitude])
          .setPopup(popup)
          .addTo(map as MapboxMap);
      });

      if (properties.length > 1) {
        map.fitBounds(bounds, { padding: 48, maxZoom: 12.5 });
      }
    }

    void createMap();

    return () => {
      stopped = true;
      markers.forEach((marker) => marker.remove());
      map?.remove();
    };
  }, [accessToken, properties]);

  if (!accessToken) {
    return (
      <div className="property-map map-token-missing" role="status">
        <p>Mapbox token is not configured.</p>
      </div>
    );
  }

  return <div className="property-map" ref={mapContainer} />;
}
