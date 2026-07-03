export function scoreColor(score: number): [number, number, number, number] {
  if (score >= 80) return [24, 121, 104, 210];
  if (score >= 65) return [72, 157, 120, 205];
  if (score >= 50) return [224, 177, 77, 205];
  if (score >= 35) return [214, 112, 74, 205];
  return [160, 62, 71, 205];
}

export function cssScoreColor(score: number): string {
  const [r, g, b] = scoreColor(score);
  return `rgb(${r}, ${g}, ${b})`;
}
