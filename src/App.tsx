import { useEffect, useMemo, useState } from "react";
import { Show } from "./types";
import { fetchShow, fetchShows } from "./api/shows";
import { ShowCard } from "./components/ShowCard";
import { AgeFilter, AGE_BUCKETS, AgeBucket } from "./components/AgeFilter";
import {
  StimulationFilter,
  StimulationFilterValue,
} from "./components/StimulationFilter";
import { ShowDetailModal } from "./components/ShowDetailModal";
import "./App.css";

const PAGE_SIZE = 25;

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedBucket, setSelectedBucket] = useState<AgeBucket>(
    AGE_BUCKETS[0],
  );
  const [selectedStimulation, setSelectedStimulation] =
    useState<StimulationFilterValue>("All");
  const [selectedShow, setSelectedShow] = useState<Show | null>(null);
  const [shows, setShows] = useState<Show[]>([]);
  const [totalShows, setTotalShows] = useState(0);
  const [isLoadingShows, setIsLoadingShows] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [pageOffset, setPageOffset] = useState(0);

  const showsQuery = useMemo(() => {
    const query = {
      q: searchTerm.trim() || undefined,
      minAge: selectedBucket.min,
      maxAge: selectedBucket.max,
      stimulationLevel:
        selectedStimulation === "All" ? undefined : selectedStimulation,
      limit: PAGE_SIZE,
      offset: pageOffset,
    };

    return query;
  }, [pageOffset, searchTerm, selectedBucket, selectedStimulation]);

  useEffect(() => {
    const controller = new AbortController();

    setIsLoadingShows(true);
    setLoadError("");
    if (showsQuery.offset === 0) {
      setShows([]);
      setTotalShows(0);
    }

    fetchShows(showsQuery, controller.signal)
      .then((response) => {
        setShows((currentShows) =>
          response.offset === 0
            ? response.items
            : [...currentShows, ...response.items],
        );
        setTotalShows(response.total);
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setShows([]);
        setTotalShows(0);
        setLoadError("Show data failed to load.");
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoadingShows(false);
        }
      });

    return () => controller.abort();
  }, [showsQuery]);

  const updateSearchTerm = (value: string) => {
    setSearchTerm(value);
    setPageOffset(0);
  };

  const updateSelectedBucket = (bucket: AgeBucket) => {
    setSelectedBucket(bucket);
    setPageOffset(0);
  };

  const updateSelectedStimulation = (value: StimulationFilterValue) => {
    setSelectedStimulation(value);
    setPageOffset(0);
  };

  const openShow = (show: Show) => {
    const controller = new AbortController();

    setSelectedShow(show);
    fetchShow(show.id, controller.signal)
      .then(setSelectedShow)
      .catch(() => {
        setSelectedShow(show);
      });
  };

  const shortlistLabel =
    selectedStimulation === "All"
      ? "Best matches for tonight"
      : `${selectedStimulation} stimulation matches`;
  const hasMoreShows = totalShows > shows.length;

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
              onChange={(e) => updateSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </section>

      <main className="main-content">
        <section className="content-area">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Browse</span>
              <h3 className="section-title">{shortlistLabel}</h3>
            </div>
            <span className="result-count">
              {isLoadingShows ? "Loading" : `${totalShows} shows`}
            </span>
          </div>

          <AgeFilter
            selectedLabel={selectedBucket.label}
            onSelect={updateSelectedBucket}
          />
          <StimulationFilter
            selected={selectedStimulation}
            onSelect={updateSelectedStimulation}
          />

          <div className="shows-grid">
            {loadError ? (
              <div className="no-results">
                <h3>{loadError}</h3>
                <p>Refresh the page and try again.</p>
              </div>
            ) : shows.length > 0 ? (
              shows.map((show) => (
                <ShowCard
                  key={show.id}
                  show={show}
                  onClick={() => openShow(show)}
                />
              ))
            ) : isLoadingShows ? (
              <div className="no-results">
                <h3>Loading shows.</h3>
                <p>Fetching the shortlist from the show-data API.</p>
              </div>
            ) : (
              <div className="no-results">
                <h3>No shows match these filters.</h3>
                <p>Try a wider age range or a different stimulation level.</p>
              </div>
            )}
          </div>

          {!loadError && hasMoreShows ? (
            <div className="pagination-controls">
              <button
                className="load-more-button"
                disabled={isLoadingShows}
                onClick={() => setPageOffset(shows.length)}
              >
                {isLoadingShows ? "Loading" : "Load more"}
              </button>
            </div>
          ) : null}
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
