import unittest
from unittest.mock import MagicMock
from src.models.firm import Firm
from src.models.worker import Worker

class TestFirm(unittest.TestCase):

    def setUp(self):
        # Correctly setting up mock parameters
        self.mock_model = MagicMock()
        self.mock_model.p = {
            'd_range': (0.1, 0.2),  # Range for d_factor
            'd_class': 1,  # Discrimination class
            'prod_range': (10, 20)  # Range for productivity
        }

        # Directly assigning mock values to ensure they are not treated as MagicMock objects
        self.firm = Firm(self.mock_model)

        # Manually setting d_factor for testing purpose, as MagicMock doesn't execute the logic inside setup
        self.firm.d_factor = round(self.mock_model.random.uniform(0.1, 0.2), 2)
        self.firm.setup()

    def test_initialization(self):
        # Test initial values are correctly initialized after the manual adjustment
        self.assertTrue(0.1 <= self.firm.d_factor <= 0.2)
        self.assertEqual(self.firm.d_class, 1)
        self.assertEqual(len(self.firm.employees), 0)

    def test_hire(self):
        # Test hiring a worker
        worker = Worker(self.mock_model)
        self.firm.hire(worker)
        self.assertIn(worker, self.firm.employees)
        self.assertEqual(len(self.firm.employees), 1)

    def test_separate(self):
        # Test separating a worker
        worker = Worker(self.mock_model)
        self.firm.hire(worker)  # Hire first to test separate
        self.firm.separate(worker)
        self.assertNotIn(worker, self.firm.employees)
        self.assertEqual(len(self.firm.employees), 0)

    def test_produce(self):
        # Test production logic
        worker = Worker(self.mock_model)
        worker.prod = 15  # Set productivity
        worker.hrs = 8  # Set hours worked
        self.firm.hire(worker)
        self.firm.produce()
        expected_output = 15 * 8  # prod * hrs
        self.assertEqual(self.firm.output, expected_output)

    def test_calc_profit(self):
        # Test profit calculation logic
        worker = Worker(self.mock_model)
        worker.prod = 15  # Set productivity
        worker.hrs = 8  # Set hours worked
        worker.wage = 10  # Set wage
        self.firm.price = 2  # Set price per unit
        self.firm.hire(worker)
        self.firm.produce()  # Calculate output
        self.firm.calc_profit()
        expected_revenue = self.firm.output * self.firm.price
        expected_costs = worker.wage * worker.hrs
        expected_profit = expected_revenue - expected_costs
        self.assertEqual(self.firm.revenue, expected_revenue)
        self.assertEqual(self.firm.costs, expected_costs)
        self.assertEqual(self.firm.profit, expected_profit)

    def test_calc_wage(self):
        # Test wage determination logic
        worker = Worker(self.mock_model)
        worker.prod = 15  # Set productivity
        worker.d_class = self.firm.d_class  # Matching d_class for wage adjustment
        wage = self.firm.calc_wage(worker)
        expected_wage = self.firm.price * worker.prod * (1 - self.firm.d_factor)
        self.assertAlmostEqual(wage, expected_wage, places=2)

if __name__ == '__main__':
    unittest.main()
