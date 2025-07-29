from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Trip, Group, GroupMember, Expense, ChecklistItem, BudgetItem, Recommendation, GalleryImage, ChatMessage
from datetime import datetime
import os
from io import BytesIO
import base64

pdf_generator_bp = Blueprint('pdf_generator_bp', __name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

@pdf_generator_bp.route('/api/trips/<int:trip_id>/generate-pdf', methods=['POST'])
@jwt_required()
def generate_trip_pdf(trip_id):
    if not REPORTLAB_AVAILABLE:
        return jsonify({'error': 'PDF generation not available. Install reportlab: pip install reportlab'}), 500
    
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Get trip details
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or unauthorized'}), 404
    
    # Get group details
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify({'error': 'No group found for this trip'}), 404
    
    # Generate PDF
    try:
        pdf_buffer = create_trip_pdf(trip, group, data.get('include_sections', {}))
        
        # Save PDF temporarily
        filename = f"trip_report_{trip_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join('uploads', filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        return jsonify({
            'message': 'PDF generated successfully',
            'filename': filename,
            'download_url': f'/api/trips/{trip_id}/download-pdf/{filename}',
            'size_bytes': len(pdf_buffer.getvalue())
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@pdf_generator_bp.route('/api/trips/<int:trip_id>/download-pdf/<filename>', methods=['GET'])
@jwt_required()
def download_trip_pdf(trip_id, filename):
    user_id = int(get_jwt_identity())
    
    # Verify trip ownership
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or unauthorized'}), 404
    
    filepath = os.path.join('uploads', filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'PDF file not found'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=f"{trip.name}_Report.pdf",
        mimetype='application/pdf'
    )

def create_trip_pdf(trip, group, include_sections):
    """Create a comprehensive PDF report for the trip"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6366f1')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#4f46e5')
    )
    
    # Build content
    content = []
    
    # Title Page
    content.append(Paragraph(f"Trip Report: {trip.name}", title_style))
    content.append(Spacer(1, 20))
    
    # Trip Overview
    content.append(Paragraph("Trip Overview", heading_style))
    
    trip_data = [
        ['Trip Name:', trip.name],
        ['Start Date:', trip.start_date],
        ['End Date:', trip.end_date],
        ['Description:', trip.description or 'No description provided'],
        ['Status:', 'Finalized' if trip.finalized else 'In Planning'],
        ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    trip_table = Table(trip_data, colWidths=[2*inch, 4*inch])
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    content.append(trip_table)
    content.append(Spacer(1, 20))
    
    # Group Members
    members = GroupMember.query.filter_by(group_id=group.id).all()
    if members or include_sections.get('members', True):
        content.append(Paragraph("Group Members", heading_style))
        
        member_data = [['Member ID', 'Join Date']]
        for member in members:
            member_data.append([
                str(member.user_id),
                'N/A'  # You could add a join_date field to GroupMember
            ])
        
        if len(member_data) > 1:
            member_table = Table(member_data, colWidths=[2*inch, 2*inch])
            member_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(member_table)
        else:
            content.append(Paragraph("No members found.", styles['Normal']))
        
        content.append(Spacer(1, 20))
    
    # Budget Summary
    if include_sections.get('budget', True):
        content.append(Paragraph("Budget Summary", heading_style))
        
        budget_items = BudgetItem.query.filter_by(group_id=group.id).all()
        expenses = Expense.query.filter_by(group_id=group.id).all()
        
        total_budget = sum(item.amount for item in budget_items)
        total_expenses = sum(expense.amount for expense in expenses)
        remaining = total_budget - total_expenses
        
        budget_summary = [
            ['Total Budget:', f'${total_budget:.2f}'],
            ['Total Expenses:', f'${total_expenses:.2f}'],
            ['Remaining:', f'${remaining:.2f}'],
            ['Budget Status:', 'Over Budget' if remaining < 0 else 'Within Budget']
        ]
        
        budget_table = Table(budget_summary, colWidths=[2*inch, 2*inch])
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ]))
        
        content.append(budget_table)
        content.append(Spacer(1, 20))
    
    # Detailed Expenses
    if include_sections.get('expenses', True) and expenses:
        content.append(Paragraph("Detailed Expenses", heading_style))
        
        expense_data = [['Date', 'Category', 'Amount', 'Note']]
        for expense in expenses:
            expense_data.append([
                expense.timestamp.strftime('%Y-%m-%d'),
                expense.category or 'Uncategorized',
                f'${expense.amount:.2f}',
                expense.note or 'No note'
            ])
        
        expense_table = Table(expense_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(expense_table)
        content.append(Spacer(1, 20))
    
    # Checklist Items
    if include_sections.get('checklist', True):
        checklist_items = ChecklistItem.query.filter_by(group_id=group.id).all()
        if checklist_items:
            content.append(Paragraph("Checklist Items", heading_style))
            
            checklist_data = [['Item', 'Type', 'Status', 'Added Date']]
            for item in checklist_items:
                checklist_data.append([
                    item.text,
                    item.type.title(),
                    '✓ Completed' if item.completed else '○ Pending',
                    item.timestamp.strftime('%Y-%m-%d')
                ])
            
            checklist_table = Table(checklist_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
            checklist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(checklist_table)
            content.append(Spacer(1, 20))
    
    # Recommendations
    if include_sections.get('recommendations', True):
        recommendations = Recommendation.query.filter_by(group_id=group.id).all()
        if recommendations:
            content.append(Paragraph("Recommendations", heading_style))
            
            rec_data = [['Title', 'Type', 'Comment', 'Date']]
            for rec in recommendations:
                rec_data.append([
                    rec.title,
                    rec.type or 'General',
                    rec.comment or 'No comment',
                    rec.timestamp.strftime('%Y-%m-%d')
                ])
            
            rec_table = Table(rec_data, colWidths=[2*inch, 1*inch, 2*inch, 1*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(rec_table)
            content.append(Spacer(1, 20))
    
    # Chat Summary
    if include_sections.get('chat', False):
        messages = ChatMessage.query.filter_by(group_id=group.id).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        if messages:
            content.append(Paragraph("Recent Chat Messages (Last 10)", heading_style))
            
            for msg in reversed(messages):  # Show oldest first
                msg_text = f"User {msg.user_id}: {msg.message}"
                content.append(Paragraph(msg_text, styles['Normal']))
                content.append(Spacer(1, 6))
    
    # Footer
    content.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    content.append(Paragraph("Generated by TripBox - Smart Travel Planning", footer_style))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    
    return buffer

@pdf_generator_bp.route('/api/trips/<int:trip_id>/pdf-preview', methods=['POST'])
@jwt_required()
def preview_pdf_content(trip_id):
    """Get a preview of what will be included in the PDF"""
    user_id = int(get_jwt_identity())
    
    # Get trip details
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return jsonify({'error': 'Trip not found or unauthorized'}), 404
    
    # Get group details
    group = Group.query.filter_by(trip_id=trip_id).first()
    if not group:
        return jsonify({'error': 'No group found for this trip'}), 404
    
    # Collect all data for preview
    members = GroupMember.query.filter_by(group_id=group.id).all()
    budget_items = BudgetItem.query.filter_by(group_id=group.id).all()
    expenses = Expense.query.filter_by(group_id=group.id).all()
    checklist_items = ChecklistItem.query.filter_by(group_id=group.id).all()
    recommendations = Recommendation.query.filter_by(group_id=group.id).all()
    messages = ChatMessage.query.filter_by(group_id=group.id).count()
    photos = GalleryImage.query.filter_by(group_id=group.id).count()
    
    preview = {
        'trip_info': {
            'name': trip.name,
            'dates': f"{trip.start_date} to {trip.end_date}",
            'description': trip.description,
            'status': 'Finalized' if trip.finalized else 'In Planning'
        },
        'statistics': {
            'members_count': len(members),
            'budget_items_count': len(budget_items),
            'expenses_count': len(expenses),
            'checklist_items_count': len(checklist_items),
            'recommendations_count': len(recommendations),
            'chat_messages_count': messages,
            'photos_count': photos
        },
        'financial_summary': {
            'total_budget': sum(item.amount for item in budget_items),
            'total_expenses': sum(expense.amount for expense in expenses),
            'remaining_budget': sum(item.amount for item in budget_items) - sum(expense.amount for expense in expenses)
        },
        'sections_available': {
            'trip_overview': True,
            'members': len(members) > 0,
            'budget_summary': len(budget_items) > 0 or len(expenses) > 0,
            'detailed_expenses': len(expenses) > 0,
            'checklist': len(checklist_items) > 0,
            'recommendations': len(recommendations) > 0,
            'chat_summary': messages > 0,
            'photo_gallery': photos > 0
        }
    }
    
    return jsonify(preview) 