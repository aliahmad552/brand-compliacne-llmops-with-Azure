import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

# define the schema for a single component
class ComplianceIssue(TypedDict):

    category: str
    description: str
    severity: str
    timestamp: Optional[str]

# define the global graph state
class VideoAuditState(TypedDict):
    """
    Defines the data schema for langgrpah execution content
    Mian container : holds all the information about the audit
    right from the initial URL to the final report
    """
    # input parameters
    video_url : str
    video_id: str

    # ingestion and extraction data
    local_file_path : Optional[str]
    video_metadata : Dict[str,Any]
    transcript : Optional[str]
    ocr_text : List[str]

    # analysis output
    compliance_results : Annotated[List[ComplianceIssue],operator.add]

    # final deliverables:
    final_status : str # PASS | FAIL
    final_report : str

    # system observability
    # errors : API timeout, system level errors
    errors : Annotated[List[str], operator.add]
