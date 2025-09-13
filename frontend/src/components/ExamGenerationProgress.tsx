import { CheckCircle, Clock, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface GenerationStep {
  step: string;
  message: string;
  progress: number;
  data?: any;
  error?: string;
  completed?: boolean;
}

interface ExamGenerationProgressProps {
  steps: GenerationStep[];
  currentStep: string;
  isGenerating: boolean;
}

export function ExamGenerationProgress({ steps, currentStep, isGenerating }: ExamGenerationProgressProps) {
  const stepLabels = {
    initializing: "初始化",
    research_topics: "生成研究主题",
    research_knowledge: "收集知识内容", 
    generate_questions: "生成题目",
    compile_metadata: "编译试卷信息",
    generate_notes: "生成学习笔记",
    generate_pdf: "生成PDF文件",
    completed: "完成",
    error: "错误"
  };

  const getStepIcon = (step: GenerationStep, isCurrent: boolean) => {
    if (step.error) {
      return <AlertCircle className="h-5 w-5 text-red-500" />;
    }
    if (step.completed || (step.progress === 100 && !step.error)) {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    if (isCurrent && isGenerating) {
      return <Clock className="h-5 w-5 text-blue-500 animate-spin" />;
    }
    if (step.progress > 0) {
      return <div className="h-5 w-5 rounded-full border-2 border-blue-500 bg-blue-100" />;
    }
    return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
  };

  const currentProgress = steps.length > 0 ? steps[steps.length - 1]?.progress || 0 : 0;

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>生成进度</span>
          {isGenerating && <Clock className="h-5 w-5 animate-spin text-blue-500" />}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 总体进度条 */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>总体进度</span>
            <span>{Math.round(currentProgress)}%</span>
          </div>
          <Progress value={currentProgress} className="w-full" />
        </div>

        {/* 步骤列表 */}
        <div className="space-y-3">
          {steps.map((step, index) => {
            const isCurrent = step.step === currentStep;
            const stepLabel = stepLabels[step.step as keyof typeof stepLabels] || step.step;
            
            return (
              <div
                key={index}
                className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                  isCurrent ? 'bg-blue-50 border border-blue-200' : 
                  step.completed || (step.progress === 100 && !step.error) ? 'bg-green-50 border border-green-200' :
                  step.error ? 'bg-red-50 border border-red-200' : 
                  step.progress > 0 ? 'bg-blue-50 border border-blue-100' : 'bg-gray-50'
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getStepIcon(step, isCurrent)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className={`font-medium ${
                      isCurrent ? 'text-blue-700' :
                      step.completed || (step.progress === 100 && !step.error) ? 'text-green-700' :
                      step.error ? 'text-red-700' : 
                      step.progress > 0 ? 'text-blue-600' : 'text-gray-700'
                    }`}>
                      {stepLabel}
                    </h4>
                    <span className="text-sm text-gray-500">
                      {step.progress}%
                    </span>
                  </div>
                  
                  <p className={`text-sm mt-1 ${
                    isCurrent ? 'text-blue-600' :
                    step.completed || (step.progress === 100 && !step.error) ? 'text-green-600' :
                    step.error ? 'text-red-600' : 
                    step.progress > 0 ? 'text-blue-500' : 'text-gray-600'
                  }`}>
                    {step.message}
                  </p>

                  {/* 步骤进度条 */}
                  {step.progress > 0 && step.progress < 100 && !step.error && (
                    <div className="mt-2">
                      <Progress value={step.progress} className="h-1" />
                    </div>
                  )}

                  {/* 显示额外数据 */}
                  {step.data && (
                    <div className="mt-2 text-xs text-gray-500">
                      {step.step === 'research_topics' && step.data.length > 0 && (
                        <div>
                          <span className="font-medium">研究主题: </span>
                          {step.data.slice(0, 2).join(', ')}
                          {step.data.length > 2 && ` 等${step.data.length}个主题`}
                        </div>
                      )}
                      {step.step === 'generate_questions' && step.data.question_count && (
                        <div>
                          <span className="font-medium">已生成题目数: </span>
                          {step.data.question_count}
                        </div>
                      )}
                      {step.step === 'compile_metadata' && step.data.title && (
                        <div>
                          <span className="font-medium">试卷标题: </span>
                          {step.data.title}
                        </div>
                      )}
                    </div>
                  )}

                  {/* 错误信息 */}
                  {step.error && (
                    <div className="mt-2 text-sm text-red-600 bg-red-100 p-2 rounded">
                      {step.error}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* 当前状态信息 */}
        {isGenerating && (
          <div className="text-center text-sm text-gray-500 mt-4">
            正在生成试卷，请稍候...
          </div>
        )}
      </CardContent>
    </Card>
  );
}