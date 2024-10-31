import { useQuery } from "@tanstack/react-query";
import { fetchInvestors } from "@/services/investorService";
import { useNavigate } from "react-router-dom";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useState } from "react";
import { Investor } from "@/types/investors";
import { ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

const Index = () => {
  const { toast } = useToast();
  const [sortField, setSortField] = useState<keyof Investor>("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ["investors"],
    queryFn: fetchInvestors,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg">Loading investors...</p>
      </div>
    );
  }

  if (error) {
    toast({
      variant: "destructive",
      title: "Error",
      description: "Failed to fetch investors data",
    });
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-red-500">Error loading investors</p>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    if (amount === 0) return "-";
    const billions = amount / 1000000000;
    return `${billions.toFixed(1)}B`;
  };

  const sortedInvestors = [...(data?.investors || [])].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];

    if (sortDirection === "asc") {
      return aValue > bValue ? 1 : -1;
    }
    return aValue < bValue ? 1 : -1;
  });

  const handleSort = (field: keyof Investor) => {
    if (field === sortField) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-4xl font-bold mb-8">Investors</h1>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => handleSort("name")}
                  className="flex items-center gap-1"
                >
                  Name
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => handleSort("investor_type")}
                  className="flex items-center gap-1"
                >
                  Type
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => handleSort("country")}
                  className="flex items-center gap-1"
                >
                  Country
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  onClick={() => handleSort("total_commitments")}
                  className="flex items-center gap-1 ml-auto"
                >
                  Total Commitment
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedInvestors.map((investor, index) => (
              <TableRow
                key={index}
                className="cursor-pointer hover:bg-muted"
                onClick={() => navigate(`/investor/${index + 1}`)}
              >
                <TableCell className="font-medium">{investor.name}</TableCell>
                <TableCell className="capitalize">
                  {investor.investor_type}
                </TableCell>
                <TableCell>{investor.country}</TableCell>
                <TableCell className="text-right">
                  <span className="font-medium text-primary hover:underline cursor-pointer transition-colors">
                    {formatCurrency(investor.total_commitments)}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default Index;
