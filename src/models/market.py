###############################################################################
# IMPORTS
###############################################################################

from agentpy import Model, AgentList
from math import ceil

from .firm import Firm
from .worker import Worker

###############################################################################
# MARKET MODEL
###############################################################################

class Market(Model):
    """
    Implements a market model consisting of worker and firm agents. The model
    simulates the interactions between workers and firms, including employment,
    wage determination, productivity, and profit calculations.

    The market model initializes with a specified number of workers and firms,
    where initially, each worker is employed by a unique firm. Throughout the
    simulation, workers can decide to pursue education based on a cost-benefit
    analysis, search for new employment opportunities based on wage offers, and
    firms produce output and calculate profits.

    Methods:
        setup(): Initializes the market model, creating workers and firms and setting initial employment relationships.
        step(): Performs a single simulation step, including worker decisions on education and employment, and firm production.
        update(): Records data from the current state of the simulation for analysis.
        end(): Finalizes the simulation, potentially performing cleanup or final data recording (currently a placeholder with no implementation).

    During each simulation step, a subset of active workers is selected to
    possibly pursue education and search for new employment opportunities based
    on a sampling of firms. Firms calculate their profits based on the current
    state of employment and production outcomes. The model records detailed
    microdata on both workers and firms for analysis.
    """

    def setup(self):
        """
        Initializes the model by creating the specified number of worker and firm agents.
        Each worker is initially employed by a unique firm, and wages are determined based on the firm's wage calculation method.
        """

        # Initialize agents.
        self.workers = AgentList(self, self.p['n_workers'], Worker)
        self.firms = AgentList(self, 2*self.p['n_workers']+1, Firm)

        # Initialize workers into singleton firms.
        for i in range(self.p['n_workers']):

            # Select worker i and firm i.
            worker = self.workers[i]
            firm = self.firms[i]

            # Have the worker i join firm i.
            worker.update_employer(firm=firm)
            firm.hire(worker)

            # Set the worker i's wage at firm i.
            worker.wage = firm.calc_wage(worker=worker)

    def step(self):
        """
        Executes a series of actions representing a single time step in the
        model. Actions include:
        - Selecting a subset of workers to potentially pursue education and
        search for new employment.
        - Workers deciding whether to get an education based on a cost-benefit
        analysis.
        - Workers searching for and possibly switching to new firms based on
        wage offers.
        - Firms producing output and calculating profits based on current
        employment.
        """

        # Restart counters.
        self.workers.search = False
        self.workers.switch = False

        # Select active workers at random.
        workers_sel = (
            self.workers
            .random(
                n=ceil(self.model.p['n_workers']*self.model.p['active'])
            )
        )

        # Decide whether to get an education.
        for worker in workers_sel:
            if worker.educ == 0:
                worker.education_decision(
                    premium=self.model.p['premium'],
                    weighted=self.model.p['weighted']
                )
        
        # Search for new firm.
        workers_sel.firm_selection(n=self.model.p['sample'])

        # All workers update their firm size.
        self.workers.employer_size = self.workers.employer.size

        # Firms produce output and calculate profits.
        self.firms.produce()
        self.firms.calc_profit()

    def update(self):
        """
        Records data from the current state of the simulation. This includes
        detailed attributes of workers and firms, such as discrimination class,
        productivity, wages, firm size, output, and profit.
        """

        # Record microdata.
        self.workers.record(
            [
                'd_class', 'prod', 'hrs', 'employer', 'employer_id',
                'employer_size', 'wage', 'educ', 'search', 'switch'
            ]
        )

        self.firms.record(
            [
                'd_factor', 'size', 'size_0', 'size_1', 'output',
                'output_0', 'output_1', 'costs', 'revenue', 'profit', 
            ]
        )
            
    def end(self):
        """
        Finalizes the simulation. This method serves as a placeholder and can
        be implemented to perform cleanup or final data recording operations at
        the end of the simulation.
        """
        pass