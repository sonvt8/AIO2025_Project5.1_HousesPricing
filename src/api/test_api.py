"""
Test script for the House Price Prediction API.
Run this script from project root: python src/api/test_api.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import requests
import json


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n🔍 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_model_info():
    """Test model info endpoint."""
    print("\n🔍 Testing /model/info endpoint...")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_predict():
    """Test single prediction endpoint."""
    print("\n🔍 Testing /predict endpoint...")

    # Sample house features
    features = {
        "MSSubClass": 60,
        "MSZoning": "RL",
        "LotArea": 8450,
        "Street": "Pave",
        "LotShape": "Reg",
        "LandContour": "Lvl",
        "Utilities": "AllPub",
        "LotConfig": "Inside",
        "LandSlope": "Gtl",
        "Neighborhood": "CollgCr",
        "Condition1": "Norm",
        "Condition2": "Norm",
        "BldgType": "1Fam",
        "HouseStyle": "2Story",
        "OverallQual": 7,
        "OverallCond": 5,
        "YearBuilt": 2003,
        "YearRemodAdd": 2003,
        "RoofStyle": "Gable",
        "RoofMatl": "CompShg",
        "Exterior1st": "VinylSd",
        "Exterior2nd": "VinylSd",
        "MasVnrType": "BrkFace",
        "MasVnrArea": 196.0,
        "ExterQual": "Gd",
        "ExterCond": "TA",
        "Foundation": "PConc",
        "BsmtQual": "Gd",
        "BsmtCond": "TA",
        "BsmtExposure": "No",
        "BsmtFinType1": "GLQ",
        "BsmtFinSF1": 706.0,
        "BsmtFinType2": "Unf",
        "BsmtFinSF2": 0.0,
        "BsmtUnfSF": 150.0,
        "TotalBsmtSF": 856.0,
        "Heating": "GasA",
        "HeatingQC": "Ex",
        "CentralAir": "Y",
        "Electrical": "SBrkr",
        "FirstFlrSF": 856,
        "SecondFlrSF": 854,
        "LowQualFinSF": 0,
        "GrLivArea": 1710,
        "BsmtFullBath": 1,
        "BsmtHalfBath": 0,
        "FullBath": 2,
        "HalfBath": 1,
        "BedroomAbvGr": 3,
        "KitchenAbvGr": 1,
        "KitchenQual": "Gd",
        "TotRmsAbvGrd": 8,
        "Functional": "Typ",
        "Fireplaces": 0,
        "FireplaceQu": None,
        "GarageType": "Attchd",
        "GarageYrBlt": 2003.0,
        "GarageFinish": "RFn",
        "GarageCars": 2,
        "GarageArea": 548.0,
        "GarageQual": "TA",
        "GarageCond": "TA",
        "PavedDrive": "Y",
        "WoodDeckSF": 0,
        "OpenPorchSF": 61,
        "EnclosedPorch": 0,
        "ThreeSsnPorch": 0,
        "ScreenPorch": 0,
        "PoolArea": 0,
        "PoolQC": None,
        "Fence": None,
        "MiscFeature": None,
        "MiscVal": 0,
        "MoSold": 2,
        "YrSold": 2008,
        "SaleType": "WD",
        "SaleCondition": "Normal",
    }

    response = requests.post(f"{BASE_URL}/predict", json=features)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Predicted price: ${result['predicted_price']:,.2f}")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
    return response.status_code == 200


def test_batch_predict():
    """Test batch prediction endpoint."""
    print("\n🔍 Testing /predict/batch endpoint...")

    houses = [
        {
            "OverallQual": 7,
            "GrLivArea": 1710,
            "YearBuilt": 2003,
            "FullBath": 2,
            "GarageCars": 2,
            "GarageArea": 548,
        },
        {
            "OverallQual": 6,
            "GrLivArea": 1262,
            "YearBuilt": 1976,
            "FullBath": 2,
            "GarageCars": 2,
            "GarageArea": 460,
        },
    ]

    payload = {"houses": houses}
    response = requests.post(f"{BASE_URL}/predict/batch", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Number of predictions: {result['count']}")
        print(f"✅ Min price: ${result['statistics']['min']:,.2f}")
        print(f"✅ Max price: ${result['statistics']['max']:,.2f}")
        print(f"✅ Mean price: ${result['statistics']['mean']:,.2f}")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
    return response.status_code == 200


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing House Price Prediction API")
    print("=" * 60)

    results = []

    results.append(("Health Check", test_health()))
    results.append(("Model Info", test_model_info()))
    results.append(("Single Prediction", test_predict()))
    results.append(("Batch Prediction", test_batch_predict()))

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("   Make sure the API is running: python run_api.py")
        exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
