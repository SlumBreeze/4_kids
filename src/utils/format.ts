export const formatAge = (age: number): string => {
  if (age < 1) {
    // Treat as months
    // e.g. 0.5 * 12 = 6
    const months = Math.round(age * 12);
    return `${months} mo`;
  }
  return `${age} yo`;
};

export const formatAgeRange = (min: number, max: number): string => {
  if (max === 99) return `${formatAge(min)}+`;
  return `${formatAge(min)} - ${formatAge(max)}`;
};
