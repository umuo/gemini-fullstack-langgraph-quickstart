import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { ExamGenerationProgress } from "@/components/ExamGenerationProgress";
import { Loader2, Download, Eye, Printer } from "lucide-react";
import { PrintPreview } from "@/components/PrintPreview";

interface ExamQuestion {
  question_id: number;
  question_type: string;
  question_text: string;
  options?: string[];
  correct_answer?: string;
  points: number;
  explanation?: string;
}

interface ExamResult {
  success: boolean;
  exam_title: string;
  exam_instructions: string;
  questions: ExamQuestion[];
  pdf_path: string;
  answer_key_path: string;
  notes_path: string;
  study_notes: any;
  message: string;
}

interface GenerationStep {
  step: string;
  message: string;
  progress: number;
  data?: any;
  error?: string;
  completed?: boolean;
}

export function ExamGenerator() {
  const [educationLevel, setEducationLevel] = useState("primary");
  const [subject, setSubject] = useState("");
  const [knowledgeTopic, setKnowledgeTopic] = useState("");
  const [difficultyLevel, setDifficultyLevel] = useState("medium");
  const [questionCount, setQuestionCount] = useState(10);
  const [questionTypes, setQuestionTypes] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [examResult, setExamResult] = useState<ExamResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [generationSteps, setGenerationSteps] = useState<GenerationStep[]>([]);
  const [currentStep, setCurrentStep] = useState<string>("");

  // 学段配置
  const educationLevels = [
    { id: "primary", label: "小学", grades: "1-6年级" },
    { id: "middle", label: "初中", grades: "7-9年级" },
    { id: "high", label: "高中", grades: "10-12年级" }
  ];

  // 学科配置
  const subjectsByLevel = {
    primary: [
      { id: "chinese", label: "语文" },
      { id: "math", label: "数学" },
      { id: "english", label: "英语" },
      { id: "science", label: "科学" },
      { id: "moral", label: "道德与法治" },
      { id: "art", label: "美术" },
      { id: "music", label: "音乐" },
      { id: "pe", label: "体育" }
    ],
    middle: [
      { id: "chinese", label: "语文" },
      { id: "math", label: "数学" },
      { id: "english", label: "英语" },
      { id: "physics", label: "物理" },
      { id: "chemistry", label: "化学" },
      { id: "biology", label: "生物" },
      { id: "history", label: "历史" },
      { id: "geography", label: "地理" },
      { id: "politics", label: "道德与法治" },
      { id: "pe", label: "体育" },
      { id: "art", label: "美术" },
      { id: "music", label: "音乐" }
    ],
    high: [
      { id: "chinese", label: "语文" },
      { id: "math", label: "数学" },
      { id: "english", label: "英语" },
      { id: "physics", label: "物理" },
      { id: "chemistry", label: "化学" },
      { id: "biology", label: "生物" },
      { id: "history", label: "历史" },
      { id: "geography", label: "地理" },
      { id: "politics", label: "思想政治" },
      { id: "technology", label: "信息技术" }
    ]
  };

  // 题目类型配置（根据学段和学科智能推荐）
  const getRecommendedQuestionTypes = (level: string, subjectId: string) => {
    const baseTypes = [
      { id: "multiple_choice", label: "选择题" },
      { id: "true_false", label: "判断题" },
      { id: "fill_blank", label: "填空题" },
      { id: "short_answer", label: "简答题" },
      { id: "essay", label: "论述题" },
      { id: "calculation", label: "计算题" },
      { id: "analysis", label: "分析题" },
      { id: "application", label: "应用题" }
    ];

    // 根据学段筛选
    let recommendedTypes = [...baseTypes];
    
    if (level === "primary") {
      // 小学：主要是基础题型
      recommendedTypes = baseTypes.filter(type => 
        ["multiple_choice", "true_false", "fill_blank", "short_answer", "calculation", "application"].includes(type.id)
      );
    } else if (level === "middle") {
      // 初中：增加分析题
      recommendedTypes = baseTypes.filter(type => 
        ["multiple_choice", "true_false", "fill_blank", "short_answer", "calculation", "analysis", "application"].includes(type.id)
      );
    }
    // 高中：所有题型都可用

    // 根据学科进一步筛选
    if (["math", "physics", "chemistry"].includes(subjectId)) {
      // 理科：重点推荐计算题和应用题
      return recommendedTypes;
    } else if (["chinese", "english", "history", "politics"].includes(subjectId)) {
      // 文科：重点推荐论述题和分析题
      return recommendedTypes.filter(type => 
        !["calculation"].includes(type.id)
      );
    }

    return recommendedTypes;
  };

  const availableQuestionTypes = getRecommendedQuestionTypes(educationLevel, subject);

  // 当学段或学科改变时，自动设置推荐的题目类型
  const handleEducationLevelChange = (level: string) => {
    setEducationLevel(level);
    setSubject(""); // 重置学科选择
    setQuestionTypes([]); // 重置题目类型
  };

  const handleSubjectChange = (subjectId: string) => {
    setSubject(subjectId);
    // 自动选择推荐的题目类型
    const recommended = getRecommendedQuestionTypes(educationLevel, subjectId);
    const defaultTypes = recommended.slice(0, 3).map(t => t.id); // 默认选择前3种
    setQuestionTypes(defaultTypes);
  };

  const handleQuestionTypeChange = (typeId: string, checked: boolean) => {
    if (checked) {
      setQuestionTypes([...questionTypes, typeId]);
    } else {
      setQuestionTypes(questionTypes.filter(t => t !== typeId));
    }
  };

  const handleGenerateExam = async () => {
    if (!subject) {
      setError("请选择学科");
      return;
    }

    if (!knowledgeTopic.trim()) {
      setError("请输入知识点主题");
      return;
    }

    if (questionTypes.length === 0) {
      setError("请至少选择一种题目类型");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setExamResult(null);
    setGenerationSteps([]);
    setCurrentStep("");

    try {
      const apiUrl = import.meta.env.DEV
        ? "http://localhost:2024"
        : "http://localhost:8123";
      
      const response = await fetch(`${apiUrl}/generate-exam-stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          education_level: educationLevel,
          subject: subject,
          knowledge_topic: knowledgeTopic,
          difficulty_level: difficultyLevel,
          question_count: questionCount,
          question_types: questionTypes,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("无法读取响应流");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              setCurrentStep(data.step);
              
              // 更新步骤列表
              setGenerationSteps(prev => {
                const newSteps = [...prev];
                const existingIndex = newSteps.findIndex(s => s.step === data.step);
                
                const stepData: GenerationStep = {
                  step: data.step,
                  message: data.message,
                  progress: data.progress,
                  data: data.data,
                  error: data.error,
                  completed: data.progress === 100 && !data.error
                };

                if (existingIndex >= 0) {
                  newSteps[existingIndex] = stepData;
                } else {
                  newSteps.push(stepData);
                }

                // 标记之前的步骤为已完成
                newSteps.forEach((step, index) => {
                  if (index < newSteps.length - 1 && step.progress === 100 && !step.error) {
                    step.completed = true;
                  }
                });

                return newSteps;
              });

              // 如果完成，设置结果
              if (data.step === 'completed' && data.result) {
                setExamResult(data.result);
              }

              // 如果有错误，设置错误信息
              if (data.error) {
                setError(data.error);
              }

            } catch (e) {
              console.error('解析SSE数据失败:', e);
            }
          }
        }
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : "生成过程中发生错误");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadPDF = (filename: string) => {
    const apiUrl = import.meta.env.DEV
      ? "http://localhost:2024"
      : "http://localhost:8123";
    const link = document.createElement("a");
    link.href = `${apiUrl}/download-pdf/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrintPreview = (filename: string) => {
    const apiUrl = import.meta.env.DEV
      ? "http://localhost:2024"
      : "http://localhost:8123";
    const pdfUrl = `${apiUrl}/download-pdf/${filename}`;
    
    // 创建新窗口用于打印预览
    const printWindow = window.open(pdfUrl, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
    
    if (printWindow) {
      // 等待PDF加载完成后自动打开打印对话框
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print();
        }, 1000);
      };
    } else {
      // 如果弹窗被阻止，则直接在当前窗口打开
      window.open(pdfUrl, '_blank');
    }
  };

  const getFilenameFromPath = (path: string) => {
    return path.split('/').pop() || path;
  };

  // 根据学段和学科获取主题占位符
  const getTopicPlaceholder = (level: string, subjectId: string) => {
    const placeholders = {
      primary: {
        chinese: "例如：拼音、识字、古诗词、阅读理解...",
        math: "例如：加减法、乘除法、分数、几何图形...",
        english: "例如：字母、单词、简单对话、语法...",
        science: "例如：动植物、天气、物质变化...",
        moral: "例如：诚实守信、团结友爱、安全知识...",
        art: "例如：色彩搭配、绘画技巧、手工制作...",
        music: "例如：节拍、音符、歌曲演唱...",
        pe: "例如：基本动作、体育游戏、健康知识..."
      },
      middle: {
        chinese: "例如：现代文阅读、古文翻译、作文写作...",
        math: "例如：代数方程、几何证明、函数图像...",
        english: "例如：语法时态、阅读理解、写作技巧...",
        physics: "例如：力学、电学、光学、热学...",
        chemistry: "例如：原子结构、化学反应、酸碱盐...",
        biology: "例如：细胞结构、遗传变异、生态系统...",
        history: "例如：中国古代史、世界史、历史事件...",
        geography: "例如：地形地貌、气候特征、人文地理...",
        politics: "例如：法律知识、道德品质、公民权利...",
        pe: "例如：体育技能、运动规则、健康知识...",
        art: "例如：美术技法、艺术欣赏、创作实践...",
        music: "例如：音乐理论、乐器演奏、音乐欣赏..."
      },
      high: {
        chinese: "例如：现代文阅读、古诗文鉴赏、议论文写作...",
        math: "例如：函数与导数、立体几何、概率统计...",
        english: "例如：阅读理解、完形填空、书面表达...",
        physics: "例如：力学、电磁学、原子物理、波动光学...",
        chemistry: "例如：有机化学、无机化学、化学平衡...",
        biology: "例如：分子生物学、遗传工程、生态环境...",
        history: "例如：中国近现代史、世界史、史学方法...",
        geography: "例如：自然地理、人文地理、区域地理...",
        politics: "例如：马克思主义、政治制度、经济生活...",
        technology: "例如：编程基础、网络技术、信息安全..."
      }
    };

    return placeholders[level as keyof typeof placeholders]?.[subjectId as keyof any] || "请输入具体的知识点主题";
  };

  return (
    <div className="h-full overflow-auto bg-neutral-800 text-neutral-100">
      <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">试卷生成器</h1>
        <p className="text-center text-muted-foreground">
          输入知识点，AI将为您生成专业的试卷
        </p>
      </div>

      {/* 进度展示 */}
      {(isGenerating || generationSteps.length > 0) && (
        <ExamGenerationProgress 
          steps={generationSteps}
          currentStep={currentStep}
          isGenerating={isGenerating}
        />
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>试卷配置</CardTitle>
          <CardDescription>
            设置试卷的基本参数和要求
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 学段选择 */}
          <div className="space-y-2">
            <Label>学段选择</Label>
            <div className="grid grid-cols-3 gap-3">
              {educationLevels.map((level) => (
                <div
                  key={level.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    educationLevel === level.id
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onClick={() => handleEducationLevelChange(level.id)}
                >
                  <div className="font-medium">{level.label}</div>
                  <div className="text-xs text-gray-500">{level.grades}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 学科选择 */}
          <div className="space-y-2">
            <Label htmlFor="subject">学科选择</Label>
            <Select value={subject} onValueChange={handleSubjectChange}>
              <SelectTrigger>
                <SelectValue placeholder="请选择学科" />
              </SelectTrigger>
              <SelectContent>
                {subjectsByLevel[educationLevel as keyof typeof subjectsByLevel]?.map((subj) => (
                  <SelectItem key={subj.id} value={subj.id}>
                    {subj.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 知识点主题 */}
          <div className="space-y-2">
            <Label htmlFor="topic">知识点主题</Label>
            <Input
              id="topic"
              placeholder={subject ? getTopicPlaceholder(educationLevel, subject) : "请先选择学科"}
              value={knowledgeTopic}
              onChange={(e) => setKnowledgeTopic(e.target.value)}
              disabled={!subject}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="difficulty">难度等级</Label>
              <Select value={difficultyLevel} onValueChange={setDifficultyLevel}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">简单</SelectItem>
                  <SelectItem value="medium">中等</SelectItem>
                  <SelectItem value="hard">困难</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="count">题目数量</Label>
              <Input
                id="count"
                type="number"
                min="5"
                max="50"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value) || 10)}
              />
            </div>
          </div>

          {/* 题目类型选择 */}
          {subject && (
            <div className="space-y-3">
              <Label>题目类型 <span className="text-sm text-gray-500">(已根据学段和学科智能推荐)</span></Label>
              <div className="grid grid-cols-2 gap-3">
                {availableQuestionTypes.map((type) => (
                  <div key={type.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={type.id}
                      checked={questionTypes.includes(type.id)}
                      onCheckedChange={(checked) => 
                        handleQuestionTypeChange(type.id, checked as boolean)
                      }
                    />
                    <Label htmlFor={type.id} className="text-sm">
                      {type.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded">
              {error}
            </div>
          )}

          <Button 
            onClick={handleGenerateExam} 
            disabled={isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                生成中...
              </>
            ) : (
              "生成试卷"
            )}
          </Button>
        </CardContent>
      </Card>

      {examResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{examResult.exam_title}</span>
              <div className="flex gap-2 flex-wrap">
                <PrintPreview
                  filename={getFilenameFromPath(examResult.pdf_path)}
                  title={examResult.exam_title}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownloadPDF(getFilenameFromPath(examResult.pdf_path))}
                >
                  <Download className="mr-2 h-4 w-4" />
                  下载试卷
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownloadPDF(getFilenameFromPath(examResult.answer_key_path))}
                >
                  <Download className="mr-2 h-4 w-4" />
                  下载答案
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownloadPDF(getFilenameFromPath(examResult.notes_path))}
                >
                  <Download className="mr-2 h-4 w-4" />
                  下载笔记
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 p-4 bg-gray-50 rounded">
              <h3 className="font-semibold mb-2">考试说明：</h3>
              <p className="text-sm whitespace-pre-wrap">{examResult.exam_instructions}</p>
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold">试卷预览：</h3>
              {examResult.questions.map((question, index) => (
                <div key={question.question_id} className="border p-4 rounded">
                  <div className="font-medium mb-2">
                    {index + 1}. {question.question_text} ({question.points}分)
                  </div>
                  
                  {question.question_type === "multiple_choice" && question.options && (
                    <div className="ml-4 space-y-1">
                      {question.options.map((option, optIndex) => (
                        <div key={optIndex} className="text-sm">
                          {String.fromCharCode(65 + optIndex)}. {option}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {question.question_type === "true_false" && (
                    <div className="ml-4 text-sm">
                      ☐ 正确 &nbsp;&nbsp;&nbsp;&nbsp; ☐ 错误
                    </div>
                  )}
                  
                  {question.question_type === "fill_blank" && (
                    <div className="ml-4 text-sm text-gray-500">
                      [填空题 - 请在空白处填入答案]
                    </div>
                  )}
                  
                  {(question.question_type === "calculation" || question.question_type === "application") && (
                    <div className="ml-4 text-sm text-gray-500">
                      [计算/应用题 - 请写出解题过程]
                    </div>
                  )}
                  
                  {question.question_type === "analysis" && (
                    <div className="ml-4 text-sm text-gray-500">
                      [分析题 - 请分析并说明理由]
                    </div>
                  )}
                  
                  {(question.question_type === "short_answer" || question.question_type === "essay") && (
                    <div className="ml-4 text-sm text-gray-500">
                      [答题区域]
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      </div>
    </div>
  );
}