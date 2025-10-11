"""
Unit tests for SP500Screener module
"""

import unittest
import pandas as pd
from tradingsuite.utils.sp500_screener import SP500Loader, SP500Screener


class TestSP500Loader(unittest.TestCase):
    """Test cases for SP500Loader class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loader = SP500Loader()
    
    def test_loader_initialization(self):
        """Test loader initializes correctly"""
        self.assertIsNotNone(self.loader.scraper)
        self.assertIsNone(self.loader.sp500_df)
    
    def test_load_data(self):
        """Test data loading from Wikipedia"""
        df = self.loader.load()
        
        # Check DataFrame is not empty
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        
        # Check expected columns exist
        expected_columns = ['Symbol', 'Security', 'GICS Sector', 'Date added']
        for col in expected_columns:
            self.assertIn(col, df.columns)
        
        # Check Date added is datetime
        self.assertEqual(df['Date added'].dtype, 'datetime64[ns]')
    
    def test_get_dataframe(self):
        """Test get_dataframe method"""
        df = self.loader.get_dataframe()
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)


class TestSP500Screener(unittest.TestCase):
    """Test cases for SP500Screener class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.screener = SP500Screener(auto_load=True)
    
    def test_screener_initialization(self):
        """Test screener initializes correctly"""
        self.assertIsNotNone(self.screener.loader)
        self.assertIsNotNone(self.screener.sp500_df)
        self.assertIsNotNone(self.screener.filtered_df)
    
    def test_filter_by_recent_additions(self):
        """Test filtering by recent additions"""
        n = 10
        self.screener.reset_filters()
        self.screener.filter_by_recent_additions(n=n)
        result = self.screener.get_results()
        
        # Check correct number of results
        self.assertEqual(len(result), n)
        
        # Check dates are sorted (most recent first)
        dates = result['Date added'].tolist()
        self.assertEqual(dates, sorted(dates, reverse=True))
    
    def test_filter_by_sector_and_recent(self):
        """Test filtering by sector and recent additions"""
        sector = 'Information Technology'
        n = 5
        
        self.screener.reset_filters()
        self.screener.filter_by_sector_and_recent(sector=sector, n=n)
        result = self.screener.get_results()
        
        # Check all results are from correct sector
        self.assertTrue(all(result['GICS Sector'] == sector))
        
        # Check correct number or less (might not have n companies in sector)
        self.assertLessEqual(len(result), n)
    
    def test_reset_filters(self):
        """Test filter reset"""
        # Apply a filter
        self.screener.filter_by_recent_additions(n=10)
        self.assertEqual(len(self.screener.filtered_df), 10)
        
        # Reset
        self.screener.reset_filters()
        
        # Should have all companies again
        self.assertGreater(len(self.screener.filtered_df), 400)  # S&P 500 has ~500 companies
    
    def test_get_tickers(self):
        """Test getting ticker list"""
        self.screener.reset_filters()
        self.screener.filter_by_recent_additions(n=5)
        tickers = self.screener.get_tickers()
        
        # Check tickers is a list
        self.assertIsInstance(tickers, list)
        
        # Check correct length
        self.assertEqual(len(tickers), 5)
        
        # Check all are strings
        self.assertTrue(all(isinstance(t, str) for t in tickers))
    
    def test_get_available_sectors(self):
        """Test getting available sectors"""
        sectors = self.screener.get_available_sectors()
        
        # Check sectors is a list
        self.assertIsInstance(sectors, list)
        
        # Check contains expected sectors
        expected_sectors = ['Information Technology', 'Health Care', 'Financials']
        for sector in expected_sectors:
            self.assertIn(sector, sectors)
    
    def test_method_chaining(self):
        """Test method chaining works correctly"""
        result = (self.screener
                  .reset_filters()
                  .filter_by_recent_additions(n=50)
                  .filter_by_sector_and_recent('Information Technology', n=10)
                  .get_results())
        
        # Check result is not empty
        self.assertGreater(len(result), 0)
        
        # Check all are from IT sector
        self.assertTrue(all(result['GICS Sector'] == 'Information Technology'))
        
        # Check max 10 results
        self.assertLessEqual(len(result), 10)


class TestQuickFunctions(unittest.TestCase):
    """Test cases for quick convenience functions"""
    
    def test_get_recent_sp500_additions(self):
        """Test quick function for recent additions"""
        from tradingsuite.utils.sp500_screener import get_recent_sp500_additions
        
        n = 5
        result = get_recent_sp500_additions(n=n)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), n)
    
    def test_get_recent_additions_by_sector(self):
        """Test quick function for sector filtering"""
        from tradingsuite.utils.sp500_screener import get_recent_additions_by_sector
        
        sector = 'Health Care'
        n = 5
        result = get_recent_additions_by_sector(sector=sector, n=n)
        
        self.assertIsInstance(result, pd.DataFrame)
        if len(result) > 0:
            self.assertTrue(all(result['GICS Sector'] == sector))


class TestDataIntegrity(unittest.TestCase):
    """Test cases for data integrity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.screener = SP500Screener(auto_load=True)
    
    def test_no_duplicate_tickers(self):
        """Test there are no duplicate tickers"""
        df = self.screener.get_results()
        duplicates = df['Symbol'].duplicated().sum()
        self.assertEqual(duplicates, 0)
    
    def test_valid_dates(self):
        """Test all dates are valid"""
        df = self.screener.get_results()
        
        # Check no NaT values
        nat_count = df['Date added'].isna().sum()
        
        # Some companies might have NaT (original members), that's ok
        # Just check that most have dates
        self.assertLess(nat_count, len(df) * 0.5)
    
    def test_sectors_valid(self):
        """Test all sectors are valid GICS sectors"""
        df = self.screener.get_results()
        
        valid_sectors = [
            'Information Technology',
            'Health Care',
            'Financials',
            'Consumer Discretionary',
            'Communication Services',
            'Industrials',
            'Consumer Staples',
            'Energy',
            'Utilities',
            'Real Estate',
            'Materials'
        ]
        
        # Check all sectors are in valid list
        unique_sectors = df['GICS Sector'].unique()
        for sector in unique_sectors:
            self.assertIn(sector, valid_sectors)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
