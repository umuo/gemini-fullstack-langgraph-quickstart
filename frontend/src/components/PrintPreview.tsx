import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Printer, Download, Eye, X, Settings } from "lucide-react";

interface PrintPreviewProps {
  filename: string;
  title: string;
  onPrint?: () => void;
}

export function PrintPreview({ filename, title, onPrint }: PrintPreviewProps) {
  const [showModal, setShowModal] = useState(false);

  const apiUrl = import.meta.env.DEV
    ? "http://localhost:2024"
    : "http://localhost:8123";

  const handlePrintPreview = () => {
    const previewUrl = `${apiUrl}/preview-pdf/${filename}`;
    const downloadUrl = `${apiUrl}/download-pdf/${filename}`;
    
    // 创建新窗口用于打印预览
    const printWindow = window.open('', '_blank', 'width=1000,height=700,scrollbars=yes,resizable=yes');
    
    if (printWindow) {
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>打印预览 - ${title}</title>
          <style>
            body {
              margin: 0;
              padding: 20px;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background-color: #f5f5f5;
            }
            .print-header {
              background: white;
              padding: 15px 20px;
              border-radius: 8px;
              margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              display: flex;
              justify-content: space-between;
              align-items: center;
            }
            .print-controls {
              display: flex;
              gap: 10px;
              align-items: center;
            }
            .print-button {
              background: #2563eb;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 14px;
              display: flex;
              align-items: center;
              gap: 6px;
            }
            .print-button:hover {
              background: #1d4ed8;
            }
            .download-button {
              background: #059669;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 14px;
              display: flex;
              align-items: center;
              gap: 6px;
            }
            .download-button:hover {
              background: #047857;
            }
            .close-button {
              background: #6b7280;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
              font-size: 14px;
            }
            .close-button:hover {
              background: #4b5563;
            }
            .pdf-container {
              background: white;
              border-radius: 8px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              overflow: hidden;
              height: calc(100vh - 200px);
            }
            iframe {
              width: 100%;
              height: 100%;
              border: none;
            }
            .loading {
              display: flex;
              justify-content: center;
              align-items: center;
              height: 200px;
              color: #6b7280;
            }
            .print-settings {
              background: white;
              padding: 15px;
              border-radius: 8px;
              margin-bottom: 20px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .settings-grid {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
              gap: 15px;
              margin-top: 10px;
            }
            .setting-item {
              display: flex;
              flex-direction: column;
              gap: 5px;
            }
            .setting-label {
              font-weight: 500;
              font-size: 14px;
              color: #374151;
            }
            select {
              padding: 6px 10px;
              border: 1px solid #d1d5db;
              border-radius: 4px;
              font-size: 14px;
            }
            @media print {
              .print-header, .print-settings {
                display: none !important;
              }
              .pdf-container {
                box-shadow: none;
                border-radius: 0;
                height: auto;
              }
              body {
                background: white;
                padding: 0;
              }
            }
          </style>
        </head>
        <body>
          <div class="print-header">
            <h2 style="margin: 0; color: #1f2937;">${title}</h2>
            <div class="print-controls">
              <button class="download-button" onclick="downloadPDF()">
                📥 下载PDF
              </button>
              <button class="print-button" onclick="printPDF()">
                🖨️ 打印
              </button>
              <button class="close-button" onclick="window.close()">
                ❌ 关闭
              </button>
            </div>
          </div>
          
          <div class="print-settings">
            <h3 style="margin: 0 0 10px 0; color: #1f2937;">打印设置</h3>
            <div class="settings-grid">
              <div class="setting-item">
                <label class="setting-label">纸张大小</label>
                <select onchange="updatePrintSettings()">
                  <option value="A4">A4 (210×297mm)</option>
                  <option value="A3">A3 (297×420mm)</option>
                  <option value="Letter">Letter (216×279mm)</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label">页面方向</label>
                <select onchange="updatePrintSettings()">
                  <option value="portrait">纵向</option>
                  <option value="landscape">横向</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label">页边距</label>
                <select onchange="updatePrintSettings()">
                  <option value="normal">标准 (2.5cm)</option>
                  <option value="narrow">窄 (1.3cm)</option>
                  <option value="wide">宽 (3.8cm)</option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="pdf-container">
            <div class="loading" id="loading">
              📄 正在加载PDF预览...
            </div>
            <iframe id="pdf-frame" src="${previewUrl}" title="PDF预览" style="display: none;"></iframe>
          </div>
          
          <script>
            function downloadPDF() {
              const link = document.createElement('a');
              link.href = '${downloadUrl}';
              link.download = '${filename}';
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            
            function printPDF() {
              // 尝试打印iframe内容
              const iframe = document.getElementById('pdf-frame');
              if (iframe.contentWindow) {
                iframe.contentWindow.print();
              } else {
                // 备选方案：打印整个窗口
                window.print();
              }
            }
            
            function updatePrintSettings() {
              console.log('打印设置已更新');
            }
            
            // PDF加载完成后显示
            window.onload = function() {
              const iframe = document.getElementById('pdf-frame');
              const loading = document.getElementById('loading');
              
              iframe.onload = function() {
                loading.style.display = 'none';
                iframe.style.display = 'block';
              };
              
              // 如果5秒后还没加载完成，显示错误信息
              setTimeout(function() {
                if (iframe.style.display === 'none') {
                  loading.innerHTML = '❌ PDF加载失败，请检查文件是否存在';
                  loading.style.color = '#ef4444';
                }
              }, 5000);
            };
          </script>
        </body>
        </html>
      `);
      printWindow.document.close();
    } else {
      // 如果弹窗被阻止，则直接在当前窗口打开预览
      window.open(previewUrl, '_blank');
    }
  };

  const handleDirectPrint = () => {
    const previewUrl = `${apiUrl}/preview-pdf/${filename}`;
    const printWindow = window.open(previewUrl, '_blank');
    
    if (printWindow) {
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print();
        }, 1500); // 增加延迟确保PDF完全加载
      };
    }
  };

  const handleDownload = () => {
    const pdfUrl = `${apiUrl}/download-pdf/${filename}`;
    const link = document.createElement("a");
    link.href = pdfUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setShowModal(true)}
      >
        <Printer className="mr-2 h-4 w-4" />
        打印预览
      </Button>

      {/* 简单的模态框 */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Printer className="h-5 w-5" />
                  打印选项
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowModal(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-gray-600">
                选择打印方式：
              </div>
              
              <div className="space-y-2">
                <Button 
                  onClick={() => {
                    handlePrintPreview();
                    setShowModal(false);
                    onPrint?.();
                  }}
                  className="w-full"
                >
                  <Eye className="mr-2 h-4 w-4" />
                  打印预览（推荐）
                </Button>
                
                <Button 
                  onClick={() => {
                    handleDirectPrint();
                    setShowModal(false);
                    onPrint?.();
                  }}
                  variant="outline"
                  className="w-full"
                >
                  <Printer className="mr-2 h-4 w-4" />
                  直接打印
                </Button>
                
                <Button 
                  onClick={() => {
                    handleDownload();
                    setShowModal(false);
                  }}
                  variant="outline"
                  className="w-full"
                >
                  <Download className="mr-2 h-4 w-4" />
                  下载PDF
                </Button>
              </div>
              
              <div className="text-xs text-gray-500 pt-2 border-t">
                💡 <strong>打印预览</strong>：在新窗口中打开PDF，可以调整打印设置<br/>
                🖨️ <strong>直接打印</strong>：立即打开打印对话框<br/>
                📥 <strong>下载PDF</strong>：保存PDF文件到本地
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}