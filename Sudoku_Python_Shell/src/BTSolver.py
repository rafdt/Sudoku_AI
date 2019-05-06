import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        for v in filter(lambda v: v.isAssigned(), self.network.getVariables()):
                v_assigned = v.getAssignment()
                for n in self.network.getNeighborsOfVariable(v):
                    if n.getAssignment() == v_assigned:
                        return False
                    if not n.isAssigned() and (v_assigned in n.getValues()):
                        self.trail.push(n)
                        n.removeValueFromDomain(v_assigned)
                        if n.size() == 0:
                            return False
                        for c in self.network.getModifiedConstraints():
                            if not c.isConsistent():
                                return False
        return True

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def norvigCheck ( self ):
        #Part 1
        for v in filter(lambda v: v.isAssigned(), self.network.getVariables()):
                v_assigned = v.getAssignment()
                for n in self.network.getNeighborsOfVariable(v):
                    if n.getAssignment() == v_assigned:
                        return False
                    if not n.isAssigned() and (v_assigned in n.getValues()):
                        self.trail.push(n)
                        n.removeValueFromDomain(v_assigned)
                        if n.size() == 0:
                            return False
                        for c in self.network.getModifiedConstraints():
                            if not c.isConsistent():
                                return False
        #Part 2
        N = self.gameboard.N
        for c in self.network.getConstraints():
            count = [0 for x in range(N)]
            for x in range(N):
                for value in c.vars[x].getValues():
                    count[value-1] += 1
            for x in range(N):
                if (count[x] == 1):
                    for v in filter(lambda v: v.getDomain().contains(x+1), c.vars):
                        v.assignValue(x+1)
                        for mod_c in self.network.getModifiedConstraints():
                            if not mod_c.isConsistent():
                                return False
        return True

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================


    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        smallest_domain = float("inf"); mrv = None
        for v in filter(lambda v: not v.isAssigned(), self.network.getVariables()):
            if v.size() < smallest_domain:
                smallest_domain = v.size(); mrv = v
        return mrv

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        smallest_domain = float("inf"); mrv = None; highest_degree = float("-inf")
        for v in filter(lambda v: not v.isAssigned(), self.network.getVariables()):
            unassigned_n = sum([1 for n in self.network.getNeighborsOfVariable(v) if not n.isAssigned()])
            if unassigned_n > highest_degree and v.size() == smallest_domain:
                mrv = v
                highest_degree = unassigned_n
            elif v.size() < smallest_domain:
                mrv = v
                highest_degree = unassigned_n
                smallest_domain = v.size()
        return mrv

    """
    Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        counter = {val:0 for val in v.getValues()}
        for n in filter(lambda n: not n.isAssigned(), self.network.getNeighborsOfVariable(v)):
                for value in filter(lambda value: value in counter, n.getValues()):
                    counter[value] += 1
        return [val for val, count in sorted(counter.items(), key=lambda value: value[-1])]

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
