"""
Pydantic models for API request and response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class HouseFeatures(BaseModel):
    """Schema for single house features."""

    MSSubClass: Optional[int] = Field(None, description="Building class")
    MSZoning: Optional[str] = Field(None, description="Zoning classification")
    LotFrontage: Optional[float] = Field(
        None, description="Linear feet of street connected to property"
    )
    LotArea: Optional[int] = Field(None, description="Lot size in square feet")
    Street: Optional[str] = Field(None, description="Type of road access")
    Alley: Optional[str] = Field(None, description="Type of alley access")
    LotShape: Optional[str] = Field(None, description="General shape of property")
    LandContour: Optional[str] = Field(None, description="Flatness of the property")
    Utilities: Optional[str] = Field(None, description="Type of utilities available")
    LotConfig: Optional[str] = Field(None, description="Lot configuration")
    LandSlope: Optional[str] = Field(None, description="Slope of property")
    Neighborhood: Optional[str] = Field(
        None, description="Physical locations within Ames city limits"
    )
    Condition1: Optional[str] = Field(
        None, description="Proximity to various conditions"
    )
    Condition2: Optional[str] = Field(
        None, description="Proximity to various conditions (if more than one)"
    )
    BldgType: Optional[str] = Field(None, description="Type of dwelling")
    HouseStyle: Optional[str] = Field(None, description="Style of dwelling")
    OverallQual: Optional[int] = Field(
        None, description="Overall material and finish quality"
    )
    OverallCond: Optional[int] = Field(None, description="Overall condition rating")
    YearBuilt: Optional[int] = Field(None, description="Original construction date")
    YearRemodAdd: Optional[int] = Field(None, description="Remodel date")
    RoofStyle: Optional[str] = Field(None, description="Type of roof")
    RoofMatl: Optional[str] = Field(None, description="Roof material")
    Exterior1st: Optional[str] = Field(None, description="Exterior covering on house")
    Exterior2nd: Optional[str] = Field(
        None, description="Exterior covering on house (if more than one material)"
    )
    MasVnrType: Optional[str] = Field(None, description="Masonry veneer type")
    MasVnrArea: Optional[float] = Field(
        None, description="Masonry veneer area in square feet"
    )
    ExterQual: Optional[str] = Field(None, description="Exterior material quality")
    ExterCond: Optional[str] = Field(
        None, description="Present condition of the material on the exterior"
    )
    Foundation: Optional[str] = Field(None, description="Type of foundation")
    BsmtQual: Optional[str] = Field(None, description="Height of the basement")
    BsmtCond: Optional[str] = Field(
        None, description="General condition of the basement"
    )
    BsmtExposure: Optional[str] = Field(
        None, description="Refers to walkout or garden level walls"
    )
    BsmtFinType1: Optional[str] = Field(
        None, description="Rating of basement finished area"
    )
    BsmtFinSF1: Optional[float] = Field(None, description="Type 1 finished square feet")
    BsmtFinType2: Optional[str] = Field(
        None, description="Rating of basement finished area (if multiple types)"
    )
    BsmtFinSF2: Optional[float] = Field(None, description="Type 2 finished square feet")
    BsmtUnfSF: Optional[float] = Field(
        None, description="Unfinished square feet of basement area"
    )
    TotalBsmtSF: Optional[float] = Field(
        None, description="Total square feet of basement area"
    )
    Heating: Optional[str] = Field(None, description="Type of heating")
    HeatingQC: Optional[str] = Field(None, description="Heating quality and condition")
    CentralAir: Optional[str] = Field(None, description="Central air conditioning")
    Electrical: Optional[str] = Field(None, description="Electrical system")
    FirstFlrSF: Optional[int] = Field(None, description="First Floor square feet")
    SecondFlrSF: Optional[int] = Field(None, description="Second floor square feet")
    LowQualFinSF: Optional[int] = Field(
        None, description="Low quality finished square feet (all floors)"
    )
    GrLivArea: Optional[int] = Field(
        None, description="Above grade (ground) living area square feet"
    )
    BsmtFullBath: Optional[int] = Field(None, description="Basement full bathrooms")
    BsmtHalfBath: Optional[int] = Field(None, description="Basement half bathrooms")
    FullBath: Optional[int] = Field(None, description="Full bathrooms above grade")
    HalfBath: Optional[int] = Field(None, description="Half baths above grade")
    BedroomAbvGr: Optional[int] = Field(
        None, description="Bedrooms above grade (does NOT include basement bedrooms)"
    )
    KitchenAbvGr: Optional[int] = Field(None, description="Kitchens above grade")
    KitchenQual: Optional[str] = Field(None, description="Kitchen quality")
    TotRmsAbvGrd: Optional[int] = Field(
        None, description="Total rooms above grade (does not include bathrooms)"
    )
    Functional: Optional[str] = Field(None, description="Home functionality rating")
    Fireplaces: Optional[int] = Field(None, description="Number of fireplaces")
    FireplaceQu: Optional[str] = Field(None, description="Fireplace quality")
    GarageType: Optional[str] = Field(None, description="Garage location")
    GarageYrBlt: Optional[float] = Field(None, description="Year garage was built")
    GarageFinish: Optional[str] = Field(
        None, description="Interior finish of the garage"
    )
    GarageCars: Optional[int] = Field(
        None, description="Size of garage in car capacity"
    )
    GarageArea: Optional[float] = Field(
        None, description="Size of garage in square feet"
    )
    GarageQual: Optional[str] = Field(None, description="Garage quality")
    GarageCond: Optional[str] = Field(None, description="Garage condition")
    PavedDrive: Optional[str] = Field(None, description="Paved driveway")
    WoodDeckSF: Optional[int] = Field(None, description="Wood deck area in square feet")
    OpenPorchSF: Optional[int] = Field(
        None, description="Open porch area in square feet"
    )
    EnclosedPorch: Optional[int] = Field(
        None, description="Enclosed porch area in square feet"
    )
    ThreeSsnPorch: Optional[int] = Field(
        None, description="Three season porch area in square feet"
    )
    ScreenPorch: Optional[int] = Field(
        None, description="Screen porch area in square feet"
    )
    PoolArea: Optional[int] = Field(None, description="Pool area in square feet")
    PoolQC: Optional[str] = Field(None, description="Pool quality")
    Fence: Optional[str] = Field(None, description="Fence quality")
    MiscFeature: Optional[str] = Field(
        None, description="Miscellaneous feature not covered in other categories"
    )
    MiscVal: Optional[int] = Field(None, description="Value of miscellaneous feature")
    MoSold: Optional[int] = Field(None, description="Month sold")
    YrSold: Optional[int] = Field(None, description="Year sold")
    SaleType: Optional[str] = Field(None, description="Type of sale")
    SaleCondition: Optional[str] = Field(None, description="Condition of sale")

    class Config:
        populate_by_name = True  # Allow both field name and alias

    @classmethod
    def get_field_mapping(cls):
        """Map field names to original column names."""
        return {
            "FirstFlrSF": "1stFlrSF",
            "SecondFlrSF": "2ndFlrSF",
            "ThreeSsnPorch": "3SsnPorch",
        }


class PredictionResponse(BaseModel):
    """Schema for prediction response."""

    predicted_price: float = Field(..., description="Predicted house price")
    confidence_interval: Optional[Dict[str, float]] = Field(
        None, description="Confidence interval for prediction"
    )


class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction request."""

    houses: List[Dict[str, Any]] = Field(
        ..., description="List of house feature dictionaries"
    )


class BatchPredictionResponse(BaseModel):
    """Schema for batch prediction response."""

    predictions: List[float] = Field(..., description="List of predicted prices")
    count: int = Field(..., description="Number of predictions")
    statistics: Dict[str, float] = Field(..., description="Statistics of predictions")


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    version: str = Field(..., description="API version")


class ModelInfoResponse(BaseModel):
    """Schema for model info response."""

    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    performance: Dict[str, float] = Field(..., description="Model performance metrics")
    features_count: int = Field(..., description="Number of features")
