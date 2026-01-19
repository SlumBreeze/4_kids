import React from "react";
import { StimulationLevel } from "../types";
import styles from "./StimulationFilter.module.css";

export type StimulationFilterValue = "All" | StimulationLevel;

const STIMULATION_OPTIONS: StimulationFilterValue[] = [
  "All",
  "Low",
  "Medium",
  "High",
];

interface StimulationFilterProps {
  selected: StimulationFilterValue;
  onSelect: (value: StimulationFilterValue) => void;
}

export const StimulationFilter: React.FC<StimulationFilterProps> = ({
  selected,
  onSelect,
}) => {
  return (
    <div className={styles.container}>
      {STIMULATION_OPTIONS.map((option) => (
        <button
          key={option}
          className={`${styles.pill} ${selected === option ? styles.active : ""}`}
          onClick={() => onSelect(option)}
        >
          {option} Stimulation
        </button>
      ))}
    </div>
  );
};
