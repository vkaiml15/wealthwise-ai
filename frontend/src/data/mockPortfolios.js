// Portfolio data for each user
export const mockPortfolios = {
  john_investor: {
    totalValue: 285000,
    cashReserve: 15000,
    invested: 270000,
    returns: {
      value: 35000,
      percentage: 14.9
    },
    riskScore: 6.2,
    
    // For donut chart
    allocation: [
      { name: "Tech Stocks", value: 95000, percentage: 35.2, color: "#4F46E5" },
      { name: "Healthcare", value: 54000, percentage: 20.0, color: "#06B6D4" },
      { name: "Finance", value: 40500, percentage: 15.0, color: "#8B5CF6" },
      { name: "Real Estate", value: 43200, percentage: 16.0, color: "#10B981" },
      { name: "Bonds", value: 37300, percentage: 13.8, color: "#F59E0B" }
    ],
    
    // For line chart - performance over time
    performance: [
      { month: "Apr", value: 245000, change: 0 },
      { month: "May", value: 252000, change: 2.9 },
      { month: "Jun", value: 258000, change: 2.4 },
      { month: "Jul", value: 262000, change: 1.6 },
      { month: "Aug", value: 268000, change: 2.3 },
      { month: "Sep", value: 273000, change: 1.9 },
      { month: "Oct", value: 285000, change: 4.4 }
    ],
    
    holdings: [
      { 
        symbol: "AAPL", 
        name: "Apple Inc.", 
        shares: 150, 
        avgPrice: 175.50, 
        currentPrice: 185.20, 
        value: 27780,
        sector: "Technology"
      },
      { 
        symbol: "MSFT", 
        name: "Microsoft Corp.", 
        shares: 100, 
        avgPrice: 340.00, 
        currentPrice: 365.80, 
        value: 36580,
        sector: "Technology"
      },
      { 
        symbol: "GOOGL", 
        name: "Alphabet Inc.", 
        shares: 80, 
        avgPrice: 125.00, 
        currentPrice: 138.50, 
        value: 11080,
        sector: "Technology"
      },
      { 
        symbol: "JNJ", 
        name: "Johnson & Johnson", 
        shares: 200, 
        avgPrice: 160.00, 
        currentPrice: 165.30, 
        value: 33060,
        sector: "Healthcare"
      },
      { 
        symbol: "JPM", 
        name: "JPMorgan Chase", 
        shares: 150, 
        avgPrice: 145.00, 
        currentPrice: 152.70, 
        value: 22905,
        sector: "Finance"
      },
      { 
        symbol: "UNH", 
        name: "UnitedHealth Group", 
        shares: 40, 
        avgPrice: 520.00, 
        currentPrice: 545.20, 
        value: 21808,
        sector: "Healthcare"
      }
    ],
    
    diversityScore: 7.8,
    lastUpdated: "2025-10-13T10:30:00Z"
  },
  
  sarah_trader: {
    totalValue: 425000,
    cashReserve: 25000,
    invested: 400000,
    returns: {
      value: 68000,
      percentage: 19.1
    },
    riskScore: 8.4,
    
    allocation: [
      { name: "Tech Stocks", value: 180000, percentage: 45.0, color: "#4F46E5" },
      { name: "Crypto", value: 60000, percentage: 15.0, color: "#EC4899" },
      { name: "Growth Stocks", value: 80000, percentage: 20.0, color: "#06B6D4" },
      { name: "ETFs", value: 50000, percentage: 12.5, color: "#10B981" },
      { name: "Options", value: 30000, percentage: 7.5, color: "#F59E0B" }
    ],
    
    performance: [
      { month: "Apr", value: 365000, change: 0 },
      { month: "May", value: 378000, change: 3.6 },
      { month: "Jun", value: 385000, change: 1.9 },
      { month: "Jul", value: 395000, change: 2.6 },
      { month: "Aug", value: 405000, change: 2.5 },
      { month: "Sep", value: 415000, change: 2.5 },
      { month: "Oct", value: 425000, change: 2.4 }
    ],
    
    holdings: [
      { symbol: "NVDA", name: "NVIDIA Corp.", shares: 400, avgPrice: 380.00, currentPrice: 450.00, value: 180000, sector: "Technology" },
      { symbol: "TSLA", name: "Tesla Inc.", shares: 300, avgPrice: 240.00, currentPrice: 266.67, value: 80000, sector: "Automotive" },
      { symbol: "COIN", name: "Coinbase", shares: 250, avgPrice: 220.00, currentPrice: 240.00, value: 60000, sector: "Crypto" },
      { symbol: "SPY", name: "SPDR S&P 500 ETF", shares: 125, avgPrice: 380.00, currentPrice: 400.00, value: 50000, sector: "ETF" }
    ],
    
    diversityScore: 6.5,
    lastUpdated: "2025-10-13T10:30:00Z"
  },
  
  mike_growth: {
    totalValue: 180000,
    cashReserve: 8000,
    invested: 172000,
    returns: {
      value: 22000,
      percentage: 13.9
    },
    riskScore: 6.8,
    
    allocation: [
      { name: "Tech Stocks", value: 68800, percentage: 40.0, color: "#4F46E5" },
      { name: "Growth ETFs", value: 51600, percentage: 30.0, color: "#06B6D4" },
      { name: "Healthcare", value: 34400, percentage: 20.0, color: "#8B5CF6" },
      { name: "Energy", value: 17200, percentage: 10.0, color: "#10B981" }
    ],
    
    performance: [
      { month: "Apr", value: 158000, change: 0 },
      { month: "May", value: 162000, change: 2.5 },
      { month: "Jun", value: 167000, change: 3.1 },
      { month: "Jul", value: 171000, change: 2.4 },
      { month: "Aug", value: 174000, change: 1.8 },
      { month: "Sep", value: 177000, change: 1.7 },
      { month: "Oct", value: 180000, change: 1.7 }
    ],
    
    holdings: [
      { symbol: "AMZN", name: "Amazon.com Inc.", shares: 200, avgPrice: 140.00, currentPrice: 172.00, value: 34400, sector: "Technology" },
      { symbol: "VGT", name: "Vanguard Tech ETF", shares: 100, avgPrice: 480.00, currentPrice: 516.00, value: 51600, sector: "ETF" },
      { symbol: "PFE", name: "Pfizer Inc.", shares: 1200, avgPrice: 27.00, currentPrice: 28.67, value: 34400, sector: "Healthcare" },
      { symbol: "XLE", name: "Energy Select ETF", shares: 200, avgPrice: 82.00, currentPrice: 86.00, value: 17200, sector: "Energy" }
    ],
    
    diversityScore: 7.2,
    lastUpdated: "2025-10-13T10:30:00Z"
  },
  
  emma_conservative: {
    totalValue: 320000,
    cashReserve: 45000,
    invested: 275000,
    returns: {
      value: 18500,
      percentage: 7.2
    },
    riskScore: 3.5,
    
    allocation: [
      { name: "Bonds", value: 110000, percentage: 40.0, color: "#F59E0B" },
      { name: "Dividend Stocks", value: 82500, percentage: 30.0, color: "#10B981" },
      { name: "Real Estate", value: 55000, percentage: 20.0, color: "#8B5CF6" },
      { name: "Blue Chips", value: 27500, percentage: 10.0, color: "#4F46E5" }
    ],
    
    performance: [
      { month: "Apr", value: 308000, change: 0 },
      { month: "May", value: 310000, change: 0.6 },
      { month: "Jun", value: 312000, change: 0.6 },
      { month: "Jul", value: 314000, change: 0.6 },
      { month: "Aug", value: 316000, change: 0.6 },
      { month: "Sep", value: 318000, change: 0.6 },
      { month: "Oct", value: 320000, change: 0.6 }
    ],
    
    holdings: [
      { symbol: "BND", name: "Vanguard Bond ETF", shares: 1000, avgPrice: 105.00, currentPrice: 110.00, value: 110000, sector: "Bonds" },
      { symbol: "VZ", name: "Verizon", shares: 2000, avgPrice: 38.00, currentPrice: 41.25, value: 82500, sector: "Telecom" },
      { symbol: "O", name: "Realty Income", shares: 1000, avgPrice: 52.00, currentPrice: 55.00, value: 55000, sector: "Real Estate" },
      { symbol: "KO", name: "Coca-Cola", shares: 500, avgPrice: 52.00, currentPrice: 55.00, value: 27500, sector: "Consumer" }
    ],
    
    diversityScore: 8.5,
    lastUpdated: "2025-10-13T10:30:00Z"
  },
  
  david_aggressive: {
    totalValue: 510000,
    cashReserve: 10000,
    invested: 500000,
    returns: {
      value: 95000,
      percentage: 22.9
    },
    riskScore: 9.1,
    
    allocation: [
      { name: "Tech Growth", value: 200000, percentage: 40.0, color: "#4F46E5" },
      { name: "Emerging Markets", value: 125000, percentage: 25.0, color: "#EC4899" },
      { name: "Small Cap", value: 100000, percentage: 20.0, color: "#06B6D4" },
      { name: "Crypto", value: 50000, percentage: 10.0, color: "#8B5CF6" },
      { name: "Options", value: 25000, percentage: 5.0, color: "#F59E0B" }
    ],
    
    performance: [
      { month: "Apr", value: 435000, change: 0 },
      { month: "May", value: 455000, change: 4.6 },
      { month: "Jun", value: 468000, change: 2.9 },
      { month: "Jul", value: 478000, change: 2.1 },
      { month: "Aug", value: 490000, change: 2.5 },
      { month: "Sep", value: 502000, change: 2.4 },
      { month: "Oct", value: 510000, change: 1.6 }
    ],
    
    holdings: [
      { symbol: "NVDA", name: "NVIDIA Corp.", shares: 200, avgPrice: 380.00, currentPrice: 450.00, value: 90000, sector: "Technology" },
      { symbol: "META", name: "Meta Platforms", shares: 200, avgPrice: 350.00, currentPrice: 550.00, value: 110000, sector: "Technology" },
      { symbol: "VWO", name: "Emerging Markets ETF", shares: 1500, avgPrice: 75.00, currentPrice: 83.33, value: 125000, sector: "ETF" },
      { symbol: "IWM", name: "Russell 2000 ETF", shares: 500, avgPrice: 180.00, currentPrice: 200.00, value: 100000, sector: "ETF" },
      { symbol: "BTC", name: "Bitcoin ETF", shares: 1000, avgPrice: 45.00, currentPrice: 50.00, value: 50000, sector: "Crypto" }
    ],
    
    diversityScore: 6.0,
    lastUpdated: "2025-10-13T10:30:00Z"
  }
};

// Helper function to get portfolio by userId
export const getPortfolioByUserId = (userId) => {
  return mockPortfolios[userId] || null;
};
