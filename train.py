"""
Main entry point for training the house price prediction model.
This script trains the model using the best configuration from experiments.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.training.train_model import train_model


def main():
    """Main training function."""
    # Paths
    data_path = "data/raw/train-house-prices-advanced-regression-techniques.csv"
    config_path = "src/configs/best_model_config.json"
    output_dir = "src/models"

    print("=" * 60)
    print("🏠 House Price Prediction - Model Training")
    print("=" * 60)

    # Check if data exists
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        sys.exit(1)

    # Check if config exists
    if not os.path.exists(config_path):
        print(f"❌ Error: Config file not found at {config_path}")
        sys.exit(1)

    # Run training
    try:
        train_model(
            data_path=data_path,
            config_path=config_path,
            output_dir=output_dir,
            mlflow_experiment="House_Price_Prediction",
        )
        print("\n" + "=" * 60)
        print("✅ Training completed successfully!")
        print("=" * 60)
        print("\n📦 Next steps:")
        print(
            "   1. Start MLflow UI: docker-compose -f deployments/mlflow/docker-compose.yaml up"
        )
        print("   2. View results at: http://localhost:5555")
        print(f"   3. Trained model saved in: {output_dir}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
