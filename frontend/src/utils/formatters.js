export function formatMoney(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2
  }).format(Number(value));
}

export function sentimentColor(score) {
  if (score > 0.12) return "rgba(16, 185, 129, 0.35)";
  if (score < -0.12) return "rgba(251, 113, 133, 0.35)";
  return "rgba(245, 158, 11, 0.25)";
}

