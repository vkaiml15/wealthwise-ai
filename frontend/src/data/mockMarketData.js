// Market trends and industry data
export const mockMarketData = {
  // Trending industries
  trending: [
    {
      id: 1,
      industry: "Artificial Intelligence",
      sector: "Technology",
      growth: 34.2,
      momentum: "Very High",
      riskLevel: "Moderate-High",
      marketCap: "$2.8T",
      topStocks: [
        { symbol: "NVDA", name: "NVIDIA", performance: 45.2 },
        { symbol: "MSFT", name: "Microsoft", performance: 28.3 },
        { symbol: "GOOGL", name: "Alphabet", performance: 32.1 }
      ],
      description: "AI and machine learning revolutionizing enterprise software and hardware",
      catalysts: ["Enterprise AI adoption", "ChatGPT integration", "Cloud AI services"],
      outlook: "Strong growth expected through 2026"
    },
    {
      id: 2,
      industry: "Renewable Energy",
      sector: "Energy",
      growth: 28.5,
      momentum: "High",
      riskLevel: "Moderate",
      marketCap: "$1.5T",
      topStocks: [
        { symbol: "ENPH", name: "Enphase Energy", performance: 38.1 },
        { symbol: "SEDG", name: "SolarEdge", performance: 31.4 },
        { symbol: "NEE", name: "NextEra Energy", performance: 22.7 }
      ],
      description: "Solar, wind, and clean energy solutions gaining market share",
      catalysts: ["Government incentives", "Falling costs", "Climate commitments"],
      outlook: "Long-term structural growth"
    },
    {
      id: 3,
      industry: "Healthcare Technology",
      sector: "Healthcare",
      growth: 22.1,
      momentum: "High",
      riskLevel: "Moderate",
      marketCap: "$980B",
      topStocks: [
        { symbol: "TDOC", name: "Teladoc Health", performance: 29.3 },
        { symbol: "VEEV", name: "Veeva Systems", performance: 26.8 },
        { symbol: "DXCM", name: "DexCom", performance: 31.2 }
      ],
      description: "Digital health, telemedicine, and healthcare IT platforms",
      catalysts: ["Aging population", "Digital transformation", "Telehealth adoption"],
      outlook: "Defensive growth opportunity"
    },
    {
      id: 4,
      industry: "Cloud Computing",
      sector: "Technology",
      growth: 26.8,
      momentum: "Very High",
      riskLevel: "Moderate",
      marketCap: "$1.9T",
      topStocks: [
        { symbol: "CRM", name: "Salesforce", performance: 24.5 },
        { symbol: "NOW", name: "ServiceNow", performance: 35.2 },
        { symbol: "SNOW", name: "Snowflake", performance: 28.9 }
      ],
      description: "Enterprise cloud infrastructure and SaaS platforms",
      catalysts: ["Cloud migration", "Hybrid work", "Digital transformation"],
      outlook: "Sustained enterprise spending"
    },
    {
      id: 5,
      industry: "Electric Vehicles",
      sector: "Automotive",
      growth: 19.3,
      momentum: "Moderate",
      riskLevel: "High",
      marketCap: "$1.2T",
      topStocks: [
        { symbol: "TSLA", name: "Tesla", performance: 22.8 },
        { symbol: "RIVN", name: "Rivian", performance: 15.4 },
        { symbol: "LCID", name: "Lucid", performance: 12.1 }
      ],
      description: "Electric vehicle manufacturers and battery technology",
      catalysts: ["Government mandates", "Battery improvements", "Charging infrastructure"],
      outlook: "Volatile but long-term potential"
    },
    {
      id: 6,
      industry: "Cybersecurity",
      sector: "Technology",
      growth: 24.7,
      momentum: "High",
      riskLevel: "Moderate",
      marketCap: "$780B",
      topStocks: [
        { symbol: "CRWD", name: "CrowdStrike", performance: 42.3 },
        { symbol: "ZS", name: "Zscaler", performance: 31.8 },
        { symbol: "PANW", name: "Palo Alto Networks", performance: 28.5 }
      ],
      description: "Enterprise and cloud security solutions",
      catalysts: ["Rising cyber threats", "Cloud security needs", "Regulatory compliance"],
      outlook: "Essential spending category"
    }
  ],

  // Market sentiment indicators
  marketSentiment: {
    overall: "Bullish",
    fearGreedIndex: 68,
    sp500Change: 2.3,
    nasdaqChange: 3.1,
    dowChange: 1.8,
    vixLevel: 14.2,
    putCallRatio: 0.85,
    sentiment: "Risk-on mood with strong tech performance"
  },

  // Sector performance
  sectorPerformance: [
    { sector: "Technology", ytdReturn: 32.4, monthReturn: 4.2, rating: "Outperform" },
    { sector: "Healthcare", ytdReturn: 18.7, monthReturn: 2.1, rating: "Market Perform" },
    { sector: "Financial", ytdReturn: 15.3, monthReturn: 1.8, rating: "Market Perform" },
    { sector: "Consumer Discretionary", ytdReturn: 22.1, monthReturn: 3.5, rating: "Outperform" },
    { sector: "Industrials", ytdReturn: 12.8, monthReturn: 1.2, rating: "Market Perform" },
    { sector: "Energy", ytdReturn: -2.4, monthReturn: -0.8, rating: "Underperform" },
    { sector: "Materials", ytdReturn: 8.5, monthReturn: 0.5, rating: "Underperform" },
    { sector: "Real Estate", ytdReturn: -8.3, monthReturn: -1.5, rating: "Underperform" },
    { sector: "Utilities", ytdReturn: 4.2, monthReturn: 0.3, rating: "Underperform" },
    { sector: "Communication", ytdReturn: 25.6, monthReturn: 3.8, rating: "Outperform" }
  ],

  // Economic indicators
  economicIndicators: {
    gdpGrowth: 2.8,
    inflation: 3.2,
    unemployment: 3.8,
    fedFundsRate: 5.25,
    tenyearYield: 4.35,
    dollarIndex: 103.5
  },

  // Market news (recent headlines)
  marketNews: [
    {
      id: 1,
      title: "Fed Signals Potential Rate Cuts in 2026",
      summary: "Federal Reserve hints at possible rate reductions if inflation continues to moderate",
      impact: "Positive",
      date: "2025-10-12"
    },
    {
      id: 2,
      title: "Tech Giants Report Strong Q3 Earnings",
      summary: "FAANG companies exceed expectations, driven by AI revenue growth",
      impact: "Positive",
      date: "2025-10-11"
    },
    {
      id: 3,
      title: "Healthcare Sector Shows Resilience",
      summary: "Defensive stocks gain favor as investors seek stability",
      impact: "Neutral",
      date: "2025-10-10"
    }
  ],

  // Investment themes
  investmentThemes: [
    {
      theme: "AI Revolution",
      description: "Artificial intelligence transforming industries",
      timeHorizon: "Long-term",
      riskLevel: "Moderate-High",
      potentialReturn: "25-40%"
    },
    {
      theme: "Energy Transition",
      description: "Shift from fossil fuels to renewable energy",
      timeHorizon: "Long-term",
      riskLevel: "Moderate",
      potentialReturn: "15-25%"
    },
    {
      theme: "Digital Health",
      description: "Technology meeting healthcare needs",
      timeHorizon: "Medium-term",
      riskLevel: "Moderate",
      potentialReturn: "18-28%"
    }
  ]
};

// Helper function to get trending industry by name
export const getTrendingIndustryByName = (industryName) => {
  return mockMarketData.trending.find(
    industry => industry.industry.toLowerCase() === industryName.toLowerCase()
  );
};

// Helper function to get sector performance
export const getSectorPerformance = (sectorName) => {
  return mockMarketData.sectorPerformance.find(
    sector => sector.sector.toLowerCase() === sectorName.toLowerCase()
  );
};