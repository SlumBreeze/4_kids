import React from "react";
import styles from "./Badge.module.css";

export type BadgeVariant = "safe" | "caution" | "unsafe" | "primary" | "secondary";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "primary",
  className = "",
}) => {
  const variantClass = styles[variant] || styles.primary;
  
  return (
    <span className={`${styles.badge} ${variantClass} ${className}`}>
      {children}
    </span>
  );
};
