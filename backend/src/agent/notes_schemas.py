"""Schemas for knowledge notes generation."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class KnowledgePoint(BaseModel):
    """Schema for a single knowledge point."""
    title: str = Field(description="知识点标题")
    definition: str = Field(description="核心定义和基本概念")
    content: str = Field(description="知识点详细内容和解释")
    importance: str = Field(description="重要程度：基础/重要/核心")
    examples: List[str] = Field(description="具体例子和应用场景")
    key_points: List[str] = Field(description="关键要点和记忆点")
    common_mistakes: Optional[List[str]] = Field(default=None, description="常见误区和注意事项")
    connections: Optional[List[str]] = Field(default=None, description="与其他知识点的关联")


class StudyTip(BaseModel):
    """Schema for study tips and techniques."""
    category: str = Field(description="技巧类别：记忆/理解/应用/解题")
    title: str = Field(description="技巧标题")
    content: str = Field(description="技巧详细内容和方法")
    steps: List[str] = Field(description="具体操作步骤")
    applicable_scenarios: List[str] = Field(description="适用场景和条件")
    examples: Optional[List[str]] = Field(default=None, description="使用实例")
    effectiveness: Optional[str] = Field(default=None, description="效果说明")


class ExtendedKnowledge(BaseModel):
    """Schema for extended knowledge."""
    title: str = Field(description="扩展知识标题")
    content: str = Field(description="扩展知识详细内容")
    connection: str = Field(description="与主题的关联和意义")
    difficulty_level: str = Field(description="难度等级：简单/中等/困难")
    applications: List[str] = Field(description="实际应用场景")
    historical_context: Optional[str] = Field(default=None, description="历史背景或发展")
    cross_subject_links: Optional[List[str]] = Field(default=None, description="跨学科联系")


class LearningResource(BaseModel):
    """Schema for learning resources."""
    type: str = Field(description="资源类型：书籍/网站/视频/工具")
    title: str = Field(description="资源标题")
    description: str = Field(description="资源描述")
    recommendation_reason: str = Field(description="推荐理由")


class FAQ(BaseModel):
    """Schema for frequently asked questions."""
    question: str = Field(description="常见问题")
    answer: str = Field(description="详细解答")
    category: str = Field(description="问题类别")


class PracticeRecommendation(BaseModel):
    """Schema for practice recommendations."""
    level: str = Field(description="练习层次：基础/提高/综合/创新")
    title: str = Field(description="练习标题")
    description: str = Field(description="练习描述")
    methods: List[str] = Field(description="具体练习方法")
    time_suggestion: str = Field(description="时间安排建议")


class StudyNotes(BaseModel):
    """Schema for complete study notes."""
    topic_overview: str = Field(description="详细主题概述")
    learning_objectives: List[str] = Field(description="学习目标")
    knowledge_points: List[KnowledgePoint] = Field(description="核心知识点")
    study_tips: List[StudyTip] = Field(description="学习技巧")
    extended_knowledge: List[ExtendedKnowledge] = Field(description="扩展知识")
    summary: str = Field(description="系统总结")
    knowledge_structure: str = Field(description="知识结构描述")
    practice_recommendations: List[PracticeRecommendation] = Field(description="分层练习推荐")
    learning_resources: List[LearningResource] = Field(description="学习资源推荐")
    faqs: List[FAQ] = Field(description="常见问题解答")
    self_assessment: List[str] = Field(description="自我检测方法")