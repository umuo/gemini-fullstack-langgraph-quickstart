"""LaTeX mathematical formula processing for PDF generation."""

import re
import os
import tempfile
from typing import Optional, Tuple
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import mathtext
from PIL import Image
import numpy as np


class LaTeXMathProcessor:
    """Processes LaTeX mathematical formulas and converts them to images."""
    
    def __init__(self):
        # 设置matplotlib支持中文和数学公式
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 数学符号到LaTeX的映射
        self.symbol_to_latex = {
            '÷': r'\div',
            '×': r'\times',
            '±': r'\pm',
            '≤': r'\leq',
            '≥': r'\geq',
            '≠': r'\neq',
            '≈': r'\approx',
            '∞': r'\infty',
            'π': r'\pi',
            '°': r'^\circ',
            '√': r'\sqrt',
            '²': r'^2',
            '³': r'^3',
            '∠': r'\angle',
            '⊥': r'\perp',
            '∥': r'\parallel',
            'α': r'\alpha',
            'β': r'\beta',
            'γ': r'\gamma',
            'δ': r'\delta',
            'θ': r'\theta',
            'λ': r'\lambda',
            'μ': r'\mu',
            'σ': r'\sigma',
            'Δ': r'\Delta',
            'Σ': r'\Sigma',
        }
    
    def detect_math_expressions(self, text: str) -> bool:
        """
        检测文本中是否包含数学表达式。
        
        Args:
            text: 输入文本
            
        Returns:
            是否包含数学表达式
        """
        # 检查是否包含数学符号
        for symbol in self.symbol_to_latex.keys():
            if symbol in text:
                return True
        
        # 检查是否包含数学模式的模式
        math_patterns = [
            r'\d+\s*[÷×]\s*\d+',  # 基本运算
            r'\d+\^[23]',          # 幂次
            r'√\d+',               # 根号
            r'\d+°',               # 角度
            r'[a-zA-Z]\s*[=<>≤≥≠]\s*\d+',  # 方程/不等式
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def convert_to_latex(self, text: str) -> str:
        """
        将包含数学符号的文本转换为LaTeX格式。
        
        Args:
            text: 原始文本
            
        Returns:
            LaTeX格式的文本
        """
        result = text
        
        # 替换数学符号
        for symbol, latex in self.symbol_to_latex.items():
            if symbol in result:
                if symbol == '√':
                    # 特殊处理根号
                    result = re.sub(r'√(\d+)', r'\\sqrt{\1}', result)
                    result = result.replace('√', '\\sqrt{}')
                elif symbol in ['²', '³']:
                    # 处理上标
                    escaped_symbol = re.escape(symbol)
                    result = re.sub(f'([a-zA-Z0-9]+){escaped_symbol}', f'\\1{latex}', result)
                elif symbol == '°':
                    # 处理度数符号 - 修复转义问题
                    result = re.sub(r'(\d+)°', r'\1^\\circ', result)
                else:
                    result = result.replace(symbol, latex)
        
        # 处理分数形式 a/b -> \frac{a}{b}
        result = re.sub(r'(\d+)\s*/\s*(\d+)', r'\\frac{\1}{\2}', result)
        
        # 处理简单的上标 a^b
        result = re.sub(r'([a-zA-Z0-9])\^([a-zA-Z0-9])', r'\1^{\2}', result)
        
        return result
    
    def render_math_to_image(self, latex_text: str, fontsize: int = 12, dpi: int = 150) -> Optional[bytes]:
        """
        将LaTeX数学公式渲染为图像。
        
        Args:
            latex_text: LaTeX格式的数学公式
            fontsize: 字体大小
            dpi: 图像分辨率
            
        Returns:
            图像的字节数据，如果渲染失败则返回None
        """
        try:
            # 创建图形
            fig, ax = plt.subplots(figsize=(8, 2))
            ax.axis('off')
            
            # 渲染LaTeX公式
            ax.text(0.5, 0.5, f'${latex_text}$', 
                   transform=ax.transAxes,
                   fontsize=fontsize,
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            # 保存为字节流
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            
            buf.seek(0)
            return buf.getvalue()
            
        except Exception as e:
            print(f"LaTeX渲染失败: {e}")
            return None
    
    def process_text_with_math(self, text: str) -> Tuple[str, list]:
        """
        处理包含数学公式的文本，返回处理后的文本和数学图像。
        
        Args:
            text: 原始文本
            
        Returns:
            (处理后的文本, 数学图像列表)
        """
        if not self.detect_math_expressions(text):
            return text, []
        
        # 找到数学表达式
        math_expressions = []
        processed_text = text
        
        # 简单的数学表达式模式
        patterns = [
            r'\d+\s*[÷×]\s*\d+\s*=\s*\d+',  # 基本运算等式
            r'√\d+\s*=\s*\d+',               # 根号等式
            r'\d+[²³]\s*[+\-]\s*\d+[²³]\s*=\s*\d+',  # 幂次运算
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                math_expr = match.group()
                latex_expr = self.convert_to_latex(math_expr)
                
                # 渲染为图像
                img_data = self.render_math_to_image(latex_expr)
                if img_data:
                    placeholder = f"[MATH_IMG_{len(math_expressions)}]"
                    processed_text = processed_text.replace(math_expr, placeholder, 1)
                    math_expressions.append({
                        'placeholder': placeholder,
                        'original': math_expr,
                        'latex': latex_expr,
                        'image_data': img_data
                    })
        
        return processed_text, math_expressions


# 全局实例
latex_processor = LaTeXMathProcessor()