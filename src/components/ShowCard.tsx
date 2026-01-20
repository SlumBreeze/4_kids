import React from "react";
import { Show } from "../types";
import { formatAgeRange } from "../utils/format";
import styles from "./ShowCard.module.css";

interface ShowCardProps {
  show: Show;
  onClick: () => void;
}

export const ShowCard: React.FC<ShowCardProps> = ({ show, onClick }) => {
  let cardStyle = styles.cardCaution;
  let badgeText = "⚠️ Caution";

  if (show.rating === "Safe") {
    cardStyle = styles.cardSafe;
    badgeText = "✅ Safe";
  } else if (show.rating === "Unsafe") {
    cardStyle = styles.cardUnsafe;
    badgeText = "🚫 Unsafe";
  }

  const ageString = formatAgeRange(show.minAge, show.maxAge);

  return (
    <div className={`${styles.card} ${cardStyle}`} onClick={onClick}>
      <div className={styles.imageContainer}>
        <img
          src={show.coverImage}
          alt={show.title}
          className={styles.image}
          loading="lazy"
        />
        <div className={styles.ratingBadge}>{badgeText}</div>
      </div>
      <div className={styles.content}>
        <h3 className={styles.title}>{show.title}</h3>
        <div className={styles.meta}>
          <span className={styles.ageTag}>{ageString}</span>
          {show.tags.length > 0 && (
            <span className={styles.genreTag}>{show.tags[0]}</span>
          )}
        </div>
      </div>
    </div>
  );
};
