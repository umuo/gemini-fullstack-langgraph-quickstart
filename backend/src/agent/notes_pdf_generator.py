"""PDF generation utilities for study notes."""

import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime

# 使用与试卷生成器相同的字体注册函数和数学符号处理
from agent.pdf_generator import register_chinese_fonts, replace_math_symbols


class StudyNotesPDFGenerator:
    """Generates PDF documents for study notes."""
    
    def __init__(self):
        self.chinese_font = register_chinese_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        print(f"Notes generator using font: {self.chinese_font}")
    
    def _get_safe_font(self):
        """获取安全的字体名称，确保中文显示"""
        if self.chinese_font in ['STSong-Light', 'STHeiti']:
            return self.chinese_font
        
        try:
            from reportlab.pdfbase import pdfmetrics
            font_names = pdfmetrics.getRegisteredFontNames()
            if self.chinese_font in font_names:
                return self.chinese_font
        except:
            pass
        
        return 'Helvetica'
    
    def _setup_custom_styles(self):
        """Setup custom styles for study notes PDF."""
        safe_font = self._get_safe_font()
        
        # 笔记标题样式
        self.styles.add(ParagraphStyle(
            name='NotesTitle',
            parent=self.styles['Title'],
            fontName=safe_font,
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            leading=22
        ))
        
        # 章节标题样式
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontName=safe_font,
            fontSize=14,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.darkgreen,
            leading=18
        ))
        
        # 子标题样式
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontName=safe_font,
            fontSize=12,
            spaceAfter=8,
            spaceBefore=10,
            textColor=colors.darkred,
            leading=16
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='NotesBody',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14,
            leftIndent=0.2*inch
        ))
        
        # 重点内容样式
        self.styles.add(ParagraphStyle(
            name='Important',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=10,
            spaceAfter=8,
            spaceBefore=4,
            leftIndent=0.3*inch,
            rightIndent=0.3*inch,
            borderColor=colors.orange,
            borderWidth=1,
            borderPadding=6,
            backColor=colors.lightyellow,
            leading=14
        ))
        
        # 例子样式
        self.styles.add(ParagraphStyle(
            name='Example',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=9,
            spaceAfter=6,
            leftIndent=0.4*inch,
            textColor=colors.darkblue,
            leading=12,
            backColor=colors.lightblue,
            borderPadding=4
        ))
        
        # 技巧样式
        self.styles.add(ParagraphStyle(
            name='Tip',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=10,
            spaceAfter=6,
            leftIndent=0.3*inch,
            textColor=colors.darkgreen,
            leading=13
        ))
    
    def generate_study_notes_pdf(
        self,
        notes_data: Dict[str, Any],
        topic: str,
        subject: str,
        education_level: str,
        output_path: str
    ) -> str:
        """
        Generate a PDF study notes document.
        
        Args:
            notes_data: Study notes data dictionary
            topic: Knowledge topic
            subject: Subject name
            education_level: Education level
            output_path: Path where PDF should be saved
            
        Returns:
            Path to the generated PDF file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build content
        story = []
        
        # Add title
        title = f"{topic} - 学习笔记"
        story.append(Paragraph(title, self.styles['NotesTitle']))
        
        # Add metadata
        date_str = datetime.now().strftime("%Y年%m月%d日")
        metadata = f"学科：{subject} | 学段：{education_level} | 生成日期：{date_str}"
        story.append(Paragraph(metadata, self.styles['NotesBody']))
        story.append(Spacer(1, 0.3*cm))
        
        # Add topic overview
        if notes_data.get('topic_overview'):
            story.append(Paragraph("📖 主题概述", self.styles['SectionTitle']))
            safe_overview = replace_math_symbols(notes_data['topic_overview'])
            story.append(Paragraph(safe_overview, self.styles['NotesBody']))
            story.append(Spacer(1, 0.2*cm))
        
        # Add learning objectives
        if notes_data.get('learning_objectives'):
            story.append(Paragraph("🎯 学习目标", self.styles['SectionTitle']))
            for i, objective in enumerate(notes_data['learning_objectives'], 1):
                safe_objective = replace_math_symbols(objective)
                story.append(Paragraph(f"{i}. {safe_objective}", self.styles['NotesBody']))
            story.append(Spacer(1, 0.2*cm))
        
        # Add knowledge points
        if notes_data.get('knowledge_points'):
            story.append(Paragraph("🎯 核心知识点", self.styles['SectionTitle']))
            
            for i, kp in enumerate(notes_data['knowledge_points'], 1):
                # Knowledge point title with importance
                importance_icon = {"基础": "🔵", "重要": "🟡", "核心": "🔴"}.get(kp.get('importance', '基础'), "🔵")
                safe_title = replace_math_symbols(kp.get('title', ''))
                kp_title = f"{i}. {importance_icon} {safe_title}"
                story.append(Paragraph(kp_title, self.styles['SubTitle']))
                
                # Definition
                if kp.get('definition'):
                    story.append(Paragraph("📝 定义：", self.styles['Tip']))
                    safe_definition = replace_math_symbols(kp['definition'])
                    story.append(Paragraph(safe_definition, self.styles['Important']))
                
                # Knowledge point content
                if kp.get('content'):
                    safe_content = replace_math_symbols(kp['content'])
                    story.append(Paragraph(safe_content, self.styles['NotesBody']))
                
                # Key points
                if kp.get('key_points'):
                    story.append(Paragraph("🔑 关键要点：", self.styles['Tip']))
                    for key_point in kp['key_points']:
                        safe_key_point = replace_math_symbols(key_point)
                        story.append(Paragraph(f"• {safe_key_point}", self.styles['NotesBody']))
                
                # Examples
                if kp.get('examples'):
                    story.append(Paragraph("💡 例子：", self.styles['Tip']))
                    for example in kp['examples']:
                        safe_example = replace_math_symbols(example)
                        story.append(Paragraph(f"• {safe_example}", self.styles['Example']))
                
                # Common mistakes
                if kp.get('common_mistakes'):
                    story.append(Paragraph("⚠️ 常见误区：", self.styles['Tip']))
                    for mistake in kp['common_mistakes']:
                        safe_mistake = replace_math_symbols(mistake)
                        story.append(Paragraph(f"• {safe_mistake}", self.styles['Example']))
                
                # Connections
                if kp.get('connections'):
                    story.append(Paragraph("🔗 知识关联：", self.styles['Tip']))
                    for connection in kp['connections']:
                        safe_connection = replace_math_symbols(connection)
                        story.append(Paragraph(f"• {safe_connection}", self.styles['NotesBody']))
                
                story.append(Spacer(1, 0.2*cm))
        
        # Add study tips
        if notes_data.get('study_tips'):
            story.append(Paragraph("🚀 学习技巧", self.styles['SectionTitle']))
            
            # Group tips by category
            tips_by_category = {}
            for tip in notes_data['study_tips']:
                category = tip.get('category', '通用')
                if category not in tips_by_category:
                    tips_by_category[category] = []
                tips_by_category[category].append(tip)
            
            category_icons = {
                "记忆": "🧠", "理解": "💡", "应用": "⚡", "解题": "🎯", "通用": "📚"
            }
            
            for category, tips in tips_by_category.items():
                icon = category_icons.get(category, "📚")
                story.append(Paragraph(f"{icon} {category}技巧", self.styles['SubTitle']))
                
                for tip in tips:
                    safe_tip_title = replace_math_symbols(tip.get('title', ''))
                    tip_title = f"• {safe_tip_title}"
                    story.append(Paragraph(tip_title, self.styles['Tip']))
                    
                    if tip.get('content'):
                        safe_tip_content = replace_math_symbols(tip['content'])
                        story.append(Paragraph(safe_tip_content, self.styles['NotesBody']))
                    
                    # Steps
                    if tip.get('steps'):
                        story.append(Paragraph("📋 操作步骤：", self.styles['Tip']))
                        for j, step in enumerate(tip['steps'], 1):
                            safe_step = replace_math_symbols(step)
                            story.append(Paragraph(f"{j}. {safe_step}", self.styles['NotesBody']))
                    
                    # Applicable scenarios
                    if tip.get('applicable_scenarios'):
                        scenarios_text = "🎯 适用场景：" + "、".join(tip['applicable_scenarios'])
                        story.append(Paragraph(scenarios_text, self.styles['Example']))
                    
                    # Examples
                    if tip.get('examples'):
                        story.append(Paragraph("💡 使用实例：", self.styles['Tip']))
                        for example in tip['examples']:
                            safe_example = replace_math_symbols(example)
                            story.append(Paragraph(f"• {safe_example}", self.styles['Example']))
                    
                    # Effectiveness
                    if tip.get('effectiveness'):
                        safe_effectiveness = replace_math_symbols(tip['effectiveness'])
                        effectiveness_text = f"✅ 效果说明：{safe_effectiveness}"
                        story.append(Paragraph(effectiveness_text, self.styles['Example']))
                
                story.append(Spacer(1, 0.15*cm))
        
        # Add extended knowledge
        if notes_data.get('extended_knowledge'):
            story.append(Paragraph("🌟 扩展知识", self.styles['SectionTitle']))
            
            for i, ek in enumerate(notes_data['extended_knowledge'], 1):
                # Extended knowledge title with difficulty
                difficulty_icon = {"简单": "⭐", "中等": "⭐⭐", "困难": "⭐⭐⭐"}.get(ek.get('difficulty_level', '中等'), "⭐⭐")
                safe_ek_title = replace_math_symbols(ek.get('title', ''))
                ek_title = f"{i}. {safe_ek_title} {difficulty_icon}"
                story.append(Paragraph(ek_title, self.styles['SubTitle']))
                
                # Content
                if ek.get('content'):
                    safe_ek_content = replace_math_symbols(ek['content'])
                    story.append(Paragraph(safe_ek_content, self.styles['NotesBody']))
                
                # Connection
                if ek.get('connection'):
                    safe_connection = replace_math_symbols(ek['connection'])
                    connection_text = f"🔗 关联：{safe_connection}"
                    story.append(Paragraph(connection_text, self.styles['Tip']))
                
                # Applications
                if ek.get('applications'):
                    story.append(Paragraph("🌍 实际应用：", self.styles['Tip']))
                    for application in ek['applications']:
                        safe_application = replace_math_symbols(application)
                        story.append(Paragraph(f"• {safe_application}", self.styles['NotesBody']))
                
                # Historical context
                if ek.get('historical_context'):
                    safe_historical = replace_math_symbols(ek['historical_context'])
                    historical_text = f"📚 历史背景：{safe_historical}"
                    story.append(Paragraph(historical_text, self.styles['Example']))
                
                # Cross-subject links
                if ek.get('cross_subject_links'):
                    story.append(Paragraph("🔄 跨学科联系：", self.styles['Tip']))
                    for link in ek['cross_subject_links']:
                        safe_link = replace_math_symbols(link)
                        story.append(Paragraph(f"• {safe_link}", self.styles['NotesBody']))
                
                story.append(Spacer(1, 0.2*cm))
        
        # Add knowledge structure
        if notes_data.get('knowledge_structure'):
            story.append(Paragraph("🗺️ 知识结构", self.styles['SectionTitle']))
            safe_structure = replace_math_symbols(notes_data['knowledge_structure'])
            story.append(Paragraph(safe_structure, self.styles['Important']))
            story.append(Spacer(1, 0.2*cm))
        
        # Add summary
        if notes_data.get('summary'):
            story.append(Paragraph("📝 系统总结", self.styles['SectionTitle']))
            safe_summary = replace_math_symbols(notes_data['summary'])
            story.append(Paragraph(safe_summary, self.styles['Important']))
            story.append(Spacer(1, 0.2*cm))
        
        # Add practice recommendations
        if notes_data.get('practice_recommendations'):
            story.append(Paragraph("💪 分层练习推荐", self.styles['SectionTitle']))
            
            level_icons = {"基础": "⭐", "提高": "⭐⭐", "综合": "⭐⭐⭐", "创新": "🌟"}
            
            for practice in notes_data['practice_recommendations']:
                level_icon = level_icons.get(practice.get('level', '基础'), "⭐")
                safe_title = replace_math_symbols(practice.get('title', ''))
                practice_title = f"{level_icon} {practice.get('level', '基础')}练习：{safe_title}"
                story.append(Paragraph(practice_title, self.styles['SubTitle']))
                
                if practice.get('description'):
                    safe_description = replace_math_symbols(practice['description'])
                    story.append(Paragraph(safe_description, self.styles['NotesBody']))
                
                if practice.get('methods'):
                    story.append(Paragraph("📋 练习方法：", self.styles['Tip']))
                    for method in practice['methods']:
                        safe_method = replace_math_symbols(method)
                        story.append(Paragraph(f"• {safe_method}", self.styles['NotesBody']))
                
                if practice.get('time_suggestion'):
                    safe_time = replace_math_symbols(practice['time_suggestion'])
                    time_text = f"⏰ 时间建议：{safe_time}"
                    story.append(Paragraph(time_text, self.styles['Example']))
                
                story.append(Spacer(1, 0.15*cm))
        
        # Add learning resources
        if notes_data.get('learning_resources'):
            story.append(Paragraph("📚 学习资源推荐", self.styles['SectionTitle']))
            
            resource_icons = {"书籍": "📖", "网站": "🌐", "视频": "🎥", "工具": "🔧"}
            
            for resource in notes_data['learning_resources']:
                resource_icon = resource_icons.get(resource.get('type', '其他'), "📎")
                safe_title = replace_math_symbols(resource.get('title', ''))
                resource_title = f"{resource_icon} {safe_title}"
                story.append(Paragraph(resource_title, self.styles['SubTitle']))
                
                if resource.get('description'):
                    safe_description = replace_math_symbols(resource['description'])
                    story.append(Paragraph(safe_description, self.styles['NotesBody']))
                
                if resource.get('recommendation_reason'):
                    safe_reason = replace_math_symbols(resource['recommendation_reason'])
                    reason_text = f"💡 推荐理由：{safe_reason}"
                    story.append(Paragraph(reason_text, self.styles['Example']))
                
                story.append(Spacer(1, 0.1*cm))
        
        # Add FAQs
        if notes_data.get('faqs'):
            story.append(Paragraph("❓ 常见问题解答", self.styles['SectionTitle']))
            
            for i, faq in enumerate(notes_data['faqs'], 1):
                safe_question = replace_math_symbols(faq.get('question', ''))
                question_text = f"Q{i}: {safe_question}"
                story.append(Paragraph(question_text, self.styles['SubTitle']))
                
                if faq.get('answer'):
                    safe_answer = replace_math_symbols(faq['answer'])
                    answer_text = f"A{i}: {safe_answer}"
                    story.append(Paragraph(answer_text, self.styles['NotesBody']))
                
                story.append(Spacer(1, 0.1*cm))
        
        # Add self-assessment
        if notes_data.get('self_assessment'):
            story.append(Paragraph("🎯 自我检测", self.styles['SectionTitle']))
            for i, assessment in enumerate(notes_data['self_assessment'], 1):
                safe_assessment = replace_math_symbols(assessment)
                assessment_text = f"{i}. {safe_assessment}"
                story.append(Paragraph(assessment_text, self.styles['NotesBody']))
        
        # Build PDF
        doc.build(story)
        return output_path