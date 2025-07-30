from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Group, GroupMember, Trip, User, Expense, Photo, ChecklistItem, Poll, PollVote, ChatMessage
from notifications import create_group_notification
import json
from datetime import datetime
import io
import os

# Try to import reportlab, but handle gracefully if not available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
    print("✅ ReportLab library available")
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab library not available - PDF generation disabled")

pdf_bp = Blueprint('pdf_bp', __name__)

# POST: Finalize group and generate PDF
@pdf_bp.route('/api/groups/<int:group_id>/finalize', methods=['POST'])
@jwt_required()
def finalize_group(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is the group creator
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    if group.creator_id != user_id:
        return jsonify({'error': 'Only the group creator can finalize the group'}), 403
    
    if not REPORTLAB_AVAILABLE:
        # Create notifications for all group members (without PDF)
        create_group_notification(
            group_id=group_id,
            notification_type='pdf_generated',
            title='Group Finalized',
            message=f'Your trip has been finalized. Text itinerary is available for download.',
            exclude_user_id=user_id
        )
        
        return jsonify({
            'message': 'Group finalized successfully (text itinerary available)',
            'pdf_url': f'/api/groups/{group_id}/pdf'
        }), 200
    
    try:
        # Generate PDF
        pdf_data = generate_trip_itinerary_pdf(group_id)
        
        # Save PDF to file (in a real app, you'd save to cloud storage)
        pdf_filename = f"itinerary_group_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join('uploads', pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        
        # Update group status (you could add a finalized field to the Group model)
        # group.finalized = True
        # db.session.commit()
        
        # Create notifications for all group members
        create_group_notification(
            group_id=group_id,
            notification_type='pdf_generated',
            title='Itinerary PDF Generated',
            message=f'Your trip itinerary PDF has been generated and is ready for download.',
            exclude_user_id=user_id
        )
        
        return jsonify({
            'message': 'Group finalized successfully',
            'pdf_filename': pdf_filename,
            'pdf_url': f'/api/groups/{group_id}/pdf'
        }), 200
        
    except Exception as e:
        print(f"Error finalizing group: {e}")
        if not REPORTLAB_AVAILABLE:
            return jsonify({'error': 'PDF generation is not available. Please install reportlab library.'}), 503
        return jsonify({'error': 'Failed to finalize group'}), 500

# GET: Download PDF itinerary
@pdf_bp.route('/api/groups/<int:group_id>/pdf', methods=['GET'])
@jwt_required()
def download_pdf(group_id):
    user_id = int(get_jwt_identity())
    
    # Check if user is a member of the group
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    if not REPORTLAB_AVAILABLE:
        # Return text-based itinerary as fallback
        return generate_text_itinerary(group_id)
    
    try:
        # Generate PDF
        pdf_data = generate_trip_itinerary_pdf(group_id)
        
        # Return PDF as file download
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'itinerary_group_{group_id}.pdf'
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({'error': 'Failed to generate PDF'}), 500

def generate_text_itinerary(group_id):
    """Generate a simple text-based itinerary when PDF is not available"""
    try:
        # Get group and trip information
        group = Group.query.get(group_id)
        trip = Trip.query.get(group.trip_id)
        
        # Get all members
        members = GroupMember.query.filter_by(group_id=group_id).all()
        member_users = [User.query.get(member.user_id) for member in members]
        
        # Get expenses
        expenses = Expense.query.filter_by(group_id=group_id).all()
        
        # Get checklist items
        checklist_items = ChecklistItem.query.filter_by(group_id=group_id).all()
        
        # Build text content
        content = f"""
TRIP ITINERARY
==============

Group: {group.name}
Trip: {trip.name}
Dates: {trip.start_date} to {trip.end_date}
Status: {'Finalized' if trip.finalized else 'Planning'}

DESCRIPTION
-----------
{trip.description or 'No description provided'}

MEMBERS
-------
"""
        
        for user in member_users:
            if user:
                content += f"- {user.name} ({user.email})\n"
        
        if expenses:
            content += "\nEXPENSES\n--------\n"
            total = 0
            for expense in expenses:
                user = User.query.get(expense.user_id)
                user_name = user.name if user else 'Unknown'
                content += f"- ${expense.amount:.2f} ({expense.category or 'General'}) by {user_name}\n"
                if expense.note:
                    content += f"  Note: {expense.note}\n"
                total += expense.amount
            content += f"\nTotal: ${total:.2f}\n"
        
        if checklist_items:
            content += "\nCHECKLIST\n---------\n"
            for item in checklist_items:
                status = "✓" if item.is_completed else "○"
                content += f"{status} {item.text} ({item.item_type})\n"
        
        # Return as text file
        return send_file(
            io.BytesIO(content.encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'itinerary_group_{group_id}.txt'
        )
        
    except Exception as e:
        print(f"Error generating text itinerary: {e}")
        return jsonify({'error': 'Failed to generate itinerary'}), 500

def generate_trip_itinerary_pdf(group_id):
    """Generate a comprehensive PDF itinerary for a group"""
    
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab library is not available")
    
    # Get group and trip information
    group = Group.query.get(group_id)
    trip = Trip.query.get(group.trip_id)
    
    # Get all members
    members = GroupMember.query.filter_by(group_id=group_id).all()
    member_users = [User.query.get(member.user_id) for member in members]
    
    # Get expenses
    expenses = Expense.query.filter_by(group_id=group_id).all()
    
    # Get photos
    photos = Photo.query.filter_by(group_id=group_id).all()
    
    # Get checklist items
    checklist_items = ChecklistItem.query.filter_by(group_id=group_id).all()
    
    # Get polls
    polls = Poll.query.filter_by(group_id=group_id).all()
    
    # Get recent chat messages
    chat_messages = ChatMessage.query.filter_by(group_id=group_id).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    normal_style = styles['Normal']
    
    # Cover page
    story.append(Paragraph(f"Trip Itinerary", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Group: {group.name}", heading_style))
    story.append(Paragraph(f"Trip: {trip.name}", heading_style))
    story.append(Paragraph(f"Dates: {trip.start_date} to {trip.end_date}", normal_style))
    if trip.description:
        story.append(Paragraph(f"Description: {trip.description}", normal_style))
    story.append(PageBreak())
    
    # Trip Information
    story.append(Paragraph("Trip Information", heading_style))
    trip_info = [
        ['Trip Name', trip.name],
        ['Start Date', trip.start_date],
        ['End Date', trip.end_date],
        ['Status', 'Finalized' if trip.finalized else 'Planning'],
    ]
    if trip.description:
        trip_info.append(['Description', trip.description])
    
    trip_table = Table(trip_info, colWidths=[2*inch, 4*inch])
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(trip_table)
    story.append(Spacer(1, 20))
    
    # Members
    story.append(Paragraph("Group Members", heading_style))
    member_data = [['Name', 'Email']]
    for user in member_users:
        if user:
            member_data.append([user.name, user.email])
    
    member_table = Table(member_data, colWidths=[2*inch, 4*inch])
    member_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(member_table)
    story.append(Spacer(1, 20))
    
    # Expenses
    if expenses:
        story.append(Paragraph("Expenses", heading_style))
        expense_data = [['Category', 'Amount', 'Note', 'Added By']]
        total_amount = 0
        
        for expense in expenses:
            user = User.query.get(expense.user_id)
            user_name = user.name if user else 'Unknown'
            expense_data.append([
                expense.category or 'General',
                f"${expense.amount:.2f}",
                expense.note or '',
                user_name
            ])
            total_amount += expense.amount
        
        expense_data.append(['TOTAL', f"${total_amount:.2f}", '', ''])
        
        expense_table = Table(expense_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 1*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(expense_table)
        story.append(Spacer(1, 20))
    
    # Checklist
    if checklist_items:
        story.append(Paragraph("Checklist & Packing List", heading_style))
        checklist_data = [['Type', 'Item', 'Status']]
        
        for item in checklist_items:
            status = 'Completed' if item.is_completed else 'Pending'
            checklist_data.append([
                item.item_type.title(),
                item.text,
                status
            ])
        
        checklist_table = Table(checklist_data, colWidths=[1.5*inch, 3.5*inch, 1*inch])
        checklist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(checklist_table)
        story.append(Spacer(1, 20))
    
    # Polls
    if polls:
        story.append(Paragraph("Group Decisions (Polls)", heading_style))
        
        for poll in polls:
            story.append(Paragraph(f"Q: {poll.question}", normal_style))
            
            if poll.is_finalized:
                story.append(Paragraph(f"Winner: {poll.winning_option}", normal_style))
            else:
                options = json.loads(poll.options)
                for option in options:
                    vote_count = PollVote.query.filter_by(poll_id=poll.id, selected_option=option).count()
                    story.append(Paragraph(f"• {option}: {vote_count} votes", normal_style))
            
            story.append(Spacer(1, 10))
        story.append(Spacer(1, 20))
    
    # Recent Chat Summary
    if chat_messages:
        story.append(Paragraph("Recent Group Chat", heading_style))
        
        for message in reversed(chat_messages):  # Show in chronological order
            user = User.query.get(message.user_id)
            user_name = user.name if user else 'Unknown'
            message_time = message.timestamp.strftime('%Y-%m-%d %H:%M')
            
            story.append(Paragraph(f"{user_name} ({message_time}): {message.message}", normal_style))
            story.append(Spacer(1, 5))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue() 