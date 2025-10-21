
from agents.strand_orchestrator import StrandOrchestrator


def create_orchestrator_agent(agent_registry):

    print("🏭 [Factory] Creating Strand Orchestrator Agent...")
    
    # Convert agents to tools format expected by orchestrator
    tools = {}
    
    if 'market' in agent_registry:
        tools['market_data'] = type('Tool', (), {
            'execute': agent_registry['market'].generate_report
        })()
    
    if 'portfolio' in agent_registry:
        tools['portfolio_analysis'] = type('Tool', (), {
            'execute': agent_registry['portfolio'].analyze_portfolio
        })()
    
    if 'recommendation' in agent_registry:
        tools['recommendations'] = type('Tool', (), {
            'execute': agent_registry['recommendation'].generate_recommendations
        })()
    
    if 'risk' in agent_registry:
        tools['risk_analysis'] = type('Tool', (), {
            'execute': agent_registry['risk'].analyze_user_risk_profile
        })()
    
    orchestrator = StrandOrchestrator(tools)
    
    print("✅ [Factory] Strand Orchestrator Agent created successfully")
    return orchestrator