#!/usr/bin/env python3
# backend_test.py
# ---------------------------------------------------------------------------
# Comprehensive testing for Football LSTM Betting Dashboard Backend
# ---------------------------------------------------------------------------

import sys
import os
import json
import pandas as pd
import tempfile
import shutil
from datetime import datetime, timedelta

# Add the app directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from betting_tracker import BettingTracker

class BettingTrackerTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.temp_dir = None
        self.original_cwd = os.getcwd()
        
    def setup_test_environment(self):
        """Setup isolated test environment"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        # Create test data directory
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/lstm", exist_ok=True)
        
        # Create sample bets_today.csv
        sample_bets = pd.DataFrame({
            'match': ['Team A vs Team B', 'Team C vs Team D'],
            'bet_on': ['Home', 'Away'],
            'bookmaker_odds': [2.1, 2.8],
            'expected_prob': [0.55, 0.45],
            'expected_value': [0.155, 0.260],
            'edge': [15.5, 26.0]
        })
        sample_bets.to_csv("data/bets_today.csv", index=False)
        
        # Create sample predictions
        sample_predictions = pd.DataFrame({
            'match': ['Team A vs Team B', 'Team C vs Team D'],
            'predicted_outcome': ['Home', 'Away'],
            'confidence': [0.78, 0.72],
            'prob_home': [0.55, 0.20],
            'prob_draw': [0.25, 0.35],
            'prob_away': [0.20, 0.45]
        })
        sample_predictions.to_csv("data/lstm/predictions_today.csv", index=False)
        
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def run_test(self, test_name, test_func):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n🔍 Testing {test_name}...")
        
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                print(f"✅ Passed - {test_name}")
                return True
            else:
                print(f"❌ Failed - {test_name}")
                return False
        except Exception as e:
            print(f"❌ Failed - {test_name}: {str(e)}")
            return False
    
    def test_tracker_initialization(self):
        """Test BettingTracker initialization"""
        tracker = BettingTracker(initial_bankroll=1000, default_bet_size=10)
        
        # Check if files are created
        if not os.path.exists("data/betting_history.csv"):
            return False
        if not os.path.exists("data/betting_config.json"):
            return False
            
        # Check config values
        config = tracker.get_config()
        if config['initial_bankroll'] != 1000:
            return False
        if config['current_bankroll'] != 1000:
            return False
        if config['default_bet_size'] != 10:
            return False
            
        return True
    
    def test_config_operations(self):
        """Test configuration loading and saving"""
        tracker = BettingTracker()
        
        # Get initial config
        config = tracker.get_config()
        original_bankroll = config['current_bankroll']
        
        # Modify and save
        config['current_bankroll'] = 1500
        tracker.save_config(config)
        
        # Load and verify
        new_config = tracker.get_config()
        if new_config['current_bankroll'] != 1500:
            return False
            
        # Check last_update was set
        if 'last_update' not in new_config:
            return False
            
        return True
    
    def test_add_todays_bets(self):
        """Test adding today's bets to history"""
        tracker = BettingTracker()
        
        # Add today's bets
        tracker.add_todays_bets(bet_size_multiplier=1.0)
        
        # Check history
        history = tracker.get_history()
        if history.empty:
            return False
            
        # Should have 2 bets from our sample data
        today = datetime.now().strftime("%Y-%m-%d")
        today_bets = history[history['date'] == today]
        if len(today_bets) != 2:
            return False
            
        # Check bet details
        first_bet = today_bets.iloc[0]
        if first_bet['match'] != 'Team A vs Team B':
            return False
        if first_bet['bet_on'] != 'Home':
            return False
        if first_bet['odds'] != 2.1:
            return False
        if first_bet['status'] != 'pending':
            return False
            
        return True
    
    def test_statistics_calculation(self):
        """Test statistics calculation"""
        tracker = BettingTracker()
        
        # Add some bets first
        tracker.add_todays_bets()
        
        # Get statistics
        stats = tracker.get_statistics()
        
        # Check required fields
        required_fields = [
            'total_bets', 'winning_bets', 'win_rate', 'total_roi',
            'roi_percentage', 'current_bankroll', 'profit_loss',
            'avg_odds', 'pending_bets'
        ]
        
        for field in required_fields:
            if field not in stats:
                return False
        
        # Check pending bets count (should be 2 from our sample)
        if stats['pending_bets'] != 2:
            return False
            
        # Check initial values
        if stats['total_bets'] != 0:  # No completed bets yet
            return False
        if stats['winning_bets'] != 0:
            return False
        if stats['win_rate'] != 0:
            return False
            
        return True
    
    def test_league_statistics(self):
        """Test league statistics calculation"""
        tracker = BettingTracker()
        
        # Add bets and simulate completion
        tracker.add_todays_bets()
        
        # Manually complete some bets for testing
        history = tracker.get_history()
        if not history.empty:
            # Simulate completing first bet as won
            history.loc[0, 'status'] = 'completed'
            history.loc[0, 'won'] = True
            history.loc[0, 'profit_loss'] = 11.0  # (2.1-1) * 10
            history.loc[0, 'actual_result'] = 'Home'
            
            # Simulate completing second bet as lost
            history.loc[1, 'status'] = 'completed'
            history.loc[1, 'won'] = False
            history.loc[1, 'profit_loss'] = -10.0
            history.loc[1, 'actual_result'] = 'Home'
            
            # Save updated history
            history.to_csv("data/betting_history.csv", index=False)
        
        # Get league statistics
        league_stats = tracker.get_league_statistics()
        
        # Should have at least one league (even if 'Inconnue')
        if league_stats.empty:
            return False
            
        # Check required columns
        required_columns = [
            'league', 'total_bets', 'winning_bets', 'win_rate',
            'total_roi', 'avg_odds', 'avg_expected_value'
        ]
        
        for col in required_columns:
            if col not in league_stats.columns:
                return False
        
        return True
    
    def test_data_file_loading(self):
        """Test loading of data files"""
        # Test bets_today.csv loading
        if not os.path.exists("data/bets_today.csv"):
            return False
            
        bets_df = pd.read_csv("data/bets_today.csv")
        if bets_df.empty:
            return False
            
        # Check required columns
        required_columns = ['match', 'bet_on', 'bookmaker_odds', 'expected_prob', 'expected_value', 'edge']
        for col in required_columns:
            if col not in bets_df.columns:
                return False
        
        # Test predictions loading
        if not os.path.exists("data/lstm/predictions_today.csv"):
            return False
            
        pred_df = pd.read_csv("data/lstm/predictions_today.csv")
        if pred_df.empty:
            return False
            
        # Check required columns
        required_columns = ['match', 'predicted_outcome', 'confidence', 'prob_home', 'prob_draw', 'prob_away']
        for col in required_columns:
            if col not in pred_df.columns:
                return False
        
        return True
    
    def test_bet_size_multiplier(self):
        """Test bet size multiplier functionality"""
        tracker = BettingTracker(default_bet_size=10)
        
        # Add bets with 2x multiplier
        tracker.add_todays_bets(bet_size_multiplier=2.0)
        
        history = tracker.get_history()
        if history.empty:
            return False
            
        # Check bet amounts are doubled
        for _, bet in history.iterrows():
            if bet['bet_amount'] != 20.0:  # 10 * 2.0
                return False
        
        return True
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🏈 Starting Football LSTM Betting Dashboard Backend Tests")
        print("=" * 60)
        
        # Setup test environment
        self.setup_test_environment()
        
        try:
            # Run all tests
            self.run_test("Tracker Initialization", self.test_tracker_initialization)
            self.run_test("Configuration Operations", self.test_config_operations)
            self.run_test("Data File Loading", self.test_data_file_loading)
            self.run_test("Add Today's Bets", self.test_add_todays_bets)
            self.run_test("Statistics Calculation", self.test_statistics_calculation)
            self.run_test("League Statistics", self.test_league_statistics)
            self.run_test("Bet Size Multiplier", self.test_bet_size_multiplier)
            
            # Print results
            print("\n" + "=" * 60)
            print(f"📊 Backend Test Results: {self.tests_passed}/{self.tests_run} tests passed")
            
            if self.tests_passed == self.tests_run:
                print("✅ All backend tests passed!")
                return True
            else:
                print(f"❌ {self.tests_run - self.tests_passed} tests failed")
                return False
                
        finally:
            # Cleanup
            self.cleanup_test_environment()

def main():
    """Main test function"""
    tester = BettingTrackerTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())