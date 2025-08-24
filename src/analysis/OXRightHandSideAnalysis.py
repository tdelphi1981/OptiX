"""
Right Hand Side Analysis Module
===============================

This module provides comprehensive analysis tools for Right Hand Side (RHS) values of
constraints across different scenarios in OptiX optimization problems. It leverages
UUID-based constraint access and the enhanced scenario management system that supports
both data object scenarios and constraint-specific scenarios for systematic sensitivity
analysis on constraint bounds and their impact on optimization outcomes.

The module implements detailed constraint-level analysis, tracking how changes in RHS
values across scenarios affect solution feasibility, shadow prices, and binding status
of constraints in the optimization model. With the addition of constraint scenarios,
it enables more precise RHS sensitivity analysis by allowing constraints to have their
own scenario-specific parameters independent of data objects.

Key Features:
    - **UUID-Based Constraint Analysis**: Direct constraint access using OptiX's UUID
      system for precise constraint identification and tracking across scenarios
    - **Dual Scenario Support**: Comprehensive analysis across both data object scenarios
      and constraint-specific scenarios, enabling fine-grained RHS sensitivity analysis
    - **Constraint-Level Scenarios**: Direct support for constraint scenarios allowing
      RHS values, operators, and names to vary independently across scenarios
    - **Automatic Scenario Discovery**: Intelligent discovery of all unique scenarios
      from both data objects and constraints for comprehensive analysis coverage
    - **Constraint Sensitivity Analysis**: Identification of constraints with highest
      sensitivity to RHS changes and their effect on objective function values
    - **Binding Status Analysis**: Tracking of constraint binding status changes across
      scenarios to identify critical constraints and bottlenecks
    - **Shadow Price Integration**: Analysis of constraint shadow prices across scenarios
      to understand marginal value of relaxing constraints
    - **Feasibility Impact Analysis**: Assessment of how RHS changes affect problem
      feasibility and solution existence across scenarios

Architecture:
    The OXRightHandSideAnalysis class integrates directly with OptiX's constraint system
    and scenario management to provide seamless analysis workflows. It uses UUID-based
    constraint access to maintain constraint identity across scenarios and provides
    detailed tracking of RHS value changes and their optimization impacts.

Example:
    RHS analysis with constraint scenarios:

    .. code-block:: python

        from analysis.OXRightHandSideAnalysis import OXRightHandSideAnalysis
        from problem.OXProblem import OXLPProblem
        from data.OXData import OXData
        
        # Create problem
        problem = OXLPProblem()
        # ... set up variables ...
        
        # Method 1: Data-driven scenarios (traditional approach)
        capacity_data = OXData()
        capacity_data.max_capacity = 100
        capacity_data.create_scenario("Expanded", max_capacity=150)
        capacity_data.create_scenario("Reduced", max_capacity=80)
        problem.db.add_object(capacity_data)
        
        # Create constraint with data-dependent RHS
        constraint1 = problem.create_constraint([x, y], [1, 1], "<=", capacity_data.max_capacity)
        
        # Method 2: Constraint-specific scenarios (enhanced approach)
        constraint2 = problem.create_constraint([x, y], [2, 3], "<=", 200)
        constraint2.create_scenario("High_Capacity", rhs=250, name="Peak capacity")
        constraint2.create_scenario("Low_Capacity", rhs=150, name="Off-peak capacity")
        constraint2.create_scenario("Emergency", rhs=300, name="Emergency capacity")
        
        # Perform RHS analysis (analyzes both data and constraint scenarios)
        analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
        results = analyzer.analyze()
        
        # Access constraint-specific results
        for constraint_id, analysis in results.constraint_analyses.items():
            print(f"Constraint: {analysis.constraint_name}")
            print(f"  RHS values: {analysis.rhs_values}")
            print(f"  Binding scenarios: {analysis.binding_scenarios}")
            print(f"  Sensitivity score: {analysis.sensitivity_score:.3f}")

Module Dependencies:
    - base: OptiX core exception handling and validation framework
    - problem: OptiX problem type definitions for LP and GP formulations
    - solvers: OptiX solver factory for multi-scenario optimization
    - constraints: OptiX constraint system with UUID-based access
    - data: OptiX data management and scenario support
    - statistics: Python standard library for statistical calculations
    - typing: Type annotations for enhanced code reliability
"""

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Set
from uuid import UUID

from base import OXObject, OXception
from constraints.OXConstraint import OXConstraint, RelationalOperators
from problem.OXProblem import OXLPProblem, OXGPProblem, OXCSPProblem
from solvers.OXSolverFactory import solve
from solvers.OXSolverInterface import OXSolutionStatus


@dataclass
class OXConstraintRHSAnalysis(OXObject):
    """
    Analysis results for a specific constraint's RHS behavior across scenarios.
    
    This class encapsulates detailed analysis of how a single constraint's right-hand
    side values change across scenarios and the resulting impact on optimization
    outcomes, binding status, and shadow prices.
    
    Attributes:
        constraint_id (UUID): Unique identifier of the analyzed constraint.
        constraint_name (str): Human-readable name of the constraint for reporting.
        rhs_values (Dict[str, float]): Dictionary mapping scenario names to their
                                     corresponding RHS values for this constraint.
        binding_scenarios (List[str]): List of scenario names where this constraint
                                     is binding (active) at the optimal solution.
        shadow_prices (Dict[str, float]): Dictionary mapping scenario names to the
                                        shadow price (dual value) of this constraint.
        slack_values (Dict[str, float]): Dictionary mapping scenario names to the
                                       slack value of this constraint at optimum.
        rhs_range (Dict[str, float]): Statistical summary of RHS values including
                                    min, max, mean, and standard deviation.
        sensitivity_score (float): Numerical measure of how sensitive the objective
                                 function is to changes in this constraint's RHS.
        constraint_type (str): The relational operator type (<=, >=, =) for context.
    """
    constraint_id: UUID = field(default_factory=lambda: UUID('00000000-0000-0000-0000-000000000000'))
    constraint_name: str = ""
    rhs_values: Dict[str, float] = field(default_factory=dict)
    binding_scenarios: List[str] = field(default_factory=list)
    shadow_prices: Dict[str, float] = field(default_factory=dict)
    slack_values: Dict[str, float] = field(default_factory=dict)
    rhs_range: Dict[str, float] = field(default_factory=dict)
    sensitivity_score: float = 0.0
    constraint_type: str = ""
    
    def get_rhs_statistics(self) -> Dict[str, float]:
        """
        Calculate comprehensive statistics for RHS values across scenarios.
        
        Returns:
            Dict[str, float]: Statistical metrics including mean, median, std_dev,
                            min, max, range, and coefficient of variation.
        """
        if not self.rhs_values:
            return {}
        
        values = list(self.rhs_values.values())
        stats = {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'variance': statistics.variance(values) if len(values) > 1 else 0.0
        }
        
        # Add coefficient of variation if mean is non-zero
        if stats['mean'] != 0:
            stats['coefficient_of_variation'] = stats['std_dev'] / abs(stats['mean'])
        else:
            stats['coefficient_of_variation'] = 0.0
            
        return stats
    
    def is_critical_constraint(self, binding_threshold: float = 0.5) -> bool:
        """
        Determine if this constraint is critical based on binding frequency.
        
        Args:
            binding_threshold (float): Minimum fraction of scenarios where constraint
                                     must be binding to be considered critical.
        
        Returns:
            bool: True if constraint is binding in more than binding_threshold
                 fraction of scenarios.
        """
        if not self.rhs_values or not self.binding_scenarios:
            return False
        
        binding_rate = len(self.binding_scenarios) / len(self.rhs_values)
        return binding_rate >= binding_threshold


@dataclass
class OXRightHandSideAnalysisResult(OXObject):
    """
    Comprehensive data structure containing Right Hand Side analysis results.
    
    This class encapsulates all analysis results from multi-scenario RHS evaluation,
    providing structured access to constraint-level analysis, scenario comparisons,
    and system-wide RHS sensitivity insights for optimization model analysis.
    
    Attributes:
        constraint_analyses (Dict[UUID, OXConstraintRHSAnalysis]): Dictionary mapping
                                                                  constraint UUIDs to their detailed RHS analysis results.
        scenario_feasibility (Dict[str, bool]): Dictionary mapping scenario names to
                                               their feasibility status across all constraints.
        scenario_objective_values (Dict[str, float]): Dictionary mapping scenario names
                                                     to optimal objective function values.
        critical_constraints (List[UUID]): List of constraint UUIDs identified as
                                          critical based on binding frequency analysis.
        most_sensitive_constraints (List[UUID]): List of constraint UUIDs with highest
                                                sensitivity scores for RHS changes.
        rhs_sensitivity_summary (Dict[str, float]): System-wide RHS sensitivity metrics
                                                   including average sensitivity and variability.
        scenario_count (int): Total number of scenarios analyzed in the study.
        feasible_scenario_count (int): Number of scenarios that yielded feasible solutions.
        success_rate (float): Percentage of scenarios with optimal solutions.
    """
    constraint_analyses: Dict[UUID, OXConstraintRHSAnalysis] = field(default_factory=dict)
    scenario_feasibility: Dict[str, bool] = field(default_factory=dict)
    scenario_objective_values: Dict[str, float] = field(default_factory=dict)
    critical_constraints: List[UUID] = field(default_factory=list)
    most_sensitive_constraints: List[UUID] = field(default_factory=list)
    rhs_sensitivity_summary: Dict[str, float] = field(default_factory=dict)
    scenario_count: int = 0
    feasible_scenario_count: int = 0
    success_rate: float = 0.0
    
    def get_constraint_analysis(self, constraint_id: UUID) -> Optional[OXConstraintRHSAnalysis]:
        """
        Retrieve detailed analysis for a specific constraint.
        
        Args:
            constraint_id (UUID): Unique identifier of the constraint.
        
        Returns:
            Optional[OXConstraintRHSAnalysis]: Detailed constraint analysis or None
                                             if constraint ID not found.
        """
        return self.constraint_analyses.get(constraint_id)
    
    def get_top_sensitive_constraints(self, top_n: int = 5) -> List[OXConstraintRHSAnalysis]:
        """
        Get the most sensitive constraints ranked by sensitivity score.
        
        Args:
            top_n (int): Number of top constraints to return.
        
        Returns:
            List[OXConstraintRHSAnalysis]: List of constraint analyses sorted by
                                         sensitivity score in descending order.
        """
        analyses = list(self.constraint_analyses.values())
        analyses.sort(key=lambda x: x.sensitivity_score, reverse=True)
        return analyses[:top_n]
    
    def get_constraints_by_binding_frequency(self, min_frequency: float = 0.3) -> List[OXConstraintRHSAnalysis]:
        """
        Get constraints that are binding in at least min_frequency of scenarios.
        
        Args:
            min_frequency (float): Minimum binding frequency (0.0 to 1.0).
        
        Returns:
            List[OXConstraintRHSAnalysis]: List of constraints meeting binding criteria.
        """
        result = []
        for analysis in self.constraint_analyses.values():
            if analysis.rhs_values and analysis.binding_scenarios:
                binding_rate = len(analysis.binding_scenarios) / len(analysis.rhs_values)
                if binding_rate >= min_frequency:
                    result.append(analysis)
        
        # Sort by binding frequency (highest first)
        result.sort(key=lambda x: len(x.binding_scenarios) / len(x.rhs_values), reverse=True)
        return result


class OXRightHandSideAnalysis:
    """
    Comprehensive Right Hand Side analysis tool for multi-scenario optimization problems.
    
    This class provides systematic analysis of constraint RHS values across different
    scenarios in OptiX optimization problems. It uses UUID-based constraint access
    to track individual constraints across scenarios and provides detailed insights
    into RHS sensitivity, binding status, and optimization impact analysis.
    
    The analyzer supports both data object scenarios and constraint-specific scenarios,
    enabling more precise RHS analysis. It automatically discovers all scenarios from
    both sources, tracks RHS values that may come from constraint scenarios or data
    scenarios, solves the optimization problem for each unique scenario configuration,
    and provides comprehensive analysis of constraint behavior and sensitivity to RHS changes.
    
    Key Capabilities:
        - **UUID-Based Constraint Tracking**: Uses OptiX's UUID system for precise
          constraint identification and analysis across scenario variations
        - **RHS Value Extraction**: Automatically extracts RHS values from constraints
          for each scenario, handling scenario data integration seamlessly
        - **Binding Status Analysis**: Identifies which constraints are binding (active)
          in each scenario's optimal solution for bottleneck analysis
        - **Shadow Price Analysis**: Extracts and analyzes shadow prices (dual values)
          to understand marginal value of constraint relaxation
        - **Sensitivity Scoring**: Computes numerical sensitivity scores to quantify
          impact of RHS changes on objective function values
        - **Critical Constraint Identification**: Identifies constraints that are
          consistently binding across scenarios as potential system bottlenecks
    
    Attributes:
        problem (Union[OXLPProblem, OXGPProblem, OXCSPProblem]): The optimization problem
                                                               to analyze with constraints and scenario data.
        solver (str): Identifier of the solver to use for all scenario solving operations.
        solver_kwargs (Dict[str, Any]): Additional parameters for solver configuration.
        target_constraints (Optional[Set[UUID]]): Specific constraint UUIDs to analyze.
                                                 If None, analyzes all constraints.
    
    Examples:
        Basic RHS analysis across all constraints:
        
        .. code-block:: python
        
            from analysis.OXRightHandSideAnalysis import OXRightHandSideAnalysis
            
            # Create analyzer
            analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
            
            # Perform comprehensive RHS analysis
            results = analyzer.analyze()
            
            # Access results
            print(f"Analyzed {len(results.constraint_analyses)} constraints")
            print(f"Critical constraints: {len(results.critical_constraints)}")
            
            # Examine most sensitive constraint
            top_sensitive = results.get_top_sensitive_constraints(1)[0]
            print(f"Most sensitive: {top_sensitive.constraint_name}")
            print(f"Sensitivity score: {top_sensitive.sensitivity_score:.3f}")
        
        Analysis with constraint-specific scenarios:
        
        .. code-block:: python
        
            # Create constraints with their own scenarios
            capacity_constraint = problem.create_constraint([x, y], [1, 1], "<=", 100)
            capacity_constraint.create_scenario("Peak_Hours", rhs=150, name="Peak capacity")
            capacity_constraint.create_scenario("Off_Peak", rhs=80, name="Off-peak capacity")
            capacity_constraint.create_scenario("Maintenance", rhs=50, name="Maintenance mode")
            
            budget_constraint = problem.create_constraint([x, y], [5, 10], "<=", 1000)
            budget_constraint.create_scenario("High_Budget", rhs=1500)
            budget_constraint.create_scenario("Low_Budget", rhs=800)
            
            # Analyze all constraint scenarios
            analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
            results = analyzer.analyze()
            
            # Results will include all unique scenarios from constraints
            print(f"Total scenarios analyzed: {results.scenario_count}")
            print(f"Scenarios: {list(results.scenario_feasibility.keys())}")
            
            # Constraint-specific analysis
            cap_analysis = results.get_constraint_analysis(capacity_constraint.id)
            print(f"\\nCapacity constraint RHS values:")
            for scenario, rhs in cap_analysis.rhs_values.items():
                print(f"  {scenario}: {rhs}")
        
        Targeted analysis of specific constraints:
        
        .. code-block:: python
        
            # Analyze only capacity constraints
            capacity_constraint_ids = {constraint.id for constraint in problem.constraints 
                                     if 'capacity' in constraint.name.lower()}
            
            analyzer = OXRightHandSideAnalysis(
                problem, 
                'Gurobi',
                target_constraints=capacity_constraint_ids,
                maxTime=300
            )
            
            results = analyzer.analyze()
            
            # Detailed constraint-level analysis
            for constraint_id in capacity_constraint_ids:
                analysis = results.get_constraint_analysis(constraint_id)
                stats = analysis.get_rhs_statistics()
                print(f"\\nConstraint: {analysis.constraint_name}")
                print(f"RHS Range: [{stats['min']:.1f}, {stats['max']:.1f}]")
                print(f"Binding Rate: {len(analysis.binding_scenarios)/len(analysis.rhs_values):.1%}")
                print(f"Sensitivity: {analysis.sensitivity_score:.3f}")
    """
    
    def __init__(self, problem: Union[OXLPProblem, OXGPProblem, OXCSPProblem], solver: str, 
                 target_constraints: Optional[Set[UUID]] = None, **kwargs):
        """
        Initialize the Right Hand Side analyzer.
        
        Args:
            problem (Union[OXLPProblem, OXGPProblem, OXCSPProblem]): The optimization problem
                                                                   to analyze with constraints and scenario data.
            solver (str): The solver identifier to use for scenario solving.
            target_constraints (Optional[Set[UUID]]): Specific constraint UUIDs to analyze.
                                                     If None, analyzes all constraints in the problem.
            **kwargs: Additional keyword arguments passed to the solver for scenario solving.
        
        Raises:
            OXception: If the problem has no constraints or if the problem database is empty.
        
        Examples:
            >>> analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
            >>> analyzer = OXRightHandSideAnalysis(problem, 'Gurobi', target_constraints={constraint.id}, maxTime=600)
        """
        if len(problem.constraints) == 0:
            raise OXception("Problem must have constraints for RHS analysis")
        
        self.problem = problem
        self.solver = solver
        self.solver_kwargs = kwargs
        self.target_constraints = target_constraints
    
    def _extract_rhs_values_for_constraint(self, constraint: OXConstraint, scenario_name: str) -> float:
        """
        Extract RHS value for a constraint in a specific scenario.
        
        This method handles the complexity of extracting RHS values from both constraint-level
        scenarios and data object scenarios in the problem database. It prioritizes constraint
        scenarios over data scenarios for more precise analysis.
        
        Args:
            constraint (OXConstraint): The constraint to analyze.
            scenario_name (str): The scenario name to extract RHS value for.
        
        Returns:
            float: The RHS value for the constraint in the given scenario.
        """
        # Store original scenario states for both constraint and data objects
        original_constraint_scenario = constraint.active_scenario
        original_data_scenarios = {}
        for data_obj in self.problem.db:
            original_data_scenarios[data_obj.id] = data_obj.active_scenario
        
        try:
            # First, check if constraint has this scenario
            if scenario_name in constraint.scenarios:
                constraint.active_scenario = scenario_name
            else:
                constraint.active_scenario = "Default"
            
            # Set all data objects to the target scenario
            for data_obj in self.problem.db:
                if scenario_name in data_obj.scenarios:
                    data_obj.active_scenario = scenario_name
                else:
                    data_obj.active_scenario = "Default"
            
            # Extract RHS value (may depend on both constraint and data scenarios)
            rhs_value = constraint.rhs
            
            return float(rhs_value)
            
        finally:
            # Restore original scenario states
            constraint.active_scenario = original_constraint_scenario
            for data_obj in self.problem.db:
                if data_obj.id in original_data_scenarios:
                    data_obj.active_scenario = original_data_scenarios[data_obj.id]
    
    def _discover_all_scenarios(self) -> Set[str]:
        """
        Discover all unique scenarios across data objects and constraints.
        
        This method scans both the problem database and all constraints to find
        all unique scenario names, enabling comprehensive analysis that includes
        both data-driven and constraint-specific scenarios.
        
        Returns:
            Set[str]: Set of all unique scenario names found.
        """
        all_scenarios = set()
        
        # Discover scenarios from data objects
        for data_obj in self.problem.db:
            all_scenarios.update(data_obj.scenarios.keys())
        
        # Discover scenarios from constraints
        for constraint in self.problem.constraints:
            all_scenarios.update(constraint.scenarios.keys())
        
        return all_scenarios
    
    def _solve_all_scenarios_with_constraints(self) -> Dict[str, dict]:
        """
        Solve the problem for all scenarios, including constraint-specific scenarios.
        
        This method extends the standard solve_all_scenarios functionality to properly
        handle constraint scenarios by synchronizing both data objects and constraints
        to their respective scenario states before solving.
        
        Returns:
            Dict[str, dict]: Dictionary mapping scenario names to solving results.
        """
        # Discover all unique scenarios (data + constraints)
        all_scenarios = self._discover_all_scenarios()
        
        if len(all_scenarios) == 0:
            raise OXception("No scenarios found in data objects or constraints")
        
        # Store original active scenarios for restoration
        original_data_scenarios = {}
        for data_obj in self.problem.db:
            original_data_scenarios[data_obj.id] = data_obj.active_scenario
        
        original_constraint_scenarios = {}
        for constraint in self.problem.constraints:
            original_constraint_scenarios[constraint.id] = constraint.active_scenario
        
        # Solve for each scenario
        scenario_results = {}
        
        try:
            for scenario_name in sorted(all_scenarios):
                # Set all data objects to the current scenario
                for data_obj in self.problem.db:
                    if scenario_name in data_obj.scenarios:
                        data_obj.active_scenario = scenario_name
                    else:
                        data_obj.active_scenario = "Default"
                
                # Set all constraints to the current scenario
                for constraint in self.problem.constraints:
                    if scenario_name in constraint.scenarios:
                        constraint.active_scenario = scenario_name
                    else:
                        constraint.active_scenario = "Default"
                
                # Solve the problem with current scenario configuration
                try:
                    status, solver_obj = solve(self.problem, self.solver, **self.solver_kwargs)
                    # Get first solution if multiple exist
                    solution = None
                    for sol in solver_obj:
                        solution = sol
                        break
                    scenario_results[scenario_name] = {
                        'status': status,
                        'solution': solution
                    }
                except Exception:
                    # Capture individual scenario errors without stopping the process
                    scenario_results[scenario_name] = {
                        'status': OXSolutionStatus.ERROR,
                        'solution': None
                    }
                    
        finally:
            # Restore original active scenarios for data objects
            for data_obj in self.problem.db:
                if data_obj.id in original_data_scenarios:
                    data_obj.active_scenario = original_data_scenarios[data_obj.id]
            
            # Restore original active scenarios for constraints
            for constraint in self.problem.constraints:
                if constraint.id in original_constraint_scenarios:
                    constraint.active_scenario = original_constraint_scenarios[constraint.id]
        
        return scenario_results
    
    def _calculate_constraint_sensitivity(self, constraint_analysis: OXConstraintRHSAnalysis, 
                                        scenario_objectives: Dict[str, float]) -> float:
        """
        Calculate sensitivity score for a constraint based on RHS and objective changes.
        
        Args:
            constraint_analysis (OXConstraintRHSAnalysis): Constraint analysis with RHS values.
            scenario_objectives (Dict[str, float]): Objective function values by scenario.
        
        Returns:
            float: Sensitivity score indicating impact of RHS changes on objective.
        """
        if len(constraint_analysis.rhs_values) < 2:
            return 0.0
        
        # Find scenarios with both RHS and objective data
        common_scenarios = set(constraint_analysis.rhs_values.keys()) & set(scenario_objectives.keys())
        if len(common_scenarios) < 2:
            return 0.0
        
        # Calculate correlation between RHS changes and objective changes
        rhs_values = [constraint_analysis.rhs_values[scenario] for scenario in common_scenarios]
        obj_values = [scenario_objectives[scenario] for scenario in common_scenarios]
        
        # Simple sensitivity: range of objective / range of RHS
        rhs_range = max(rhs_values) - min(rhs_values)
        obj_range = max(obj_values) - min(obj_values)
        
        if rhs_range == 0:
            return 0.0
        
        return abs(obj_range / rhs_range)
    
    def analyze(self) -> OXRightHandSideAnalysisResult:
        """
        Perform comprehensive Right Hand Side analysis across all scenarios.
        
        This method orchestrates the complete RHS analysis workflow including scenario
        discovery, multi-scenario solving, constraint RHS extraction, binding status
        analysis, and sensitivity calculation to provide comprehensive RHS insights.
        
        Analysis Workflow:
            1. **Scenario Solving**: Uses solve_all_scenarios to solve the problem
               under each scenario configuration with the specified solver
            2. **Constraint Discovery**: Identifies target constraints for analysis
               based on constructor parameters and problem structure
            3. **RHS Extraction**: Extracts RHS values for each constraint across
               all scenarios, handling scenario data dependencies
            4. **Binding Analysis**: Analyzes constraint solutions to identify
               binding status and slack values for each scenario
            5. **Sensitivity Calculation**: Computes sensitivity scores based on
               correlation between RHS changes and objective function changes
            6. **Result Aggregation**: Organizes all analysis results into structured
               format for easy access and reporting
        
        Returns:
            OXRightHandSideAnalysisResult: Comprehensive RHS analysis results containing
                                         constraint-level analysis, sensitivity metrics,
                                         and system-wide RHS insights.
        
        Raises:
            OXception: If no scenarios are found or if all scenarios fail to solve.
        
        Examples:
            >>> analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
            >>> results = analyzer.analyze()
            >>> print(f"Most sensitive constraint: {results.get_top_sensitive_constraints(1)[0].constraint_name}")
        """
        # Solve all scenarios including constraint-specific scenarios
        scenario_results = self._solve_all_scenarios_with_constraints()
        
        if not scenario_results:
            raise OXception("No scenarios found for RHS analysis")
        
        # Initialize result object
        result = OXRightHandSideAnalysisResult()
        result.scenario_count = len(scenario_results)
        
        # Determine target constraints
        if self.target_constraints:
            target_constraint_ids = self.target_constraints
        else:
            target_constraint_ids = {constraint.id for constraint in self.problem.constraints}
        
        # Extract scenario results and feasibility
        for scenario_name, scenario_result in scenario_results.items():
            status = scenario_result['status']
            solution = scenario_result['solution']
            
            result.scenario_feasibility[scenario_name] = (status == OXSolutionStatus.OPTIMAL)
            
            if status == OXSolutionStatus.OPTIMAL and solution is not None:
                result.scenario_objective_values[scenario_name] = solution.objective_function_value
                result.feasible_scenario_count += 1
        
        # Calculate success rate
        result.success_rate = result.feasible_scenario_count / result.scenario_count if result.scenario_count > 0 else 0.0
        
        # Analyze each target constraint
        for constraint in self.problem.constraints:
            if constraint.id not in target_constraint_ids:
                continue
            
            # Initialize constraint analysis
            constraint_analysis = OXConstraintRHSAnalysis()
            constraint_analysis.constraint_id = constraint.id
            constraint_analysis.constraint_name = constraint.name or f"Constraint_{constraint.id}"
            constraint_analysis.constraint_type = constraint.relational_operator.value
            
            # Extract RHS values across scenarios
            scenario_names = list(scenario_results.keys())
            for scenario_name in scenario_names:
                try:
                    rhs_value = self._extract_rhs_values_for_constraint(constraint, scenario_name)
                    constraint_analysis.rhs_values[scenario_name] = rhs_value
                except Exception:
                    # Skip scenarios where RHS extraction fails
                    continue
            
            # Analyze binding status and slack values from solutions
            for scenario_name, scenario_result in scenario_results.items():
                if scenario_result['status'] == OXSolutionStatus.OPTIMAL and scenario_result['solution'] is not None:
                    solution = scenario_result['solution']
                    
                    # Check if constraint is in solution constraint values
                    if constraint.id in solution.constraint_values:
                        lhs, operator, rhs = solution.constraint_values[constraint.id]
                        
                        # Calculate slack value
                        if constraint.relational_operator == RelationalOperators.LESS_THAN_EQUAL:
                            slack = rhs - lhs
                        elif constraint.relational_operator == RelationalOperators.GREATER_THAN_EQUAL:
                            slack = lhs - rhs
                        else:  # EQUAL
                            slack = abs(lhs - rhs)
                        
                        constraint_analysis.slack_values[scenario_name] = slack
                        
                        # Determine if constraint is binding (slack near zero)
                        if abs(slack) < 1e-6:  # Tolerance for binding detection
                            constraint_analysis.binding_scenarios.append(scenario_name)
            
            # Calculate sensitivity score
            constraint_analysis.sensitivity_score = self._calculate_constraint_sensitivity(
                constraint_analysis, result.scenario_objective_values
            )
            
            # Calculate RHS statistics
            constraint_analysis.rhs_range = constraint_analysis.get_rhs_statistics()
            
            # Store constraint analysis
            result.constraint_analyses[constraint.id] = constraint_analysis
        
        # Identify critical constraints (binding in >50% of scenarios)
        result.critical_constraints = [
            constraint_id for constraint_id, analysis in result.constraint_analyses.items()
            if analysis.is_critical_constraint(0.5)
        ]
        
        # Identify most sensitive constraints (top 25% by sensitivity score)
        if result.constraint_analyses:
            sensitivity_scores = [analysis.sensitivity_score for analysis in result.constraint_analyses.values()]
            if sensitivity_scores:
                sensitivity_threshold = statistics.quantiles(sensitivity_scores, n=4)[2]  # 75th percentile
                result.most_sensitive_constraints = [
                    constraint_id for constraint_id, analysis in result.constraint_analyses.items()
                    if analysis.sensitivity_score >= sensitivity_threshold
                ]
        
        # Calculate system-wide RHS sensitivity summary
        if result.constraint_analyses:
            all_sensitivities = [analysis.sensitivity_score for analysis in result.constraint_analyses.values()]
            result.rhs_sensitivity_summary = {
                'mean_sensitivity': statistics.mean(all_sensitivities),
                'max_sensitivity': max(all_sensitivities),
                'min_sensitivity': min(all_sensitivities),
                'std_sensitivity': statistics.stdev(all_sensitivities) if len(all_sensitivities) > 1 else 0.0
            }
        
        return result
    
    def analyze_constraint_subset(self, constraint_ids: Set[UUID]) -> Dict[UUID, OXConstraintRHSAnalysis]:
        """
        Analyze a specific subset of constraints for focused RHS analysis.
        
        This method provides targeted analysis of specific constraints, useful for
        analyzing particular constraint categories or investigating specific bottlenecks.
        
        Args:
            constraint_ids (Set[UUID]): Set of constraint UUIDs to analyze.
        
        Returns:
            Dict[UUID, OXConstraintRHSAnalysis]: Dictionary mapping constraint UUIDs
                                               to their detailed RHS analysis results.
        
        Raises:
            OXception: If any specified constraint ID is not found in the problem.
        
        Examples:
            >>> # Analyze only capacity constraints
            >>> capacity_ids = {c.id for c in problem.constraints if 'capacity' in c.name}
            >>> analyzer = OXRightHandSideAnalysis(problem, 'ORTools')
            >>> capacity_analysis = analyzer.analyze_constraint_subset(capacity_ids)
            >>> for constraint_id, analysis in capacity_analysis.items():
            ...     print(f"{analysis.constraint_name}: sensitivity = {analysis.sensitivity_score:.3f}")
        """
        # Validate constraint IDs exist
        problem_constraint_ids = {constraint.id for constraint in self.problem.constraints}
        invalid_ids = constraint_ids - problem_constraint_ids
        if invalid_ids:
            raise OXception(f"Constraint IDs not found in problem: {invalid_ids}")
        
        # Temporarily set target constraints
        original_target = self.target_constraints
        self.target_constraints = constraint_ids
        
        try:
            # Perform full analysis with subset
            full_results = self.analyze()
            return full_results.constraint_analyses
        finally:
            # Restore original target constraints
            self.target_constraints = original_target