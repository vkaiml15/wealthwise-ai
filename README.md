# WealthWise AI Robo-Advisor

**Your Intelligent Investment Companion** - An AI-powered robo-advisor built with Strand SDK and AWS services that provides personalized investment recommendations, portfolio analysis, and market insights.

## 🚀 Features

### Core Capabilities
- **🤖 Explainable AI (XAI) Recommendations** - Transparent, interpretable investment advice with detailed reasoning
- **📊 AI-Powered Portfolio Analysis** - Comprehensive portfolio health scoring with confidence metrics
- **📈 Real-Time Market Data** - Live market data integration with intelligent fallback systems
- **🎯 Personalized Risk Assessment** - Advanced risk profiling with explainable factors
- **💬 Conversational AI Interface** - Natural language chat with multi-agent orchestration
- **☁️ AWS Q Business Integration** - Enterprise-grade financial insights and document analysis
- **📋 Comprehensive Logging** - CloudWatch integration for audit trails and performance monitoring

### 🧠 Explainable AI (XAI) Features

#### **Transparent Decision Making**
- **Methodology Disclosure** - Clear explanation of recommendation algorithms combining Modern Portfolio Theory and behavioral finance
- **Factor Attribution** - Detailed breakdown of factors influencing each recommendation (age, risk tolerance, market conditions, etc.)
- **Confidence Scoring** - Quantified confidence levels for all recommendations with explanations
- **Personalization Transparency** - Clear indication of how user profile affects recommendations

#### **Comprehensive Audit Trail**
- **CloudWatch Integration** - All AI decisions logged with timestamps and reasoning
- **Recommendation Lineage** - Full traceability from input data to final recommendations  
- **Performance Metrics** - Confidence scores, data quality assessments, and model performance tracking
- **User Context Logging** - Detailed logging of user interactions and AI responses for compliance

#### **AI Agents (Strand SDK)**
- **Market Agent** - Real-time market data analysis with explainable market sentiment
- **Portfolio Agent** - Portfolio health scoring with detailed factor breakdown
- **Recommendation Agent** - Personalized investment advice with XAI insights and confidence metrics
- **Risk Agent** - Risk profiling with transparent factor analysis and scoring methodology
- **Orchestrator Agent** - Multi-agent coordination with conversation context and decision routing

## 🏗️ Architecture

```
WealthWise/
├── backend/                 # FastAPI Python backend
│   ├── agents/             # Strand SDK AI agents
│   ├── services/           # AWS service integrations
│   ├── tools/              # Utility functions
│   └── server.py           # Main FastAPI application
├── frontend/               # React.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── context/        # React context providers
│   └── public/             # Static assets
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: Strand SDK with AWS Bedrock (Claude Sonnet 4)
- **Database**: AWS DynamoDB
- **Authentication**: bcrypt password hashing
- **Market Data**: Yahoo Finance, Alpha Vantage, Finnhub APIs
- **Cloud Services**: AWS Q Business, AWS Bedrock

### Frontend
- **Framework**: React.js 18
- **UI Library**: Material-UI (MUI) + Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React, MUI Icons
- **HTTP Client**: Axios
- **Routing**: React Router DOM

### Infrastructure
- **Cloud Provider**: AWS
- **Deployment**: AWS Amplify (frontend), EC2/Lambda (backend)
- **Storage**: DynamoDB tables for users and portfolios

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+** 
- **AWS Account** with administrative access
- **AWS CLI** installed and configured
- **API Keys** (optional but recommended for better market data):
  - Alpha Vantage API key (free tier available)
  - Finnhub API key (free tier available)

## 🚀 Quick Start (Cross-Platform)

### Option 1: Local Development Setup

#### **Recommended: Cross-Platform Python Script**
```bash
# Works on Windows, macOS, and Linux with Python 3.6+
python infrastructure/scripts/setup-local.py
```

#### **Alternative: Platform-Specific Scripts**

**Windows (Command Prompt)**
```cmd
infrastructure\scripts\setup-local.bat
```

**macOS/Linux (Bash)**
```bash
chmod +x infrastructure/scripts/setup-local.sh
./infrastructure/scripts/setup-local.sh
```

### Option 2: CloudFormation Deployment
```bash
# Deploy complete AWS infrastructure
chmod +x infrastructure/scripts/deploy-cloudformation.sh
./infrastructure/scripts/deploy-cloudformation.sh dev us-east-1
```

### Option 3: Terraform Deployment
```bash
# Deploy with Terraform (infrastructure versioning)
chmod +x infrastructure/scripts/deploy-terraform.sh
./infrastructure/scripts/deploy-terraform.sh dev us-east-1
```

### Option 4: Docker Compose (Local Development)
```bash
# Run everything in containers
cd infrastructure/docker
cp .env.example .env  # Edit with your AWS credentials
docker-compose up -d
```

## 🛠️ Manual Setup Guide

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd wealthwise-ai
```

### Step 2: AWS Account Setup

#### 2.1 Create AWS Account
1. Go to [AWS Console](https://aws.amazon.com/)
2. Create a new account or sign in to existing account
3. Complete account verification

#### 2.2 Install and Configure AWS CLI
```bash
# Install AWS CLI
# Windows: Download from https://aws.amazon.com/cli/
# macOS: brew install awscli
# Linux: sudo apt-get install awscli

# Configure AWS CLI
aws configure
```
When prompted, enter:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key  
- **Default region**: `us-east-1` (recommended)
- **Default output format**: `json`

#### 2.3 Create IAM User (Alternative to Root Account)
```bash
# Create IAM user with programmatic access
aws iam create-user --user-name wealthwise-user

# Attach necessary policies
aws iam attach-user-policy --user-name wealthwise-user --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-user-policy --user-name wealthwise-user --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam attach-user-policy --user-name wealthwise-user --policy-arn arn:aws:iam::aws:policy/AmazonQBusinessFullAccess

# Create access keys
aws iam create-access-key --user-name wealthwise-user
```

### Step 3: Create AWS Resources

#### 3.1 Create DynamoDB Tables
```bash
# Create Users table
aws dynamodb create-table \
    --table-name WealthWiseUsers \
    --attribute-definitions \
        AttributeName=userId,AttributeType=S \
    --key-schema \
        AttributeName=userId,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

# Create Portfolios table  
aws dynamodb create-table \
    --table-name WealthWisePortfolios \
    --attribute-definitions \
        AttributeName=userId,AttributeType=S \
    --key-schema \
        AttributeName=userId,KeyType=HASH \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5

# Wait for tables to be created
aws dynamodb wait table-exists --table-name WealthWiseUsers
aws dynamodb wait table-exists --table-name WealthWisePortfolios
```

#### 3.2 Enable AWS Bedrock Models
```bash
# Enable Claude Sonnet model in Bedrock (us-east-1 region)
# Note: This may require manual approval in AWS Console
aws bedrock list-foundation-models --region us-east-1
```

**Important**: Go to AWS Bedrock Console → Model Access → Request access to Claude models

#### 3.3 Set up AWS Q Business (Optional)
1. Go to AWS Q Business Console
2. Create a new application
3. Note the Application ID for configuration

### Step 4: Get API Keys (Optional)

#### 4.1 Alpha Vantage API Key
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for free API key
3. Note the API key

#### 4.2 Finnhub API Key  
1. Visit [Finnhub](https://finnhub.io/register)
2. Sign up for free account
3. Get API key from dashboard

### Step 5: Backend Setup

#### 5.1 Python Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 5.2 Environment Configuration
```bash
# Create environment file
touch .env  # Linux/macOS
# OR
echo. > .env  # Windows

# Edit .env file with your configuration
```

**Backend .env file contents:**
```env
# AWS Configuration
AWS_REGION=us-east-1
# Note: AWS credentials will be picked up from AWS CLI configuration
# If running on EC2, IAM roles are used automatically

# Optional API Keys (for enhanced market data)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# Q Business Configuration (if using)
QBUSINESS_APPLICATION_ID=your_qbusiness_app_id_here

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Step 6: Frontend Setup

#### 6.1 Install Dependencies
```bash
cd frontend

# Install Node.js dependencies
npm install
```

#### 6.2 Frontend Configuration
```bash
# Create environment file
touch .env  # Linux/macOS
# OR  
echo. > .env  # Windows
```

**Frontend .env file contents:**
```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Environment
REACT_APP_ENVIRONMENT=development
```

### Step 7: Verify Setup

#### 7.1 Test AWS Connection
```bash
# Test DynamoDB connection
aws dynamodb list-tables

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

#### 7.2 Test Backend
```bash
cd backend
python server.py
```
You should see:
```
🔧 STRAND SDK - WealthWise AI Robo-Advisor
✅ DynamoDB connected! Found 2 tables
✅ Market and Portfolio agents initialized
✅ Q Business Service initialized
```

### Step 8: Run the Application

#### 8.1 Start Backend Server
```bash
# Terminal 1 - Backend
cd backend
python server.py
```

#### 8.2 Start Frontend Development Server
```bash
# Terminal 2 - Frontend  
cd frontend
npm start
```

### Step 9: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Infrastructure as Code

This project includes complete Infrastructure as Code (IaC) templates for easy deployment:

### Available IaC Options
- **CloudFormation**: AWS-native infrastructure templates
- **Terraform**: Cross-platform infrastructure with state management  
- **Docker Compose**: Containerized local development
- **Deployment Scripts**: Automated setup and deployment

### Quick Commands
```bash
# Complete local setup
./infrastructure/scripts/setup-local.sh

# Deploy to AWS (CloudFormation)
./infrastructure/scripts/deploy-cloudformation.sh dev

# Deploy to AWS (Terraform) 
./infrastructure/scripts/deploy-terraform.sh dev

# Clean up AWS resources
./infrastructure/scripts/cleanup.sh dev
```

**📚 Detailed IaC Documentation**: See [infrastructure/README.md](infrastructure/README.md)

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# AWS Configuration
AWS_REGION=us-east-1
# AWS credentials are automatically picked up from:
# 1. AWS CLI configuration (~/.aws/credentials)
# 2. IAM roles (when running on EC2)
# 3. Environment variables (if needed)

# Optional: Only if not using AWS CLI or IAM roles
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key

# Market Data APIs (Optional - improves data quality)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# Q Business (Optional)
QBUSINESS_APPLICATION_ID=your_qbusiness_app_id

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

### AWS Credentials Priority Order
The application uses AWS credentials in this order:
1. **IAM Roles** (when running on EC2/ECS/Lambda)
2. **AWS CLI credentials** (`~/.aws/credentials`)
3. **Environment variables** (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
4. **Instance metadata** (EC2 instances with IAM roles)

## 📚 API Documentation

### Core Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/onboarding/complete` - Complete user onboarding

#### Portfolio Management
- `GET /api/portfolio/{email}` - Get user portfolio
- `GET /api/portfolio/{email}/dashboard` - Complete dashboard data
- `PUT /api/portfolio/{email}` - Update portfolio

#### AI-Powered Analysis with Explainable AI (Strand SDK)
- `POST /api/chat` - Conversational interface with XAI explanations
- `GET /api/portfolio/{email}/analysis` - Portfolio analysis with confidence metrics
- `GET /api/portfolio/{email}/recommendations` - AI recommendations with detailed reasoning
- `GET /api/portfolio/{email}/risk-analysis` - Risk assessment with factor attribution
- `POST /api/portfolio/{email}/ask` - Ask specific questions with explainable responses

#### XAI-Enhanced Response Format
All AI endpoints return explainable responses with:
```json
{
  "success": true,
  "recommendations": [...],
  "ai_insights": "Personalized explanation generated by Claude Sonnet 4",
  "explainability": {
    "methodology": "Modern Portfolio Theory + Behavioral Finance",
    "factors_considered": [
      "User age and risk profile",
      "Portfolio allocation and diversification", 
      "Market conditions and timing",
      "Investment horizon and goals"
    ]
  },
  "confidence": {
    "recommendation_confidence": "high",
    "data_quality": {
      "risk_assessment": "high",
      "market_data": "medium", 
      "user_profile": "high"
    },
    "explanation": "Confidence based on data completeness and model certainty"
  },
  "metadata": {
    "user": {...},
    "portfolio": {...},
    "market_context": {...}
  }
}
```

#### Q Business Integration
- `POST /api/qbusiness/chat` - Q Business chat interface
- `GET /api/qbusiness/conversations` - List conversations
- `DELETE /api/qbusiness/conversations/{id}` - Delete conversation

### Example API Usage

```javascript
// Get AI recommendations
const response = await fetch('/api/portfolio/user@example.com/recommendations');
const data = await response.json();

// Chat with AI
const chatResponse = await fetch('/api/chat?user_email=user@example.com', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: "Should I rebalance my portfolio?" })
});
```

## 🤖 AI Agents with Explainable AI

### Market Agent
- **Real-time Data Analysis** - Fetches and analyzes live market data with confidence scoring
- **Market Sentiment Analysis** - Provides explainable market condition assessments
- **Multi-source Integration** - Intelligent fallback systems with data quality metrics
- **Audit Logging** - All market data requests and responses logged to CloudWatch

### Portfolio Agent  
- **Health Scoring** - Transparent portfolio health calculations with factor breakdown
- **Diversification Analysis** - Explainable diversification metrics and recommendations
- **Performance Attribution** - Clear explanation of portfolio performance drivers
- **Risk-Return Analysis** - Detailed risk-adjusted return calculations with methodology disclosure

### Recommendation Agent (XAI-Enhanced)
- **Personalized Advice Generation** - AI-powered recommendations with detailed reasoning
- **Confidence Metrics** - Quantified confidence scores for each recommendation
- **Factor Attribution** - Clear breakdown of recommendation drivers:
  - User age and investment horizon
  - Risk tolerance and investment goals  
  - Current portfolio allocation
  - Market conditions and timing
  - Historical performance data
- **Methodology Transparency** - Disclosure of Modern Portfolio Theory and behavioral finance principles
- **Explainable Insights** - Natural language explanations generated by Claude Sonnet 4

### Risk Agent
- **Transparent Risk Assessment** - Clear methodology for risk tolerance evaluation
- **Factor Analysis** - Detailed breakdown of risk factors considered
- **Scoring Methodology** - Explainable risk scoring with confidence intervals
- **Behavioral Finance Integration** - Consideration of behavioral biases with explanations

### Orchestrator Agent
- **Conversation Management** - Context-aware multi-agent coordination
- **Decision Routing** - Transparent routing of queries to appropriate agents
- **Response Synthesis** - Coherent combination of multi-agent responses
- **Audit Trail** - Complete logging of agent interactions and decision paths

## 🔒 Security & Compliance

### Security Features
- Password hashing with bcrypt
- AWS IAM role-based access control
- Environment variable configuration
- Input validation with Pydantic models

### Explainable AI Compliance
- **Regulatory Compliance** - Meets requirements for transparent AI in financial services
- **Audit Trail** - Complete logging of all AI decisions for regulatory review
- **Bias Monitoring** - Continuous monitoring for algorithmic bias and fairness
- **Model Governance** - Version control and change management for AI models
- **Right to Explanation** - Users can request detailed explanations for any AI recommendation
- **Data Lineage** - Full traceability of data sources used in AI decisions

### Financial Services Compliance
- **GDPR Compliance** - Right to explanation and data portability for AI decisions
- **MiFID II Compliance** - Transparent investment advice with documented reasoning
- **Fiduciary Standards** - AI recommendations include disclosure of methodology and limitations
- **Risk Disclosure** - Clear communication of AI model limitations and confidence levels

## 🧪 Testing

### Automated Local Environment Testing
```bash
# Cross-platform comprehensive testing (recommended)
python infrastructure/scripts/test-local.py

# Unix/Linux/macOS testing
chmod +x infrastructure/scripts/test-local.sh
./infrastructure/scripts/test-local.sh
```

### Manual Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### What the Automated Tests Check
- ✅ Environment file configuration
- ✅ Dependencies installation
- ✅ Backend service startup and health
- ✅ Frontend service startup and accessibility
- ✅ API endpoint functionality
- ✅ Cross-platform compatibility

## � Monityoring & Explainable AI Logging

### CloudWatch Integration
- **AI Decision Logging** - All recommendation decisions logged with full context
- **Performance Metrics** - Real-time monitoring of AI agent performance and response times
- **Confidence Tracking** - Historical tracking of recommendation confidence scores
- **Error Analysis** - Detailed logging of AI failures with root cause analysis

### Audit Trail Features
- **Recommendation Lineage** - Complete traceability from user input to AI recommendation
- **Factor Attribution Logs** - Detailed logging of all factors considered in recommendations
- **Model Performance Tracking** - Continuous monitoring of AI model accuracy and drift
- **Compliance Logging** - Regulatory-compliant audit trails for financial recommendations

### XAI Transparency Reports
- **Decision Explanations** - Automated generation of human-readable decision explanations
- **Confidence Intervals** - Statistical confidence bounds for all AI predictions
- **Bias Detection** - Monitoring for algorithmic bias in recommendations
- **Model Interpretability** - SHAP-style feature importance for recommendation factors

### Real-time Monitoring
```bash
# View AI decision logs
aws logs filter-log-events --log-group-name "/aws/wealthwise/prod/ai-decisions"

# Monitor recommendation confidence
aws logs filter-log-events --log-group-name "/aws/wealthwise/prod/confidence-metrics"

# Track XAI explanations
aws logs filter-log-events --log-group-name "/aws/wealthwise/prod/explainability"
```

## 📈 Deployment

### AWS Amplify (Frontend)
```bash
cd frontend
npm run build
# Deploy build/ directory to Amplify
```

### AWS EC2/Lambda (Backend)
```bash
cd backend
# Package and deploy using your preferred method
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the troubleshooting section below

## 🔧 Troubleshooting

### Common Issues by Platform

#### **Windows-Specific Issues**

1. **PowerShell Execution Policy**
   ```powershell
   # If you get execution policy error
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # Or run with bypass
   powershell -ExecutionPolicy Bypass -File .\infrastructure\scripts\setup-local.ps1
   ```

2. **Python Command Not Found**
   ```cmd
   # Try different Python commands
   python --version
   python3 --version
   py --version
   
   # Add Python to PATH or reinstall from python.org
   ```

3. **Long Path Issues**
   ```cmd
   # Enable long paths in Windows
   # Run as Administrator in Command Prompt:
   reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
   ```

#### **macOS-Specific Issues**

1. **Permission Denied on Scripts**
   ```bash
   # Make scripts executable
   chmod +x infrastructure/scripts/*.sh
   
   # Or run with bash directly
   bash infrastructure/scripts/setup-local.sh
   ```

2. **Node.js/npm Issues**
   ```bash
   # Install using Homebrew
   brew install node
   
   # Or use Node Version Manager
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install node
   ```

#### **Linux-Specific Issues**

1. **Permission Issues**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ~/.npm
   
   # Or use node version manager to avoid sudo
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   ```

2. **Missing Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3-venv python3-pip nodejs npm git curl
   
   # CentOS/RHEL
   sudo yum install python3 python3-pip nodejs npm git curl
   ```

#### **Cross-Platform Issues**

1. **AWS Credentials Issues**
   ```bash
   # Check AWS CLI configuration
   aws configure list
   
   # Test AWS access
   aws sts get-caller-identity
   
   # If using IAM user, ensure policies are attached:
   aws iam list-attached-user-policies --user-name wealthwise-user
   ```

2. **DynamoDB Connection Issues**
   ```bash
   # Verify tables exist
   aws dynamodb list-tables
   
   # Check table status
   aws dynamodb describe-table --table-name WealthWiseUsers
   aws dynamodb describe-table --table-name WealthWisePortfolios
   ```

3. **Bedrock Access Issues**
   ```bash
   # Check available models
   aws bedrock list-foundation-models --region us-east-1
   
   # Verify model access (may need manual approval in console)
   ```

4. **Market Data API Failures**
   - Check API key configuration in .env
   - Verify rate limits aren't exceeded
   - Application has fallback mechanisms for missing API keys

5. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   
   # Check Node.js version
   node --version  # Should be 16+
   ```

6. **Port Conflicts**
   ```bash
   # Check if ports are in use
   # Windows:
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   
   # macOS/Linux:
   lsof -i :8000
   lsof -i :3000
   ```

### Debug Mode
Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

### First Time Setup Checklist
- [ ] AWS Account created and verified
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] DynamoDB tables created (WealthWiseUsers, WealthWisePortfolios)
- [ ] Bedrock model access enabled (Claude Sonnet)
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Environment files configured (.env in both backend and frontend)
- [ ] Backend server starts successfully (`python server.py`)
- [ ] Frontend server starts successfully (`npm start`)
- [ ] Can access http://localhost:3000 and http://localhost:8000/docs

### Production Deployment Notes
- Use IAM roles instead of access keys when deploying to AWS
- Set up proper VPC and security groups
- Use RDS or DynamoDB with proper backup strategies
- Configure CloudWatch for monitoring and logging
- Use AWS Secrets Manager for sensitive configuration
- Set up CI/CD pipeline with AWS CodePipeline or GitHub Actions

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced portfolio optimization algorithms
- [ ] Integration with more brokerages
- [ ] Enhanced AI conversation capabilities
- [ ] Real-time notifications
- [ ] Social trading features

---

**Built with ❤️ using Strand SDK, AWS, and modern web technologies**