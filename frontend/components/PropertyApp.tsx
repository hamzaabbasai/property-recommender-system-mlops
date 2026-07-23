"use client";

import {
  Bath,
  BedDouble,
  Building2,
  Check,
  ChevronDown,
  GitCompareArrows,
  Heart,
  MapPin,
  Search,
  SlidersHorizontal,
  Star,
  Users,
  X,
} from "lucide-react";
import Image from "next/image";
import { FormEvent, useMemo, useState } from "react";
import PropertyMap from "./PropertyMap";

type Property = {
  id: string;
  title: string;
  neighborhood: string;
  city: string;
  price: number;
  bedrooms: number;
  beds: number;
  bathrooms: number;
  accommodates: number;
  property_type: string;
  room_detail: string;
  amenities: string[];
  minimum_nights: number;
  availability_365: number;
  rating: number;
  review_count: number;
  image_url: string;
  match_label: string;
  reasons: string[];
  latitude: number;
  longitude: number;
};

type Filters = {
  maxBudget: number;
  bedrooms: number;
  propertyTypes: string[];
  amenities: string[];
};

const initialFilters: Filters = {
  maxBudget: 180,
  bedrooms: 2,
  propertyTypes: ["Entire home/apt"],
  amenities: ["Wifi", "Kitchen", "Washer"],
};

const sampleProperties: Property[] = [
  {
    id: "berlin-101",
    title: "Sunny apartment near Boxhagener Platz",
    neighborhood: "Friedrichshain-Kreuzberg",
    city: "Berlin",
    price: 145,
    bedrooms: 2,
    beds: 2,
    bathrooms: 1,
    accommodates: 4,
    property_type: "Entire home/apt",
    room_detail: "Entire rental unit",
    amenities: ["Wifi", "Kitchen", "Washer", "Balcony"],
    minimum_nights: 2,
    availability_365: 184,
    rating: 4.88,
    review_count: 126,
    image_url: "/properties/property-1.png",
    match_label: "Best match",
    reasons: ["Within nightly budget", "Has Wifi", "Highly rated"],
    latitude: 52.5158,
    longitude: 13.4542,
  },
  {
    id: "berlin-102",
    title: "Modern stay with a quiet balcony",
    neighborhood: "Pankow",
    city: "Berlin",
    price: 169,
    bedrooms: 2,
    beds: 3,
    bathrooms: 1.5,
    accommodates: 5,
    property_type: "Entire home/apt",
    room_detail: "Entire condo",
    amenities: ["Wifi", "Kitchen", "Washer", "Balcony"],
    minimum_nights: 3,
    availability_365: 201,
    rating: 4.79,
    review_count: 84,
    image_url: "/properties/property-2.png",
    match_label: "Good match",
    reasons: ["Within nightly budget", "Has Kitchen", "Highly rated"],
    latitude: 52.5411,
    longitude: 13.4248,
  },
  {
    id: "berlin-103",
    title: "Charming Altbau near the canal",
    neighborhood: "Neukölln",
    city: "Berlin",
    price: 158,
    bedrooms: 2,
    beds: 2,
    bathrooms: 1,
    accommodates: 4,
    property_type: "Entire home/apt",
    room_detail: "Entire rental unit",
    amenities: ["Wifi", "Kitchen", "Washer"],
    minimum_nights: 2,
    availability_365: 97,
    rating: 4.72,
    review_count: 61,
    image_url: "/properties/property-3.png",
    match_label: "Good match",
    reasons: ["Within nightly budget", "Has Washer", "Popular listing"],
    latitude: 52.4812,
    longitude: 13.4356,
  },
  {
    id: "berlin-104",
    title: "Quiet courtyard home near Viktoriapark",
    neighborhood: "Friedrichshain-Kreuzberg",
    city: "Berlin",
    price: 176,
    bedrooms: 2,
    beds: 2,
    bathrooms: 1,
    accommodates: 4,
    property_type: "Entire home/apt",
    room_detail: "Entire rental unit",
    amenities: ["Wifi", "Kitchen", "Washer", "Pets allowed"],
    minimum_nights: 4,
    availability_365: 143,
    rating: 4.83,
    review_count: 73,
    image_url: "/properties/property-1.png",
    match_label: "Good match",
    reasons: ["Within nightly budget", "Has Wifi", "Highly rated"],
    latitude: 52.4898,
    longitude: 13.3813,
  },
];

const propertyTypes = ["Entire home/apt", "Private room", "Shared room", "Hotel room"];
const amenityOptions = ["Wifi", "Kitchen", "Washer", "Balcony", "Pets allowed"];

function toggleItem(items: string[], value: string) {
  return items.includes(value)
    ? items.filter((item) => item !== value)
    : [...items, value];
}

function formatPrice(price: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(price);
}

export default function PropertyApp() {
  const [query, setQuery] = useState(
    "Entire apartment in Berlin under €180 per night with Wifi and kitchen",
  );
  const [filters, setFilters] = useState(initialFilters);
  const [results, setResults] = useState(sampleProperties);
  const [saved, setSaved] = useState<string[]>([]);
  const [compared, setCompared] = useState<string[]>([]);
  const [openReasons, setOpenReasons] = useState<string[]>([]);
  const [activeView, setActiveView] = useState("Discover");
  const [isLoading, setIsLoading] = useState(false);

  const visibleResults = useMemo(() => {
    let items = results.filter(
      (property) =>
        property.price <= filters.maxBudget &&
        property.bedrooms >= filters.bedrooms &&
        filters.propertyTypes.includes(property.property_type) &&
        filters.amenities.every((amenity) => property.amenities.includes(amenity)),
    );

    if (activeView === "Saved") {
      items = items.filter((property) => saved.includes(property.id));
    }

    if (activeView === "Compare") {
      items = items.filter((property) => compared.includes(property.id));
    }

    return items;
  }, [activeView, compared, filters, results, saved]);

  async function applyFilters(event?: FormEvent) {
    event?.preventDefault();
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          city: "Berlin",
          max_budget: filters.maxBudget,
          bedrooms: filters.bedrooms,
          property_types: filters.propertyTypes,
          amenities: filters.amenities,
          top_k: 10,
        }),
      });

      if (!response.ok) throw new Error("The API did not return results.");
      const data = await response.json();
      setResults(data.results);
    } catch {
      // Keep the current results when the API is offline.
    } finally {
      setIsLoading(false);
      setActiveView("Discover");
    }
  }

  function resetFilters() {
    setFilters(initialFilters);
    setQuery("Entire apartment in Berlin under €180 per night with Wifi and kitchen");
    setResults(sampleProperties);
  }

  function toggleSaved(id: string) {
    setSaved((items) => toggleItem(items, id));
  }

  function toggleCompared(id: string) {
    setCompared((items) => {
      if (items.includes(id)) return items.filter((item) => item !== id);
      return items.length < 3 ? [...items, id] : items;
    });
  }

  function toggleReasons(id: string) {
    setOpenReasons((items) => toggleItem(items, id));
  }

  return (
    <main className="property-app">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Property Recommender home">
          Property Recommender
        </a>
        <nav aria-label="Main navigation">
          {["Discover", "Saved", "Compare"].map((item) => (
            <button
              className={activeView === item ? "nav-link active" : "nav-link"}
              key={item}
              onClick={() => setActiveView(item)}
            >
              {item}
              {item === "Saved" && saved.length > 0 && <span>{saved.length}</span>}
              {item === "Compare" && compared.length > 0 && <span>{compared.length}</span>}
            </button>
          ))}
        </nav>
        <button
          className="preferences-button"
          onClick={() => window.scrollTo({ top: 140, behavior: "smooth" })}
          type="button"
        >
          <span className="avatar">HA</span>
          My preferences
          <ChevronDown size={16} />
        </button>
      </header>

      <section className="search-area" id="top">
        <form className="search-form" onSubmit={applyFilters}>
          <Search size={22} />
          <input
            aria-label="Search properties"
            onChange={(event) => setQuery(event.target.value)}
            value={query}
          />
          <button aria-label="Clear search" onClick={() => setQuery("")} type="button">
            <X size={21} />
          </button>
        </form>

        <div className="search-meta">
          <div className="preference-chips" aria-label="Quick preferences">
            <span className="location-chip">
              <MapPin size={17} /> Berlin stays
            </span>
            {["Wifi", "Kitchen"].map((item) => (
              <button
                className={filters.amenities.includes(item) ? "selected" : ""}
                key={item}
                onClick={() =>
                  setFilters((current) => ({
                    ...current,
                    amenities: toggleItem(current.amenities, item),
                  }))
                }
                type="button"
              >
                {item === "Wifi" ? <Building2 size={17} /> : <BedDouble size={17} />}
                {item}
              </button>
            ))}
          </div>
          <button className="edit-button" onClick={() => window.scrollTo({ top: 140, behavior: "smooth" })}>
            <SlidersHorizontal size={17} /> Edit preferences
          </button>
        </div>
      </section>

      <div className="dashboard-layout">
        <aside className="filters-panel">
          <div className="panel-heading">
            <h2>Filters</h2>
            <button onClick={resetFilters} type="button">Reset</button>
          </div>

          <div className="filter-group">
            <label htmlFor="budget">Budget <span>(per night)</span></label>
            <input
              id="budget"
              max="300"
              min="50"
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  maxBudget: Number(event.target.value),
                }))
              }
              step="10"
              type="range"
              value={filters.maxBudget}
            />
            <div className="range-values">
              <span>€50</span>
              <strong>{formatPrice(filters.maxBudget)}</strong>
            </div>
          </div>

          <div className="filter-group">
            <p className="filter-label">Bedrooms</p>
            <div className="option-list compact">
              {[1, 2, 3].map((number) => (
                <label key={number}>
                  <input
                    checked={filters.bedrooms === number}
                    name="bedrooms"
                    onChange={() => setFilters((current) => ({ ...current, bedrooms: number }))}
                    type="radio"
                  />
                  <span className="control"><Check size={13} /></span>
                  {number === 3 ? "3+" : number}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <p className="filter-label split">Property type <ChevronDown size={15} /></p>
            <div className="option-list">
              {propertyTypes.map((item) => (
                <label key={item}>
                  <input
                    checked={filters.propertyTypes.includes(item)}
                    onChange={() =>
                      setFilters((current) => ({
                        ...current,
                        propertyTypes: toggleItem(current.propertyTypes, item),
                      }))
                    }
                    type="checkbox"
                  />
                  <span className="control"><Check size={13} /></span>
                  {item}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <p className="filter-label split">Amenities <ChevronDown size={15} /></p>
            <div className="option-list">
              {amenityOptions.map((item) => (
                <label key={item}>
                  <input
                    checked={filters.amenities.includes(item)}
                    onChange={() =>
                      setFilters((current) => ({
                        ...current,
                        amenities: toggleItem(current.amenities, item),
                      }))
                    }
                    type="checkbox"
                  />
                  <span className="control"><Check size={13} /></span>
                  {item}
                </label>
              ))}
            </div>
          </div>

          <button className="apply-button" disabled={isLoading} onClick={() => applyFilters()} type="button">
            {isLoading ? "Updating..." : "Apply filters"}
          </button>
          <p className="match-count">{visibleResults.length} matches</p>
        </aside>

        <section className="results-panel">
          <div className="results-heading">
            <div>
              <p className="eyebrow">{activeView}</p>
              <h1>{activeView === "Discover" ? "Recommended for you" : `${activeView} properties`}</h1>
            </div>
            <span>{visibleResults.length} results</span>
          </div>

          <div className="property-list">
            {visibleResults.length === 0 && (
              <div className="empty-state">
                <Building2 size={30} />
                <h2>No properties found</h2>
                <p>Change your filters or return to Discover.</p>
              </div>
            )}

            {visibleResults.map((property, index) => (
              <article className="property-card" id={`property-${property.id}`} key={property.id}>
                <div className="image-wrap">
                  <Image
                    alt={`${property.title} in ${property.neighborhood}`}
                    height={540}
                    sizes="(max-width: 600px) 100vw, (max-width: 1180px) 36vw, 300px"
                    src={property.image_url}
                    width={720}
                  />
                  <span className="rank-number">{index + 1}</span>
                </div>
                <div className="property-info">
                  <div className="property-title-row">
                    <div>
                      <h2>{property.title}</h2>
                      <p>{property.neighborhood}, {property.city}</p>
                    </div>
                    <button
                      aria-label={saved.includes(property.id) ? "Remove saved property" : "Save property"}
                      className={saved.includes(property.id) ? "save-button saved" : "save-button"}
                      onClick={() => toggleSaved(property.id)}
                    >
                      <Heart fill={saved.includes(property.id) ? "currentColor" : "none"} size={19} />
                      {saved.includes(property.id) ? "Saved" : "Save"}
                    </button>
                  </div>

                  <p className="price">{formatPrice(property.price)} <span>/ night</span></p>
                  <div className="property-facts">
                    <span><BedDouble size={17} /> {property.bedrooms} bedrooms</span>
                    <span><Users size={17} /> {property.accommodates} guests</span>
                    <span><Bath size={17} /> {property.bathrooms} baths</span>
                    <span><Star size={17} /> {property.rating.toFixed(2)}</span>
                  </div>

                  <div className="card-bottom">
                    <div>
                      <span className={property.match_label === "Best match" ? "match-label best" : "match-label"}>
                        {property.match_label}
                      </span>
                      <p className="reasons">{property.reasons.join(" · ")}</p>
                      <button className="why-button" onClick={() => toggleReasons(property.id)}>
                        Why recommended <ChevronDown className={openReasons.includes(property.id) ? "open" : ""} size={16} />
                      </button>
                      {openReasons.includes(property.id) && (
                        <p className="reason-detail">
                          These reasons come from the ranking features. They are not a match probability.
                        </p>
                      )}
                    </div>
                    <label className="compare-control">
                      <input
                        checked={compared.includes(property.id)}
                        onChange={() => toggleCompared(property.id)}
                        type="checkbox"
                      />
                      <span className="control"><Check size={13} /></span>
                      Compare
                    </label>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="map-column">
          <div className="map-card" aria-label="Map of recommended properties">
            <PropertyMap properties={visibleResults.slice(0, 10)} />
          </div>

          <div className="summary-card">
            <p className="summary-title"><MapPin size={18} /> Search summary</p>
            <h2>{visibleResults.length} matching properties</h2>
            <dl>
              <div><dt>Location</dt><dd>Berlin</dd></div>
              <div><dt>Nightly budget</dt><dd>Up to {formatPrice(filters.maxBudget)}</dd></div>
              <div><dt>Bedrooms</dt><dd>{filters.bedrooms}</dd></div>
            </dl>
            <button onClick={() => applyFilters()} type="button">
              <GitCompareArrows size={17} /> Refresh ranking
            </button>
          </div>
        </aside>
      </div>
    </main>
  );
}
