export interface HDProduct {
  id: string;
  connection_type: string;
  media_type: string;
  name: string;
  original_price: number;
  current_price: number;
  url: string;
  source: string;
  vendor_sku: string;
  manufacturer: string;
  gb_per_eur: number;
  discount: number;
  size_tb: number;
  eur_per_tb: number | null;
}

export interface HDProductEx extends HDProduct {
  discount_pct: number;
}
