import boto3
from typing import Dict, Optional
from decimal import Decimal
import os


class SmartQBusinessService:
    def __init__(self, users_table, portfolios_table, region_name='us-east-1'):
        """Initialize with existing DynamoDB table references"""
        self.q_business = boto3.client('qbusiness', region_name=region_name)
        self.application_id = os.getenv('Q_BUSINESS_APPLICATION_ID')
        
        self.users_table = users_table
        self.portfolios_table = portfolios_table
        
        print(f"✅ Smart Q Business Service initialized")
        print(f"   Users Table: {self.users_table.table_name}")
        print(f"   Portfolios Table: {self.portfolios_table.table_name}")
        
        # Keywords for query classification
        self.personal_keywords = [
            'my', 'i', 'me', 'mine', 'our',
            'portfolio', 'holdings', 'stocks', 'bonds',
            'investment', 'should i', 'can i', 
            'risk profile', 'diversification',
            'rebalance', 'sell', 'buy',
            'allocation', 'performance',
            'my name', 'who am i', 'my age', 'my risk',
            'my goal', 'my horizon', 'my investment',
            'how old', 'what is my'
        ]
        
        self.general_keywords = [
            'what is', 'what are', 'explain', 'define',
            'how does', 'how do', 'tell me about',
            'difference between', 'types of',
            'market trend', 'industry', 'sector',
            'general', 'overview', 'introduction'
        ]
        
        # ✅ NEW: Greeting keywords
        self.greeting_keywords = [
            'hi', 'hello', 'hey', 'hola', 'greetings',
            'good morning', 'good afternoon', 'good evening',
            'howdy', 'sup', "what's up", 'whats up',
            'how are you', 'how do you do',
            'nice to meet you', 'thanks', 'thank you',
            'bye', 'goodbye', 'see you', 'take care'
        ]
    
    def classify_query(self, query: str) -> str:
        """
        Classify if query is PERSONAL, GENERAL, or GREETING
        
        Returns:
            'greeting' - Casual conversation (no data needed)
            'personal' - Needs user context from DynamoDB
            'general' - Can use only S3 knowledge base
        """
        query_lower = query.lower().strip()
        
        # ✅ Check for greetings FIRST (highest priority)
        # Check if the entire query is just a greeting (short queries)
        if len(query_lower.split()) <= 5:  # Short queries only
            if any(greeting in query_lower for greeting in self.greeting_keywords):
                print(f"👋 Query classified as GREETING")
                return 'greeting'
        
        # Check for personal keywords
        personal_score = sum(1 for keyword in self.personal_keywords 
                           if keyword in query_lower)
        
        # Check for general keywords
        general_score = sum(1 for keyword in self.general_keywords 
                          if keyword in query_lower)
        
        if personal_score > 0:
            print(f"🎯 Query classified as PERSONAL (score: {personal_score})")
            return 'personal'
        elif general_score > 0:
            print(f"📚 Query classified as GENERAL (score: {general_score})")
            return 'general'
        else:
            print(f"❓ Query ambiguous, defaulting to GENERAL")
            return 'general'
    
    def build_user_context(self, user_email: str) -> Optional[str]:
        """Build user context from DynamoDB"""
        try:
            print(f"🔍 Fetching user: {user_email}")
            
            user_resp = self.users_table.get_item(Key={'userId': user_email})
            user = user_resp.get('Item')
            
            if not user:
                print(f"⚠️ User not found: {user_email}")
                return None
            
            portfolio_resp = self.portfolios_table.get_item(Key={'userId': user_email})
            portfolio = portfolio_resp.get('Item', {})
            
            # Calculate totals
            stocks = portfolio.get('stocks', [])
            bonds = portfolio.get('bonds', [])
            etfs = portfolio.get('etfs', [])
            cash = float(portfolio.get('cashSavings', 0))
            
            stock_value = sum(float(s.get('quantity', 0)) * float(s.get('avgPrice', 0)) 
                            for s in stocks)
            bond_value = sum(float(b.get('quantity', 0)) * float(b.get('avgPrice', 0)) 
                           for b in bonds)
            etf_value = sum(float(e.get('quantity', 0)) * float(e.get('avgPrice', 0)) 
                          for e in etfs)
            total_value = stock_value + bond_value + etf_value + cash
            
            # Format holdings
            holdings_text = []
            for stock in stocks:
                holdings_text.append(
                    f"  • {stock.get('symbol', 'N/A')}: {stock.get('quantity', 0)} shares @ "
                    f"₹{float(stock.get('avgPrice', 0)):.2f}"
                )
            for bond in bonds:
                holdings_text.append(
                    f"  • {bond.get('symbol', 'N/A')} (Bond): {bond.get('quantity', 0)} units"
                )
            for etf in etfs:
                holdings_text.append(
                    f"  • {etf.get('symbol', 'N/A')} (ETF): {etf.get('quantity', 0)} units"
                )
            
            # Risk analysis
            risk_analysis = user.get('riskAnalysis', {})
            user_name = user.get('name', 'N/A')
            user_age = user.get('age', 'N/A')
            
            # Build context with explicit instructions
            context = f"""You are answering questions for a specific user. Use this information to answer their personal questions.

USER PERSONAL INFORMATION:
- Full Name: {user_name}
- Email: {user_email}
- Age: {user_age} years old
- Occupation: {user.get('occupation', 'Professional')}
- Risk Tolerance: {user.get('riskTolerance', 'Moderate')}
- Investment Horizon: {user.get('investmentHorizon', '5-10 years')}
- Investment Goal: {user.get('investmentGoal', 'Wealth Accumulation')}
- Monthly Contribution: ₹{float(user.get('monthlyContribution', 0)):,.2f}

PORTFOLIO SUMMARY:
- Total Value: ₹{total_value:,.2f}
- Cash/Savings: ₹{cash:,.2f}
- Stocks: ₹{stock_value:,.2f}
- Bonds: ₹{bond_value:,.2f}
- ETFs: ₹{etf_value:,.2f}

HOLDINGS:
{chr(10).join(holdings_text) if holdings_text else '  No holdings'}

RISK PROFILE:
- Risk Score: {risk_analysis.get('overallRiskScore', 'N/A')}/100
- Health Score: {risk_analysis.get('healthScore', 'N/A')}/100

IMPORTANT: When the user asks personal questions like "what is my name?", use the information above directly.
- If asked "what is my name?" → Answer: "Your name is {user_name}"
- If asked "how old am I?" → Answer: "You are {user_age} years old"
"""
            print("✅ User context built successfully")
            return context
            
        except Exception as e:
            print(f"❌ Error building context: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def chat_sync(
            self,
            user_message: str,
            user_email: str,
            conversation_id: Optional[str] = None,
            parent_message_id: Optional[str] = None
        ) -> Dict:
    
        try:
            print(f"\n{'='*60}")
            print(f"💬 Processing Query: {user_message[:50]}...")
            print(f"👤 User: {user_email}")
            
            # Classify query
            query_type = self.classify_query(user_message)
            
            # ✅ Handle greetings with friendly instructions
            if query_type == 'greeting':
                enhanced_message = f"""The user said: "{user_message}"

    This is a greeting or casual message. Respond warmly and professionally as a financial advisor assistant. 

    Examples:
    - If they say "hi" or "hello" → Greet them back and offer to help with their investments
    - If they say "thanks" → Acknowledge and offer further assistance
    - If they say "goodbye" → Wish them well

    Keep your response brief (1-2 sentences) and friendly. Mention that you can help with portfolio analysis, investment advice, or financial questions.
    """
                print("👋 Greeting detected - adding response instructions")
            
            # Handle personal queries
            elif query_type == 'personal':
                print("📥 Fetching user context from DynamoDB...")
                user_context = self.build_user_context(user_email)
                
                if user_context:
                    enhanced_message = f"""{user_context}

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    USER QUESTION: {user_message}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Answer this question using the user's personal information provided above. The answer is in the context. Provide a direct, friendly response.
    """
                    print("✅ User context injected")
                else:
                    enhanced_message = user_message
                    print("⚠️ Could not fetch user context, using query only")
            
            # Handle general queries
            else:
                enhanced_message = user_message
                print("📚 Using query only (will search S3 documents)")
            
            # Prepare request
            request_params = {
                'applicationId': self.application_id,
                'userMessage': enhanced_message
            }
            
            if conversation_id:
                request_params['conversationId'] = conversation_id
            if parent_message_id:
                request_params['parentMessageId'] = parent_message_id
            
            # Call Q Business
            print("🚀 Calling Q Business...")
            response = self.q_business.chat_sync(**request_params)
            
            print("✅ Q Business responded successfully")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'systemMessage': response.get('systemMessage', ''),
                'conversationId': response.get('conversationId'),
                'systemMessageId': response.get('systemMessageId'),
                'userMessageId': response.get('userMessageId'),
                'sourceAttributions': response.get('sourceAttributions', []),
                'queryType': query_type,
                'contextInjected': query_type == 'personal' and user_context is not None
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'systemMessage': f"Sorry, I encountered an error: {str(e)}"
            }


# Singleton pattern
_smart_qbusiness_service = None

def get_qbusiness_service(users_table=None, portfolios_table=None) -> SmartQBusinessService:
    """Get or create Smart Q Business service instance"""
    global _smart_qbusiness_service
    
    if _smart_qbusiness_service is None:
        if users_table is None or portfolios_table is None:
            raise ValueError("Tables must be provided for first initialization")
        _smart_qbusiness_service = SmartQBusinessService(users_table, portfolios_table)
    
    return _smart_qbusiness_service