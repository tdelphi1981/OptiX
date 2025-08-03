"""
OptiX Analysis Module
=====================

This module provides comprehensive analysis tools for OptiX optimization problems,
including sensitivity analysis, scenario comparison, and performance evaluation
capabilities that leverage the built-in scenario management system.

The analysis module is designed to work seamlessly with OptiX's optimization
framework, providing detailed insights into problem behavior under different
parameter configurations and enabling data-driven decision making.

Available Analysis Tools:
    - OXObjectiveFunctionAnalysis: Comprehensive objective function analysis across scenarios
    - OXRightHandSideAnalysis: Right Hand Side constraint analysis with UUID-based tracking
    - OXSensitivityAnalysis: Parameter sensitivity analysis (future implementation)
    - OXScenarioComparison: Detailed scenario comparison tools (future implementation)

Example:
    Basic usage of the analysis module:
    
    .. code-block:: python
    
        from analysis import OXObjectiveFunctionAnalysis, OXRightHandSideAnalysis
        from problem.OXProblem import OXLPProblem
        
        # Create and configure your optimization problem
        problem = OXLPProblem()
        # ... set up variables, constraints, objective function with scenario data ...
        
        # Perform objective function analysis
        obj_analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
        obj_results = obj_analyzer.analyze()
        
        # Perform RHS constraint analysis
        rhs_analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
        rhs_results = rhs_analyzer.analyze()
        
        # Access analysis results
        print(f"Best scenario: {obj_results.best_scenario}")
        print(f"Critical constraints: {len(rhs_results.critical_constraints)}")
        print(f"Success rate: {obj_results.success_rate:.1%}")
"""

from .OXObjectiveFunctionAnalysis import OXObjectiveFunctionAnalysis, OXObjectiveFunctionAnalysisResult
from .OXRightHandSideAnalysis import OXRightHandSideAnalysis, OXRightHandSideAnalysisResult, OXConstraintRHSAnalysis

__all__ = [
    'OXObjectiveFunctionAnalysis',
    'OXObjectiveFunctionAnalysisResult',
    'OXRightHandSideAnalysis', 
    'OXRightHandSideAnalysisResult',
    'OXConstraintRHSAnalysis'
]