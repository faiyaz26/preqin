import { useQuery } from "@tanstack/react-query";
import { fetchInvestorDetails } from "@/services/investorService";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/components/ui/use-toast";
import { ChevronLeft } from "lucide-react";
import { useState } from "react";

const InvestorDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [selectedAssetClass, setSelectedAssetClass] = useState<string | null>(
    null
  );

  const { data, isLoading, error } = useQuery({
    queryKey: ["investor", id],
    queryFn: () => fetchInvestorDetails(Number(id)),
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg">Loading investor details...</p>
      </div>
    );
  }

  if (error) {
    toast({
      variant: "destructive",
      title: "Error",
      description: "Failed to fetch investor details",
    });
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-red-500">Error loading investor details</p>
      </div>
    );
  }

  const formatAmount = (amount: number) => {
    const millions = amount / 1000000;
    return `${millions.toFixed(1)}M`;
  };

  const calculateTotalsByAssetClass = () => {
    const totals = new Map<string, number>();
    let total = 0;

    data?.commitments.forEach((commitment) => {
      const current = totals.get(commitment.asset_class) || 0;
      totals.set(commitment.asset_class, current + commitment.amount);
      total += commitment.amount;
    });

    totals.set("All", total);
    return totals;
  };

  const totals = calculateTotalsByAssetClass();

  const filteredCommitments =
    selectedAssetClass && selectedAssetClass !== "All"
      ? data?.commitments.filter(
          (commitment) => commitment.asset_class === selectedAssetClass
        )
      : data?.commitments;

  const handleAssetClassClick = (assetClass: string) => {
    setSelectedAssetClass(
      assetClass === selectedAssetClass ? null : assetClass
    );
  };

  return (
    <div className="container mx-auto py-10">
      <Button variant="ghost" onClick={() => navigate("/")} className="mb-6">
        <ChevronLeft className="h-4 w-4 mr-2" />
        Back to Investors
      </Button>

      <h1 className="text-4xl font-bold mb-8">Commitments</h1>

      <div className="flex flex-wrap gap-4 mb-8">
        {Array.from(totals.entries()).map(([assetClass, amount]) => (
          <div
            key={assetClass}
            className={`border rounded-md p-4 min-w-[200px] cursor-pointer transition-colors ${
              selectedAssetClass === assetClass
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
            onClick={() => handleAssetClassClick(assetClass)}
          >
            <div className="text-lg font-semibold">{assetClass}</div>
            <div className="text-xl">£{formatAmount(amount)}</div>
          </div>
        ))}
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Id</TableHead>
              <TableHead>Asset Class</TableHead>
              <TableHead>Currency</TableHead>
              <TableHead className="text-right">Amount</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredCommitments?.map((commitment) => (
              <TableRow key={commitment.id}>
                <TableCell>{commitment.id}</TableCell>
                <TableCell>{commitment.asset_class}</TableCell>
                <TableCell>{commitment.currency}</TableCell>
                <TableCell className="text-right">
                  {formatAmount(commitment.amount)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default InvestorDetail;
