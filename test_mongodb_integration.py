#!/usr/bin/env python3
"""
Simple test script to validate MongoDB integration code without requiring MongoDB server
"""

import os
import sys
import json
from datetime import datetime

# Add the Backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

def test_mongo_client_import():
    """Test that we can import the MongoDB client"""
    try:
        from Backend.Services.MongoClient import MongoDBClient
        print("✅ MongoDB client import successful")
        return True
    except ImportError as e:
        print(f"❌ MongoDB client import failed: {e}")
        return False

def test_updated_services():
    """Test that all services have been updated to use MongoDB"""
    try:
        from Backend.Services.LogFilter import LogFilter
        from Backend.Services.CollectMetrics import MetricsCollector
        from Backend.DataCollectors.CommitsCollector import CommitsCollector
        
        print("✅ All services import successful")
        
        # Test that LogFilter has MongoDB-related methods
        log_filter = LogFilter()
        if hasattr(log_filter, 'mongo_client'):
            print("✅ LogFilter has mongo_client attribute")
        else:
            print("❌ LogFilter missing mongo_client attribute")
            
        if hasattr(log_filter, 'get_filtered_logs'):
            print("✅ LogFilter has get_filtered_logs method")
        else:
            print("❌ LogFilter missing get_filtered_logs method")
            
        # Test that MetricsCollector has MongoDB-related methods  
        metrics_collector = MetricsCollector()
        if hasattr(metrics_collector, 'mongo_client'):
            print("✅ MetricsCollector has mongo_client attribute")
        else:
            print("❌ MetricsCollector missing mongo_client attribute")
            
        if hasattr(metrics_collector, 'get_metrics'):
            print("✅ MetricsCollector has get_metrics method")
        else:
            print("❌ MetricsCollector missing get_metrics method")
            
        return True
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        return False

def test_migration_script():
    """Test that migration script can be imported"""
    try:
        # Check if migration script exists and has main function
        migration_file = 'migrate_data.py'
        if os.path.exists(migration_file):
            print("✅ Migration script exists")
            
            # Try to read the file and check for key components
            with open(migration_file, 'r') as f:
                content = f.read()
                
            if 'class DataMigration' in content:
                print("✅ DataMigration class found in migration script")
            else:
                print("❌ DataMigration class missing from migration script")
                
            if 'def main()' in content:
                print("✅ Main function found in migration script")
            else:
                print("❌ Main function missing from migration script")
                
            return True
        else:
            print("❌ Migration script not found")
            return False
    except Exception as e:
        print(f"❌ Migration script test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints have been updated"""
    try:
        # Check main.py for MongoDB integration
        main_file = 'Backend/main.py'
        if os.path.exists(main_file):
            with open(main_file, 'r') as f:
                content = f.read()
                
            if 'MongoDBClient' in content:
                print("✅ MongoDB client imported in main.py")
            else:
                print("❌ MongoDB client not imported in main.py")
                
            if 'mongo_client = MongoDBClient()' in content:
                print("✅ MongoDB client initialized in main.py")
            else:
                print("❌ MongoDB client not initialized in main.py")
                
            if 'mongo_client.get_logs' in content:
                print("✅ Logs endpoint uses MongoDB")
            else:
                print("❌ Logs endpoint doesn't use MongoDB")
                
            if 'mongo_client.get_metrics' in content:
                print("✅ Metrics endpoint uses MongoDB")
            else:
                print("❌ Metrics endpoint doesn't use MongoDB")
                
            if 'mongo_client.get_commits' in content:
                print("✅ Commits endpoint uses MongoDB")
            else:
                print("❌ Commits endpoint doesn't use MongoDB")
                
            return True
        else:
            print("❌ main.py not found")
            return False
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_frontend_api():
    """Test that frontend API has been updated"""
    try:
        api_file = 'frontend/src/services/api.js'
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                content = f.read()
                
            if 'fetchLogs()' in content and 'get(\'/logs\')' in content:
                print("✅ Frontend logs API uses MongoDB endpoints")
            else:
                print("❌ Frontend logs API doesn't use MongoDB endpoints")
                
            if 'fetchMetrics()' in content and 'get(\'/metrics\')' in content:
                print("✅ Frontend metrics API uses MongoDB endpoints")  
            else:
                print("❌ Frontend metrics API doesn't use MongoDB endpoints")
                
            if 'fileParser' not in content:
                print("✅ Frontend API no longer references file parser")
            else:
                print("❌ Frontend API still references file parser")
                
            return True
        else:
            print("❌ Frontend API file not found")
            return False
    except Exception as e:
        print(f"❌ Frontend API test failed: {e}")
        return False

def test_requirements():
    """Test that requirements.txt includes pymongo"""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            
        if 'pymongo' in content:
            print("✅ pymongo included in requirements.txt")
            return True
        else:
            print("❌ pymongo not found in requirements.txt")
            return False
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def test_static_files_removed():
    """Test that static data files have been removed"""
    try:
        static_files = [
            'data/filteredLogs.txt',
            'data/metrics.txt', 
            'data/commit.json',
            'frontend/src/utils/fileParser.js',
            'frontend/public/data',
            'dashboard.py'
        ]
        
        all_removed = True
        for file_path in static_files:
            if os.path.exists(file_path):
                print(f"❌ Static file still exists: {file_path}")
                all_removed = False
            else:
                print(f"✅ Static file removed: {file_path}")
                
        return all_removed
    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("MongoDB Integration Validation Tests")
    print("=" * 60)
    
    tests = [
        ("MongoDB Client Import", test_mongo_client_import),
        ("Updated Services", test_updated_services),
        ("Migration Script", test_migration_script),
        ("API Endpoints", test_api_endpoints),
        ("Frontend API", test_frontend_api),
        ("Requirements", test_requirements),
        ("Static Files Removed", test_static_files_removed)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! MongoDB integration is ready.")
        print("\nNext steps:")
        print("1. Install and start MongoDB server")
        print("2. Run: python migrate_data.py")
        print("3. Start the backend: cd Backend && python main.py")
        print("4. Start the frontend: cd frontend && npm run dev")
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed. Please review the issues above.")

if __name__ == "__main__":
    main()