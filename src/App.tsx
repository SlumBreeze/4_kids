import { useState, useMemo } from "react";
import { Show } from "./types";
import { mockShows } from "./data/mockShows";
import { filterShows, sortShows } from "./utils/filter";
import { ShowCard } from "./components/ShowCard";
import { AgeFilter, AGE_BUCKETS, AgeBucket } from "./components/AgeFilter";
import {
  StimulationFilter,
  StimulationFilterValue,
} from "./components/StimulationFilter";
import { ShowDetailModal } from "./components/ShowDetailModal";
import "./App.css";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedBucket, setSelectedBucket] = useState<AgeBucket>(
    AGE_BUCKETS[0],
  );
  const [selectedStimulation, setSelectedStimulation] =
    useState<StimulationFilterValue>("All");
  const [selectedShow, setSelectedShow] = useState<Show | null>(null);

  const isInteracted = useMemo(() => {
    return (
      searchTerm.trim() !== "" ||
      selectedBucket.label !== AGE_BUCKETS[0].label ||
      selectedStimulation !== "All"
    );
  }, [searchTerm, selectedBucket, selectedStimulation]);

  const filteredShows = useMemo(() => {
    const shows = filterShows(
      mockShows,
      searchTerm,
      selectedBucket.min,
      selectedBucket.max,
      selectedStimulation,
      undefined,
      isInteracted,
    );

    return sortShows(shows, searchTerm);
  }, [searchTerm, selectedBucket, selectedStimulation, isInteracted]);

  const shortlistLabel =
    selectedStimulation === "All"
      ? "Best matches for tonight"
      : `${selectedStimulation} stimulation matches`;

  return (
    <div className="app-container">
      <header className="app-header">
        <div>
          <h1 className="logo">KidShow Scout</h1>
        </div>
        <button className="account-button" onClick={() => alert("Login coming soon!")}>
          Login
        </button>
      </header>

      <section className="hero-section">
        <div className="hero-content">
          <h2 className="hero-title">Tonight's Shortlist</h2>
          <p className="hero-subtitle">
            Find something age-fit, safe enough, and calm enough before bedtime
            becomes a negotiation.
          </p>

          <div className="search-bar-container">
            <input
              type="text"
              placeholder="Search shows"
              className="search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </section>

      <main className="main-content">
        <section className={`content-area ${searchTerm.trim() ? "searching" : ""}`}>
          <div className="section-heading">
            <div>
              <span className="eyebrow">Browse</span>
              <h3 className="section-title">{shortlistLabel}</h3>
            </div>
            <span className="result-count">{filteredShows.length} shows</span>
          </div>

          <AgeFilter
            selectedLabel={selectedBucket.label}
            onSelect={setSelectedBucket}
          />
          <StimulationFilter
            selected={selectedStimulation}
            onSelect={setSelectedStimulation}
          />

          <div className="shows-grid">
            {filteredShows.length > 0 ? (
              filteredShows.map((show) => (
                <ShowCard
                  key={show.id}
                  show={show}
                  onClick={() => setSelectedShow(show)}
                />
              ))
            ) : (
              <div className="no-results">
                <h3>No shows match these filters.</h3>
                <p>Try a wider age range or a different stimulation level.</p>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Modal Overlay */}
      <ShowDetailModal
        show={selectedShow}
        onClose={() => setSelectedShow(null)}
      />
    </div>
  );
}

export default App;
