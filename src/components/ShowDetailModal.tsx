import React, { useEffect } from "react";
import { Show } from "../types";
import { formatAgeRange } from "../utils/format";
import styles from "./ShowDetailModal.module.css";

interface ShowDetailModalProps {
  show: Show | null;
  onClose: () => void;
}

export const ShowDetailModal: React.FC<ShowDetailModalProps> = ({
  show,
  onClose,
}) => {
  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  if (!show) return null;

  const stimLevel = show.stimulationLevel || "Medium"; // Default

  // Helper for stimulation badge style
  const stimStyle = {
    Low: { bg: "#E8F5E9", color: "#2E7D32", text: "🍃 Low Stimulation" },
    Medium: { bg: "#FFF3E0", color: "#E65100", text: "⚡ Medium Stimulation" },
    High: { bg: "#F3E5F5", color: "#7B1FA2", text: "🚀 High Stimulation" },
  }[stimLevel];

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          ×
        </button>

        <div className={styles.header}>
          <img
            src={show.coverImage}
            alt={show.title}
            className={styles.coverImage}
          />

          <div className={styles.headerInfo}>
            <div className={styles.badges}>
              <span
                className={`${styles.ratingBadge} ${show.rating === "Safe" ? styles.safe : styles.caution}`}
              >
                {show.rating === "Safe"
                  ? "✅ Safe"
                  : show.rating === "Unsafe"
                    ? "🚫 Unsafe"
                    : "⚠️ Caution"}
              </span>
              <span className={styles.ageBadge}>
                {formatAgeRange(show.minAge, show.maxAge)}
              </span>

              <span
                className={styles.stimBadge}
                style={{
                  backgroundColor: stimStyle.bg,
                  color: stimStyle.color,
                }}
              >
                {stimStyle.text}
              </span>
            </div>

            <div className={styles.titleGroup}>
              <h2 className={styles.title}>{show.title}</h2>
              <span className={styles.year}>
                {show.releaseYear && show.releaseYear}
                {show.releaseYear && show.runtime && " • "}
                {show.runtime && show.runtime}
              </span>
            </div>

            <div className={styles.tags}>
              {show.tags.map((tag) => (
                <span key={tag} className={styles.tag}>
                  {tag}
                </span>
              ))}
            </div>

            <p className={styles.synopsis}>{show.synopsis}</p>
          </div>
        </div>

        <div className={styles.body}>
          <div className={styles.section}>
            <h3>🎭 Cast</h3>
            <div className={styles.castList}>
              {show.cast.length > 0 ? (
                show.cast.map((actor) => (
                  <span key={actor} className={styles.castMember}>
                    {actor}
                  </span>
                ))
              ) : (
                <span className={styles.placeholder}>
                  No cast info available.
                </span>
              )}
            </div>
          </div>

          <div className={styles.section}>
            <h3>🛡️ Safety Assessment</h3>
            <div className={styles.reasoningBox}>{show.reasoning}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
