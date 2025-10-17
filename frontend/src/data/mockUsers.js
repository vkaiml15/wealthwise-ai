// User credentials and basic info
export const mockUsers = {
  // Existing users with portfolios
  existing: [
    {
      userId: "john_investor",
      password: "Invest@2024",
      name: "John Smith",
      email: "john.smith@example.com",
      age: 35,
      phone: "+1 (555) 123-4567",
      riskProfile: "moderate",
      riskTolerance: "moderate",
      investmentGoal: "growth",
      investmentHorizon: "5-10",
      monthlyContribution: "500",
      hasPortfolio: true,
      createdAt: "2024-01-15"
    },
    {
      userId: "sarah_trader",
      password: "Trade@2024",
      name: "Sarah Johnson",
      email: "sarah.j@example.com",
      age: 29,
      phone: "+1 (555) 234-5678",
      riskProfile: "aggressive",
      riskTolerance: "aggressive",
      investmentGoal: "growth",
      investmentHorizon: "3-5",
      monthlyContribution: "1000",
      hasPortfolio: true,
      createdAt: "2023-11-20"
    },
    {
      userId: "mike_growth",
      password: "Growth@2024",
      name: "Mike Chen",
      email: "mike.chen@example.com",
      age: 42,
      phone: "+1 (555) 345-6789",
      riskProfile: "moderate",
      riskTolerance: "moderate",
      investmentGoal: "growth",
      investmentHorizon: "5-10",
      monthlyContribution: "750",
      hasPortfolio: true,
      createdAt: "2023-08-10"
    },
    {
      userId: "emma_conservative",
      password: "Safe@2024",
      name: "Emma Davis",
      email: "emma.davis@example.com",
      age: 58,
      phone: "+1 (555) 456-7890",
      riskProfile: "conservative",
      riskTolerance: "conservative",
      investmentGoal: "preservation",
      investmentHorizon: "10+",
      monthlyContribution: "300",
      hasPortfolio: true,
      createdAt: "2023-05-25"
    },
    {
      userId: "david_aggressive",
      password: "Risk@2024",
      name: "David Wilson",
      email: "david.wilson@example.com",
      age: 31,
      phone: "+1 (555) 567-8901",
      riskProfile: "aggressive",
      riskTolerance: "aggressive",
      investmentGoal: "growth",
      investmentHorizon: "3-5",
      monthlyContribution: "1500",
      hasPortfolio: true,
      createdAt: "2024-02-01"
    }
  ],
  
  // New users (need onboarding)
  new: [
    {
      userId: "new_user1",
      password: "Welcome@123",
      hasPortfolio: false
    },
    {
      userId: "new_user2",
      password: "Welcome@123",
      hasPortfolio: false
    },
    {
      userId: "new_user3",
      password: "Welcome@123",
      hasPortfolio: false
    },
    {
      userId: "new_user4",
      password: "Welcome@123",
      hasPortfolio: false
    },
    {
      userId: "new_user5",
      password: "Welcome@123",
      hasPortfolio: false
    }
  ]
};

// Helper function to get user by userId
export const getUserById = (userId) => {
  const allUsers = [...mockUsers.existing, ...mockUsers.new];
  return allUsers.find(user => user.userId === userId);
};

// Helper function to validate credentials
export const validateCredentials = (userId, password) => {
  const allUsers = [...mockUsers.existing, ...mockUsers.new];
  return allUsers.find(user => user.userId === userId && user.password === password);
};
