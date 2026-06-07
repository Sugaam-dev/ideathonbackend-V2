# # from typing import List, Optional
# # import io
# # from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, BackgroundTasks, Header
# # from fastapi.responses import StreamingResponse 
# # from sqlalchemy.orm import Session
# # from app.database import get_db
# # from app.features.auth.models import User
# # from app.features.auth.dependencies import get_current_user
# # from app.features.ideas.schemas import IdeaCreateOrUpdateRequest, IdeaResponse, AttachmentResponse
# # from app.features.ideas.models import Attachment, Idea 
# # from app.features.ideas import services

# # router = APIRouter(prefix="/api/ideas", tags=["Participant Portfolio Space"])

# # @router.post("", status_code=status.HTTP_201_CREATED, response_model=IdeaResponse)
# # def submit_new_idea(req: IdeaCreateOrUpdateRequest, background_tasks: BackgroundTasks, x_idempotency_key: Optional[str] = Header(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     return services.log_new_participant_idea(db, current_user.name, current_user.email, current_user.id, req, background_tasks, idempotency_key=x_idempotency_key)

# # @router.get("/my", response_model=List[IdeaResponse])
# # def get_my_ideas_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     return services.fetch_participant_portfolio_summary(db, current_user.id)

# # @router.get("/{idea_id}", response_model=IdeaResponse)
# # def get_idea_profile(idea_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     return services.fetch_single_idea_secured(db, idea_id, current_user.id, current_user.role)

# # @router.put("/{idea_id}", response_model=IdeaResponse)
# # def edit_idea_submission(idea_id: str, req: IdeaCreateOrUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     return services.modify_existing_participant_idea(db, idea_id, current_user.id, current_user.role == "ADMIN", req)

# # @router.post("/{idea_id}/attachments", status_code=status.HTTP_201_CREATED, response_model=AttachmentResponse)
# # async def upload_idea_document(idea_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     if file.size and file.size > 25 * 1024 * 1024:
# #         raise HTTPException(status_code=400, detail="Document assets cannot pass 25MB metrics.")
# #     return await services.store_idea_binary_file(db, idea_id, current_user.id, current_user.role == "ADMIN", file)

# # @router.get("/attachments/download/{attachment_id}")
# # def download_idea_document(attachment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     """Extracts binary BLOB arrays from cell storage and streams it to authorized callers."""
# #     attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
# #     if not attachment:
# #         raise HTTPException(status_code=404, detail="Requested file record does not exist on the server.")

# #     idea = db.query(Idea).filter(Idea.id == attachment.idea_id).first()
# #     if current_user.role not in ["ADMIN", "JURY"] and idea.user_id != current_user.id:
# #         raise HTTPException(status_code=403, detail="Access denied. Permissions insufficient.")

# #     # Stream file binary string straight out of database RAM allocations
# #     file_stream = io.BytesIO(attachment.file_data)
# #     return StreamingResponse(
# #         file_stream, 
# #         media_type="application/octet-stream", 
# #         headers={"Content-Disposition": f'attachment; filename="{attachment.original_name}"'}
# #     )

# # @router.delete("/attachments/{attachment_id}", status_code=status.HTTP_200_OK)
# # def delete_idea_document(attachment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
# #     return services.delete_idea_attachment(db, attachment_id, current_user.id, current_user.role == "ADMIN")


# from typing import List, Optional
# import io
# from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, BackgroundTasks, Header
# from fastapi.responses import StreamingResponse 
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.features.auth.models import User
# from app.features.auth.dependencies import get_current_user, require_completed_profile
# from app.features.ideas.schemas import IdeaCreateOrUpdateRequest, IdeaResponse, AttachmentResponse
# from app.features.ideas.models import Attachment, Idea 
# from app.features.ideas import services

# router = APIRouter(
#     prefix="/api/ideas",
#     tags=["Participant Portfolio Space"],
#     dependencies=[Depends(require_completed_profile)]
# )

# @router.post("", status_code=status.HTTP_201_CREATED, response_model=IdeaResponse)
# def submit_new_idea(req: IdeaCreateOrUpdateRequest, background_tasks: BackgroundTasks, x_idempotency_key: Optional[str] = Header(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     return services.log_new_participant_idea(db, current_user.name, current_user.email, current_user.id, req, background_tasks, idempotency_key=x_idempotency_key)

# @router.get("/my", response_model=List[IdeaResponse])
# def get_my_ideas_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     return services.fetch_participant_portfolio_summary(db, current_user.id)

# @router.get("/{idea_id}", response_model=IdeaResponse)
# def get_idea_profile(idea_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     return services.fetch_single_idea_secured(db, idea_id, current_user.id, current_user.role)

# @router.put("/{idea_id}", response_model=IdeaResponse)
# def edit_idea_submission(idea_id: str, req: IdeaCreateOrUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     return services.modify_existing_participant_idea(db, idea_id, current_user.id, current_user.role == "ADMIN", req)

# @router.post("/{idea_id}/attachments", status_code=status.HTTP_201_CREATED, response_model=AttachmentResponse)
# async def upload_idea_document(idea_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     if file.size and file.size > 25 * 1024 * 1024:
#         raise HTTPException(status_code=400, detail="Document assets cannot pass 25MB metrics.")
#     return await services.store_idea_binary_file(db, idea_id, current_user.id, current_user.role == "ADMIN", file)

# @router.get("/attachments/download/{attachment_id}")
# def download_idea_document(attachment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     """Extracts binary BLOB arrays from cell storage and streams it to authorized callers."""
#     attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
#     if not attachment:
#         raise HTTPException(status_code=404, detail="Requested file record does not exist on the server.")

#     idea = db.query(Idea).filter(Idea.id == attachment.idea_id).first()
#     if current_user.role not in ["ADMIN", "JURY"] and idea.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="Access denied. Permissions insufficient.")

#     # Stream file binary string straight out of database RAM allocations
#     file_stream = io.BytesIO(attachment.file_data)
#     return StreamingResponse(
#         file_stream, 
#         media_type="application/octet-stream", 
#         headers={"Content-Disposition": f'attachment; filename="{attachment.original_name}"'}
#     )

# @router.delete("/attachments/{attachment_id}", status_code=status.HTTP_200_OK)
# def delete_idea_document(attachment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     return services.delete_idea_attachment(db, attachment_id, current_user.id, current_user.role == "ADMIN")



from typing import List, Optional
import io
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse 
from sqlalchemy.orm import Session
from app.database import get_db
from app.features.auth.models import User
from app.features.auth.dependencies import get_current_user, require_completed_profile
from app.features.ideas.schemas import IdeaCreateOrUpdateRequest, IdeaResponse, AttachmentResponse
from app.features.ideas.models import Attachment, AttachmentData, Idea 
from app.features.ideas import services
router = APIRouter(
    prefix="/api/ideas",
    tags=["Participant Portfolio Space"],
    dependencies=[Depends(require_completed_profile)]
)
@router.post("", status_code=status.HTTP_201_CREATED, response_model=IdeaResponse)
def submit_new_idea(req: IdeaCreateOrUpdateRequest, background_tasks: BackgroundTasks, x_idempotency_key: Optional[str] = Header(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.log_new_participant_idea(db, current_user.name, current_user.email, current_user.id, req, background_tasks, idempotency_key=x_idempotency_key)
@router.get("/my", response_model=List[IdeaResponse])
def get_my_ideas_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.fetch_participant_portfolio_summary(db, current_user.id)
@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea_profile(idea_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.fetch_single_idea_secured(db, idea_id, current_user.id, current_user.role)
@router.put("/{idea_id}", response_model=IdeaResponse)
def edit_idea_submission(idea_id: str, req: IdeaCreateOrUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.modify_existing_participant_idea(db, idea_id, current_user.id, current_user.role == "ADMIN", req)
@router.post("/{idea_id}/attachments", status_code=status.HTTP_201_CREATED, response_model=AttachmentResponse)
async def upload_idea_document(idea_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if file.size and file.size > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Document assets cannot pass 25MB metrics.")
    return await services.store_idea_binary_file(db, idea_id, current_user.id, current_user.role == "ADMIN", file)
@router.get("/attachments/download/{attachment_id}")
def download_idea_document(attachment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Extracts binary BLOB arrays from separate data table and streams it to authorized callers."""
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Requested file record does not exist on the server.")
    idea = db.query(Idea).filter(Idea.id == attachment.idea_id).first()
    if current_user.role not in ["ADMIN", "JURY"] and idea.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied. Permissions insufficient.")
    # Retrieve from separate binary table
    binary_data = db.query(AttachmentData).filter(AttachmentData.attachment_id == attachment_id).first()
    if not binary_data:
        raise HTTPException(status_code=404, detail="Document binary file payload not found in database.")
    # Stream file binary string straight out of database RAM allocations
    file_stream = io.BytesIO(binary_data.file_data)
    return StreamingResponse(
        file_stream, 
        media_type="application/octet-stream", 
        headers={"Content-Disposition": f'attachment; filename="{attachment.original_name}"'}
    )
@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_200_OK)
def delete_idea_document(attachment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.delete_idea_attachment(db, attachment_id, current_user.id, current_user.role == "ADMIN")
