import unittest
from unittest.mock import MagicMock
from numpy import mean
from src.models.worker import Worker

class TestWorker(unittest.TestCase):

    def setUp(self):
        # Mock the model and its parameters
        self.mock_model = MagicMock()
        self.mock_model.p = {'prod_range': (10, 20), 'premium': 0.1, 'weighted': False}
        self.mock_model.random.choice.return_value = 1
        self.mock_model.random.randint.return_value = 15

        # Instantiate a Worker with the mocked model
        self.worker = Worker(self.mock_model)
        self.worker.setup()

    def test_initialization(self):
        # Test initial values are set correctly
        self.assertIn(self.worker.d_class, [0, 1])
        self.assertTrue(10 <= self.worker.prod <= 20)
        self.assertEqual(self.worker.hrs, 8)
        self.assertFalse(self.worker.educ)
        self.assertEqual(self.worker.wage, 0)

    def test_update_employer(self):
        # Mock a Firm object and update the employer of the worker
        mock_firm = MagicMock()
        mock_firm.id = 1
        mock_firm.size = 10
        self.worker.update_employer(mock_firm)

        # Test if the employer has been updated correctly
        self.assertEqual(self.worker.employer, mock_firm)
        self.assertEqual(self.worker.employer_id, mock_firm.id)
        self.assertEqual(self.worker.employer_size, mock_firm.size)

    def test_get_education(self):
        # Test the effect of getting an education
        initial_prod = self.worker.prod
        self.worker.get_education(self.mock_model.p['premium'])

        # Check if productivity and education flag are updated correctly
        self.assertTrue(self.worker.educ)
        self.assertEqual(self.worker.prod, initial_prod * (1 + self.mock_model.p['premium']))

    def test_switch_employer(self):
        # Mock the current and new employer firms
        current_employer = MagicMock()
        new_employer = MagicMock()
        self.worker.update_employer(current_employer)

        # Simulate switching employers
        self.worker.switch_employer(new_employer)

        # Check if the worker has correctly switched employers
        self.assertEqual(self.worker.employer, new_employer)
        self.assertTrue(new_employer.hire.called)  # Assert the new employer's hire method was called
        self.assertTrue(current_employer.separate.called)  # Assert the old employer's separate method was called

    def test_calc_avg_d(self):
        # Mock firms and their discrimination factors
        mock_firm_1 = MagicMock()
        mock_firm_1.d_factor = 0.1
        mock_firm_1.size = 10
        mock_firm_2 = MagicMock()
        mock_firm_2.d_factor = 0.2
        mock_firm_2.size = 20

        self.mock_model.firms.select.return_value = [mock_firm_1, mock_firm_2]

        # Test unweighted average discrimination factor
        avg_d_unweighted = self.worker.calc_avg_d(weighted=False)
        expected_unweighted = mean([mock_firm_1.d_factor, mock_firm_2.d_factor])
        self.assertEqual(avg_d_unweighted, expected_unweighted)

        # Test weighted average discrimination factor
        avg_d_weighted = self.worker.calc_avg_d(weighted=True)
        total_size = mock_firm_1.size + mock_firm_2.size
        expected_weighted = (mock_firm_1.d_factor * mock_firm_1.size + mock_firm_2.d_factor * mock_firm_2.size) / total_size
        self.assertEqual(avg_d_weighted, expected_weighted)

    def test_education_decision(self):
        # Mock the calculation of average discrimination for a weighted scenario
        self.worker.calc_avg_d = MagicMock(return_value=0.15)
        self.worker.prod = 18  # Higher than avg_prod to ensure decision leads to getting education

        self.worker.education_decision(premium=self.mock_model.p['premium'], weighted=True)

        # Assert the worker decided to get an education
        self.assertTrue(self.worker.educ)
        self.assertGreater(self.worker.prod, 18)  # Productivity should increase

    def test_firm_selection(self):
        # This test requires simulating the firm selection process
        # Mock firms and their wage offers
        mock_firm = MagicMock()
        mock_firm.calc_wage.return_value = 20  # Simulate a higher wage offer
        self.worker.select_firms = MagicMock(return_value=[mock_firm])  # Mock the selection of firms
        self.worker.rank_firms = MagicMock(return_value=(mock_firm, 20))  # Mock the ranking of firms

        initial_wage = 15
        self.worker.wage = initial_wage
        self.worker.firm_selection(n=1)  # Simulate the firm selection process

        # Assert the worker decided to switch due to a higher wage offer
        self.assertTrue(self.worker.search)
        self.assertTrue(self.worker.switch)
        self.assertEqual(self.worker.wage, 20)  # Wage should be updated to the higher offer

if __name__ == '__main__':
    unittest.main()
