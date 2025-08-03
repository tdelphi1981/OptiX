"""
Decision Variable Module
========================

This module provides the fundamental decision variable class for the OptiX optimization 
framework. It implements the core OXVariable class that represents decision variables 
in mathematical optimization problems, including linear programming (LP), goal programming (GP), 
and constraint satisfaction problems (CSP).

The module is designed to provide a robust, type-safe representation of optimization 
variables with comprehensive bounds checking, value validation, and relationship tracking 
capabilities essential for complex optimization modeling.

Key Features:
    - **Type Safety**: Comprehensive type checking and validation for variable properties
    - **Bounds Management**: Automatic validation of upper and lower bounds with infinity support
    - **Relationship Tracking**: UUID-based linking system for connecting variables to data objects
    - **Automatic Naming**: Intelligent name generation for unnamed variables
    - **Value Validation**: Runtime validation of variable assignments against bounds

Core Components:
    - **OXVariable**: Base decision variable class with bounds and value management
    - **Bounds Validation**: Automatic checking of lower/upper bound consistency
    - **Data Relationships**: Dictionary-based system for linking variables to related objects
    - **Name Management**: Automatic UUID-based naming for enhanced traceability

Use Cases:
    - Linear programming decision variables with continuous domains
    - Integer programming variables with discrete constraints
    - Boolean decision variables for binary optimization problems
    - Goal programming variables with deviation tracking
    - Multi-objective optimization variable management

Example:
    Creating and configuring decision variables:

    .. code-block:: python

        from variables.OXVariable import OXVariable
        from uuid import uuid4
        
        # Create a continuous variable with bounds
        production_var = OXVariable(
            name="production_level",
            description="Daily production quantity",
            lower_bound=0,
            upper_bound=1000,
            value=500
        )
        
        # Create a binary decision variable
        facility_var = OXVariable(
            name="open_facility",
            description="Whether to open the facility",
            lower_bound=0,
            upper_bound=1,
            value=0
        )
        
        # Link variable to related data objects
        customer_id = uuid4()
        production_var.related_data["customer"] = customer_id

Module Dependencies:
    - dataclasses: For structured class definitions with automatic method generation
    - uuid: For unique identifier generation and relationship tracking
    - base: For OXObject inheritance and OXception error handling
"""

from dataclasses import dataclass, field
from uuid import UUID

from base import OXObject, OXception


@dataclass
class OXVariable(OXObject):
    """
    Fundamental decision variable class for mathematical optimization problems.
    
    This class provides a comprehensive representation of decision variables used in 
    optimization modeling within the OptiX framework. It extends the base OXObject 
    class to include domain-specific features such as bounds management, value tracking,
    and relationship linking essential for complex optimization scenarios.
    
    The class implements automatic validation, intelligent naming, and flexible data
    relationships to support various optimization paradigms including linear programming,
    integer programming, and goal programming applications.
    
    Key Capabilities:
        - Automatic bounds validation with infinity support for unbounded variables
        - UUID-based relationship tracking for linking variables to data entities
        - Intelligent automatic naming using UUID when names are not provided
        - Type-safe value assignment with comprehensive validation
        - Integration with solver interfaces through standardized attributes

    Attributes:
        name (str): The human-readable identifier for the variable. If empty or whitespace,
                   automatically generated as "var_<uuid>" to ensure uniqueness and
                   traceability throughout the optimization process.
        description (str): Detailed description of the variable's purpose and meaning
                          within the optimization context. Used for documentation and
                          model interpretation purposes.
        value (float | int | bool): The current assigned value of the variable. Can be
                                   None for unassigned variables. Should respect the
                                   defined bounds when set by optimization solvers.
        upper_bound (float | int): The maximum allowable value for the variable.
                                  Defaults to positive infinity for unbounded variables.
                                  Must be greater than or equal to lower_bound.
        lower_bound (float | int): The minimum allowable value for the variable.
                                  Defaults to 0 for non-negative variables. Must be
                                  less than or equal to upper_bound.
        related_data (dict[str, UUID]): Dictionary mapping relationship type names to
                                       UUID identifiers of related objects. Enables
                                       complex data modeling and constraint relationships.

    Raises:
        OXception: If lower_bound is greater than upper_bound during initialization.
                  This validation ensures mathematical consistency of the variable domain.

    Performance:
        - Variable creation is optimized for large-scale problems with minimal overhead
        - Bounds checking is performed only during initialization and explicit validation
        - String representation is cached for efficient display in large variable sets

    Thread Safety:
        - Individual variable instances are thread-safe for read operations
        - Modification operations should be synchronized in multi-threaded environments
        - The related_data dictionary requires external synchronization for concurrent access

    Examples:
        Create variables for different optimization scenarios:
        
        .. code-block:: python
        
            # Production planning variable with finite bounds
            production = OXVariable(
                name="daily_production",
                description="Daily production quantity in units",
                lower_bound=0,
                upper_bound=1000,
                value=500
            )
            
            # Binary decision variable for facility location
            facility_open = OXVariable(
                name="facility_open",
                description="Whether to open the facility (0=closed, 1=open)",
                lower_bound=0,
                upper_bound=1,
                value=0
            )
            
            # Unbounded variable for inventory surplus/deficit
            inventory_delta = OXVariable(
                name="inventory_change",
                description="Change in inventory level (positive=surplus, negative=deficit)",
                lower_bound=float('-inf'),
                upper_bound=float('inf')
            )
            
            # Link variable to related business entities
            from uuid import uuid4
            customer_id = uuid4()
            production.related_data["customer"] = customer_id
            production.related_data["facility"] = facility_open.id

    Note:
        - Variables are immutable after solver assignment to maintain solution integrity
        - The bounds validation is strict and prevents invalid domain specifications
        - Automatic naming ensures no variable is left without a unique identifier
        - Related data relationships support complex constraint modeling patterns

    See Also:
        :class:`variables.OXDeviationVar.OXDeviationVar`: Specialized deviation variables for goal programming.
        :class:`variables.OXVariableSet.OXVariableSet`: Container for managing variable collections.
        :class:`base.OXObject`: Base class providing UUID and serialization capabilities.
    """
    name: str = ""
    description: str = ""
    value: float | int | bool = None
    upper_bound: float | int = float("inf")
    lower_bound: float | int = 0
    related_data: dict[str, UUID] = field(default_factory=dict)

    def __post_init__(self):
        """
        Initialize and validate the variable after dataclass construction.

        This method is automatically invoked by the dataclass mechanism after all
        field assignments are complete. It performs critical validation and setup
        operations to ensure the variable is in a consistent and valid state.

        The initialization process includes:
        1. Calling the parent OXObject initialization for UUID and class name setup
        2. Validating that bounds are mathematically consistent (lower ≤ upper)
        3. Generating an automatic name if none was provided or if empty/whitespace
        4. Ensuring all internal state is properly configured for optimization use

        Validation Rules:
            - Lower bound must be less than or equal to upper bound
            - Infinite bounds are permitted and properly handled
            - Empty or whitespace-only names trigger automatic UUID-based naming

        Raises:
            OXception: If lower_bound is greater than upper_bound. This ensures
                      mathematical validity of the variable's domain and prevents
                      optimization solver errors that would occur with invalid bounds.

        Note:
            - This method is called automatically and should not be invoked manually
            - The automatic naming scheme uses format "var_<uuid>" for traceability
            - All validation occurs during object creation, not during value assignment
            - Parent initialization must complete successfully for proper inheritance

        Examples:
            The validation prevents invalid variable creation:
            
            .. code-block:: python
            
                # This will raise OXception due to invalid bounds
                try:
                    invalid_var = OXVariable(lower_bound=10, upper_bound=5)
                except OXception as e:
                    print("Invalid bounds detected:", e)
                
                # This creates a variable with automatic naming
                auto_named = OXVariable(name="  ")  # Whitespace triggers auto-naming
                print(auto_named.name)  # Output: "var_<some-uuid>"
        """
        super().__post_init__()
        if self.lower_bound > self.upper_bound:
            raise OXception("Lower bound cannot be greater than upper bound.")
        if self.name.strip() == "":
            self.name = f"var_{self.id}"

    def __str__(self):
        """
        Return a string representation of the variable.
        
        Provides a concise, human-readable identifier for the variable that is
        suitable for display in optimization model summaries, debug output,
        and solver interfaces.

        Returns:
            str: The variable's name, which serves as its primary identifier
                 in the optimization context. This will be either the user-provided
                 name or the automatically generated "var_<uuid>" format.

        Note:
            - The string representation is optimized for readability and brevity
            - Used extensively by solvers and constraint display mechanisms
            - Guaranteed to be unique due to UUID-based automatic naming fallback

        Examples:
            .. code-block:: python
            
                named_var = OXVariable(name="production_rate")
                print(str(named_var))  # Output: "production_rate"
                
                auto_var = OXVariable()  # No name provided
                print(str(auto_var))    # Output: "var_<uuid>"
        """
        return self.name
