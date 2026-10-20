import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "gads-ai-bridge — Google Ads API Tool Design Document")
            self.setStrokeColor(colors.HexColor("#CCCCCC"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, text)
        self.drawString(54, 40, "Confidential — For Google Ads API Basic Access Review Only")
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=64
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A73E8"),
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#444444"),
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A73E8"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#202124"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#333333"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4
    )

    meta_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#DADCE0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E8EAED")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#202124")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#3C4043")),
    ])

    code_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ])

    story = []

    # Title & Metadata
    story.append(Paragraph("Google Ads API Design & Functional Document", title_style))
    story.append(Paragraph("Tool Name: <b>gads-ai-bridge</b> | In-House Campaign Performance & Audit Tool", subtitle_style))

    meta_data = [
        [Paragraph("Application Name:"), Paragraph("gads-ai-bridge")],
        [Paragraph("Tool Type:"), Paragraph("Internal In-House Marketing Reporting & Audit Tool")],
        [Paragraph("Access Level Requested:"), Paragraph("Basic Access (Developer Token)")],
        [Paragraph("Target Audience:"), Paragraph("Internal PPC specialists, marketing analysts (Strictly In-House)")],
        [Paragraph("API Version & Transport:"), Paragraph("Google Ads REST API v22 via searchStream (GAQL)")],
        [Paragraph("App Event / MMP Tracking:"), Paragraph("None (Tool does NOT use App Conversion / MMP APIs)")],
    ]
    meta_table = Table(meta_data, colWidths=[160, 344])
    meta_table.setStyle(meta_table_style)
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Section 1
    story.append(Paragraph("1. Tool Overview & Business Model", h1_style))
    story.append(Paragraph(
        "<b>gads-ai-bridge</b> is an internal command-line interface (CLI) application developed exclusively for our internal marketing and PPC management team. "
        "The tool provides automated read-only reporting and search term auditing capabilities across our own Google Ads advertising accounts.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Business Model:</b> This software is strictly for internal organizational use. It is <b>not</b> commercialized, licensed, sold as SaaS, or distributed to any third parties or outside clients. "
        "The tool exists solely to help our internal performance marketers monitor campaign health, track advertising return on spend (ROAS), and eliminate wasted ad spend by mining irrelevant search terms.",
        body_style
    ))

    # Section 2
    story.append(Paragraph("2. Architecture & Authentication Flow", h1_style))
    story.append(Paragraph(
        "The architecture is designed following Google's strict security and privacy best practices:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Desktop OAuth 2.0 Flow:</b> Authentication is performed once via Google Cloud Console Desktop App OAuth client. The user approves access via standard browser OAuth consent.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Local Credential Storage:</b> OAuth tokens (access and refresh tokens) and Developer Token credentials are saved strictly on the local user machine under <code>~/.gads/token.json</code> with strict local OS file permissions. No credentials or data are ever transmitted to third-party servers.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Direct HTTPS REST Communication:</b> All API calls communicate directly between the local CLI runtime and Google's official endpoints at <code>https://googleads.googleapis.com/v22/customers/{customer_id}/googleAds:searchStream</code> over TLS 1.3.",
        body_style
    ))

    # Section 3
    story.append(Paragraph("3. Specific API Services & GAQL Queries Used", h1_style))
    story.append(Paragraph(
        "Our integration is strictly read-only and uses the high-performance <b>searchStream</b> service to execute Google Ads Query Language (GAQL) queries across the following core resources:",
        body_style
    ))

    story.append(Paragraph("A. Campaign Performance Summary (<code>gads campaigns</code>)", h2_style))
    story.append(Paragraph(
        "Pulls aggregated performance metrics to monitor active campaigns, daily spend, and conversion trends:",
        body_style
    ))
    q1 = Paragraph("SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,<br/>"
                   "       metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.ctr, metrics.conversions<br/>"
                   "FROM campaign<br/>"
                   "WHERE segments.date DURING LAST_30_DAYS AND campaign.status != 'REMOVED'", code_style)
    t1 = Table([[q1]], colWidths=[504])
    t1.setStyle(code_table_style)
    story.append(t1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("B. Search Terms Waste Mining (<code>gads search-terms</code>)", h2_style))
    story.append(Paragraph(
        "Used by our PPC specialists to audit actual search queries triggering our ads, specifically filtering for queries that accrued ad spend without generating conversions (identifying negative keyword candidates):",
        body_style
    ))
    q2 = Paragraph("SELECT search_term_view.search_term, campaign.name, ad_group.name,<br/>"
                   "       metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions<br/>"
                   "FROM search_term_view<br/>"
                   "WHERE segments.date DURING LAST_30_DAYS<br/>"
                   "  AND metrics.cost_micros > 0<br/>"
                   "ORDER BY metrics.cost_micros DESC", code_style)
    t2 = Table([[q2]], colWidths=[504])
    t2.setStyle(code_table_style)
    story.append(t2)
    story.append(Spacer(1, 6))

    story.append(Paragraph("C. Keyword Performance Audit (<code>gads keywords</code>)", h2_style))
    story.append(Paragraph(
        "Pulls keyword-level metrics to evaluate match types, cost-per-click (CPC), and keyword quality:",
        body_style
    ))
    q3 = Paragraph("SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,<br/>"
                   "       ad_group_criterion.status, metrics.cost_micros, metrics.clicks, metrics.conversions<br/>"
                   "FROM keyword_view<br/>"
                   "WHERE segments.date DURING LAST_30_DAYS", code_style)
    t3 = Table([[q3]], colWidths=[504])
    t3.setStyle(code_table_style)
    story.append(t3)
    story.append(Spacer(1, 10))

    # Section 4
    story.append(Paragraph("4. User Interface & CLI Output Examples", h1_style))
    story.append(Paragraph(
        "Below are actual terminal execution examples showing the input commands and formatted ASCII table output rendered to stdout:",
        body_style
    ))

    cli_sample = Paragraph(
        "<b>$ gads campaigns --customer-id 168-927-0028 --days 30</b><br/>"
        "Campaign Name                      | Spend      | Clicks | Impressions | CTR   | Conversions<br/>"
        "-----------------------------------+------------+--------+-------------+-------+------------<br/>"
        "Search - Brand Core (EN)           | $1,420.50  | 3,820  | 42,100      | 9.07% | 142        <br/>"
        "Performance Max - Tier 1 Countries | $3,850.10  | 12,410 | 280,450     | 4.42% | 89         <br/>"
        "Search - Competitors Conquest      | $920.40   | 1,150  | 18,900      | 6.08% | 24         <br/><br/>"
        "<b>$ gads search-terms --customer-id 168-927-0028 --zero-conversions --min-spend 25</b><br/>"
        "Search Term                        | Campaign               | Spend   | Clicks | Conversions<br/>"
        "-----------------------------------+------------------------+---------+--------+------------<br/>"
        "free online cracked tool download  | Search - Core Feature  | $48.20  | 28     | 0          <br/>"
        "login help contact number customer | Search - Brand Generic | $35.10  | 14     | 0          ",
        code_style
    )
    t_cli = Table([[cli_sample]], colWidths=[504])
    t_cli.setStyle(code_table_style)
    story.append(t_cli)
    story.append(Spacer(1, 10))

    # Section 5
    story.append(Paragraph("5. Data Privacy, Storage & Security Governance", h1_style))
    story.append(Paragraph(
        "• <b>Strictly Read-Only:</b> The tool performs reporting only. It does not create, modify, pause, or remove live advertising campaigns or budgets without explicit human review.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>No External Data Transmission:</b> Data retrieved from the API is displayed locally on the user's terminal or exported to internal local spreadsheets. Data is never shared with third parties or external data aggregators.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Credential Isolation:</b> OAuth Client Secrets and Developer Tokens are stored locally and are excluded from source control (Git) via <code>.gitignore</code>.",
        body_style
    ))

    # Section 6
    story.append(Paragraph("6. Statement on App Conversion Tracking & Remarketing API", h1_style))
    story.append(Paragraph(
        "<b>gads-ai-bridge</b> does <b>NOT</b> integrate with, forward data to, or interact with the App Conversion Tracking & Remarketing API. "
        "The tool does not act as a Mobile Measurement Partner (MMP) and does not process device identifiers (such as IDFA, GAID) or mobile app in-app events. "
        "Its functionality is 100% focused on standard web campaign performance reporting and search term hygiene.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    out_dir = r"C:\folder\JOB\VS_Code_AL\gads-ai-bridge"
    out_file = os.path.join(out_dir, "Google_Ads_API_Design_Document.pdf")
    build_pdf(out_file)
