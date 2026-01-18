export const formatAge = (age: number): string => {
  if (age < 1) {
    // Treat decimals as months in tenths (e.g. 0.5 => 5 months)
    const months = Math.round(age * 10);
    return `${months} mo`;
  }
  return `${age} yo`;
};

export const formatAgeRange = (min: number, max: number): string => {
  if (max === 99) return `${formatAge(min)}+`;
  return `${formatAge(min)} - ${formatAge(max)}`;
};
