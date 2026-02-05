import { useState, useMemo } from "react";
import { Show, StimulationLevel } from "./types";
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
    let shows = filterShows(mockShows, searchTerm, undefined, isInteracted);

    if (selectedBucket.label !== "All Ages") {
      shows = shows.filter((show) => {
        return (
          show.minAge <= selectedBucket.max && show.maxAge >= selectedBucket.min
        );
      });
    }

    if (selectedStimulation !== "All") {
      shows = shows.filter((show) => {
        const stim = (show.stimulationLevel || "Medium") as StimulationLevel;
        return stim === selectedStimulation;
      });
    }

    return sortShows(shows);
  }, [searchTerm, selectedBucket, selectedStimulation, isInteracted]);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="logo">KidShow Scout 🛡️</h1>
        <button
          style={{ color: "var(--c-blue)" }}
          onClick={() => alert("Login coming soon!")}
        >
          Parents Login
        </button>
      </header>

      <section className="hero-section">
        <div className="hero-content">
          <h2 className="hero-title">Safe shows for your little ones.</h2>
          <p className="hero-subtitle">
            Curated, opinionated, and always age-appropriate. Find the perfect
            show in seconds.
          </p>

          <div className="search-bar-container">
            <input
              type="text"
              placeholder="Search for 'Bluey'..."
              className="search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="hero-image-container">
          <img
            src="/assets/mascots.png"
            alt="Friendly Mascots"
            className="hero-mascot"
          />
        </div>
      </section>

      <main className="main-content">
        <section className="content-area">
          <h3 className="section-title">Top Picks For You</h3>

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
                <h3>Uh oh! No shows found for this age.</h3>
                <p>Try selecting a different age group.</p>
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
