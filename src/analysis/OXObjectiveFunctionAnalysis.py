"""
Objective Function Analysis Module
==================================

This module provides comprehensive analysis tools for objective function behavior across
different scenarios in OptiX optimization problems. It leverages the built-in scenario
feature to perform systematic sensitivity analysis and comparative evaluation of objective
function values under varying parameter conditions.

The module implements statistical analysis, visualization capabilities, and performance
metrics to help users understand how changes in problem parameters affect the optimal
objective function values across different scenarios.

Key Features:
    - **Scenario-Based Analysis**: Automatic integration with OptiX scenario management
      for systematic objective function evaluation across parameter variations
    - **Statistical Metrics**: Comprehensive statistical analysis including mean, median,
      standard deviation, variance, and percentile calculations
    - **Sensitivity Analysis**: Identification of scenarios with highest and lowest
      objective function values to understand parameter sensitivity
    - **Comparative Analysis**: Side-by-side comparison of objective function values
      across all scenarios with detailed performance metrics
    - **Result Aggregation**: Structured data organization for easy integration with
      external analysis and visualization tools

Architecture:
    The OXObjectiveFunctionAnalysis class integrates directly with the OptiX solver factory
    and scenario management system to provide seamless analysis workflows. It automatically
    handles scenario discovery, problem solving, and result aggregation to deliver
    comprehensive objective function insights.

Example:
    Basic objective function analysis across scenarios:

    .. code-block:: python

        from analysis.OXObjectiveFunctionAnalysis import OXObjectiveFunctionAnalysis
        from problem.OXProblem import OXLPProblem
        from data.OXData import OXData
        
        # Create problem with scenario data
        problem = OXLPProblem()
        # ... set up variables, constraints ...
        
        # Create data with scenarios
        cost_data = OXData()
        cost_data.unit_cost = 10.0
        cost_data.create_scenario("High_Cost", unit_cost=15.0)
        cost_data.create_scenario("Low_Cost", unit_cost=8.0)
        problem.db.add_object(cost_data)
        
        # Create objective function using scenario data
        problem.create_objective_function([x, y], [cost_data.unit_cost, 5], "maximize")
        
        # Perform analysis
        analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
        results = analyzer.analyze()
        
        # Access results
        print(f"Best scenario: {results.best_scenario}")
        print(f"Worst scenario: {results.worst_scenario}")
        print(f"Average objective value: {results.statistics['mean']}")

Module Dependencies:
    - base: OptiX core exception handling and validation framework
    - problem: OptiX problem type definitions for LP and GP formulations
    - solvers: OptiX solver factory for multi-scenario optimization
    - data: OptiX data management and scenario support
    - statistics: Python standard library for statistical calculations
    - typing: Type annotations for enhanced code reliability
"""

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any

from base import OXObject, OXception
from problem.OXProblem import OXLPProblem, OXGPProblem
from solvers.OXSolverFactory import solve_all_scenarios
from solvers.OXSolverInterface import OXSolutionStatus


@dataclass
class OXObjectiveFunctionAnalysisResult(OXObject):
    """
    Comprehensive data structure containing objective function analysis results.
    
    This class encapsulates all analysis results from multi-scenario objective function
    evaluation, providing structured access to statistical metrics, scenario comparisons,
    and performance insights for systematic analysis and reporting.
    
    The result structure is designed to support both programmatic analysis and human-readable
    reporting, with detailed metadata and comprehensive statistical information for
    thorough objective function sensitivity analysis.
    
    Attributes:
        scenario_values (Dict[str, float]): Dictionary mapping scenario names to their
                                          corresponding optimal objective function values.
                                          Only includes scenarios that achieved optimal
                                          solutions for accurate statistical analysis.
                                          
        scenario_statuses (Dict[str, OXSolutionStatus]): Dictionary mapping scenario names
                                                        to their solution termination status.
                                                        Enables identification of scenarios
                                                        that failed to solve optimally.
                                                        
        statistics (Dict[str, float]): Comprehensive statistical analysis of objective
                                     function values across all optimal scenarios including:
                                     - mean: Average objective function value
                                     - median: Middle value when scenarios are sorted
                                     - std_dev: Standard deviation measuring variability
                                     - variance: Statistical variance of objective values
                                     - min: Minimum objective function value observed
                                     - max: Maximum objective function value observed
                                     - range: Difference between maximum and minimum values
                                     
        best_scenario (Optional[str]): Name of the scenario that achieved the best
                                     (highest for maximization, lowest for minimization)
                                     objective function value. None if no optimal solutions.
                                     
        worst_scenario (Optional[str]): Name of the scenario that achieved the worst
                                      (lowest for maximization, highest for minimization)
                                      objective function value. None if no optimal solutions.
                                      
        optimal_scenario_count (int): Number of scenarios that achieved optimal solutions.
                                    Important metric for understanding solution reliability
                                    across different parameter configurations.
                                    
        total_scenario_count (int): Total number of scenarios analyzed, including those
                                  that failed to solve optimally. Used for calculating
                                  success rates and identifying problematic scenarios.
                                  
        success_rate (float): Percentage of scenarios that achieved optimal solutions.
                            Calculated as (optimal_scenario_count / total_scenario_count).
                            High success rates indicate robust problem formulation.
                            
        objective_direction (str): Direction of optimization ("maximize" or "minimize")
                                 used to correctly identify best and worst scenarios.
                                 Automatically determined from problem configuration.
    
    Examples:
        >>> result = OXObjectiveFunctionAnalysisResult()
        >>> print(f"Success rate: {result.success_rate:.1%}")
        >>> print(f"Best scenario: {result.best_scenario} = {result.scenario_values[result.best_scenario]}")
        >>> print(f"Statistical summary: mean={result.statistics['mean']:.2f}, std={result.statistics['std_dev']:.2f}")
    """
    scenario_values: Dict[str, float] = field(default_factory=dict)
    scenario_statuses: Dict[str, OXSolutionStatus] = field(default_factory=dict)
    statistics: Dict[str, float] = field(default_factory=dict)
    best_scenario: Optional[str] = None
    worst_scenario: Optional[str] = None
    optimal_scenario_count: int = 0
    total_scenario_count: int = 0
    success_rate: float = 0.0
    objective_direction: str = "maximize"
    
    def get_scenario_ranking(self) -> List[tuple[str, float]]:
        """
        Get scenarios ranked by objective function value.
        
        Returns scenarios sorted by objective function value according to the optimization
        direction. For maximization problems, scenarios are sorted in descending order
        (best to worst). For minimization problems, scenarios are sorted in ascending
        order (best to worst).
        
        Returns:
            List[tuple[str, float]]: List of (scenario_name, objective_value) tuples
                                   sorted by performance. Only includes scenarios that
                                   achieved optimal solutions.
        
        Examples:
            >>> result = analyzer.analyze()
            >>> ranking = result.get_scenario_ranking()
            >>> for rank, (scenario, value) in enumerate(ranking, 1):
            ...     print(f"{rank}. {scenario}: {value:.2f}")
        """
        if not self.scenario_values:
            return []
        
        reverse_sort = (self.objective_direction == "maximize")
        return sorted(self.scenario_values.items(), key=lambda x: x[1], reverse=reverse_sort)
    
    def get_percentile(self, percentile: float) -> Optional[float]:
        """
        Calculate percentile value for objective function distribution.
        
        Args:
            percentile (float): Percentile value between 0 and 100.
        
        Returns:
            Optional[float]: Percentile value, or None if no optimal scenarios exist.
        
        Examples:
            >>> result = analyzer.analyze()
            >>> median = result.get_percentile(50)  # Same as statistics['median']
            >>> q75 = result.get_percentile(75)     # 75th percentile
        """
        if not self.scenario_values:
            return None
        
        values = list(self.scenario_values.values())
        return statistics.quantiles(values, n=100)[int(percentile) - 1] if len(values) > 1 else values[0]


class OXObjectiveFunctionAnalysis:
    """
    Comprehensive objective function analysis tool for multi-scenario optimization problems.
    
    This class provides systematic analysis of objective function behavior across different
    scenarios in OptiX optimization problems. It leverages the built-in scenario management
    system to automatically solve problems under various parameter configurations and
    provides detailed statistical analysis and comparative insights.
    
    The analyzer is designed to work seamlessly with linear programming (LP) and goal
    programming (GP) problems that have objective functions, automatically handling
    scenario discovery, problem solving, and result aggregation to deliver comprehensive
    objective function sensitivity analysis.
    
    Key Capabilities:
        - **Automatic Scenario Discovery**: Scans problem database to identify all available
          scenarios across data objects for comprehensive analysis coverage
        - **Multi-Scenario Solving**: Systematically solves the optimization problem under
          each scenario configuration using the specified solver
        - **Statistical Analysis**: Computes comprehensive statistics including central
          tendency, variability, and distribution metrics for objective function values
        - **Performance Ranking**: Identifies best and worst performing scenarios based
          on optimization direction (maximization or minimization)
        - **Success Rate Analysis**: Tracks solver success rates across scenarios to
          identify problematic parameter configurations
        - **Comparative Insights**: Provides structured comparison framework for evaluating
          parameter sensitivity and scenario impact on optimization outcomes
    
    Attributes:
        problem (Union[OXLPProblem, OXGPProblem]): The optimization problem instance to
                                                  analyze. Must have an objective function
                                                  and scenario-enabled data objects.
                                                  
        solver (str): Identifier of the solver to use for all scenario solving operations.
                     Must be available in the OptiX solver registry.
                     
        solver_kwargs (Dict[str, Any]): Additional parameters passed to the solver for
                                       each scenario solving operation. Enables custom
                                       solver configuration and performance tuning.
    
    Examples:
        Basic objective function analysis:
        
        .. code-block:: python
        
            from analysis.OXObjectiveFunctionAnalysis import OXObjectiveFunctionAnalysis
            
            # Create analyzer
            analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
            
            # Perform analysis
            results = analyzer.analyze()
            
            # Access comprehensive results
            print(f"Analyzed {results.total_scenario_count} scenarios")
            print(f"Success rate: {results.success_rate:.1%}")
            print(f"Best scenario: {results.best_scenario}")
            print(f"Objective value range: {results.statistics['min']:.2f} - {results.statistics['max']:.2f}")
        
        Advanced analysis with custom solver parameters:
        
        .. code-block:: python
        
            # Create analyzer with custom solver settings
            analyzer = OXObjectiveFunctionAnalysis(
                problem, 
                'Gurobi',
                maxTime=300,
                use_continuous=True
            )
            
            # Perform analysis
            results = analyzer.analyze()
            
            # Detailed scenario ranking
            ranking = results.get_scenario_ranking()
            print("Scenario Performance Ranking:")
            for rank, (scenario, value) in enumerate(ranking, 1):
                print(f"{rank:2d}. {scenario:20s}: {value:10.2f}")
            
            # Statistical insights
            stats = results.statistics
            print(f"\\nStatistical Summary:")
            print(f"Mean: {stats['mean']:.2f} ± {stats['std_dev']:.2f}")
            print(f"Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
            print(f"Coefficient of Variation: {stats['std_dev']/stats['mean']:.3f}")
    """
    
    def __init__(self, problem: Union[OXLPProblem, OXGPProblem], solver: str, **kwargs):
        """
        Initialize the objective function analyzer.
        
        Args:
            problem (Union[OXLPProblem, OXGPProblem]): The optimization problem to analyze.
                                                      Must have an objective function and
                                                      scenario-enabled data in the database.
                                                      
            solver (str): The solver identifier to use for scenario solving.
                         Must be available in the OptiX solver registry.
                         
            **kwargs: Additional keyword arguments passed to the solver for each
                     scenario solving operation. Enables custom solver configuration.
        
        Raises:
            OXception: If the problem doesn't have an objective function or if
                      the problem database is empty.
        
        Examples:
            >>> analyzer = OXObjectiveFunctionAnalysis(lp_problem, 'ORTools')
            >>> analyzer = OXObjectiveFunctionAnalysis(gp_problem, 'Gurobi', maxTime=600)
        """
        if not hasattr(problem, 'objective_function'):
            raise OXception("Problem must have an objective function for analysis")
        
        if len(problem.db) == 0:
            raise OXception("Problem database must contain data objects with scenarios")
        
        self.problem = problem
        self.solver = solver
        self.solver_kwargs = kwargs
    
    def analyze(self) -> OXObjectiveFunctionAnalysisResult:
        """
        Perform comprehensive objective function analysis across all scenarios.
        
        This method orchestrates the complete analysis workflow including scenario
        discovery, multi-scenario solving, statistical computation, and result
        aggregation to provide comprehensive objective function insights.
        
        Analysis Workflow:
            1. **Scenario Solving**: Uses solve_all_scenarios to solve the problem
               under each scenario configuration with the specified solver
            2. **Data Extraction**: Extracts objective function values from optimal
               solutions and tracks solution status for each scenario
            3. **Statistical Analysis**: Computes comprehensive statistics including
               central tendency, variability, and distribution metrics
            4. **Performance Ranking**: Identifies best and worst scenarios based
               on optimization direction (maximization or minimization)
            5. **Result Aggregation**: Organizes all analysis results into a
               structured OXObjectiveFunctionAnalysisResult for easy access
        
        Returns:
            OXObjectiveFunctionAnalysisResult: Comprehensive analysis results containing
                                           scenario values, statistical metrics,
                                           performance rankings, and success rates.
        
        Raises:
            OXception: If no scenarios are found or if all scenarios fail to solve.
        
        Examples:
            >>> analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
            >>> results = analyzer.analyze()
            >>> print(f"Best scenario: {results.best_scenario} = {results.scenario_values[results.best_scenario]:.2f}")
        """
        # Solve all scenarios
        scenario_results = solve_all_scenarios(self.problem, self.solver, **self.solver_kwargs)
        
        if not scenario_results:
            raise OXception("No scenarios found for analysis")
        
        # Initialize result object
        result = OXObjectiveFunctionAnalysisResult()
        result.total_scenario_count = len(scenario_results)
        
        # Determine optimization direction
        if hasattr(self.problem, 'objective_type'):
            result.objective_direction = self.problem.objective_type.value if hasattr(self.problem.objective_type, 'value') else str(self.problem.objective_type)
        else:
            result.objective_direction = "minimize"  # Default assumption
        
        # Extract objective function values from optimal solutions
        for scenario_name, scenario_result in scenario_results.items():
            status = scenario_result['status']
            solution = scenario_result['solution']
            
            result.scenario_statuses[scenario_name] = status
            
            if status in [OXSolutionStatus.OPTIMAL, OXSolutionStatus.FEASIBLE] and solution is not None:
                objective_value = solution.objective_function_value
                result.scenario_values[scenario_name] = objective_value
                result.optimal_scenario_count += 1
        
        # Calculate success rate
        result.success_rate = result.optimal_scenario_count / result.total_scenario_count if result.total_scenario_count > 0 else 0.0
        
        if not result.scenario_values:
            raise OXception("No scenarios achieved optimal solutions - cannot perform analysis")
        
        # Compute statistical metrics
        values = list(result.scenario_values.values())
        result.statistics = {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'variance': statistics.variance(values) if len(values) > 1 else 0.0
        }
        
        # Identify best and worst scenarios
        if result.objective_direction.lower() == "maximize":
            result.best_scenario = max(result.scenario_values.items(), key=lambda x: x[1])[0]
            result.worst_scenario = min(result.scenario_values.items(), key=lambda x: x[1])[0]
        else:  # minimize
            result.best_scenario = min(result.scenario_values.items(), key=lambda x: x[1])[0]
            result.worst_scenario = max(result.scenario_values.items(), key=lambda x: x[1])[0]
        
        return result
    
    def compare_scenarios(self, scenario_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Compare specific scenarios in detail.
        
        This method provides detailed comparison of specified scenarios including
        objective function values, solution status, and relative performance metrics
        for focused analysis of particular parameter configurations.
        
        Args:
            scenario_names (List[str]): List of scenario names to compare.
                                      Must be valid scenario names from the problem database.
        
        Returns:
            Dict[str, Dict[str, Any]]: Detailed comparison results for each scenario
                                     including objective values, status, and rankings.
        
        Raises:
            OXception: If any specified scenario name is not found in the analysis results.
        
        Examples:
            >>> analyzer = OXObjectiveFunctionAnalysis(problem, 'ORTools')
            >>> results = analyzer.analyze()
            >>> comparison = analyzer.compare_scenarios(['High_Demand', 'Low_Demand'])
            >>> for scenario, details in comparison.items():
            ...     print(f"{scenario}: {details['objective_value']:.2f} ({details['status']})")
        """
        # First perform full analysis to get all scenario results
        full_results = self.analyze()
        
        comparison = {}
        for scenario_name in scenario_names:
            if scenario_name not in full_results.scenario_statuses:
                raise OXception(f"Scenario '{scenario_name}' not found in analysis results")
            
            scenario_info = {
                'status': full_results.scenario_statuses[scenario_name],
                'objective_value': full_results.scenario_values.get(scenario_name),
                'rank': None,
                'percentile_rank': None
            }
            
            # Add ranking information if scenario has optimal solution
            if scenario_name in full_results.scenario_values:
                ranking = full_results.get_scenario_ranking()
                for rank, (name, value) in enumerate(ranking, 1):
                    if name == scenario_name:
                        scenario_info['rank'] = rank
                        scenario_info['percentile_rank'] = (rank / len(ranking)) * 100
                        break
            
            comparison[scenario_name] = scenario_info
        
        return comparison