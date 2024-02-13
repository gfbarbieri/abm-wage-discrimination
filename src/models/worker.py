###############################################################################
# IMPORTS
###############################################################################

from agentpy import Agent
from numpy import mean

###############################################################################
# WORKER AGENT
###############################################################################

class Worker(Agent):
    """
    Represents a worker in the market model, capable of making decisions
    about employment, productivity, and education based on model
    parameters and interactions with firms.

    A worker can be hired or separated by firms, decide to get an education
    based on a cost-benefit analysis, and switch employers if a better wage
    offer is available. The worker's decisions and actions are influenced by
    their productivity, the average discrimination factor in the market, and
    their personal characteristics.

    Attributes:
        d_class (int): The discrimination class of the worker, randomly assigned at setup.
        prod (float): The productivity of the worker, determined randomly within a specified range at setup.
        avg_prod (float): The average productivity level, calculated based on the model's productivity range.
        hrs (int): The fixed number of hours the worker is available to work, set at 8.
        educ (bool): Indicates whether the worker has received education, initially False.
        wage (float): The wage of the worker, initially 0 and updated based on employment status and decisions.
        employer (Firm or None): The current employer of the worker, if any.
        employer_id (int or None): The unique ID of the worker's current employer, if any.
        employer_size (int or None): The size of the worker's current employer, if any.
        search (bool): Indicates whether the worker is actively searching for a new employer.
        switch (bool): Indicates whether the worker has switched employers in the current model step.

    Methods:
        setup(): Initializes worker attributes based on model parameters.
        update_employer(firm): Updates the worker's employment status and employer-related attributes.
        switch_employer(firm): Switches the worker's employment to a new firm, handling separation and hiring.
        calc_avg_d(weighted=False): Calculates the average discrimination factor among active firms.
        get_education(premium): Grants the worker education, increasing productivity and potentially wages.
        education_decision(premium, weighted): Decides whether to get education based on a cost-benefit analysis.
        select_firms(n): Selects a sample of firms that are not the worker's current employer.
        rank_firms(n): Ranks potential employers based on the wage offers for the worker.
        firm_selection(n): Decides whether to switch employers based on wage offers from ranked firms.
    """

    ###########################################################################
    # INITIALIZATION
    ###########################################################################

    def setup(self):
        """
        Initializes the worker's attributes, including productivity,
        discrimination class, and initial employment status.
        """

        self.d_class = self.model.random.choice([1, 0])
        self.prod = self.model.random.randint(self.model.p['prod_range'][0], self.model.p['prod_range'][1])
        self.avg_prod = (self.model.p['prod_range'][1] + self.model.p['prod_range'][0]) / 2
        self.hrs = 8
        self.educ = False
        self.wage = 0
        
        self.employer = None
        self.employer_id = None

        self.employer_size = None
        self.search = False
        self.switch = False

    ###########################################################################
    # SETTERS
    ###########################################################################

    def update_employer(self, firm):
        """
        Updates the worker's employer information, including setting or
        clearing the current employer.

        Parameters:
            firm (Firm or None): The new employer firm or None if becoming unemployed.
        """

        if firm:
            self.employer = firm
            self.employer_id = firm.id
            self.employer_size = firm.size
        else:
            self.employer = None
            self.employer_id = None
            self.employer_size  = None

    def switch_employer(self, firm):
        """
        Handles the process of switching employers, including separating from
        the current employer and joining a new one.

        Parameters:
            firm (Firm): The firm to switch to as the new employer.
        """

        # If employed, separate from current employer.
        if self.employer:
            self.employer.separate(worker=self)

        # Have the new firm add the worker to firm.
        firm.hire(worker=self)

        # Update worker's employer to the new firm.
        self.update_employer(firm=firm)

    ###########################################################################
    # EDUCATION
    ###########################################################################

    def calc_avg_d(self, weighted=False):
        """
        Calculates the average discrimination factor across active firms,
        optionally weighted by firm size.

        Parameters:
            weighted (bool): If True, calculates a weighted average based on
            firm size. Defaults to False.

        Returns:
            float: The average discrimination factor.
        """

        # Find active firms.
        firms = (
            self.model.firms
            .select(self.model.firms.size > 0)
        )

        # Calculate average discrimination factor. If weighted, then calculate
        # weighted average based on firm size.
        if weighted:
            size = sum(firm.size for firm in firms)
            avg = sum(firm.d_factor * (firm.size / size) for firm in firms)
        else:
            avg = mean([firm.d_factor for firm in firms])
        
        return avg

    def get_education(self, premium):
        """
        Grants the worker education, increasing their productivity and
        adjusting their wage if employed.

        Parameters:
            premium (float): The productivity increase percentage from obtaining education.
        """

        # Set educatoin flag to True and adjust productivity to reflect
        # education.
        self.educ = True
        self.prod = self.prod * (1 + premium)

        # If currently employed, immediately adjust wage to match gains
        # from education.
        if self.employer:
            self.wage = self.employer.calc_wage(worker=self)

    def education_decision(self, premium, weighted):
        """
        Makes a decision on whether to pursue education based on a cost-benefit
        analysis, considering potential wage increases and discrimination factors.

        Parameters:
            premium (float): The productivity increase percentage from obtaining education.
            weighted (bool): If True, uses a weighted average of discrimination factors in the cost-benefit analysis.
        """


        # Cost-benefit: Costs are inversely proportional to productivity.
        # Cost factor is calculated such that decision threashold is
        # always mean productivity. Benefits are increases to productivity.
        # Discriminated classes adjust benefits by the average discrimination
        # factor of active businesses.
        cost = (self.avg_prod**2 * premium) / self.prod
        benefit = self.prod * premium

        if self.d_class == 1:
            d_avg = self.calc_avg_d(weighted=weighted)
            benefit = benefit * (1 - d_avg)

        # Decision: If agent is above mean productivity, then  benefit
        # is greater than cost. If the benefit is equal to cost, then
        # solve indifference with random choice.
        if benefit > cost:
            self.get_education(premium=premium)
        elif benefit == cost:
            if self.model.random.choice([True, False]):
                self.get_education(premium=premium)
    
    ###########################################################################
    # FIRM SELECTION
    ###########################################################################
    
    def select_firms(self, n):
        """
        Selects a random sample of firms, excluding the worker's current employer,
        for potential employment.

        Parameters:
            n (int): The number of firms to sample.

        Returns:
            list: A list of sampled firm agents.
        """

        # Select a random sample of firms that are not the agent's firm.
        firms = (
            self.model.firms
            .select(self.model.firms.id != self.employer_id)
            .random(n=n, replace=False)
            .to_list()
        )
    
        return firms

    def rank_firms(self, n):
        """
        Ranks potential employers based on wage offers and selects the best option.

        Parameters:
            n (int): The number of firms to consider in the ranking process.

        Returns:
            tuple: The best firm and the wage offer from that firm.
        """

        # Find potential employers.
        firms = self.select_firms(n=n)

        # Get a wage from each employer.
        wages = [
            firm.calc_wage(worker=self) for firm in firms
        ]
    
        # Get the index value of the firm with the highest growth rate.
        max_idx = wages.index(max(wages))
  
        return firms[max_idx], wages[max_idx]

    def firm_selection(self, n):
        """
        Decides whether to switch employers based on the comparison of current
        wage and potential new wage offers.

        Parameters:
            n (int): The number of potential new employers to consider.
        """

        # Search for firms, find best option.
        self.search = True
        firm, wage = self.rank_firms(n=n)

        # If best option offers higher wage than current wage, then
        # switch employers.
        if wage > self.wage:
            self.switched = True
            self.wage = wage
            self.switch_employer(firm=firm)