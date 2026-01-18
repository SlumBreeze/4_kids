import React from "react";
import styles from "./AgeFilter.module.css";

export interface AgeBucket {
  label: string;
  min: number;
  max: number;
}

export const AGE_BUCKETS: AgeBucket[] = [
  { label: "All Ages", min: 0, max: 99 },
  { label: "3–5 mo", min: 0.3, max: 0.5 },
  { label: "6–8 mo", min: 0.6, max: 0.8 },
  { label: "9–12 mo", min: 0.9, max: 1.0 },
  { label: "1–2 yr", min: 1, max: 2 },
  { label: "2–3 yr", min: 2, max: 3 },
  { label: "3–4 yr", min: 3, max: 4 },
  { label: "5–6 yr", min: 5, max: 6.9 },
  { label: "7–9 yr", min: 7, max: 9.9 },
  { label: "10–12 yr", min: 10, max: 12.9 },
];

interface AgeFilterProps {
  selectedLabel: string;
  onSelect: (bucket: AgeBucket) => void;
}

export const AgeFilter: React.FC<AgeFilterProps> = ({
  selectedLabel,
  onSelect,
}) => {
  return (
    <div className={styles.container}>
      {AGE_BUCKETS.map((bucket) => (
        <button
          key={bucket.label}
          className={`${styles.pill} ${selectedLabel === bucket.label ? styles.active : ""}`}
          onClick={() => onSelect(bucket)}
        >
          {bucket.label}
        </button>
      ))}
    </div>
  );
};
