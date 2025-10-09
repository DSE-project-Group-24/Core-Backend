from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.transfer import   TransferApprove, TransferReject, TransferCreateIn, TransferApproveIn
from app.auth.dependencies import get_current_user
from app.services.transfer_service import (
    create_transfer_request_service,
    list_my_outgoing_transfers_service,
    list_incoming_transfers_for_admin_service,
    approve_transfer_service,
    reject_transfer_service,
)
router = APIRouter()


@router.post("/", summary="Create a transfer request (nurse)")
def create_transfer(
    body: TransferCreateIn,
    user= Depends(get_current_user),
):
    """
    - Only a nurse who **currently manages** the accident may create the transfer.
    - `from_hospital` is taken from the nurse's hospital (server-side).
    - `approved_by` and `transfer time to second hospital` are **not** set here.
    """
    return create_transfer_request_service(
        accident_id=body.accident_id,
        to_hospital_id=body.to_hospital,
        user=user,
    )


@router.get("/outgoing", summary="List my outgoing transfer requests (nurse)")
def list_outgoing_transfers(
    user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Transfers created from the nurse's hospital.
    """
    return list_my_outgoing_transfers_service(user=user)


@router.get("/incoming", summary="List incoming transfer requests (admin)")
def list_incoming_transfers_for_admin(
    user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Pending transfers where `to_hospital` equals the admin's hospital.
    """
    return list_incoming_transfers_for_admin_service(user=user)


@router.post("/{transfer_id}/approve", summary="Approve a transfer (admin)")
def approve_transfer(
    transfer_id: str,
    body: TransferApproveIn,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Approves a transfer **atomically** (via SQL function `approve_transfer`):
      1) Reassigns Accident Record.managed_by to the selected nurse
      2) Fills `approved_by` and `"transfer time to second hospital"`
      3) Inserts into `Hospital_Patient`
    """
    return approve_transfer_service(
        transfer_id=transfer_id,
        new_nurse_user_id=body.new_nurse_user_id,
        transfer_time_category=body.transfer_time_category,
        user=user,
    )


@router.delete("/{transfer_id}", summary="Reject a transfer (admin)")
def reject_transfer(
    transfer_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Rejects a pending transfer (deletes the Transfer row).
    """
    return reject_transfer_service(
        transfer_id=transfer_id,
        user=user,
    )