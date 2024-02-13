###############################################################################
# IMPORTS
###############################################################################

from agentpy import Agent

###############################################################################
# FIRM AGENT
###############################################################################

class Firm(Agent):
    """
    Represents a firm in the market model that can hire workers, produce goods, and calculate profits.

    The firm's behavior includes hiring and separating workers, producing goods based on the productivity
    and hours worked by its employees, calculating revenue and costs to determine profit, and determining
    wages for its workers based on productivity and observed characteristics.

    Attributes:
        d_factor (float): A unique factor for wage determination based on worker characteristics, determined
            randomly within a specified range at setup.
        d_class (int): The observed worker characteristic class used in wage determination.
        employees (list): A list of worker agents employed by the firm.
        size (int): The current size of the firm, in terms of number of employees.
        size_0 (int): The number of employees belonging to characteristic class 0.
        size_1 (int): The number of employees belonging to characteristic class 1.
        price (float): The price of the goods produced by the firm.
        costs (float): The total costs incurred by the firm, primarily wages paid to employees.
        revenue (float): The total revenue generated from selling the goods produced.
        profit (float): The net profit of the firm, calculated as revenue minus costs.
        output (float): The total output produced by the firm.
        output_0 (float): The output produced by employees belonging to characteristic class 0.
        output_1 (float): The output produced by employees belonging to characteristic class 1.

    Methods:
        setup(): Initializes the firm's attributes.
        set_size(): Updates the firm's size and the distribution of employees by characteristic class.
        hire(worker): Adds a worker to the firm's list of employees and updates the firm's size.
        separate(worker): Removes a worker from the firm's list of employees and updates the firm's size.
        produce(): Calculates the firm's total output based on the productivity and hours worked by employees.
        calc_profit(): Calculates the firm's profit by subtracting total costs from total revenue.
        calc_wage(worker): Determines the wage for a given worker based on productivity and characteristic class.
    """

    ###########################################################################
    # INITIALIZATION
    ###########################################################################

    def setup(self):
        """
        Initializes firm-specific attributes based on model parameters and sets initial values for financial
        and production metrics.
        """

        self.d_factor = round(self.model.random.uniform(self.model.p['d_range'][0], self.model.p['d_range'][1]), 2)
        self.d_class = self.model.p['d_class']

        self.employees = []
        self.size = 0
        self.size_0 = 0
        self.size_1 = 0

        self.price = 1
        self.costs = 0
        self.revenue = 0
        self.profit = 0

        self.output = 0
        self.output_0 = 0
        self.output_1 = 0

    ###########################################################################
    # HIRING AND SEPARATIONS
    ###########################################################################

    def set_size(self):
        """
        Updates the firm's size attributes based on the current list of employees and their characteristic classes.
        """

        self.size = len(self.employees)
        self.size_1 = len([employee for employee in self.employees if employee.d_class == 1])
        self.size_0 = len([employee for employee in self.employees if employee.d_class == 0])

    def hire(self, worker):
        """
        Adds a worker to the firm's list of employees if not already hired and updates the firm's size.

        Parameters:
            worker (Worker): The worker agent to be hired.
        """

        if worker not in self.employees:
            self.employees.append(worker)

        self.set_size()

    def separate(self, worker):
        """
        Removes a worker from the firm's list of employees if currently employed and updates the firm's size.

        Parameters:
            worker (Worker): The worker agent to be separated from the firm.
        """

        if worker in self.employees:
            self.employees.remove(worker)
        
        self.set_size()
    
    ###########################################################################
    # PRODUCTION
    ###########################################################################

    def produce(self):
        """
        Calculates the total output of the firm based on the productivity and hours worked by each employee,
        separated by characteristic class.
        """

        # Q = sum(prod/hr * hr).
        self.output = sum([employee.prod * employee.hrs for employee in self.employees])
        self.output_0 = sum([employee.prod * employee.hrs for employee in self.employees if employee.d_class == 0])
        self.output_1 = sum([employee.prod * employee.hrs for employee in self.employees if employee.d_class == 1])

    def calc_profit(self):
        """
        Calculates the firm's total revenue from selling goods, total costs from paying wages, and net profit.
        """

        # Profit = TR - TC = P*Q - sum(wage/hr * hr)
        self.revenue = self.output * self.price
        self.costs = sum([employee.wage * employee.hrs for employee in self.employees])
        self.profit = self.revenue - self.costs

    ###########################################################################
    # WAGE DETERMINATION
    ###########################################################################

    def calc_wage(self, worker):
        """
        Determines the wage for a given worker based on their productivity and observed characteristic class,
        applying a unique factor for wage determination.

        Parameters:
            worker (Worker): The worker agent for whom the wage is being calculated.

        Returns:
            float: The calculated wage for the worker.
        """

        # Set wage equal to MPL.
        wage = self.price * worker.prod

        # Apply wage factor based on observed worker characteristic.
        if worker.d_class == self.d_class:
            wage = wage * (1 - self.d_factor)

        return wage