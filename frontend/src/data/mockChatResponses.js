// Intent detection function
export const detectIntent = (message, conversationContext) => {
  const lowerMessage = message.toLowerCase();
  
  // Check if referring to previous context
  if (conversationContext.lastIntent === 'portfolioAnalysis') {
    if (lowerMessage.includes('what should') || 
        lowerMessage.includes('recommend') || 
        lowerMessage.includes('what can') ||
        lowerMessage.includes('how can')) {
      return 'contextual_recommendation';
    }
  }
  
  // Portfolio Analysis
  if ((lowerMessage.includes('portfolio') || lowerMessage.includes('my investment')) && 
      (lowerMessage.includes('analyz') || lowerMessage.includes('review') || 
       lowerMessage.includes('check') || lowerMessage.includes('look'))) {
    return 'portfolioAnalysis';
  }
  
  // Recommendations
  if (lowerMessage.includes('recommend') || 
      lowerMessage.includes('suggest') || 
      lowerMessage.includes('stock pick') ||
      (lowerMessage.includes('what') && lowerMessage.includes('buy'))) {
    return 'recommendations';
  }
  
  // Market Trends
  if ((lowerMessage.includes('market') || lowerMessage.includes('industry')) && 
      (lowerMessage.includes('trend') || lowerMessage.includes('doing') || 
       lowerMessage.includes('update') || lowerMessage.includes('news'))) {
    return 'marketTrends';
  }
  
  // Industry/Sector Analysis
  if (lowerMessage.includes('industry') || 
      lowerMessage.includes('sector') || 
      lowerMessage.includes('which') && (lowerMessage.includes('invest') || lowerMessage.includes('booming'))) {
    return 'industryRecommendation';
  }
  
  // Rebalancing
  if (lowerMessage.includes('rebalanc') || 
      lowerMessage.includes('adjust') || 
      lowerMessage.includes('reallocat')) {
    return 'rebalancing';
  }
  
  // Risk Analysis
  if (lowerMessage.includes('risk') && 
      (lowerMessage.includes('analys') || lowerMessage.includes('profile') || 
       lowerMessage.includes('score') || lowerMessage.includes('assess'))) {
    return 'riskAnalysis';
  }
  
  // Tax Impact
  if (lowerMessage.includes('tax') || lowerMessage.includes('capital gain')) {
    return 'taxAnalysis';
  }
  
  // Diversification
  if (lowerMessage.includes('divers') || lowerMessage.includes('spread')) {
    return 'diversification';
  }
  
  return 'general';
};

// Pre-defined chat responses
export const mockChatResponses = {
  portfolioAnalysis: {
    message: `Based on your portfolio analysis, here are the key insights:

✅ **Strengths:**
- Well-diversified across 5 major sectors
- Strong tech allocation (35%) aligned with current growth trends
- Healthy returns of 14.9% over the past 6 months
- Good balance between growth and stability

⚠️ **Areas of Concern:**
- Cash reserve is only 5.3% (recommended: 10-15%)
- Tech sector is slightly overweight by 5 percentage points
- Healthcare exposure could be increased for better diversification
- Consider rebalancing to reduce concentration risk

📊 **Risk Score:** 6.2/10 (Moderate) - Matches your risk profile

**Reasoning:** Your portfolio demonstrates solid diversification principles, but the low cash reserve limits your ability to capitalize on market opportunities or handle emergencies. The tech overweight, while profitable, increases volatility exposure.`,
    followUp: "Since increasing your cash reserve is important, would you like personalized recommendations for defensive stocks that can provide liquidity?"
  },
  
  recommendations: {
    message: `Here are personalized stock recommendations based on your moderate risk profile:

🎯 **Top Picks for You:**

1. **NVIDIA (NVDA)** - Technology/AI
   • Target Price: $485 | Current: $445
   • Growth Potential: 22% upside
   • Why: Leading AI chip manufacturer with strong market position
   • Risk Level: Moderate-High

2. **UnitedHealth Group (UNH)** - Healthcare
   • Target Price: $580 | Current: $535
   • Growth Potential: 15% upside
   • Why: Defensive sector with steady growth and dividends
   • Risk Level: Low-Moderate

3. **Visa Inc. (V)** - Financial Services
   • Target Price: $285 | Current: $265
   • Growth Potential: 18% upside
   • Why: Global payment leader with consistent performance
   • Risk Level: Low

**Allocation Suggestion:**
- 40% NVDA - Growth driver
- 35% UNH - Stability anchor
- 25% V - Balanced growth

**Reasoning:** These recommendations balance growth potential with your moderate risk tolerance while improving sector diversification beyond your current tech-heavy holdings.`,
    followUp: "Would you like me to analyze how adding these stocks would impact your overall portfolio allocation and risk score?"
  },
  
  marketTrends: {
    message: `🌍 **Current Market Trends (October 2025):**

📈 **Booming Industries:**

1. **Artificial Intelligence & Cloud Computing**
   • YTD Performance: +34.2%
   • Key Drivers: Enterprise AI adoption, ChatGPT integration, cloud migration
   • Leading Stocks: NVDA (+45%), MSFT (+28%), GOOGL (+32%)
   • Outlook: Strong momentum expected through Q4

2. **Renewable Energy**
   • YTD Performance: +28.5%
   • Key Drivers: Government incentives, falling technology costs
   • Leading Stocks: ENPH (+38%), SEDG (+31%), NEE (+22%)
   • Outlook: Long-term growth trajectory

3. **Healthcare Technology**
   • YTD Performance: +22.1%
   • Key Drivers: Aging population, digital health transformation
   • Leading Stocks: TDOC (+29%), VEEV (+26%), DXCM (+31%)
   • Outlook: Defensive growth opportunity

📉 **Underperforming Sectors:**
- Commercial Real Estate: -8.3%
- Traditional Retail: -5.7%

**Market Sentiment:** Bullish (Fear & Greed Index: 68/100)

**Reasoning:** AI continues to dominate as enterprises accelerate adoption. Renewable energy benefits from policy support and cost improvements. Healthcare tech offers defensive growth in uncertain times.`,
    followUp: "Would you like specific stock recommendations in the AI sector that match your risk profile?"
  },
  
  industryRecommendation: {
    message: `🎯 **Best Industry for Your Profile: Healthcare Technology**

**Why Healthcare Tech?**

💡 **Perfect Fit Analysis:**
- Risk Level: Moderate (6.5/10) - Matches your 6.2 risk score
- Expected Returns: 15-20% annually
- Volatility: Lower than pure tech, higher than traditional healthcare
- Defensive Characteristics: Healthcare demand is recession-resistant

**Market Drivers:**
✓ Aging global population (65+ demographic growing 3.5% annually)
✓ Digital health transformation accelerating post-pandemic
✓ Telehealth adoption now at 40% (vs 10% in 2019)
✓ Government healthcare spending increasing globally
✓ AI integration improving diagnostics and efficiency

**Growth Catalysts:**
- Medicare expansion supporting digital health
- Hospital system modernization ($200B market)
- Chronic disease management platforms
- Wearable health tech adoption

**Expected Performance:**
- 3-Year Outlook: 12-18% annual returns
- Lower correlation with tech sector (reduces your risk)
- Dividend potential: 1-2% yield in some stocks

**Reasoning:** Healthcare technology provides growth potential similar to pure tech but with the defensive characteristics of healthcare. This aligns perfectly with your moderate risk profile while diversifying away from your current tech concentration.`,
    followUp: "Since Healthcare Technology aligns well with your profile, would you like personalized stock picks in this sector?"
  },
  
  rebalancing: {
    message: `⚖️ **Portfolio Rebalancing Recommendations:**

**Current vs Target Allocation:**

📊 **Overweight Positions:**
- Tech: 35% → Target: 30% (Reduce by $13,500)
- Reason: Concentration risk, take some profits

📊 **Underweight Positions:**
- Bonds: 13.8% → Target: 20% (+$16,700)
- Cash: 5.3% → Target: 12% (+$19,200)
- Healthcare: 20% → Target: 25% (+$13,500)

**Recommended Actions:**

1️⃣ **Sell (Trim Positions):**
   • AAPL: Sell 50 shares → ~$9,260
   • GOOGL: Sell 30 shares → ~$4,155
   • Total Cash Generated: $13,415

2️⃣ **Buy (Add Positions):**
   • Bond ETF (BND): $16,700
   • Healthcare (UNH): $13,500
   
3️⃣ **Hold Cash:** $19,200 in reserve

**Impact Analysis:**
- New Risk Score: 6.2 → 5.8 (Better aligned)
- Expected Volatility: -12%
- Liquidity: Improved significantly
- Tax Impact: ~$1,850 in capital gains (15% bracket)

**Benefits:**
✓ Reduced concentration risk
✓ Better downside protection
✓ Improved liquidity for opportunities
✓ More balanced growth potential

**Timeline:** Execute over 2-3 weeks to average entry/exit prices

**Reasoning:** This rebalancing maintains your growth potential while significantly reducing risk and improving financial flexibility. The tax cost is manageable compared to the risk reduction benefit.`,
    followUp: "Would you like a detailed breakdown of which specific holdings to sell and the exact rebalancing trades to execute?"
  },
  
  riskAnalysis: {
    message: `🎲 **Comprehensive Risk Profile Analysis:**

**Your Overall Risk Score: 6.2/10** (Moderate)

📊 **Risk Breakdown:**

1. **Asset Concentration Risk: 7.5/10** ⚠️
   • Tech stocks represent 35% of portfolio
   • Top 3 holdings are 33% of total value
   • Recommendation: Diversify into 2-3 more sectors

2. **Volatility Exposure: 6.0/10**
   • Expected annual volatility: 18-22%
   • vs S&P 500: 15-18% (You're +4% higher)
   • Within acceptable range for moderate profile

3. **Liquidity Risk: 4.5/10** ⚠️
   • Only 5.3% in cash reserves
   • Recommendation: Increase to 10-12%
   • Impact: Better ability to handle emergencies

4. **Market Correlation: 6.8/10**
   • 0.82 correlation with S&P 500
   • Portfolio moves closely with market
   • Limited downside protection

5. **Sector Risk: 6.5/10**
   • Tech-heavy allocation in cyclical sector
   • Healthcare provides some balance
   • Bonds: 13.8% (could be higher)

**Risk Comparison:**
- Conservative Profile: 3-4 ❌
- Moderate Profile: 5-7 ✅ **You are here**
- Aggressive Profile: 8-10 ❌

**Positive Risk Indicators:**
✅ No leveraged positions
✅ Quality blue-chip holdings
✅ Some sector diversification
✅ No concentrated single-stock exposure (>15%)

**Areas Needing Attention:**
⚠️ Increase cash reserves
⚠️ Reduce tech concentration
⚠️ Add defensive positions

**Stress Test Results:**
- Market Drop (-20%): Your portfolio: -22%
- Market Rally (+20%): Your portfolio: +23%
- Conclusion: Slightly amplified movements

**Reasoning:** Your risk level appropriately matches your stated moderate preference. However, low cash reserves and tech concentration create vulnerability during market corrections. These are easily addressable through rebalancing.`,
    followUp: "Would you like recommendations to reduce your risk score to 5.5 while maintaining similar return potential?"
  },
  
  taxAnalysis: {
    message: `💰 **Tax Impact Analysis:**

**Current Tax Situation:**

**Unrealized Gains:**
- Total: $35,000
- Short-term (<1 year): $8,200
- Long-term (>1 year): $26,800

**Estimated Tax Liability if Sold Today:**
- Short-term gains: $8,200 × 24% = $1,968
- Long-term gains: $26,800 × 15% = $4,020
- **Total Tax Bill: $5,988**

**Tax-Efficient Strategies:**

1️⃣ **Tax Loss Harvesting**
   • No current losses to harvest
   • Monitor for opportunities in volatile markets

2️⃣ **Hold for Long-Term**
   • If possible, hold positions >1 year
   • Saves 9% in taxes (24% vs 15%)

3️⃣ **Strategic Selling**
   • Sell long-term positions first
   • Minimize short-term capital gains

**2025 Year-End Planning:**
- Estimated realized gains YTD: $12,500
- Tax owed: ~$1,875
- Consider offsetting with losses if available

**Dividend Income:**
- Qualified dividends: ~$2,400/year
- Tax rate: 15%
- Annual tax: ~$360

**Recommendations:**
✓ Defer selling short-term positions if possible
✓ Use tax-advantaged accounts for future trades
✓ Consider municipal bonds for tax-free income
✓ Consult tax professional for personalized strategy

**Reasoning:** Strategic tax planning can save thousands annually. Focus on long-term capital gains rates and timing of sales.`,
    followUp: "Would you like strategies to minimize taxes while rebalancing your portfolio?"
  },
  
  diversification: {
    message: `🎯 **Portfolio Diversification Analysis:**

**Current Diversification Score: 7.8/10** (Good)

**Sector Breakdown:**
- Technology: 35% ⚠️ (Overweight)
- Healthcare: 20% ✓
- Finance: 15% ✓
- Real Estate: 16% ✓
- Bonds: 13.8% ⚠️ (Underweight)

**Geographic Diversification:**
- US Markets: 92%
- International: 8% ⚠️ (Could be higher)

**Asset Class Diversification:**
- Stocks: 70%
- Bonds: 14%
- Cash: 5%
- REITs: 11%

**Correlation Analysis:**
- Average correlation between holdings: 0.65
- Ideal: <0.60 for better diversification
- Your portfolio moves somewhat together

**Missing Exposures:**
❌ Emerging Markets
❌ Commodities
❌ International Developed Markets
❌ Small Cap Value

**Recommendations to Improve:**

1️⃣ **Add International Exposure (10-15%)**
   • VEA (Developed Markets ETF)
   • VWO (Emerging Markets ETF)

2️⃣ **Increase Bond Allocation (20%)**
   • BND (Total Bond Market)
   • VGIT (Intermediate-Term Treasury)

3️⃣ **Add Alternative Assets (5-10%)**
   • GLD (Gold ETF) - inflation hedge
   • DBC (Commodities ETF)

**Expected Impact:**
- Diversification Score: 7.8 → 8.9
- Volatility Reduction: -8%
- Better downside protection
- More consistent returns

**Reasoning:** While your diversification is good, adding international exposure and alternatives would provide better protection during US market downturns and reduce overall portfolio correlation.`,
    followUp: "Would you like specific ETF recommendations to improve your diversification?"
  },
  
  contextual_recommendation: {
    message: `Based on our previous portfolio analysis where we identified low cash reserves and tech overweight, here's what I recommend:

💰 **Immediate Action Plan:**

**Phase 1: Build Cash Reserve (Priority)**
1. Sell partial positions to raise cash
   • AAPL: 30 shares → $5,556
   • GOOGL: 40 shares → $5,540
   • Total: $11,096 → moves cash to 9.2%

**Phase 2: Rebalance Overweight Tech**
2. Trim additional tech if comfortable
   • MSFT: 15 shares → $5,487
   • Brings tech from 35% → 30%

**Phase 3: Reinvest Strategically**
3. Add to underweight sectors
   • Healthcare: $5,500 (UNH)
   • Bonds: $5,500 (BND)

**Alternative (More Conservative):**
If you don't want to sell:
- Direct next 4-6 months contributions to cash
- Temporarily pause new stock purchases
- Builds reserve over time without selling

**Impact Summary:**
- Cash Reserve: 5.3% → 12%
- Tech Allocation: 35% → 30%
- Risk Score: 6.2 → 5.7
- Tax Impact: ~$1,100

**Timeline:** Execute over 2-3 weeks

**Reasoning:** This directly addresses the concerns from your portfolio analysis - low cash and tech concentration - while maintaining your growth trajectory.`,
    followUp: "Would you like me to identify which specific tech stocks to partially sell for optimal tax efficiency?"
  },
  
  general: {
    message: `Hello! I'm your AI Investment Advisor, powered by advanced market analysis and portfolio optimization algorithms.

I can help you with:

📊 **Portfolio Analysis** - Comprehensive review of your holdings, risk, and returns

💡 **Stock Recommendations** - Personalized picks based on your profile and goals

📈 **Market Trends** - Latest insights on sectors and industries

⚖️ **Rebalancing** - Optimize your allocation for better risk-adjusted returns

🎲 **Risk Assessment** - Detailed analysis of your portfolio risk factors

🏭 **Industry Analysis** - Identify booming sectors for investment

💰 **Tax Planning** - Strategies to minimize capital gains taxes

🎯 **Diversification** - Improve your portfolio's risk profile

**What would you like to explore today?**`,
    followUp: null
  }
};

// Simulated typing effect helper (optional)
export const simulateTyping = (text, callback, speed = 50) => {
  const words = text.split(' ');
  let currentText = '';
  let index = 0;
  
  const interval = setInterval(() => {
    if (index < words.length) {
      currentText += (index > 0 ? ' ' : '') + words[index];
      callback(currentText);
      index++;
    } else {
      clearInterval(interval);
    }
  }, speed);
  
  return interval;
};
