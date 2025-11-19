import pandas as pd
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from django.db.models import Count
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime

from .models import EquipmentDataset, Equipment
from .serializers import EquipmentDatasetSerializer, DatasetSummarySerializer, EquipmentSerializer


class EquipmentDatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing equipment datasets.
    Supports CRUD operations and CSV upload with analysis.
    """
    queryset = EquipmentDataset.objects.all()
    serializer_class = EquipmentDatasetSerializer
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] for production
    
    def get_queryset(self):
        """Return all datasets for retrieve, or last 5 for list"""
        if self.action == 'list':
            return EquipmentDataset.objects.all().order_by('-uploaded_at')[:5]
        return EquipmentDataset.objects.all()
    
    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """
        Upload and process a CSV file containing equipment data.
        Automatically calculates summary statistics.
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        # Validate file extension
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Read CSV file using pandas
            df = pd.read_csv(csv_file)
            
            # Validate required columns
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            if not all(col in df.columns for col in required_columns):
                return Response(
                    {'error': f'CSV must contain columns: {", ".join(required_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate summary statistics
            total_count = len(df)
            avg_flowrate = float(df['Flowrate'].mean())
            avg_pressure = float(df['Pressure'].mean())
            avg_temperature = float(df['Temperature'].mean())
            
            # Get equipment type distribution
            type_distribution = df['Type'].value_counts().to_dict()
            
            # Create dataset record
            dataset_name = csv_file.name
            dataset = EquipmentDataset.objects.create(
                name=dataset_name,
                uploaded_by=request.user if request.user.is_authenticated else None,
                file=csv_file,
                total_count=total_count,
                avg_flowrate=avg_flowrate,
                avg_pressure=avg_pressure,
                avg_temperature=avg_temperature,
                equipment_types=type_distribution
            )
            
            # Create equipment records
            equipment_objects = []
            for _, row in df.iterrows():
                equipment_objects.append(
                    Equipment(
                        dataset=dataset,
                        equipment_name=row['Equipment Name'],
                        type=row['Type'],
                        flowrate=float(row['Flowrate']),
                        pressure=float(row['Pressure']),
                        temperature=float(row['Temperature'])
                    )
                )
            
            # Bulk create equipment records
            Equipment.objects.bulk_create(equipment_objects)
            
            # Maintain only last 5 datasets
            all_datasets = EquipmentDataset.objects.all()
            if all_datasets.count() > 5:
                datasets_to_delete = all_datasets[5:]
                for ds in datasets_to_delete:
                    ds.delete()
            
            # Return the created dataset with equipment items
            serializer = self.get_serializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get summary statistics for a specific dataset"""
        dataset = self.get_object()
        
        summary_data = {
            'id': dataset.id,
            'name': dataset.name,
            'uploaded_at': dataset.uploaded_at,
            'total_count': dataset.total_count,
            'statistics': {
                'avg_flowrate': round(dataset.avg_flowrate, 2),
                'avg_pressure': round(dataset.avg_pressure, 2),
                'avg_temperature': round(dataset.avg_temperature, 2),
            },
            'equipment_types': dataset.equipment_types,
        }
        
        return Response(summary_data)
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate a PDF report for a specific dataset"""
        dataset = self.get_object()
        
        # Create the HttpResponse object with PDF header
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset.id}.pdf"'
        
        # Create the PDF object
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
        )
        
        # Title
        title = Paragraph("Chemical Equipment Analysis Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Dataset Info
        info_data = [
            ['Dataset Name:', dataset.name],
            ['Upload Date:', dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Equipment:', str(dataset.total_count)],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary Statistics
        elements.append(Paragraph("Summary Statistics", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        stats_data = [
            ['Metric', 'Average Value'],
            ['Flowrate', f"{dataset.avg_flowrate:.2f}"],
            ['Pressure', f"{dataset.avg_pressure:.2f}"],
            ['Temperature', f"{dataset.avg_temperature:.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Equipment Type Distribution
        elements.append(Paragraph("Equipment Type Distribution", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        type_data = [['Equipment Type', 'Count']]
        for eq_type, count in dataset.equipment_types.items():
            type_data.append([eq_type, str(count)])
        
        type_table = Table(type_data, colWidths=[3*inch, 3*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(type_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Equipment Details
        elements.append(Paragraph("Equipment Details", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
        for equipment in dataset.equipment_items.all()[:20]:  # Limit to first 20
            equipment_data.append([
                equipment.equipment_name[:20],  # Truncate long names
                equipment.type[:15],
                f"{equipment.flowrate:.1f}",
                f"{equipment.pressure:.1f}",
                f"{equipment.temperature:.1f}"
            ])
        
        equipment_table = Table(equipment_data, colWidths=[1.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(equipment_table)
        
        # Build PDF
        doc.build(elements)
        
        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def history_list(request):
    """Get list of all dataset summaries (last 5)"""
    datasets = EquipmentDataset.objects.all().order_by('-uploaded_at')[:5]
    serializer = DatasetSummarySerializer(datasets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'ok',
        'message': 'Chemical Equipment Visualizer API is running',
        'timestamp': datetime.now().isoformat()
    })
