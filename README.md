# WealthWise AI Robo-Advisor

**Your Intelligent Investment Companion** - An AI-powered robo-advisor built with Strand SDK and AWS services that provides personalized investment recommendations, portfolio analysis, and market insights.

## 🚀 Features

### Core Capabilities
- **AI-Powered Portfolio Analysis** - Comprehensive portfolio health scoring and recommendations
- **Real-Time Market Data** - Live market data integration with intelligent fallback systems
- **Personalized Recommendations** - AI-generated investment advice tailored to user profiles
- **Risk Assessment** - Advanced risk profiling and tolerance analysis
- **Conversational Interface** - Natural language chat with AI agents
- **Q Business Integration** - AWS Q Business for enhanced financial insights

### AI Agents (Strand SDK)
- **Market Agent** - Real-time market data and analysis
- **Portfolio Agent** - Portfolio health scoring and optimization
- **Recommendation Agent** - Personalized investment recommendations
- **Risk Agent** - Risk profiling and assessment
- **Orchestrator Agent** - Coordinates multi-agent conversations

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

## 🚀 Complete Setup Guide

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

#### AI-Powered Analysis (Strand SDK)
- `POST /api/chat` - Conversational interface
- `GET /api/portfolio/{email}/analysis` - Portfolio analysis
- `GET /api/portfolio/{email}/recommendations` - AI recommendations
- `GET /api/portfolio/{email}/risk-analysis` - Risk assessment
- `POST /api/portfolio/{email}/ask` - Ask specific questions

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

## 🤖 AI Agents

### Market Agent
- Fetches real-time market data
- Provides market analysis and trends
- Supports multiple data sources with fallback

### Portfolio Agent
- Analyzes portfolio health and performance
- Calculates diversification metrics
- Provides optimization recommendations

### Recommendation Agent
- Generates personalized investment advice
- Considers user risk profile and goals
- Provides explainable AI insights

### Risk Agent
- Assesses user risk tolerance
- Analyzes portfolio risk metrics
- Provides risk-adjusted recommendations

## 🔒 Security

- Password hashing with bcrypt
- AWS IAM role-based access control
- Environment variable configuration
- Input validation with Pydantic models

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
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

### Common Issues

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