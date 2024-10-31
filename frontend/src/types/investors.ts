export interface Investor {
  name: string;
  investor_type: string;
  country: string;
  total_commitments: number;
}

export interface InvestorsResponse {
  investors: Investor[];
}

export interface Commitment {
  amount: number;
  id: number;
  investor_id: number;
  asset_class: string;
  currency: string;
}
export interface InvestorDetail {
  name: string;
  investor_type: string;
  country: string;
  commitments: Commitment[];
}
