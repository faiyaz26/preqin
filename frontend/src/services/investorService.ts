import { InvestorsResponse, InvestorDetail } from "@/types/investors";

export const fetchInvestors = async (): Promise<InvestorsResponse> => {
  // Replace this URL with your actual API endpoint
  const response = await fetch("http://127.0.0.1:8000/investors");
  if (!response.ok) {
    throw new Error("Failed to fetch investors");
  }
  return response.json();
};

export const fetchInvestorDetails = async (
  id: number
): Promise<InvestorDetail> => {
  const response = await fetch(`http://127.0.0.1:8000/investor/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch investor details");
  }
  return response.json();
};
