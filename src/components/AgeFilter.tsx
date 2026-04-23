import React from "react";
import styles from "./AgeFilter.module.css";

export interface AgeBucket {
  label: string;
  min: number;
  max: number;
}

export const AGE_BUCKETS: AgeBucket[] = [
  { label: "Toddlers (3mo–2yr)", min: 0.3, max: 2 },
  { label: "Preschoolers (3–5yr)", min: 3, max: 5 },
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