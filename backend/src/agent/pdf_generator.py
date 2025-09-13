"""PDF generation utilities for exam creation."""

import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from datetime import datetime
import platform
import re
from io import BytesIO

# 导入LaTeX数学处理器
try:
    from agent.latex_math import latex_processor
    LATEX_AVAILABLE = True
except ImportError:
    LATEX_AVAILABLE = False
    print("Warning: LaTeX math processing not available. Install matplotlib and sympy for math formula support.")

# 数学符号映射表（作为LaTeX的备选方案）
MATH_SYMBOL_MAP = {
    '÷': '/',      # 除号替换为斜杠
    '×': '*',      # 乘号替换为星号
    '√': 'sqrt',   # 根号替换为sqrt
    '²': '^2',     # 平方替换为^2
    '³': '^3',     # 立方替换为^3
    '±': '+/-',    # 正负号
    '≤': '<=',     # 小于等于
    '≥': '>=',     # 大于等于
    '≠': '!=',     # 不等于
    '≈': '≈',      # 约等于保持不变
    '∞': 'infinity', # 无穷大
    'π': 'pi',     # 圆周率
    '°': 'deg',    # 度数
    '∠': 'angle',  # 角度
    '⊥': 'perp',   # 垂直
    '∥': 'parallel', # 平行
}

def process_math_content(text: str, story: list, style) -> None:
    """
    处理包含数学公式的内容，优先使用LaTeX渲染。
    
    Args:
        text: 原始文本
        story: PDF内容列表
        style: 文本样式
    """
    if not text:
        return
    
    # 如果LaTeX可用且文本包含数学表达式，使用LaTeX渲染
    if LATEX_AVAILABLE and latex_processor.detect_math_expressions(text):
        try:
            processed_text, math_images = latex_processor.process_text_with_math(text)
            
            # 如果有数学图像，分段处理
            if math_images:
                current_text = processed_text
                for math_img in math_images:
                    # 分割文本
                    parts = current_text.split(math_img['placeholder'], 1)
                    
                    # 添加前面的文本
                    if parts[0].strip():
                        story.append(Paragraph(parts[0].strip(), style))
                    
                    # 添加数学图像
                    img_buffer = BytesIO(math_img['image_data'])
                    img = RLImage(img_buffer, width=100, height=30)  # 调整大小
                    story.append(img)
                    
                    # 更新当前文本为剩余部分
                    current_text = parts[1] if len(parts) > 1 else ""
                
                # 添加剩余文本
                if current_text.strip():
                    story.append(Paragraph(current_text.strip(), style))
                
                return
        except Exception as e:
            print(f"LaTeX渲染失败，使用备选方案: {e}")
    
    # 备选方案：使用符号替换
    safe_text = replace_math_symbols(text)
    story.append(Paragraph(safe_text, style))


def replace_math_symbols(text: str) -> str:
    """
    替换文本中的数学符号为字体支持的字符（备选方案）。
    
    Args:
        text: 原始文本
        
    Returns:
        替换后的文本
    """
    if not text:
        return text
    
    result = text
    
    # 特殊处理需要保持空格的符号
    special_replacements = [
        ('÷', '/'),      # 除号
        ('×', '*'),      # 乘号  
        ('∠', 'angle '), # 角度符号后加空格
    ]
    
    for symbol, replacement in special_replacements:
        if symbol in result:
            result = result.replace(symbol, replacement)
    
    # 处理根号的特殊情况
    if '√' in result:
        # 匹配 √数字 的模式
        result = re.sub(r'√(\d+)', r'sqrt(\1)', result)
        # 处理其他根号情况
        result = result.replace('√', 'sqrt')
    
    # 处理其他符号
    other_symbols = {
        '²': '^2', '³': '^3', '±': '+/-', 
        '≤': '<=', '≥': '>=', '≠': '!=', 
        '∞': 'infinity', 'π': 'pi', '°': 'deg',
        '⊥': 'perp', '∥': 'parallel'
    }
    
    for symbol, replacement in other_symbols.items():
        if symbol in result:
            result = result.replace(symbol, replacement)
    
    # 清理多余的空格
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result

# 注册中文字体
def register_chinese_fonts():
    """注册中文字体以支持中文显示"""
    try:
        # 首先尝试使用内置的中文字体支持
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        
        # 尝试注册CID字体（更好的中文支持）
        cid_fonts = ['STSong-Light', 'STHeiti', 'MSung-Light', 'MHei-Medium']
        for cid_font in cid_fonts:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont(cid_font))
                print(f"Successfully registered CID font: {cid_font}")
                return cid_font
            except Exception as e:
                print(f"Failed to register CID font {cid_font}: {e}")
                continue
        
        # 如果CID字体不可用，尝试系统字体
        system = platform.system()
        font_candidates = []
        
        if system == "Darwin":  # macOS
            font_candidates = [
                # macOS 系统字体
                ("/System/Library/Fonts/Helvetica.ttc", "Helvetica"),
                ("/System/Library/Fonts/Times.ttc", "Times"),
                ("/Library/Fonts/Arial.ttf", "Arial"),
                ("/System/Library/Fonts/Supplemental/Arial.ttf", "Arial"),
                # 尝试一些可能的中文字体路径
                ("/System/Library/Fonts/PingFang.ttc", "PingFang"),
                ("/Library/Fonts/STHeiti Light.ttc", "STHeiti"),
            ]
        elif system == "Windows":
            font_candidates = [
                ("C:/Windows/Fonts/arial.ttf", "Arial"),
                ("C:/Windows/Fonts/times.ttf", "Times"),
                ("C:/Windows/Fonts/msyh.ttf", "MicrosoftYaHei"),  # 微软雅黑
                ("C:/Windows/Fonts/simsun.ttc", "SimSun"),  # 宋体
                ("C:/Windows/Fonts/simhei.ttf", "SimHei"),   # 黑体
            ]
        else:  # Linux
            font_candidates = [
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans"),
                ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "Liberation"),
                ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", "NotoSans"),
            ]
        
        # 尝试注册字体
        for font_path, font_name in font_candidates:
            if os.path.exists(font_path):
                try:
                    # 对于TTF文件
                    if font_path.endswith('.ttf'):
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        print(f"Successfully registered font: {font_name} from {font_path}")
                        return font_name
                    # 对于TTC文件，尝试使用第一个字体
                    elif font_path.endswith('.ttc'):
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=0))
                            print(f"Successfully registered TTC font: {font_name} from {font_path}")
                            return font_name
                        except:
                            # 如果TTC失败，跳过
                            continue
                except Exception as e:
                    print(f"Failed to register font {font_name}: {e}")
                    continue
        
        # 如果所有字体都失败，使用Helvetica并警告
        print("Warning: No suitable Chinese font found, using Helvetica. Chinese characters may not display correctly.")
        return 'Helvetica'
        
    except Exception as e:
        print(f"Error in font registration: {e}")
        return 'Helvetica'


class TwoColumnDocTemplate(BaseDocTemplate):
    """自定义双栏文档模板"""
    
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        
        # 页面尺寸
        page_width, page_height = A4
        
        # 边距
        left_margin = 1*cm
        right_margin = 1*cm
        top_margin = 1*cm
        bottom_margin = 1*cm
        
        # 计算栏宽
        frame_width = (page_width - left_margin - right_margin - 0.5*cm) / 2  # 0.5cm为栏间距
        frame_height = page_height - top_margin - bottom_margin
        
        # 左栏
        left_frame = Frame(
            left_margin, bottom_margin,
            frame_width, frame_height,
            leftPadding=0, rightPadding=0.25*cm,
            topPadding=0, bottomPadding=0,
            id='left'
        )
        
        # 右栏
        right_frame = Frame(
            left_margin + frame_width + 0.5*cm, bottom_margin,
            frame_width, frame_height,
            leftPadding=0.25*cm, rightPadding=0,
            topPadding=0, bottomPadding=0,
            id='right'
        )
        
        # 创建页面模板
        template = PageTemplate(id='TwoColumn', frames=[left_frame, right_frame])
        self.addPageTemplates([template])


class ExamPDFGenerator:
    """Generates PDF documents for exams."""
    
    def __init__(self):
        self.chinese_font = register_chinese_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        print(f"Using font: {self.chinese_font}")
    
    def _get_safe_font(self):
        """获取安全的字体名称，确保中文显示"""
        # 如果是CID字体，直接返回
        if self.chinese_font in ['STSong-Light', 'STHeiti']:
            return self.chinese_font
        
        # 对于其他字体，检查是否已注册
        try:
            # 测试字体是否可用
            from reportlab.pdfbase import pdfmetrics
            font_names = pdfmetrics.getRegisteredFontNames()
            if self.chinese_font in font_names:
                return self.chinese_font
        except:
            pass
        
        # 回退到Helvetica
        return 'Helvetica'
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF with Chinese font support."""
        safe_font = self._get_safe_font()
        
        # 试卷标题样式 - 极度紧凑
        self.styles.add(ParagraphStyle(
            name='ExamTitle',
            parent=self.styles['Title'],
            fontName=safe_font,
            fontSize=16,  # 进一步减小字体
            spaceAfter=8,   # 大幅减少后间距
            alignment=TA_CENTER,
            textColor=colors.black,
            leading=18
        ))
        
        # 副标题样式 - 极度紧凑
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=10,
            spaceAfter=5,   # 进一步减少间距
            alignment=TA_CENTER,
            textColor=colors.grey,
            leading=12
        ))
        
        # 考试信息样式 - 极度紧凑
        self.styles.add(ParagraphStyle(
            name='ExamInfo',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=9,
            spaceAfter=6,   # 进一步减少间距
            alignment=TA_LEFT,
            leading=10
        ))
        
        # 题目样式 - 适应双栏布局
        self.styles.add(ParagraphStyle(
            name='Question',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=9,   # 双栏需要更小字体
            spaceAfter=2,
            spaceBefore=3,
            leftIndent=0,
            leading=11,
            textColor=colors.black
        ))
        
        # 选项样式 - 适应双栏布局
        self.styles.add(ParagraphStyle(
            name='Option',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=8,   # 双栏需要更小字体
            spaceAfter=1,
            leftIndent=0.15*inch,  # 减少缩进以适应窄栏
            leading=9
        ))
        
        # 答题区域样式 - 极度紧凑
        self.styles.add(ParagraphStyle(
            name='AnswerSpace',
            parent=self.styles['Normal'],
            fontName=safe_font,
            fontSize=8,
            spaceAfter=1,   # 极小间距
            leftIndent=0.2*inch,
            textColor=colors.grey,
            leading=9
        ))
        
        # 分割线样式
        self.styles.add(ParagraphStyle(
            name='Separator',
            parent=self.styles['Normal'],
            fontSize=1,
            spaceAfter=10,
            spaceBefore=10
        ))
    
    def generate_exam_pdf(
        self,
        exam_title: str,
        instructions: str,
        questions: List[Dict[str, Any]],
        output_path: str,
        include_answers: bool = False
    ) -> str:
        """
        Generate a PDF exam document.
        
        Args:
            exam_title: Title of the exam
            instructions: Exam instructions
            questions: List of question dictionaries
            output_path: Path where PDF should be saved
            include_answers: Whether to include answer key
            
        Returns:
            Path to the generated PDF file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document with two-column layout
        doc = TwoColumnDocTemplate(output_path, pagesize=A4)
        
        # Build content
        story = []
        
        # Add title only - 简化头部，只保留标题
        story.append(Paragraph(exam_title, self.styles['ExamTitle']))
        
        # Add minimal exam info in one line
        date_str = datetime.now().strftime("%Y年%m月%d日")
        total_points = sum(q.get('points', 1) for q in questions)
        info_text = f"日期：{date_str} | 题数：{len(questions)}题 | 总分：{total_points}分 | 时间：90分钟"
        story.append(Paragraph(info_text, self.styles['ExamInfo']))
        story.append(Spacer(1, 0.2*cm))
        
        # Add questions with better spacing for two-column layout
        for i, question in enumerate(questions, 1):
            # 将每个题目包装在KeepTogether中，避免跨栏分割
            question_content = []
            self._add_question_to_story(question_content, i, question, include_answers)
            
            # 将题目内容作为一个整体添加
            if question_content:
                story.extend(question_content)
                # 在题目之间添加适当间距
                story.append(Spacer(1, 0.1*cm))
        
        # Generate answer key if requested
        if include_answers:
            story.append(PageBreak())
            story.append(Paragraph("参考答案", self.styles['ExamTitle']))
            story.append(Spacer(1, 0.15*cm))  # 进一步减少间距
            
            for i, question in enumerate(questions, 1):
                self._add_answer_to_story(story, i, question)
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _add_question_to_story(self, story: List, question_num: int, question: Dict[str, Any], include_answers: bool = False):
        """Add a single question to the PDF story."""
        points = question.get('points', 1)
        # 处理数学内容
        question_text = f"<b>{question_num}. </b>{question['question_text']} <b>({points}分)</b>"
        
        # 如果包含数学符号，使用特殊处理
        if LATEX_AVAILABLE and latex_processor.detect_math_expressions(question['question_text']):
            # 分别处理题号和题目内容
            story.append(Paragraph(f"<b>{question_num}. </b>", self.styles['Question']))
            process_math_content(question['question_text'], story, self.styles['Question'])
            story.append(Paragraph(f"<b>({points}分)</b>", self.styles['Question']))
        else:
            safe_question_text = replace_math_symbols(question['question_text'])
            question_text = f"<b>{question_num}. </b>{safe_question_text} <b>({points}分)</b>"
            story.append(Paragraph(question_text, self.styles['Question']))
        
        question_type = question.get('question_type', 'short_answer')
        
        if question_type == 'multiple_choice':
            options = question.get('options', [])
            for i, option in enumerate(options):
                letter = chr(65 + i)  # A, B, C, D
                # 替换选项中的数学符号
                safe_option = replace_math_symbols(option)
                
                # 更强力的重复标号清理
                import re
                # 清理各种可能的重复标号格式
                patterns_to_remove = [
                    r'^[A-D][\.\)]\s*',      # A. 或 A) 
                    r'^[A-D][\.\)]\s*[A-D][\.\)]\s*',  # A. A. 或 A) A)
                    r'^\([A-D]\)\s*',        # (A) 
                    r'^[A-D]\s*[\.\)]\s*',   # A . 或 A )
                ]
                
                for pattern in patterns_to_remove:
                    safe_option = re.sub(pattern, '', safe_option)
                
                # 清理开头的多余空格
                safe_option = safe_option.strip()
                
                option_text = f"{letter}. {safe_option}"
                if include_answers and question.get('correct_answer') == option:
                    option_text = f"<b>{option_text} ✓</b>"
                story.append(Paragraph(option_text, self.styles['Option']))
        
        elif question_type == 'true_false':
            tf_text = "☐ 正确 &nbsp;&nbsp;&nbsp;&nbsp; ☐ 错误"
            if include_answers:
                correct = replace_math_symbols(question.get('correct_answer', '')).lower()
                if 'true' in correct or '正确' in correct:
                    tf_text = "☑ 正确 &nbsp;&nbsp;&nbsp;&nbsp; ☐ 错误"
                else:
                    tf_text = "☐ 正确 &nbsp;&nbsp;&nbsp;&nbsp; ☑ 错误"
            story.append(Paragraph(tf_text, self.styles['Option']))
        
        elif question_type == 'fill_blank':
            if not include_answers:
                story.append(Paragraph("答案：_____________", self.styles['Option']))
            else:
                answer = replace_math_symbols(question.get('correct_answer', '参考答案略'))
                story.append(Paragraph(f"答案：{answer}", self.styles['Option']))
        
        elif question_type == 'calculation':
            if not include_answers:
                story.append(Paragraph("解：", self.styles['Option']))
                # 极度压缩答题行数
                for _ in range(2):  # 从3行减少到2行
                    story.append(Paragraph("_" * 40, self.styles['AnswerSpace']))  # 进一步缩短线长
            else:
                answer = replace_math_symbols(question.get('correct_answer', '参考解答略'))
                story.append(Paragraph(f"解：{answer}", self.styles['Option']))
        
        elif question_type == 'application':
            if not include_answers:
                story.append(Paragraph("解：", self.styles['Option']))
                # 极度压缩答题行数
                for _ in range(2):  # 从3行减少到2行
                    story.append(Paragraph("_" * 40, self.styles['AnswerSpace']))
            else:
                answer = replace_math_symbols(question.get('correct_answer', '参考答案略'))
                story.append(Paragraph(f"答案：{answer}", self.styles['Option']))
        
        elif question_type == 'analysis':
            if not include_answers:
                story.append(Paragraph("分析：", self.styles['Option']))
                # 极度压缩答题行数
                for _ in range(2):  # 从3行减少到2行
                    story.append(Paragraph("_" * 40, self.styles['AnswerSpace']))
            else:
                answer = replace_math_symbols(question.get('correct_answer', '参考分析略'))
                story.append(Paragraph(f"分析：{answer}", self.styles['Option']))
        
        elif question_type == 'short_answer':
            if not include_answers:
                story.append(Paragraph("答：", self.styles['Option']))
                # 极度压缩答题行数
                story.append(Paragraph("_" * 40, self.styles['AnswerSpace']))  # 只保留1行
            else:
                answer = replace_math_symbols(question.get('correct_answer', '参考答案略'))
                story.append(Paragraph(f"答：{answer}", self.styles['Option']))
        
        elif question_type == 'essay':
            if not include_answers:
                story.append(Paragraph("答：", self.styles['Option']))
                # 论述题也大幅压缩
                for _ in range(3):  # 从4行减少到3行
                    story.append(Paragraph("_" * 40, self.styles['AnswerSpace']))
            else:
                answer = replace_math_symbols(question.get('correct_answer', '参考答案略，请根据评分标准评判'))
                story.append(Paragraph(f"答案要点：{answer}", self.styles['Option']))
        
        story.append(Spacer(1, 0.08*cm))  # 极度减少题目间距
    
    def _add_answer_to_story(self, story: List, question_num: int, question: Dict[str, Any]):
        """Add answer to the answer key section."""
        answer_text = f"<b>{question_num}. </b>"
        
        if question.get('correct_answer'):
            # 替换答案中的数学符号
            safe_answer = replace_math_symbols(question['correct_answer'])
            answer_text += safe_answer
        else:
            answer_text += "请参考评分标准"
        
        if question.get('explanation'):
            # 替换解析中的数学符号
            safe_explanation = replace_math_symbols(question['explanation'])
            answer_text += f"<br/><i>解析：{safe_explanation}</i>"
        
        story.append(Paragraph(answer_text, self.styles['ExamInfo']))
        story.append(Spacer(1, 0.05*cm))  # 极度减少答案间距