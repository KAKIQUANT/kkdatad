from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import pandas as pd

from kkdatad.utils.database import get_db
from kkdatad.utils.auth import get_current_user
import kkdatad.utils.models as models
from kkfadb.validation.validators import FactorValidator
from kkfadb.visualization.plots import FactorVisualizer
from kkfadb.factors.technical.momentum import MomentumFactor, VolumePriceFactor
from kkdatad.utils.factor_utils import compute_factor, get_factor_data, compute_factor_exposure, compute_factor_return

factor_router = APIRouter()

class FactorCreate(BaseModel):
    name: str
    description: str
    category: str
    code: str
    metadata: dict = {}
    is_public: bool = False

class FactorResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    version: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    is_public: bool

@factor_router.post("/factors/", response_model=FactorResponse)
async def create_factor(
    factor: FactorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new factor"""
    db_factor = models.Factor(
        name=factor.name,
        description=factor.description,
        category=factor.category,
        code=factor.code,
        metadata=factor.metadata,
        is_public=factor.is_public,
        created_by=current_user.id
    )
    db.add(db_factor)
    db.commit()
    db.refresh(db_factor)
    return db_factor

@factor_router.get("/factors/", response_model=List[FactorResponse])
async def list_factors(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List factors with optional category filter"""
    query = db.query(models.Factor).filter(
        (models.Factor.created_by == current_user.id) |
        (models.Factor.is_public == True)
    )
    if category:
        query = query.filter(models.Factor.category == category)
    return query.all()

@factor_router.get("/factors/{factor_id}", response_model=FactorResponse)
async def get_factor(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get factor details"""
    factor = db.query(models.Factor).filter(models.Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")
    if not factor.is_public and factor.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this factor")
    return factor

@factor_router.put("/factors/{factor_id}")
async def update_factor(
    factor_id: int,
    factor_update: FactorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update factor"""
    factor = db.query(models.Factor).filter(models.Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")
    if factor.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this factor")
    
    for key, value in factor_update.dict().items():
        setattr(factor, key, value)
    factor.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(factor)
    return factor

@factor_router.delete("/factors/{factor_id}")
async def delete_factor(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete factor"""
    factor = db.query(models.Factor).filter(models.Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")
    if factor.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this factor")
    
    db.delete(factor)
    db.commit()
    return {"detail": "Factor deleted"}

@factor_router.post("/factors/{factor_id}/evaluate")
async def evaluate_factor(
    factor_id: int,
    returns_data: pd.DataFrame,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Evaluate factor performance"""
    factor = db.query(models.Factor).filter(models.Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")

    # Use kkfadb validator
    validator = FactorValidator()
    
    # Get factor data
    factor_data = compute_factor(factor.code, returns_data)
    
    # Run validations
    evaluation = {
        "coverage": validator.check_coverage(factor_data),
        "normality": validator.check_normality(factor_data),
        "autocorr": validator.check_autocorrelation(factor_data),
        "ic": validator.compute_ic(factor_data, returns_data['returns'])
    }
    
    # Save evaluation results
    db_eval = models.FactorEvaluation(
        factor_id=factor_id,
        user_id=current_user.id,
        ic_mean=evaluation['ic']['ic'],
        ic_std=evaluation['ic']['t_stat'],
        metadata=evaluation
    )
    db.add(db_eval)
    db.commit()
    
    return evaluation 

@factor_router.get("/factors/{factor_id}/plot")
async def plot_factor(
    factor_id: int,
    plot_type: str = "returns",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate factor visualization"""
    factor = db.query(models.Factor).filter(models.Factor.id == factor_id).first()
    if not factor:
        raise HTTPException(status_code=404, detail="Factor not found")
        
    # Get factor data
    factor_data = get_factor_data(factor_id)
    
    visualizer = FactorVisualizer()
    
    if plot_type == "returns":
        return visualizer.plot_factor_returns(factor_data)
    elif plot_type == "distribution":
        return visualizer.plot_factor_distribution(factor_data)
    else:
        raise HTTPException(status_code=400, detail="Invalid plot type")

@factor_router.post("/factors/compute/technical")
async def compute_technical_factor(
    factor_type: str,
    parameters: Dict,
    data: pd.DataFrame,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Compute technical factor values"""
    if factor_type == "momentum":
        factor = MomentumFactor(lookback_period=parameters.get("lookback_period", 20))
    elif factor_type == "volume_price":
        factor = VolumePriceFactor(window=parameters.get("window", 20))
    else:
        raise HTTPException(status_code=400, detail="Unsupported factor type")
        
    try:
        factor_data = factor.compute(data)
        return {
            "name": factor.name,
            "data": factor_data.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@factor_router.get("/factors/exposure")
async def get_factor_exposure(
    order_book_ids: str,
    start_date: str,
    end_date: str,
    factors: Optional[str] = None,
    industry_mapping: str = 'sws_2021',
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get factor exposure data"""
    # Parse parameters
    order_book_id_list = order_book_ids.split(',')
    factor_list = factors.split(',') if factors else None
    
    # Get factor data and calculate exposures
    data = compute_factor_exposure(
        order_book_id_list,
        start_date,
        end_date,
        factor_list,
        industry_mapping
    )
    
    return {"data": data.to_dict()}

@factor_router.get("/factors/return")
async def get_factor_return(
    start_date: str,
    end_date: str,
    factors: Optional[str] = None,
    universe: str = 'whole_market',
    method: str = 'implicit',
    industry_mapping: str = 'sws_2021',
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get factor returns"""
    factor_list = factors.split(',') if factors else None
    
    # Calculate factor returns
    data = compute_factor_return(
        start_date,
        end_date,
        factor_list,
        universe,
        method,
        industry_mapping
    )
    
    return {"data": data.to_dict()}