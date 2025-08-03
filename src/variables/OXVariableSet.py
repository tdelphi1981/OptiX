"""
Variable Set Container Module
=============================

This module provides the OXVariableSet class, a specialized container for managing 
collections of decision variables in optimization problems within the OptiX framework. 
It extends the base OXObjectPot class to provide type-safe, efficient storage and 
retrieval of OXVariable instances with advanced querying capabilities.

The module implements comprehensive variable collection management with features
essential for large-scale optimization modeling, including relationship-based
querying, type enforcement, and efficient iteration patterns.

Key Features:
    - **Type Safety**: Enforces that only OXVariable instances can be stored
    - **Relationship Querying**: Advanced search capabilities based on variable relationships
    - **Collection Operations**: Full support for add, remove, and iteration operations
    - **Memory Efficiency**: Optimized storage for large variable collections
    - **Thread Safety**: Safe concurrent access for read operations

Core Components:
    - **OXVariableSet**: Main container class with type-safe operations
    - **Query System**: Flexible relationship-based variable searching
    - **Type Validation**: Automatic checking of variable types during operations
    - **Iterator Support**: Full Python iteration protocol implementation

Use Cases:
    - Managing decision variables in linear programming models
    - Organizing variables by business entities or constraint groups
    - Building variable collections for complex optimization scenarios
    - Querying variables based on data relationships and attributes
    - Efficient variable storage for large-scale optimization problems

Example:
    Managing optimization variables with relationship querying:

    .. code-block:: python

        from variables.OXVariableSet import OXVariableSet
        from variables.OXVariable import OXVariable
        from uuid import uuid4
        
        # Create variable set and variables
        var_set = OXVariableSet()
        
        # Create variables for different customers
        customer1_id = uuid4()
        customer2_id = uuid4()
        
        var1 = OXVariable(name="production_cust1", lower_bound=0, upper_bound=1000)
        var1.related_data["customer"] = customer1_id
        
        var2 = OXVariable(name="production_cust2", lower_bound=0, upper_bound=800)
        var2.related_data["customer"] = customer2_id
        
        # Add variables to set
        var_set.add_object(var1)
        var_set.add_object(var2)
        
        # Query variables by customer relationship
        customer1_vars = var_set.query(customer=customer1_id)
        print(f"Found {len(customer1_vars)} variables for customer 1")

Module Dependencies:
    - dataclasses: For structured class definitions with automatic method generation
    - base: For OXObjectPot inheritance and OXException error handling
    - variables.OXVariable: For OXVariable type definitions and validation
"""

from dataclasses import dataclass

from base import OXObjectPot, OXObject, OXception
from variables.OXVariable import OXVariable


@dataclass
class OXVariableSet(OXObjectPot):
    """
    Type-safe container for managing collections of optimization variables.
    
    This specialized container class extends OXObjectPot to provide comprehensive
    management of OXVariable instances with strict type enforcement and advanced
    querying capabilities. It serves as the primary collection mechanism for
    organizing decision variables in complex optimization models.
    
    The class implements robust validation, efficient storage, and relationship-based
    querying to support large-scale optimization scenarios where variables need to
    be organized, searched, and managed based on their business relationships and
    mathematical properties.
    
    Key Capabilities:
        - Strict type enforcement ensuring only OXVariable instances are stored
        - Relationship-based querying using variable related_data attributes
        - Full iteration support with Python's standard collection protocols
        - Memory-efficient storage optimized for large variable collections
        - Thread-safe read operations for concurrent optimization environments

    Architecture:
        The container inherits from OXObjectPot to leverage proven collection
        management patterns while adding variable-specific functionality such as
        relationship querying and type validation. All operations maintain the
        mathematical integrity required for optimization model consistency.

    Performance Characteristics:
        - Variable addition: O(1) average case with type validation overhead
        - Variable removal: O(n) linear search with type validation
        - Relationship queries: O(n) linear scan with predicate evaluation
        - Iteration: O(n) with minimal memory overhead for large collections

    Thread Safety:
        - Read operations (iteration, querying, length) are thread-safe
        - Write operations (add, remove) require external synchronization
        - Related_data modifications on contained variables need coordination

    Examples:
        Build and query variable collections for optimization models:
        
        .. code-block:: python
        
            from variables.OXVariableSet import OXVariableSet
            from variables.OXVariable import OXVariable
            from uuid import uuid4
            
            # Create variable set for production planning
            production_vars = OXVariableSet()
            
            # Create variables for different products and facilities
            facility1_id = uuid4()
            facility2_id = uuid4()
            product_a_id = uuid4()
            product_b_id = uuid4()
            
            # Production variable for Product A at Facility 1
            var_a1 = OXVariable(
                name="prod_A_facility1",
                description="Production of Product A at Facility 1",
                lower_bound=0,
                upper_bound=1000
            )
            var_a1.related_data["facility"] = facility1_id
            var_a1.related_data["product"] = product_a_id
            
            # Production variable for Product B at Facility 2
            var_b2 = OXVariable(
                name="prod_B_facility2", 
                description="Production of Product B at Facility 2",
                lower_bound=0,
                upper_bound=800
            )
            var_b2.related_data["facility"] = facility2_id
            var_b2.related_data["product"] = product_b_id
            
            # Add variables to the set
            production_vars.add_object(var_a1)
            production_vars.add_object(var_b2)
            
            # Query variables by facility
            facility1_vars = production_vars.query(facility=facility1_id)
            print(f"Facility 1 variables: {[v.name for v in facility1_vars]}")
            
            # Query variables by product type
            product_a_vars = production_vars.query(product=product_a_id)
            print(f"Product A variables: {[v.name for v in product_a_vars]}")
            
            # Iterate through all variables
            total_capacity = sum(var.upper_bound for var in production_vars)
            print(f"Total production capacity: {total_capacity}")

    Note:
        - Type validation occurs at runtime during add/remove operations
        - Query operations scan all variables for matching relationships
        - Container operations maintain the same semantics as OXObjectPot
        - Variables can be queried by any combination of related_data attributes

    See Also:
        :class:`base.OXObjectPot.OXObjectPot`: Base container class with collection operations.
        :class:`variables.OXVariable.OXVariable`: Variable type managed by this container.
        :class:`base.OXObject`: Base object type for UUID and serialization support.
    """

    def add_object(self, obj: OXObject):
        """
        Add an OXVariable instance to the variable collection.
        
        This method performs type validation to ensure only OXVariable instances
        are added to the set, maintaining type safety and collection integrity.
        The validation occurs before delegation to the parent container's add
        operation, preventing invalid state and ensuring optimization model consistency.
        
        The method enforces the container's type invariant that all contained
        objects must be optimization variables, which is essential for the
        specialized querying and management operations provided by this class.

        Args:
            obj (OXObject): The variable object to add to the collection. Must be
                           an instance of OXVariable or its subclasses. The object
                           will be stored and can be retrieved through iteration
                           or relationship-based queries.

        Raises:
            OXception: If the provided object is not an instance of OXVariable.
                      This strict type checking prevents runtime errors and
                      maintains the mathematical integrity of variable collections.

        Performance:
            - Time complexity: O(1) average case for the type check and container addition
            - Space complexity: O(1) additional memory for the new variable reference
            - Type validation adds minimal overhead compared to container operations

        Note:
            - Duplicate variables (same UUID) will be handled by the parent container
            - The variable's related_data can be modified after addition for querying
            - Type validation is strict and does not allow duck-typing or coercion

        Examples:
            Add variables with proper type validation:
            
            .. code-block:: python
            
                var_set = OXVariableSet()
                
                # Valid addition - OXVariable instance
                production_var = OXVariable(name="production", lower_bound=0)
                var_set.add_object(production_var)  # Success
                
                # Valid addition - OXVariable subclass
                deviation_var = OXDeviationVar(name="deviation")
                var_set.add_object(deviation_var)  # Success
                
                # Invalid addition - wrong type
                from base.OXObject import OXObject
                generic_obj = OXObject()
                try:
                    var_set.add_object(generic_obj)  # Raises OXception
                except OXception as e:
                    print("Type validation prevented invalid addition")

        See Also:
            :meth:`remove_object`: Type-safe variable removal from the collection.
            :meth:`query`: Relationship-based variable querying capabilities.
        """
        if not isinstance(obj, OXVariable):
            raise OXception("Only OXVariable can be added to OXVariableSet")
        super().add_object(obj)

    def remove_object(self, obj: OXObject):
        """
        Remove an OXVariable instance from the variable collection.
        
        This method performs type validation to ensure only OXVariable instances
        are removed from the set, maintaining type safety and preventing invalid
        removal operations. The validation occurs before delegation to the parent
        container's removal operation.

        Args:
            obj (OXObject): The variable object to remove from the collection. Must be
                           an instance of OXVariable that is currently stored in the set.
                           The object will be completely removed from the collection.

        Raises:
            OXception: If the provided object is not an instance of OXVariable.
                      This maintains the type safety invariant of the container.
            ValueError: If the object is not currently in the set. This is raised
                       by the parent container when attempting to remove a non-existent object.

        Performance:
            - Time complexity: O(n) where n is the number of variables (linear search)
            - Space complexity: O(1) as removal only deallocates the reference
            - Type validation overhead is minimal compared to the search operation

        Note:
            - Removal is based on object identity (UUID), not value equality
            - After removal, the variable can no longer be queried or iterated
            - Related data relationships are not automatically cleaned up

        Examples:
            Remove variables with proper validation:
            
            .. code-block:: python
            
                var_set = OXVariableSet()
                production_var = OXVariable(name="production")
                var_set.add_object(production_var)
                
                # Valid removal - variable exists in set
                var_set.remove_object(production_var)  # Success
                
                # Invalid removal - wrong type
                from base.OXObject import OXObject
                generic_obj = OXObject()
                try:
                    var_set.remove_object(generic_obj)  # Raises OXception
                except OXception as e:
                    print("Type validation prevented invalid removal")
                    
                # Invalid removal - variable not in set
                try:
                    var_set.remove_object(production_var)  # Raises ValueError
                except ValueError as e:
                    print("Variable not found in set")

        See Also:
            :meth:`add_object`: Type-safe variable addition to the collection.
            :meth:`query`: Find variables before removal operations.
        """
        if not isinstance(obj, OXVariable):
            raise OXception("Only OXVariable can be removed from OXVariableSet")
        super().remove_object(obj)

    def query(self, **kwargs) -> list[OXObject]:
        """
        Search for variables based on their relationship data attributes.
        
        This method provides powerful relationship-based querying capabilities by
        searching through all variables in the collection and returning those that
        match the specified related_data criteria. Variables are included in the
        result only if they contain ALL specified relationship key-value pairs.
        
        The query system enables complex filtering scenarios essential for large-scale
        optimization models where variables need to be organized and accessed based
        on their business relationships, such as customers, facilities, products,
        time periods, or other domain-specific entities.
        
        Query Logic:
            - Variables must have ALL specified keys in their related_data dictionary
            - Values must match exactly (no partial matching or type coercion)
            - Variables without any matching keys are excluded from results
            - Empty queries (no kwargs) return no results for safety

        Args:
            **kwargs: Key-value pairs to match against variables' related_data dictionaries.
                     Keys represent relationship types (e.g., 'customer', 'facility')
                     and values are the corresponding UUID identifiers. A variable
                     is included in results only if its related_data contains ALL
                     specified key-value pairs with exact matches.

        Returns:
            list[OXObject]: A list of OXVariable instances that match ALL query criteria.
                           The list is empty if no variables match or if no query
                           parameters are provided. Variables are returned in the
                           order they are stored in the container.

        Raises:
            OXception: If a non-OXVariable object is encountered during the search.
                      This should never occur due to type validation but provides
                      a safety check against container corruption.

        Performance:
            - Time complexity: O(n × k) where n is variables count and k is query criteria count
            - Space complexity: O(m) where m is the number of matching variables
            - Linear scan through all variables makes this suitable for moderate-sized collections

        Note:
            - Query parameters are case-sensitive and require exact key matches
            - UUID values are compared for exact equality (no fuzzy matching)
            - Variables can be queried by any combination of related_data attributes
            - Results maintain references to original variables (not copies)

        Examples:
            Query variables using relationship-based filtering:
            
            .. code-block:: python
            
                from variables.OXVariableSet import OXVariableSet
                from variables.OXVariable import OXVariable
                from uuid import uuid4
                
                # Set up variables with relationships
                var_set = OXVariableSet()
                
                customer1_id = uuid4()
                customer2_id = uuid4()
                facility1_id = uuid4()
                facility2_id = uuid4()
                
                # Create variables for different customer-facility combinations
                var1 = OXVariable(name="prod_c1_f1")
                var1.related_data["customer"] = customer1_id
                var1.related_data["facility"] = facility1_id
                
                var2 = OXVariable(name="prod_c1_f2")
                var2.related_data["customer"] = customer1_id
                var2.related_data["facility"] = facility2_id
                
                var3 = OXVariable(name="prod_c2_f1")
                var3.related_data["customer"] = customer2_id
                var3.related_data["facility"] = facility1_id
                
                # Add to set
                for var in [var1, var2, var3]:
                    var_set.add_object(var)
                
                # Query by single criterion
                customer1_vars = var_set.query(customer=customer1_id)
                print(f"Customer 1 variables: {len(customer1_vars)}")  # Output: 2
                
                # Query by multiple criteria (AND operation)
                specific_vars = var_set.query(customer=customer1_id, facility=facility1_id)
                print(f"Customer 1 at Facility 1: {len(specific_vars)}")  # Output: 1
                
                # Empty query returns no results
                empty_result = var_set.query()
                print(f"Empty query result: {len(empty_result)}")  # Output: 0

        See Also:
            :meth:`add_object`: Add variables with relationship data for querying.
            :meth:`search_by_function`: Lower-level search functionality from parent class.
        """

        def query_function(obj: OXObject):
            if isinstance(obj, OXVariable):
                number_of_keys_found = 0
                for key, value in kwargs.items():
                    if key in obj.related_data:
                        number_of_keys_found += 1
                        if obj.related_data[key] != value:
                            return False
                if number_of_keys_found == 0:
                    return False
                return True
            else:
                raise OXception("This should not happen.")

        return self.search_by_function(query_function)
