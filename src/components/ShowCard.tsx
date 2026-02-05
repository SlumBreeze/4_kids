import React from "react";
import { Show } from "../types";
import { formatAgeRange } from "../utils/format";
import styles from "./ShowCard.module.css";
import { Badge } from "./Badge";

interface ShowCardProps {
  show: Show;
  onClick: () => void;
}

export const ShowCard: React.FC<ShowCardProps> = ({ show, onClick }) => {
  let variant: "safe" | "caution" | "unsafe" = "caution";
  let badgeText = "⚠️ Caution";
  let cardStyle = styles.cardCaution;

  if (show.rating === "Safe") {
    variant = "safe";
    badgeText = "✅ Safe";
    cardStyle = styles.cardSafe;
  } else if (show.rating === "Unsafe") {
    variant = "unsafe";
    badgeText = "🚫 Unsafe";
    cardStyle = styles.cardUnsafe;
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
        <div className={styles.ratingBadge}>
          <Badge variant={variant}>{badgeText}</Badge>
        </div>
      </div>
      <div className={styles.content}>
        <h3 className={styles.title}>{show.title}</h3>
        <div className={styles.meta}>
          <Badge variant="primary">{ageString}</Badge>
          {show.tags.length > 0 && (
            <Badge variant="secondary">{show.tags[0]}</Badge>
          )}
        </div>
      </div>
    </div>
  );
};
