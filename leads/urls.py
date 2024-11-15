from django.urls import path
from leads.views import *



urlpatterns = [



    # Leads
    path('create_lead/upload', CreateLeadUpload.as_view(), name='create_lead_upload'), #file upload
    path('create_lead/manual', CreateLeadManual.as_view(), name='create_lead_manual'), #file upload
    path('update_lead/<str:client_id>', UpdateLead.as_view(),  name='update_lead' ), #view_all_leads

    # all leads
    path('all_leads/<int:limit>/<int:page>', AllLeads.as_view()), #all_leads



    path('lead_related_services/<str:client_id>', LeadRelatedServices.as_view(), name='lead_related_services'), #view_all_leads
    path('lead_visibility/<str:type>/<int:id>', LeadVisibility.as_view(), name='lead_visibility'), #view_all_leads
    path('add_service_category', AddServiceCategory.as_view(), name='add_service_category'), #all tables submit
    path('lead_status_update', LeadStatusUpdate.as_view(), name="lead_status_update"), #all tables submit

    path('lead_history/<str:lead_id>', GetLeadHistory.as_view(), name='lead_history'),
    
    path('add_subscription_duration/<str:lead_id>', AddSubscriptionDuration.as_view(), name='add_subscription_duration'),
    path('service_associate/submit/<str:lead_id>', ServiceAssociateSubmit.as_view(), name="service_associate_submit"),
    path('create_followup', CreateFollowUp.as_view(), name="create_followup"), #all tables submit
    path('ask_for_details_email', AskForDetailEmail.as_view(), name="ask_for_details_email"),
    path('preview_mou/<str:lead_id>', PreviewMou.as_view(), name="preview_mou"),
    path('email_mou/<str:lead_id>', EmailMou.as_view(), name="email_mou"),
    path('mou_for_approval/<str:lead_id>', UploadMouApproval.as_view(), name="mou_for_approval"),
    path('payment_proof_for_approval/<str:lead_id>', UploadPaymentProofApproval.as_view(), name="payment_proof_for_approval"),
    path('raise_invoice/<str:lead_id>', RaiseInvoice.as_view(), name="raise_invoice"),
    path('reason_submit/<str:table>', ReasonSubmit.as_view(), name="reason_submit"), #all tables submit
    path('lead_search/<str:attribute>/<str:data>', LeadsSearch.as_view(), name="lead_search"), #view_all_leads

    



    # payments
    path('update_payment_status/<str:lead_id>/<str:payment_approval_status>', UpdatePaymentStatus.as_view(), name="update_payment_status"),






    # Lead Actions
    path('assign_associate', AssignAssociate.as_view(), name='assign_associate'), #all tables submit
    path('email_proposal', EmailProposal.as_view(), name='email_proposal'),
    path('bulk_actions_lead/<str:type>', BulkActionLead.as_view(), name='bulk_actions_lead'),



    # services
    path('create_services/<str:type>', CreateServices.as_view(), name='create_services'),
    path('update_services/<str:type>/<int:id>', UpdateServices.as_view(), name='update_services'),
    path('archive_services/<str:type>/<int:id>', ArchiveServices.as_view(), name='archive_services'),
    path('restore_services/<str:type>/<int:id>', RestoreServices.as_view(), name='restore_services'),





    # path('create_segment', CreateSegment.as_view(), name='create_segment'),
    # path('view_segment', ViewSegment.as_view()),
    # path('edit_segment/<int:id>', EditSegment.as_view(), name="edit_segment"),
    # path('archive_segment/<int:id>', ArchiveSegment.as_view(), name='archive_segment'),
    # path('view_archive_segment', ViewArchiveSegment.as_view(), name='view_archive_segment'),
    # path('unarchive_segment/<int:id>', UnarchiveSegment.as_view(), name='restore_segment' ),

    # path('create_service', CreateService.as_view(), name="create_service"),
    # path('view_service', ViewService.as_view()),
    # path('edit_service/<int:id>', EditService.as_view(), name="edit_service"),
    # path('archive_service/<int:id>', ArchiveService.as_view(), name='archive_service'),
    # path('view_archive_service', ViewArchiveService.as_view()),
    # path('unarchive_service/<int:id>', UnarchiveService.as_view(), name='restore_service'),

    # path('create_marketplace', CreateMarketplace.as_view(), name='create_marketplace'),
    # path('view_marketplace', ViewMarketplace.as_view()),
    # path('edit_marketplace/<int:id>', EditMarketplace.as_view(), name='edit_marketplace'),
    # path('archive_marketplace/<int:id>', ArchiveMarketplace.as_view(), name='archive_marketplace'),
    # path('view_archive_marketplace', ViewArchiveMarketplace.as_view() ),
    # path('unarchive_marketplace/<int:id>', UnarchiveMarketplace.as_view(), name='restore_marketplace' ),

    # path('create_program', CreateProgram.as_view(), name="create_program"),
    # path('view_program', ViewProgram.as_view()),
    # path('edit_program/<int:id>', EditProgram.as_view(), name='edit_program'),
    # path('archive_program/<int:id>', ArchiveProgram.as_view(),  name='archive_program'),
    # path('view_archive_program', ViewArchiveProgram.as_view()),
    # path('unarchive_program/<int:id>', UnarchiveProgram.as_view(), name='restore_program'),

    # commercials
    path('active_commercials/<int:program_id>', ActiveCommercials.as_view(), name="active_commercials"),
    path('inactive_commercials/<int:program_id>', InactiveCommercials.as_view(), name="inactive_commercials"),
    path('commercial_visibility/<str:type>/<int:id>', CommercialVisibility.as_view(), name='commercial_visibility'),
    path('approve_commercial/<str:approval_type>/<str:lead_id>', ApproveCommercial.as_view(), name="approve_commercial" ), #view_all_leads
    path('reject_commercial/<str:approval_type>/<str:lead_id>', RejectCommercial.as_view(), name="reject_commercial" ), #view_all_leads


    
    # path('restore_commercials/<int:id>', UnarchiveServiceCommercials.as_view(), name='restore_commercials'),
    
]
